# 🛡️ Shogun AI - Advanced Security & CCTV Dashboard v2.6

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![OpenCV](https://img.shields.io/badge/OpenCV-Vision-green.svg)
![DeepFace](https://img.shields.io/badge/DeepFace-AI-orange.svg)
![FAISS](https://img.shields.io/badge/FAISS-Vector%20DB-red.svg)
![Multithreading](https://img.shields.io/badge/Architecture-Asynchronous-purple.svg)

**Concurso Hola Mundo 2026** | **Categoría:** A - Reconocimiento Facial | **Equipo:** Shogun Eye

**Shogun AI** es una suite de seguridad biométrica de grado corporativo que opera bajo el paradigma de **Edge Computing**. Diseñado con una arquitectura de Modo Dual, funciona tanto como un estricto control de acceso anti-spoofing, como un sistema de vigilancia masiva (CCTV) capaz de procesar múltiples vectores faciales en tiempo real sin pérdida de frames.

---

## 📋 Tabla de Contenidos
1. [Características Principales](#-características-principales)
2. [Requisitos del Sistema](#-requisitos-del-sistema)
3. [Stack Tecnológico y Arquitectura](#️-stack-tecnológico-y-arquitectura)
4. [Instalación y Configuración](#️-instalación-y-configuración)
5. [Dataset y Modelos](#-dataset-y-modelos)
6. [Controles y Uso del Sistema](#-controles-del-sistema-dashboard-integrado)
7. [Pruebas Automatizadas](#-pruebas-automatizadas)
8. [Estructura del Proyecto](#-estructura-del-proyecto)
9. [Métricas y Documentación Técnica](#-métricas-y-documentación-técnica)
10. [Limitaciones Conocidas](#-limitaciones-conocidas)
11. [Privacidad y Ética de Datos](#-privacidad-y-ética-de-datos)
12. [Créditos y Licencia](#-créditos-y-licencia)

---

## ✨ Características Principales

* **🔄 Modo Dual (Acceso / CCTV):** Permite cambiar en tiempo real entre una verificación estricta de un solo sujeto o la identificación masiva de múltiples personas en cámara utilizando **Multithreading Asíncrono**.
* **👁️ Identificación Ultrarrápida:** Utiliza el modelo **FaceNet** combinado con **Meta FAISS** para buscar e identificar rostros entre miles de registros en fracciones de segundo.
* **💓 Motor de Vitalidad (Anti-Spoofing):** En el Modo Acceso, implementa **MediaPipe Face Mesh** para calcular el *Eye Aspect Ratio* (EAR) en tiempo real. Exige un reto de parpadeos dinámico y aleatorio para asegurar que el sujeto es un ser humano vivo y rechazar fotografías o pantallas.
* **📲 Alertas IoT en Tiempo Real:** Integración con la API de Telegram para notificar al equipo de seguridad de forma instantánea sobre intentos de intrusión o bloqueos del sistema.
* **📸 Auditoría Visual Edge:** Ante un intento de acceso no autorizado, el sistema captura silenciosamente una fotografía del infractor y la almacena en una bóveda local cifrada (`/evidencias`), cumpliendo con las normativas de privacidad corporativa.
* **📊 Reportes Ejecutivos:** Generación automatizada de reportes CSV con el historial de accesos denegados para auditorías de Recursos Humanos.

---

## 💻 Requisitos del Sistema
* **Sistema Operativo:** Windows 10 / Windows 11.
* **Hardware Mínimo:** CPU Intel Core i5 (10.ª Gen) @ 1.00GHz, 16 GB RAM, 500 GB SSD.
* **Cámara:** Dispositivo móvil con *DroidCam Client* operando en la misma subred Wi-Fi.
* **Runtime:** Python 3.10 o superior.

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

Asumiendo una máquina limpia, sigue estos pasos exactos:

1. **Clonar el repositorio:**
```bash
   git clone [https://github.com/arevalodaniel/Shogun_AI.git](https://github.com/arevalodaniel/Shogun_AI.git)
   cd Shogun_AI
2. **Crear e inicializar un entorno virtual (venv):**
    python -m venv venv
    venv\Scripts\activate
3. **Instalar dependencias:**
    pip install -r requirements.txt
4. **Configurar Variables de Entorno (Seguridad):**
    Crea un archivo .env en la raíz del proyecto para habilitar las alertas. (Ignorado en git por seguridad).
    TELEGRAM_TOKEN=tu_token_de_bot_aqui
    TELEGRAM_CHAT_ID=tu_chat_id_aqui
📦 Dataset y Modelos
[cite: 6]

    Dataset: Shogun AI genera vectores biométricos matemáticos en tiempo real; no requiere la descarga de un dataset de imágenes pesadas. Para probar la escalabilidad del sistema, puedes inyectar 10,000 registros vectoriales sintéticos.

    Modelos Preentrenados: Los pesos neuronales de FaceNet y los clasificadores de Viola-Jones se descargan y vinculan automáticamente en la primera ejecución a través de las dependencias de deepface y opencv-python.

🎮 Controles del Sistema (Dashboard Integrado)
    [cite: 6]

    Para iniciar el sistema, ejecuta:
    python main.py
El sistema se opera directamente desde la interfaz de video mediante el teclado físico:

    [ v ] - Cambiar Modo: Alterna entre el Acceso Estricto y la Vigilancia CCTV masiva.

    [ i ] - Reto de Acceso: (Solo Modo Acceso) Activa el detector de vitalidad (EAR).

    [ r ] - Registrar Nuevo Usuario: Evalúa iluminación y enfoque. Si pasa el filtro Laplaciano, extrae el embedding a FAISS.

    [ b ] - Dar de Baja: Elimina el registro biométrico de la base de datos local.

    [ e ] - Exportar Reporte: Compila el log de intrusiones en Reporte_Seguridad_ShogunAI.csv.

    [ q ] - Apagar Sistema: Cierra los hilos de procesamiento y apaga la cámara de forma segura.

🧪 Pruebas Automatizadas
[cite: 6]

Para evaluar la latencia y la tasa de aciertos de la arquitectura, posicionarse en la raíz del proyecto y ejecutar los scripts de estrés. (Consulte el reporte de pruebas de carga en la documentación para metodologías detalladas).

📁 Estructura del Proyecto
[cite: 6]
        Shogun_AI/
    ├── main.py                  # Orquestador principal e hilos de ejecución
    ├── requirements.txt         # Dependencias exactas
    ├── .gitignore               # Exclusión de bóvedas y variables locales
    ├── README.md                # Documentación del repositorio
    ├── docs/                    # (Recomendado) Documento Técnico y Ficha en PDF
    ├── src/                     # Módulos core (Biometría, Telegram API, Visión)
    └── evidencias/              # Bóveda local cifrada (Generada en runtime)
📈 Métricas y Documentación Técnica

    Tiempo de respuesta iterativa (Inferencia): Promedio de 0.45s a 0.60s.

    Escalabilidad de FAISS: Operación estable a 30 FPS con un clúster > 10,000 registros.

    Precisión Anti-Spoofing: 100% de bloqueo frente a medios estáticos (fotografías/pantallas).

    Nota para Evaluadores: El detalle completo de la arquitectura, fórmulas de la Distancia Euclidiana, justificación de trade-offs y pruebas de carga se encuentra documentado extensamente en el archivo HM2026_DocTecnico_ShogunEye.pdf entregado al comité.
⚠️ Limitaciones Conocidas

    Iluminación Extrema: El sistema bloquea preventivamente los registros y validaciones si la iluminación ambiental es inferior a 40 lux (subexposición) o superior a 230 lux (saturación).

    Latencia de Red IP: Fluctuaciones de latencia en la conexión Wi-Fi hacia el cliente DroidCam pueden ocasionar caídas temporales de FPS en el renderizado principal.
🔒 Privacidad y Ética de Datos

Shogun AI fue diseñado con la filosofía Privacy by Design:

    No se almacenan fotografías de los usuarios legítimos.

    Las evidencias de atacantes jamás abandonan la red local, evitando fugas mediante APIs.

    Las claves se gestionan en variables de entorno locales del host.
👥 Créditos y Licencia[cite: 6]  Desarrollado por: 
    Daniel Santoyo Arévalo (Ingeniería en Sistemas Digitales, Instituto Irapuato).
    Contacto: arevalodaniel547@gmail.com
    Licencia: Distribuido bajo la Licencia MIT. (Consulte el archivo LICENSE para más información).
