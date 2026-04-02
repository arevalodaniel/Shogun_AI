# 🛡️ Shogun AI v2.0 - Advanced Biometric Recognition System

Sistema de reconocimiento facial progresivo con validación de calidad en tiempo real y detección de vitalidad (Anti-Spoofing). Desarrollado para operar bajo estrictos estándares de ciberseguridad, privacidad de datos y eficiencia computacional en el borde (Edge Computing).

## ✨ Características Principales
* **Anti-Spoofing Biométrico (Liveness Detection):** Implementación de Google MediaPipe para calcular el *Eye Aspect Ratio* (EAR) en tiempo real, monitoreando la fluctuación del parpadeo y bloqueando ataques de suplantación con fotografías estáticas.
* **Arquitectura Asíncrona (Multithreading):** Separación paralela de la captura I/O de video y la inferencia de la Red Neuronal (CNN) para mantener el rendimiento fluido (>30 FPS) en hardware estándar sin bloqueos en la interfaz.
* **Reconocimiento con FaceNet:** Extracción de características (embeddings) irreversibles de 128 dimensiones mediante TensorFlow/Keras, comparados a través de Distancia Euclidiana.
* **Tolerancia al Estrés (O(N)):** Motor de búsqueda optimizado con NumPy, capaz de buscar y validar identidades en una base de datos con más de 10,000 registros en un promedio inferior a 0.60 segundos.
* **HUD Cibernético:** Interfaz superpuesta (Overlay) generada con OpenCV que muestra en tiempo real telemetría de rendimiento (FPS), datos de vitalidad, distancias matemáticas y estado del sistema.

## 🛠️ Tecnologías y Dependencias
Para garantizar la estabilidad del sistema y evitar conflictos de compatibilidad de arquitectura cruzada, se requiere el siguiente entorno lógico estricto:
* Python 3.10
* TensorFlow == 2.15.0
* Keras == 2.15.0
* tf-keras == 2.15.0
* MediaPipe == 0.10.5
* DeepFace
* OpenCV-Python
* CustomTkinter

## 🚀 Instalación y Despliegue

1. **Clonar el repositorio:**
   ```bash
   git clone [https://github.com/TU_USUARIO/shogun-ai.git](https://github.com/TU_USUARIO/shogun-ai.git)
   cd shogun-ai
2. **Crear y activar entorno virtual (Recomendado):**
    python -m venv env
    # En Windows:
    env\Scripts\activate

3. **Instalar dependencias blindadas:**
    pip install -r requirements.txt

4. **Generar la Base de Datos de Prueba (Stress Test):
    (Por motivos de seguridad y optimización de almacenamiento en el repositorio, la base de datos no se incluye. Debes generarla localmente).**
    python generador_dummies.py

5. **Ejecutar el sistema:** 
    python main.py

🎮 Controles del Sistema

    r : Registrar rostro nuevo (Inicia el protocolo de extracción biométrica. Requiere validación de vitalidad obligatoria).

    i : Identificar (Procesa el frame actual a través de la red neuronal).

    b : Dar de baja (Elimina el vector de un usuario de la base de datos).

    q : Salir (Cierra los hilos de ejecución y apaga la cámara).

**Autor: Daniel Santoyo Arevalo**