import cv2
from ultralytics import YOLO
import requests
import time

# Cargar un modelo ultra ligero de IA (YOLOv8 Nano)
# La primera vez que corre descarga un archivo .pt muy liviano
model = YOLO('yolov8n.pt') 

# Inicializar cámara web (0 suele ser la cámara integrada o web USB)
cap = cv2.VideoCapture(0)

SERVER_URL = "http://localhost:5000"
perro_detectado_previo = False

print("Iniciando detector de mascotas...")

while True:
    ret, frame = cap.read()
    if not ret:
        time.sleep(1)
        continue

    # Ejecutar la detección en el cuadro actual
    results = model(frame, verbose=False)
    
    perro_presente = False
    
    # Recorrer las detecciones del modelo
    for r in results:
        for box in r.boxes:
            # En el dataset COCO, la clase 16 corresponde a "dog" (perro)
            # (También puedes agregar la clase 15 si tienes gatos)
            cls_id = int(box.cls[0])
            conf = float(box.conf[0])
            
            if cls_id == 16 and conf > 0.5:  # Confianza mayor al 50%
                perro_presente = True
                break

    # Lógica de reacción cuando aparece el perrito
    if perro_presente and not perro_detectado_previo:
        print("¡Perrito detectado frente a la pantalla!")
        
        try:
            # 1. Encender la pantalla de la tablet
            requests.post(f"{SERVER_URL}/api/encender_pantalla")
            
            # 2. Reaccion opcional: poner un video de YouTube automáticamente
            # payload = {"url": "https://www.youtube.com/watch?v=tu_video_favorito"}
            # requests.post(f"{SERVER_URL}/api/reproducir_enlace", json=payload)
            
        except Exception as e:
            print(f"Error al comunicar con el servidor Flask: {e}")
            
        perro_detectado_previo = True

    elif not perro_presente and perro_detectado_previo:
        print("El perrito se ha retirado.")
        perro_detectado_previo = False

    # Analizar un fotograma cada 1 o 2 segundos para no saturar el procesador de la tablet
    time.sleep(1.5)

cap.release()