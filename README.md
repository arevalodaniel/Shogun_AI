# 🥷 Shogun AI 
**Sistema Biométrico de Reconocimiento Facial Progresivo con Validación de Calidad**

Proyecto desarrollado para la **Categoría A**, diseñado bajo estrictos estándares de ciberseguridad, privacidad (Minimización de Datos) y alta eficiencia computacional (Edge Computing).

## ✨ Características Principales
* **Respuesta de ultra baja latencia:** Tiempos de identificación de `< 0.60s`.
* **Escalabilidad masiva:** Testeado con bases de datos superiores a **10,000 registros**.
* **Privacidad por diseño (Zero Visual Storage):** El sistema **no almacena imágenes**. Extrae un vector matemático (*embedding*) utilizando `FaceNet` y descarta la fotografía.
* **Robustez ante oclusiones:** Capacidad de identificación con rostros parcialmente cubiertos mediante enrolamiento continuo.

## ⚙️ Instalación y Ejecución
1. Instalar dependencias: `pip install -r requirements.txt`
2. Ejecutar el sistema: `python main.py`