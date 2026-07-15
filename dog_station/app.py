import os
import subprocess
import re
from flask import Flask, render_template, jsonify

app = Flask(__name__)

# Configuración de rutas
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
M3U_DIR = os.path.join(BASE_DIR, "m3u_list")
NIRCMD_PATH = os.path.join(BASE_DIR, "nircmd.exe")

# Asegurar que la carpeta m3u_list exista
if not os.path.exists(M3U_DIR):
    os.makedirs(M3U_DIR)

# Variable global para rastrear el canal en reproducción
canal_actual_index = -1

def cargar_canales_desde_m3u():
    """Busca todos los archivos .m3u en la carpeta m3u_list y extrae los canales."""
    canales = []
    
    if not os.path.exists(M3U_DIR):
        return canales

    # Buscar todos los archivos que terminen en .m3u o .m3u8 en la carpeta
    archivos_m3u = [f for f in os.listdir(M3U_DIR) if f.lower().endswith(('.m3u', '.m3u8'))]

    for archivo in archivos_m3u:
        ruta_archivo = os.path.join(M3U_DIR, archivo)
        try:
            with open(ruta_archivo, 'r', encoding='utf-8', errors='ignore') as f:
                lineas = f.readlines()
                
            nombre_canal = None
            for linea in lineas:
                linea = linea.strip()
                if not linea:
                    continue
                
                # Buscar metadatos del canal (#EXTINF:)
                if linea.startswith('#EXTINF:'):
                    # Intentar extraer el nombre del canal después de la última coma
                    match = re.search(r',\s*(.*)', linea)
                    if match:
                        nombre_canal = match.group(1).strip()
                    else:
                        nombre_canal = "Canal sin nombre"
                # Si la línea es una URL y ya tenemos un nombre guardado previamente
                elif linea.startswith(('http://', 'https://', 'rtmp://', 'rtsp://')):
                    if nombre_canal:
                        canales.append({
                            "nombre": nombre_canal,
                            "url": linea
                        })
                        nombre_canal = None  # Resetear para el siguiente canal
                    else:
                        # Si hay una URL directa sin metadatos previos
                        canales.append({
                            "nombre": f"Canal alternativo ({linea[:30]}...)",
                            "url": linea
                        })
        except Exception as e:
            print(f"Error leyendo el archivo {archivo}: {e}")
            
    print(f"--- Se cargaron exitosamente {len(canales)} canales desde la carpeta m3u_list ---")
    return canales

def ejecutar_nircmd(comando):
    if os.path.exists(NIRCMD_PATH):
        subprocess.run([NIRCMD_PATH] + comando.split(), shell=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/siguiente_canal', methods=['POST'])
def siguiente_canal():
    global canal_actual_index
    
    # Recargar la lista en tiempo real por si metiste archivos nuevos
    canales_iptv = cargar_canales_desde_m3u()
    
    if not canales_iptv:
        return jsonify({
            "status": "No se encontraron canales en la carpeta m3u_list",
            "canal_nombre": "Sin canales configurados",
            "index": 0,
            "total": 0
        }), 404
        
    # Incrementar índice y reiniciar si llega al final de la lista cargada
    canal_actual_index = (canal_actual_index + 1) % len(canales_iptv)
    canal = canales_iptv[canal_actual_index]
    
    # Cerrar proceso de VLC anterior
    os.system("taskkill /f /im vlc.exe 2>nul")
    
    # Abrir el nuevo stream en VLC en pantalla completa
    comando_vlc = f'start "" "C:\\Program Files\\VideoLAN\\VLC\\vlc.exe" --fullscreen "{canal["url"]}"'
    os.system(comando_vlc)
    
    return jsonify({
        "status": "Cambiando canal",
        "canal_nombre": canal["nombre"],
        "index": canal_actual_index + 1,
        "total": len(canales_iptv)
    })

@app.route('/api/apagar_pantalla', methods=['POST'])
def apagar_pantalla():
    os.system("taskkill /f /im vlc.exe 2>nul")
    ejecutar_nircmd("monitor off")
    return jsonify({"status": "Pantalla apagada y VLC cerrado"})

@app.route('/api/encender_pantalla', methods=['POST'])
def encender_pantalla():
    ejecutar_nircmd("sendmouse move 1 1")
    return jsonify({"status": "Pantalla activa"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)