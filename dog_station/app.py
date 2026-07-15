import os
import subprocess
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Configuración de los canales de video (Rutas a tus archivos locales de video o URLs de YouTube)
CANALES = {
    "1": r"C:\videos_perro\ardillas.mp4",        # Cambia por tus rutas reales
    "2": r"C:\videos_perro\pajaros.mp4",
    "3": "https://www.youtube.com/watch?v=XudYHs1du84" # URL de YouTube
}

# Ruta a NirCmd para apagar la pantalla
NIRCMD_PATH = os.path.join(os.path.dirname(__file__), "nircmd.exe")

def ejecutar_nircmd(comando):
    """Ejecuta un comando de NirCmd si el archivo existe."""
    if os.path.exists(NIRCMD_PATH):
        subprocess.run([NIRCMD_PATH] + comando.split(), shell=True)
    else:
        print("Error: No se encuentra nircmd.exe en la carpeta raíz.")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/pantalla', methods=['POST'])
def controlar_pantalla():
    data = request.get_json()
    accion = data.get("accion")
    
    if accion == "apagar":
        # Comando para apagar la pantalla físicamente de inmediato
        ejecutar_nircmd("monitor off")
        return jsonify({"status": "Pantalla apagada"})
    elif accion == "encender":
        # Al mover el mouse sutilmente, Windows enciende la pantalla de inmediato
        ejecutar_nircmd("movecursor 1 1")
        ejecutar_nircmd("movecursor -1 -1")
        return jsonify({"status": "Pantalla encendida"})
    
    return jsonify({"status": "Acción no válida"}), 400

@app.route('/api/canal', methods=['POST'])
def cambiar_canal():
    data = request.get_json()
    canal_id = data.get("canal")
    
    if canal_id in CANALES:
        ruta_video = CANALES[canal_id]
        
        # Cerramos cualquier instancia previa de VLC para que no se encimen
        os.system("taskkill /f /im vlc.exe 2>nul")
        
        # Iniciamos VLC en pantalla completa con el video seleccionado
        # --fullscreen: Pantalla completa, --loop: Repetición infinita
        comando_vlc = f'start "" "C:\\Program Files\\VideoLAN\\VLC\\vlc.exe" --fullscreen --loop "{ruta_video}"'
        os.system(comando_vlc)
        
        return jsonify({"status": f"Cargando canal {canal_id}"})
    
    return jsonify({"status": "Canal no encontrado"}), 404

@app.route('/api/premio', methods=['POST'])
def lanzar_premio():
    # Aquí la tableta le avisa al ESP32 que dispense un premio.
    # Reemplaza con la IP real que le asigne tu módem al ESP32.
    esp32_ip = "192.168.1.100" 
    import requests
    try:
        response = requests.get(f"http://{esp32_ip}/dar-premio", timeout=3)
        return jsonify({"status": "Premio enviado exitosamente", "esp32_response": response.text})
    except Exception as e:
        return jsonify({"status": "Error de comunicación con el ESP32", "error": str(e)}), 500

if __name__ == '__main__':
    # Escucha en el puerto 5000 para toda tu red local
    app.run(host='0.0.0.0', port=5000, debug=True)