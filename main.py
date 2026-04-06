import cv2
import os
import pickle
import numpy as np
import time
import threading
import math
import customtkinter as ctk
import pyttsx3
from deepface import DeepFace
import mediapipe as mp

# --- 1. CONFIGURACIONES INICIALES ---
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")
app = ctk.CTk()
app.withdraw()

# Configuración de Voz
def hablar(texto):
    def tarea_voz():
        motor = pyttsx3.init()
        motor.setProperty('rate', 150)
        motor.say(texto)
        motor.runAndWait()
    threading.Thread(target=tarea_voz, daemon=True).start()

# --- 2. MOTOR DE ANTI-SPOOFING (VITALIDAD) ---
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(max_num_faces=1, refine_landmarks=True, min_detection_confidence=0.5)

def calcular_distancia(p1, p2, w, h):
    return math.hypot((p2.x - p1.x) * w, (p2.y - p1.y) * h)

def calcular_ear(rostro_landmarks, w, h):
    try:
        # Puntos del ojo izquierdo y derecho según MediaPipe
        v1_izq = calcular_distancia(rostro_landmarks[159], rostro_landmarks[145], w, h)
        v2_izq = calcular_distancia(rostro_landmarks[158], rostro_landmarks[153], w, h)
        h_izq = calcular_distancia(rostro_landmarks[33], rostro_landmarks[133], w, h)
        ear_izq = (v1_izq + v2_izq) / (2.0 * h_izq)

        v1_der = calcular_distancia(rostro_landmarks[386], rostro_landmarks[374], w, h)
        v2_der = calcular_distancia(rostro_landmarks[385], rostro_landmarks[380], w, h)
        h_der = calcular_distancia(rostro_landmarks[362], rostro_landmarks[263], w, h)
        ear_der = (v1_der + v2_der) / (2.0 * h_der)

        return (ear_izq + ear_der) / 2.0
    except:
        return 0.0

# --- 3. VARIABLES GLOBALES PARA MULTIHILO ---
frame_global = None
corriendo = True
estado_sistema = "ESPERANDO BIOMETRIA"
color_estado = (0, 255, 255) # Amarillo
distancia_actual = 0.0
tiempo_ia = 0.0
ear_actual = 0.0
es_humano_vivo = False

# --- 4. HILO DE LA CÁMARA (Procesamiento Asíncrono) ---
def hilo_captura():
    global frame_global, corriendo
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    
    while corriendo:
        ret, frame = cap.read()
        if ret:
            frame_global = frame
        time.sleep(0.01) # Libera CPU
    cap.release()

# Arrancamos el motor de la cámara en segundo plano
threading.Thread(target=hilo_captura, daemon=True).start()

# --- 5. CARGA DE BASES DE DATOS E IA ---
archivo_db = "shogun_db.pkl"
if os.path.exists(archivo_db):
    with open(archivo_db, "rb") as f: base_de_datos = pickle.load(f)
else: base_de_datos = {}

# NUEVO: Lista de intentos inválidos
archivo_invalidos = "shogun_invalidos.pkl"
if os.path.exists(archivo_invalidos):
    with open(archivo_invalidos, "rb") as f: lista_invalidos = pickle.load(f)
else: lista_invalidos = []

def registrar_invalido(motivo):
    """Guarda un registro del intento fallido de seguridad"""
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    lista_invalidos.append({"fecha": timestamp, "motivo": motivo})
    with open(archivo_invalidos, "wb") as f: pickle.dump(lista_invalidos, f)
    print(f"🚨 [ALERTA DE SEGURIDAD] Guardado en lista de inválidos: {motivo}")

print(f"¡Shogun AI 2.0 Listo! - {len(base_de_datos)} registros cargados.")
print(f"Auditoría activa: {len(lista_invalidos)} intentos bloqueados registrados.")

print("Calentando FaceNet...")
try: DeepFace.represent(img_path=np.zeros((224, 224, 3), dtype=np.uint8), model_name="Facenet", enforce_detection=False)
except: pass
print("¡Motor IA cargado en RAM!")

# --- 6. HILO DE INTELIGENCIA ARTIFICIAL (FaceNet) ---
def procesar_identificacion(rostro):
    global estado_sistema, color_estado, distancia_actual, tiempo_ia
    inicio = time.time()
    try:
        resultado = DeepFace.represent(img_path=rostro, model_name="Facenet", enforce_detection=False)
        embedding_actual = np.array(resultado[0]["embedding"])
        
        mejor_similitud = float("inf")
        identidad = "Desconocido"
        for nombre, emb_guardado in base_de_datos.items():
            dist = np.linalg.norm(embedding_actual - emb_guardado)
            if dist < mejor_similitud:
                mejor_similitud = dist
                identidad = nombre
                
        tiempo_ia = time.time() - inicio
        distancia_actual = mejor_similitud
        
        if mejor_similitud < 10.0:
            estado_sistema = f"ACCESO: {identidad.upper()}"
            color_estado = (0, 255, 0) # Verde
            hablar(f"Acceso autorizado. Hola, {identidad}.")
        else:
            estado_sistema = "ACCESO DENEGADO"
            color_estado = (0, 0, 255) # Rojo
            hablar("Acceso denegado. Rostro desconocido.")
    except Exception as e:
        estado_sistema = "ERROR DE LECTURA"

# --- 7. DISEÑO DEL HUD CIBERNÉTICO ---
def dibujar_hud(img, fps, ear, vivo, estado, color_est, dist, t_ia):
    h, w = img.shape[:2]
    # Panel lateral semitransparente
    overlay = img.copy()
    cv2.rectangle(overlay, (0, 0), (300, h), (15, 15, 15), -1)
    cv2.addWeighted(overlay, 0.6, img, 0.4, 0, img)
    
    # Textos del HUD
    cv2.putText(img, "SHOGUN AI v2.0", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
    cv2.putText(img, f"FPS Reales: {int(fps)}", (20, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
    
    # Liveness Data
    color_ear = (0, 255, 0) if vivo else (0, 0, 255)
    txt_vivo = "VIVO (Organico)" if vivo else "SPOOF (Foto/Estatico)"
    cv2.putText(img, f"EAR (Ojos): {ear:.2f}", (20, 130), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color_ear, 1)
    cv2.putText(img, txt_vivo, (20, 160), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color_ear, 1)
    
    # Separador
    cv2.line(img, (20, 190), (280, 190), (100, 100, 100), 1)
    
    # Resultados IA
    cv2.putText(img, "ESTADO SISTEMA:", (20, 230), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
    cv2.putText(img, estado, (20, 260), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color_est, 2)
    cv2.putText(img, f"Distancia: {dist:.2f}", (20, 300), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
    cv2.putText(img, f"Tiempo IA: {t_ia:.2f}s", (20, 330), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)

    cv2.putText(img, f"DB Total: {len(base_de_datos)} rostros", (20, 370), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 1)

def dibujar_esquinas(img, x, y, w, h, color=(0, 255, 0), grosor=2, longitud=20):
    cv2.line(img, (x, y), (x+longitud, y), color, grosor)
    cv2.line(img, (x, y), (x, y+longitud), color, grosor)
    cv2.line(img, (x+w, y), (x+w-longitud, y), color, grosor)
    cv2.line(img, (x+w, y), (x+w, y+longitud), color, grosor)
    cv2.line(img, (x, y+h), (x+longitud, y+h), color, grosor)
    cv2.line(img, (x, y+h), (x, y+h-longitud), color, grosor)
    cv2.line(img, (x+w, y+h), (x+w-longitud, y+h), color, grosor)
    cv2.line(img, (x+w, y+h), (x+w, y+h-longitud), color, grosor)

# --- 8. CICLO PRINCIPAL (Renderizado) ---
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
tiempo_anterior = time.time()

while frame_global is None:
    time.sleep(0.1)

while corriendo:
    frame = frame_global.copy()
    h_img, w_img = frame.shape[:2]
    
    # Cálculo de FPS (Con escudo anti-ZeroDivision)
    tiempo_actual = time.time()
    if (tiempo_actual - tiempo_anterior) > 0:
        fps = 1 / (tiempo_actual - tiempo_anterior)
    else:
        fps = 0.0
    tiempo_anterior = tiempo_actual
    
    # --- 🕹️ LECTOR ÚNICO DE TECLADO ---
    tecla = cv2.waitKey(1) & 0xFF
    
    # --- [q] SALIR DEL PROGRAMA ---
    if tecla == ord('q'):
        print("Apagando Shogun AI...")
        corriendo = False
        break

    # --- [b] BORRAR USUARIO ---
    if tecla == ord('b'):
        estado_sistema = "MODO DE BAJAS ACTIVO"
        color_estado = (0, 0, 255)
        dibujar_hud(frame, fps, ear_actual, es_humano_vivo, estado_sistema, color_estado, distancia_actual, tiempo_ia)
        cv2.imshow('Shogun AI', frame) 
        
        dialog = ctk.CTkInputDialog(text="🗑️ ELIMINAR REGISTRO\n\nIngresa el nombre del usuario a borrar:", title="Shogun AI - Bajas")
        nombre_borrar = dialog.get_input()
        
        if nombre_borrar:
            if nombre_borrar in base_de_datos:
                del base_de_datos[nombre_borrar]
                with open(archivo_db, "wb") as f: pickle.dump(base_de_datos, f)
                hablar(f"Usuario {nombre_borrar} eliminado del sistema.")
            else:
                hablar("Error. Usuario no encontrado.")
        estado_sistema = "ESPERANDO BIOMETRIA"
    
    # Procesamiento de MediaPipe para Liveness
    resultados_mesh = face_mesh.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    if resultados_mesh.multi_face_landmarks:
        ear_actual = calcular_ear(resultados_mesh.multi_face_landmarks[0].landmark, w_img, h_img)
        es_humano_vivo = True if ear_actual > 0.22 else False
    else:
        ear_actual = 0.0
        es_humano_vivo = False

    # Detección de rostro tradicional para la IA
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.1, 5, minSize=(30, 30))

    for (x, y, w, h) in faces:
        dibujar_esquinas(frame, x, y, w, h)
        rostro_recortado = frame[y:y+h, x:x+w].copy()
        
        # --- [i] IDENTIFICAR ---
        if tecla == ord('i'):
            if es_humano_vivo:
                estado_sistema = "PROCESANDO RED NEURONAL..."
                color_estado = (0, 255, 255)
                threading.Thread(target=procesar_identificacion, args=(rostro_recortado,), daemon=True).start()
            else:
                estado_sistema = "ALERTA: POSIBLE FOTO"
                color_estado = (0, 0, 255)
                hablar("Alerta de seguridad. Signos vitales no detectados.")
                registrar_invalido("Intento de identificación con foto estática (Anti-Spoofing)")
                
        # --- [r] REGISTRAR NUEVO ROSTRO ---
        elif tecla == ord('r'):
            if es_humano_vivo: 
                # NUEVO: Filtro Laplaciano de Varianza (Como dice tu PDF)
                rostro_gris = gray[y:y+h, x:x+w]
                varianza_enfoque = cv2.Laplacian(rostro_gris, cv2.CV_64F).var()
                
                if varianza_enfoque < 60.0:
                    estado_sistema = "RECHAZO: IMAGEN BORROSA"
                    color_estado = (0, 0, 255)
                    hablar("Registro denegado. La imagen está demasiado borrosa.")
                    registrar_invalido(f"Intento de registro borroso (Varianza: {varianza_enfoque:.2f})")
                else:
                    estado_sistema = "EXTRAYENDO BIOMETRIA..."
                    color_estado = (255, 255, 0)
                    dibujar_hud(frame, fps, ear_actual, es_humano_vivo, estado_sistema, color_estado, distancia_actual, tiempo_ia)
                    cv2.imshow('Shogun AI', frame)
                    
                    try:
                        resultado = DeepFace.represent(img_path=rostro_recortado, model_name="Facenet", enforce_detection=False)
                        embedding = np.array(resultado[0]["embedding"])
                        
                        dialog = ctk.CTkInputDialog(text="🧬 BIOMETRÍA REQUERIDA\n\nIngresa el nombre del nuevo rostro:", title="Shogun AI - Altas")
                        nombre = dialog.get_input()
                        
                        if nombre:
                            base_de_datos[nombre] = embedding
                            with open(archivo_db, "wb") as f: pickle.dump(base_de_datos, f)
                            hablar(f"Biometría registrada con éxito. Bienvenido a Shogun AI, {nombre}.")
                    except Exception as e:
                        print(f"Error en registro: {e}")
            else:
                estado_sistema = "ALERTA: POSIBLE FOTO"
                color_estado = (0, 0, 255)
                hablar("Registro denegado. Se requiere un rostro humano vivo.")
                registrar_invalido("Intento de registro con foto estática (Anti-Spoofing)")
                
    dibujar_hud(frame, fps, ear_actual, es_humano_vivo, estado_sistema, color_estado, distancia_actual, tiempo_ia)
    cv2.imshow('Shogun AI', frame)

cv2.destroyAllWindows()