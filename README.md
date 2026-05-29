# 🛡️ Shogun AI - Advanced Security & CCTV Dashboard v2.6

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![OpenCV](https://img.shields.io/badge/OpenCV-Vision-green.svg)
![DeepFace](https://img.shields.io/badge/DeepFace-AI-orange.svg)
![FAISS](https://img.shields.io/badge/FAISS-Vector%20DB-red.svg)
![Multithreading](https://img.shields.io/badge/Architecture-Asynchronous-purple.svg)

**Shogun AI** es una suite de seguridad biométrica de grado corporativo que opera bajo el paradigma de **Edge Computing**. Diseñado con una arquitectura de Modo Dual, funciona tanto como un estricto control de acceso anti-spoofing, como un sistema de vigilancia masiva (CCTV) capaz de procesar múltiples vectores faciales en tiempo real sin pérdida de frames.

---

## ✨ Características Principales

* **🔄 Modo Dual (Acceso / CCTV):** Permite cambiar en tiempo real entre una verificación estricta de un solo sujeto o la identificación masiva de múltiples personas en cámara utilizando **Multithreading Asíncrono**.
* **👁️ Identificación Ultrarrápida:** Utiliza el modelo **FaceNet** combinado con **Meta FAISS** para buscar e identificar rostros entre miles de registros en fracciones de segundo.
* **💓 Motor de Vitalidad (Anti-Spoofing):** En el Modo Acceso, implementa **MediaPipe Face Mesh** para calcular el *Eye Aspect Ratio* (EAR) en tiempo real. Exige un reto de parpadeos dinámico y aleatorio para asegurar que el sujeto es un ser humano vivo y rechazar fotografías o pantallas.
* **📲 Alertas IoT en Tiempo Real:** Integración con la API de Telegram para notificar al equipo de seguridad de forma instantánea sobre intentos de intrusión o bloqueos del sistema.
* **📸 Auditoría Visual Edge:** Ante un intento de acceso no autorizado, el sistema captura silenciosamente una fotografía del infractor y la almacena en una bóveda local cifrada (`/evidencias`), cumpliendo con las normativas de privacidad corporativa.
* **📊 Reportes Ejecutivos:** Generación automatizada de reportes CSV con el historial de accesos denegados para auditorías de Recursos Humanos.

---

## 🛠️ Stack Tecnológico y Arquitectura

* **Core & Lógica:** Python, Multithreading (para mantener FPS estables durante cálculos de IA).
* **Visión por Computadora:** OpenCV (Detección Haar Cascades, renderizado HUD cibernético).
* **Deep Learning & Biometría:** DeepFace (FaceNet) para la extracción de embeddings faciales (vectores de 128 dimensiones).
* **Base de Datos Vectorial:** FAISS (Facebook AI Similarity Search) para escalabilidad masiva.
* **Liveness Detection:** MediaPipe Face Mesh.
* **Notificaciones y Red:** `requests` para la API de Telegram.
* **Seguridad de Credenciales:** `python-dotenv` para protección de secretos de entorno.

---

## ⚙️ Instalación y Configuración

1. **Clonar el repositorio:**
   ```bash
   git clone [https://github.com/arevalodaniel/shogun_AI.git](https://github.com/arevalodaniel/shogun_AI.git)
   cd shogun_AI
2. Instalar las dependencias:
    Se recomienda usar un entorno virtual (venv).
    pip install -r requirements.txt
3. Configurar Variables de Entorno (Seguridad):
Para habilitar las alertas de Telegram, crea un archivo .env en la raíz del proyecto y agrega tus credenciales. (Nota: Este archivo está ignorado en git por seguridad).
    TELEGRAM_TOKEN=tu_token_de_bot_aqui
    TELEGRAM_CHAT_ID=tu_chat_id_aqui
4. Ejecutar el sistema:
    python main.py
5. Controles del Sistema (Dashboard Integrado)

El sistema se opera directamente desde la interfaz de cámara mediante comandos de teclado físicos para garantizar una respuesta inmediata en terminales de seguridad:

    [ v ] - Cambiar Modo (Acceso / CCTV): Alterna entre la puerta de seguridad estricta y el monitoreo asíncrono de múltiples objetivos.

    [ i ] - Iniciar Reto de Acceso: (Solo Modo Acceso) Activa el detector de vitalidad y solicita un número aleatorio de parpadeos antes de procesar la biometría.

    [ r ] - Registrar Nuevo Usuario: Evalúa la iluminación y el enfoque (Laplacian Variance). Si la calidad es óptima, extrae el vector biométrico y lo añade a la base de datos local.

    [ b ] - Dar de Baja: Elimina el registro biométrico de un usuario específico de la base de datos de FAISS.

    [ e ] - Exportar Reporte: Compila el log de intrusiones y genera el archivo Reporte_Seguridad_ShogunAI.csv.

    [ q ] - Apagar Sistema: Cierra los hilos de procesamiento y apaga la cámara de forma segura.
6. 🔒 Privacidad y Ética de Datos

Shogun AI fue diseñado con la filosofía Privacy by Design:

    No se almacenan fotografías de los usuarios legítimos (solo representaciones matemáticas unidireccionales de sus rostros).

    Las evidencias fotográficas de atacantes jamás abandonan la red local, evitando fugas de información a través de APIs de terceros.

    Todas las claves de API se gestionan mediante variables de entorno exclusivas del servidor host.

Desarrollado por Daniel Santoyo Arevalo. 🚀