import cv2
from ultralytics import YOLO

# Cargar el modelo super ligero (se descargará solo la primera vez, pesa solo ~6MB)
print("Cargando modelo de IA...")
model = YOLO('yolov8n.pt')

# Abrir cámara web (0 es la cámara predeterminada de la tablet)
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Error: No se pudo acceder a la cámara web.")
    exit()

print("Cámara lista. Presiona la tecla 'q' en la ventana para salir.")

while True:
    ret, frame = cap.read()
    if not ret:
        print("No se pudo recibir señal de la cámara.")
        break

    # Ejecutar detección (confianza mínima del 40%)
    results = model(frame, conf=0.4, verbose=False)

    # Dibujar las cajas de detección sobre la imagen
    annotated_frame = results[0].plot()

    # Mostrar la ventana en pantalla
    cv2.imshow("Prueba de Vision - Dog Station", annotated_frame)

    # Salir si se presiona la tecla 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()