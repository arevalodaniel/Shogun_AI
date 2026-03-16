# 🥷 Shogun AI - Sistema Biométrico Facial de Grado Industrial

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![OpenCV](https://img.shields.io/badge/OpenCV-4.x-green.svg)
![TensorFlow](https://img.shields.io/badge/TensorFlow-2.x-orange.svg)
![DeepFace](https://img.shields.io/badge/DeepFace-Facenet-red.svg)

**Shogun AI** es un sistema avanzado de reconocimiento facial diseñado para entornos de control de acceso y seguridad perimetral. Utiliza modelos de Deep Learning (*Facenet*) para extraer embeddings faciales y calcular distancias euclidianas en tiempo real, logrando tiempos de respuesta de **~0.40 segundos**.

## ✨ Características Principales

* ⚡ **Ultra Baja Latencia:** Identificación biométrica en menos de 0.5 segundos.
* 🧠 **Deep Learning (Facenet):** Uso de redes neuronales convolucionales para extraer topología facial en lugar de almacenar fotografías, maximizando la precisión y la privacidad.
* 🛡️ **Filtro de Calidad por Varianza Laplaciana:** El sistema rechaza automáticamente rostros borrosos o saturados de luz para mantener la integridad de la base de datos.
* 🧵 **Arquitectura Multihilo (Threading):** Retroalimentación por voz (Text-to-Speech) asíncrona que no bloquea el hilo principal de procesamiento de video.
* 🔌 **Tolerancia a Fallos de Red:** Reconexión automática (*Graceful Disconnect*) diseñada para operar con cámaras IP y redes WiFi inestables.
* 💻 **UI Asíncrona:** Interfaz gráfica oscura construida con `CustomTkinter` para el enrolamiento continuo de usuarios sin detener la ejecución del sistema.

## ⚙️ Requisitos y Dependencias

Asegúrate de tener instalado Python 3.8 o superior. Puedes instalar todas las dependencias necesarias ejecutando:

```bash
pip install -r requirements.txt

Nota: Shogun AI requiere una cámara web estándar o una cámara IP (compatible con DroidCam/OpenCV) para operar.

🚀 Instalación y Uso

    1. Clonar el repositorio:
    git clone [https://github.com/tu-usuario/Shogun_AI.git](https://github.com/tu-usuario/Shogun_AI.git)
    cd Shogun_AI
    2. Ejecutar el sistema:
    python main.py
    3. Controles en tiempo real:
    Presiona r : Para registrar un nuevo rostro (requiere validación de calidad).

    Presiona i : Para identificar un rostro en pantalla.

    Presiona b: para borrar
    
    Presiona q : Para salir y cerrar el sistema de forma segura.

🔒 Ética y Privacidad de Datos

En cumplimiento con las mejores prácticas de ciberseguridad, Shogun AI NO almacena imágenes en crudo de los usuarios en su base de datos principal. El sistema convierte los rostros en representaciones matemáticas (embeddings multidimensionales). Los archivos .pkl que contienen esta información han sido excluidos del control de versiones por seguridad y privacidad.