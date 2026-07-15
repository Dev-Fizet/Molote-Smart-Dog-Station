# Smart Dog Station IoT 🐾📺

Este proyecto convierte una tableta con recursos limitados (Windows 8.1 Lite) en una **Estación Inteligente de Cuidado, Monitoreo y Entretenimiento Canino**. El sistema utiliza la tableta como el cerebro multimedia (HMI) y un **ESP32** como nodo de hardware para interactuar con sensores y actuadores físicos en tiempo real.

---

## 🛠️ Arquitectura del Sistema

[ Celular (Control) ] <--- (Wi-Fi Local) ---> [ Tablet (Servidor Flask) ]
▲ (Control de VLC / Cámara)
▼ (HTTP API / WebSockets)
[ Nodo ESP32 ] <---> [ Servidores Físicos ]


---

## 📋 Características Principales

1. **Control Remoto de Canales:** Interfaz web responsiva para cambiar videos locales o listas de YouTube en VLC Media Player al instante.
2. **Monitoreo en Tiempo Real:** Transmisión de video en vivo de la cámara integrada de la tablet (sensores `ov2680`/`ov5648`) mediante un stream MJPEG de bajo consumo.
3. **Modo Suspensión Inteligente (Ahorro de Energía):** Apagado lógico de la retroiluminación de la pantalla de la tablet sin suspender el sistema operativo, manteniendo activos los servidores y la comunicación.
4. **Dispensador de Premios Automatizado:** Control de un servomotor acoplado al ESP32 desde un botón dedicado en el celular.
5. **Detección de Presencia:** Automatización mediante un sensor PIR conectado al ESP32 que enciende la pantalla cuando el perro se acerca y la apaga tras un tiempo de inactividad.

---

## 🗂️ Requisitos de Hardware y Software

### Hardware
* **Cerebro:** Tableta Intel Atom (Ej. TR10RS1) corriendo **Windows 8.1 Pro Lite**.
* **Microcontrolador:** ESP32 (NodeMCU o equivalente).
* **Sensor de Presencia:** Sensor de movimiento PIR (HC-SR501).
* **Actuador de Premios:** Servomotor SG90 + mecanismo impreso en 3D o dosificador.
* **Extras opcionales:** Sensor de temperatura/humedad DHT22 y fotoresistencia LDR.

### Software en la Tableta
* **Servidor Local:** Python 3.8.x + Flask (o Node.js).
* **Reproductor Multimedia:** VLC Media Player (con la interfaz web HTTP habilitada).
* **Cámara Streamer:** Yawcam o script nativo en Python con OpenCV.
* **Controlador de Pantalla:** Herramienta `NirCmd` (para suspender la pantalla por consola).

### Software en el ESP32
* **Entorno de desarrollo:** PlatformIO o Arduino IDE.
* **Firmware:** C++ con librerías para conexión Wi-Fi, clientes HTTP y control de servos.

---

## 🚀 Guía de Instalación Rápida

### Paso 1: Configurar la Tableta (Windows 8.1 Lite)
1. Instala los controladores originales para el audio (`Realtek RT5640`) y las cámaras (`ov2680`/`ov5648`) desde el Administrador de Dispositivos usando tu respaldo de drivers.
2. Instala **VLC Media Player**:
   * Activa el acceso web en `Preferencias > Todo > Interfaces principales > Web`.
   * Define una contraseña para la interfaz web (la usará la app de Python).
3. Instala **Python 3.8.x** (última versión compatible con Win 8.1) y añade las dependencias:
   ```bash
   pip install flask requests opencv-python
