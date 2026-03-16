import cv2
import os
import pickle
import numpy as np
import time
from deepface import DeepFace
from datetime import datetime
import customtkinter as ctk
import pyttsx3
import customtkinter as ctk
import pyttsx3
import threading 

# --- Configuración de la Voz de Shogun AI ---
# --- Función Multihilo para la Voz de Shogun AI ---
def hablar(texto):
    def tarea_voz():
        motor = pyttsx3.init()
        motor.setProperty('rate', 150)
        motor.say(texto)
        motor.runAndWait()
    # Ejecuta la voz en el fondo sin pausar el video
    threading.Thread(target=tarea_voz).start()
# --------------------------------------------------
# --------------------------------------------

# --- Configuración Visual de CustomTkinter ---
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")

# Truco para que la ventana oscura conviva bien con OpenCV
app = ctk.CTk()
app.withdraw()

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

# --- 3. Inicializar Cámara ---
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

print("\nEncendiendo cámara... (el foquito debería prender)")
# 🔥 HACK DE WINDOWS: cv2.CAP_DSHOW fuerza a que la ventana abra al instante
#cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
url_camara = "http://192.168.3.10:4747/video"
cap = cv2.VideoCapture(url_camara) 

tiempo_anterior = 0

print("\nCalentando motores de la IA... (esto tomará unos segundos)")
try:
    dummy_img = np.zeros((224, 224, 3), dtype=np.uint8)
    DeepFace.represent(img_path=dummy_img, model_name="Facenet", enforce_detection=False)
    print("¡IA lista y cargada en la memoria RAM!")
except Exception as e:
    pass

print("\n--- CONTROLES SHOGUN AI ---")
print("[r] - Registrar rostro nuevo")
print("[i] - Identificar rostro")
print("[b] - Borrar rostro")
print("[q] - Salir")

# --- 🟢 CICLO PRINCIPAL INMORTAL ---
while True:
    success, image = cap.read()
    
    if not success: 
        print("🛑 ¡No encuentro la cámara! Reconectando...")
        time.sleep(2) 
        #cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        cap = cv2.VideoCapture(url_camara)
        continue

    # --- Cálculo de FPS en tiempo real ---
    tiempo_actual = time.time()
    fps = 1 / (tiempo_actual - tiempo_anterior) if tiempo_anterior > 0 else 0
    tiempo_anterior = tiempo_actual
    
    cv2.putText(image, f"FPS: {int(fps)}", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

    # Leemos la tecla presionada en cada frame
    tecla = cv2.waitKey(1) & 0xFF
    
    # --- 🗑️ MÓDULO DE BAJAS INDEPENDIENTE (No necesita rostro) ---
    if tecla == ord('b'):
        print("\nIniciando protocolo de borrado...")
        cap.release()
        
        dialog = ctk.CTkInputDialog(
            text="🗑️ ELIMINAR REGISTRO\n\nIngresa el nombre exacto del usuario a borrar:", 
            title="Shogun AI - Consola de Bajas"
        )
        nombre_borrar = dialog.get_input()
        
        if nombre_borrar:
            if nombre_borrar in base_de_datos:
                del base_de_datos[nombre_borrar]
                with open(archivo_db, "wb") as f: pickle.dump(base_de_datos, f)
                print(f"[-] Usuario '{nombre_borrar}' eliminado de la base de datos.")
                hablar(f"Usuario {nombre_borrar} eliminado del sistema.")
            else:
                print(f"[ERROR] El usuario '{nombre_borrar}' no existe.")
                hablar("Error. Usuario no encontrado en la base de datos.")
        else:
            print("Operación de borrado cancelada.")

        # VOLVEMOS A CONECTAR LA CÁMARA
        cap = cv2.VideoCapture(url_camara) 
        continue # Brincamos al siguiente frame para que no marque errores
    # --------------------------------------------------------------

    # --- Alerta de Rostro No Detectado ---
    if len(faces) == 0 and tecla in [ord('r'), ord('i')]:
        print("\n[ALERTA] ¡No veo ningún rostro! Quédate quieto.")

    for (x, y, w, h) in faces:
        cv2.rectangle(image, (x, y), (x+w, y+h), (0, 255, 0), 2)
        rostro_recortado = image[y:y+h, x:x+w]
        
        # --- Módulo de Registro (Altas) ---
        if tecla == ord('r'):
            es_valido, mensaje_calidad = evaluar_calidad(rostro_recortado)
            if not es_valido:
                print(f"\n[ALERTA] Registro denegado: {mensaje_calidad}")
                continue
                
            print(f"\n[OK] {mensaje_calidad}. Procesando IA para registro...")
            try:
                inicio_ia = time.time()
                resultado = DeepFace.represent(img_path=rostro_recortado, model_name="Facenet", enforce_detection=False)
                fin_ia = time.time()
                
                embedding = np.array(resultado[0]["embedding"])
                
                # --- DESCONECTAMOS LA CÁMARA PARA QUE TKINTER NO SE TRABE ---
                cap.release()
                
                dialog = ctk.CTkInputDialog(
                    text="🧬 BIOMETRÍA REQUERIDA\n\nIngresa el nombre del nuevo rostro:", 
                    title="Shogun AI - Consola de Registro"
                )
                nombre = dialog.get_input()
                
                if nombre:
                    base_de_datos[nombre] = embedding
                    with open(archivo_db, "wb") as f: pickle.dump(base_de_datos, f)
                    print(f"¡{nombre} guardado en la BD! (Tiempo: {fin_ia - inicio_ia:.2f}s)")

                    # --- SHOGUN AI HABLA ---
                    hablar(f"Biometría registrada con éxito. Bienvenido a Shogun AI, {nombre}.")

                else:
                    print("Registro cancelado.")

                # --- VOLVEMOS A CONECTAR LA CÁMARA ---
                #cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
                cap = cv2.VideoCapture(url_camara)
                
            except Exception as e: 
                print(f"Error al procesar el rostro: {e}")
                #cap = cv2.VideoCapture(0, cv2.CAP_DSHOW) # Por si explota, reconectamos
                cap = cv2.VideoCapture(url_camara)

        # --- Módulo de Identificación ---
        elif tecla == ord('i'):
            print("\nBuscando coincidencias...")
            if len(base_de_datos) == 0:
                print("La base de datos está vacía. Registra a alguien primero con 'r'.")
                continue
            try:
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
                    hablar(f"Acceso autorizado. Hola, {identidad}.")
                else:
                    print(f"ROSTRO DESCONOCIDO (Distancia más cercana: {mejor_similitud:.2f}) | Tiempo: {tiempo_respuesta:.2f}s")
                    hablar("Acceso denegado. Rostro desconocido.")
            except Exception as e: 
                print(f"Error al identificar: {e}")

    cv2.imshow('Shogun AI', image)
    if tecla == ord('q'): break

cap.release()
cv2.destroyAllWindows()