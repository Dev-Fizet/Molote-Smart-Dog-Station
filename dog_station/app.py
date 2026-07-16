import os
import subprocess
import re
from flask import Flask, render_template, jsonify, request

app = Flask(__name__)

# Configuración de rutas
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
M3U_DIR = os.path.join(BASE_DIR, "m3u_list")
YT_DIR = os.path.join(BASE_DIR, "youtube_list")
NIRCMD_PATH = os.path.join(BASE_DIR, "nircmd.exe")

# Asegurar que las carpetas existan
for carpeta in [M3U_DIR, YT_DIR]:
    if not os.path.exists(carpeta):
        os.makedirs(carpeta)

canal_actual_index = -1

def cargar_canales_desde_m3u():
    """Lee todos los archivos .m3u de la carpeta m3u_list con codificación UTF-8."""
    canales = []
    if not os.path.exists(M3U_DIR):
        return canales
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
                if linea.startswith('#EXTINF:'):
                    match = re.search(r',\s*(.*)', linea)
                    nombre_canal = match.group(1).strip() if match else "Canal sin nombre"
                elif linea.startswith(('http://', 'https://', 'rtmp://', 'rtsp://')):
                    if nombre_canal:
                        canales.append({"nombre": nombre_canal, "url": linea})
                        nombre_canal = None
                    else:
                        canales.append({"nombre": f"Canal alternativo ({linea[:30]}...)", "url": linea})
        except Exception as e:
            print(f"Error leyendo M3U {archivo}: {e}")
    return canales

def cargar_videos_youtube():
    """Lee todos los archivos .txt de la carpeta youtube_list con codificación UTF-8."""
    videos = []
    if not os.path.exists(YT_DIR):
        return videos
    archivos_txt = [f for f in os.listdir(YT_DIR) if f.lower().endswith('.txt')]
    for archivo in archivos_txt:
        ruta_archivo = os.path.join(YT_DIR, archivo)
        try:
            with open(ruta_archivo, 'r', encoding='utf-8', errors='ignore') as f:
                for linea in f:
                    linea = linea.strip()
                    if not linea or linea.startswith('#'):
                        continue
                    if '|' in linea:
                        partes = linea.split('|', 1)
                        nombre = partes[0].strip()
                        url = partes[1].strip()
                    else:
                        nombre = linea
                        url = linea
                    if "youtube.com" in url or "youtu.be" in url:
                        videos.append({"nombre": nombre, "url": url})
        except Exception as e:
            print(f"Error leyendo txt de YouTube {archivo}: {e}")
    return videos

def cerrar_reproductores():
    os.system("taskkill /f /im vlc.exe 2>nul")
    os.system("taskkill /f /im msedge.exe 2>nul")

# --- RUTAS DE NAVEGACIÓN ---

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/lista')
def lista_canales():
    canales = cargar_canales_desde_m3u()
    videos_yt = cargar_videos_youtube()
    return render_template('lista.html', canales=canales, videos_yt=videos_yt)

# --- API DE CONTROL ---

@app.route('/api/siguiente_canal', methods=['POST'])
def siguiente_canal():
    global canal_actual_index
    canales_iptv = cargar_canales_desde_m3u()
    if not canales_iptv:
        return jsonify({"status": "No hay canales", "canal_nombre": "Sin canales", "index": 0, "total": 0}), 404
    canal_actual_index = (canal_actual_index + 1) % len(canales_iptv)
    canal = canales_iptv[canal_actual_index]
    cerrar_reproductores()
    comando_vlc = f'start "" "C:\\Program Files\\VideoLAN\\VLC\\vlc.exe" --fullscreen "{canal["url"]}"'
    os.system(comando_vlc)
    return jsonify({"status": "Cambiando canal", "canal_nombre": canal["nombre"], "index": canal_actual_index + 1, "total": len(canales_iptv)})

@app.route('/api/reproducir_especifico', methods=['POST'])
def reproducir_especifico():
    data = request.json
    idx = data.get('index')
    canales_iptv = cargar_canales_desde_m3u()
    if idx is None or idx < 0 or idx >= len(canales_iptv):
        return jsonify({"status": "Indice invalido"}), 400
    global canal_actual_index
    canal_actual_index = idx
    canal = canales_iptv[canal_actual_index]
    cerrar_reproductores()
    comando_vlc = f'start "" "C:\\Program Files\\VideoLAN\\VLC\\vlc.exe" --fullscreen "{canal["url"]}"'
    os.system(comando_vlc)
    return jsonify({"status": "Reproduciendo canal", "canal_nombre": canal["nombre"]})

@app.route('/api/reproducir_enlace', methods=['POST'])
def reproducir_enlace():
    data = request.json
    url = data.get('url', '').strip()
    if not url:
        return jsonify({"status": "Enlace vacio"}), 400
    
    cerrar_reproductores()
    
    # Si es YouTube, abrimos el enlace normal para saltarnos el "Error 153" de incrustacion.
    # El parametro autoplay=1 hara que empiece solo.
    if "youtube.com" in url or "youtu.be" in url:
        conector = "&" if "?" in url else "?"
        url_final = f"{url}{conector}autoplay=1"
        comando_edge = f'start msedge --kiosk "{url_final}" --edge-kiosk-type=fullscreen'
        os.system(comando_edge)
        tipo = "Navegador (YouTube Kiosco)"
    else:
        comando_vlc = f'start "" "C:\\Program Files\\VideoLAN\\VLC\\vlc.exe" --fullscreen "{url}"'
        os.system(comando_vlc)
        tipo = "Stream (VLC)"
        
    return jsonify({"status": f"Reproduciendo en {tipo}"})

@app.route('/api/youtube_kiosk', methods=['POST'])
def youtube_kiosk():
    cerrar_reproductores()
    comando_edge = 'start msedge --kiosk "https://www.youtube.com" --edge-kiosk-type=fullscreen'
    os.system(comando_edge)
    return jsonify({"status": "Abriendo YouTube en modo Kiosco"})

@app.route('/api/apagar_pantalla', methods=['POST'])
def apagar_pantalla():
    cerrar_reproductores()
    subprocess.Popen(f'"{NIRCMD_PATH}" monitor off', shell=True)
    return jsonify({"status": "Pantalla apagada y reproductores cerrados"})

@app.route('/api/encender_pantalla', methods=['POST'])
def encender_pantalla():
    if os.path.exists(NIRCMD_PATH):
        subprocess.run([NIRCMD_PATH, "sendmouse", "move", "1", "1"], shell=True)
    return jsonify({"status": "Pantalla activa"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
