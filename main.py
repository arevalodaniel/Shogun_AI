import cv2
import os
import pickle
import numpy as np
import time
from deepface import DeepFace
from datetime import datetime
import tkinter as tk
from tkinter import simpledialog

# Ocultamos la ventana principal de tkinter para usar solo los popups
ROOT = tk.Tk()
ROOT.withdraw()

# --- 1. Inicializar Bases de Datos ---
archivo_db = "shogun_db.pkl"
archivo_invalidos = "shogun_invalidos.pkl"

if os.path.exists(archivo_db):
    with open(archivo_db, "rb") as f:
        base_de_datos = pickle.load(f)
    print(f"¡Base de datos principal cargada! {len(base_de_datos)} registros.")
else:
    base_de_datos = {}

if os.path.exists(archivo_invalidos):
    with open(archivo_invalidos, "rb") as f:
        lista_invalidos = pickle.load(f)
else:
    lista_invalidos = []

# --- 2. Función de Validación de Calidad ---
def evaluar_calidad(rostro):
    gris = cv2.cvtColor(rostro, cv2.COLOR_BGR2GRAY)
    varianza_laplaciana = cv2.Laplacian(gris, cv2.CV_64F).var()
    if varianza_laplaciana < 60.0:
        return False, f"Rostro muy borroso (Varianza: {varianza_laplaciana:.1f})"
    brillo_promedio = np.mean(gris)
    if brillo_promedio < 40:
        return False, f"Poca luz/Muy oscuro (Brillo: {brillo_promedio:.1f})"
    if brillo_promedio > 230:
        return False, f"Exceso de luz/Saturado (Brillo: {brillo_promedio:.1f})"
    return True, "Calidad óptima"

# --- 3. Inicializar Cámara y Variables ---
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
# Recuerda poner la IP de tu DroidCam aquí:
cap = cv2.VideoCapture('http://192.168.x.x:4747/video') 

# Variables para calcular FPS
tiempo_anterior = 0

print("\n--- CONTROLES SHOGUN AI ---")
print("[r] - Registrar rostro nuevo")
print("[i] - Identificar rostro")
print("[q] - Salir")

print("\nCalentando motores de la IA... (esto tomará unos segundos)")
try:
    # Creamos una imagen falsa (negra) de 224x224 píxeles
    dummy_img = np.zeros((224, 224, 3), dtype=np.uint8)
    DeepFace.represent(img_path=dummy_img, model_name="Facenet", enforce_detection=False)
    print("¡IA lista y cargada en la memoria RAM!")
except Exception as e:
    pass

while cap.isOpened():
    success, image = cap.read()
    if not success: continue

    # --- Cálculo de FPS en tiempo real ---
    tiempo_actual = time.time()
    fps = 1 / (tiempo_actual - tiempo_anterior) if tiempo_anterior > 0 else 0
    tiempo_anterior = tiempo_actual
    
    # Dibujar los FPS en la esquina del video
    cv2.putText(image, f"FPS: {int(fps)}", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

    # Leemos la tecla presionada en cada frame
    tecla = cv2.waitKey(1) & 0xFF
    
    # --- Alerta de Rostro No Detectado ---
    if len(faces) == 0 and tecla in [ord('r'), ord('i')]:
        print("\n[ALERTA] ¡No veo ningún rostro! Quédate quieto o mejora la iluminación bro. :3")

    for (x, y, w, h) in faces:
        cv2.rectangle(image, (x, y), (x+w, y+h), (0, 255, 0), 2)
        rostro_recortado = image[y:y+h, x:x+w]
        
        # --- Módulo de Registro (Altas) ---
        if tecla == ord('r'):
            es_valido, mensaje_calidad = evaluar_calidad(rostro_recortado)
            if not es_valido:
                print(f"\n[ALERTA] Registro denegado: {mensaje_calidad}")
                registro_fallido = {"fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "motivo": mensaje_calidad}
                lista_invalidos.append(registro_fallido)
                with open(archivo_invalidos, "wb") as f: pickle.dump(lista_invalidos, f)
                continue
                
            print(f"\n[OK] {mensaje_calidad}. Procesando IA para registro...")
            try:
                # Iniciamos cronómetro de la IA
                inicio_ia = time.time()
                resultado = DeepFace.represent(img_path=rostro_recortado, model_name="Facenet", enforce_detection=False)
                fin_ia = time.time()
                
                embedding = np.array(resultado[0]["embedding"])
                
                # Generamos un nombre automático en vez de usar input()
                nuevo_id = len(base_de_datos) + 1
                # Abre una ventanita gráfica para escribir el nombre
                nombre = simpledialog.askstring("Registro Shogun AI", "Ingresa el nombre del rostro:")
                
                # Si el usuario escribió un nombre y le dio OK:
                if nombre:
                    base_de_datos[nombre] = embedding
                    with open(archivo_db, "wb") as f: pickle.dump(base_de_datos, f)
                    print(f"¡{nombre} guardado en la BD! (Tiempo: {fin_ia - inicio_ia:.2f}s)")
                else:
                    print("Registro cancelado (no se ingresó nombre).")
                # --------------------------
            except Exception as e: 
                print(f"Error al procesar el rostro: {e}")
        # --- Módulo de Identificación ---
        elif tecla == ord('i'):
            print("\nBuscando coincidencias...")
            if len(base_de_datos) == 0:
                print("La base de datos está vacía. Registra a alguien primero con 'r'.")
                continue
            try:
                # Iniciamos cronómetro de respuesta
                inicio_ia = time.time()
                resultado = DeepFace.represent(img_path=rostro_recortado, model_name="Facenet", enforce_detection=False)
                embedding_actual = np.array(resultado[0]["embedding"])
                
                mejor_similitud = float("inf")
                identidad = "Desconocido"
                
                for nombre_registrado, embedding_guardado in base_de_datos.items():
                    distancia = np.linalg.norm(embedding_actual - embedding_guardado)
                    if distancia < mejor_similitud:
                        mejor_similitud = distancia
                        identidad = nombre_registrado
                
                fin_ia = time.time()
                tiempo_respuesta = fin_ia - inicio_ia
                
                umbral = 10.0 
                if mejor_similitud < umbral:
                    print(f"¡IDENTIFICADO! Eres: {identidad} (Distancia: {mejor_similitud:.2f}) | Tiempo: {tiempo_respuesta:.2f}s")
                else:
                    print(f"ROSTRO DESCONOCIDO (Distancia más cercana: {mejor_similitud:.2f}) | Tiempo: {tiempo_respuesta:.2f}s")
            except Exception as e: print(f"Error al identificar: {e}")

    cv2.imshow('Shogun AI', image)
    if tecla == ord('q'): break

cap.release()
cv2.destroyAllWindows()