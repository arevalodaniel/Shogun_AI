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
import faiss
import random
import winsound
import csv
import requests
from dotenv import load_dotenv

# Cargamos secretos desde el .env (CERO HARDCODEO)
load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# --- 1. CONFIGURACIONES INICIALES ---
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")
app = ctk.CTk()
app.withdraw()

if not os.path.exists("evidencias"):
    os.makedirs("evidencias")

def enviar_alerta_telegram(motivo):
    """Envía una alerta en tiempo real al administrador por Telegram"""
    def tarea_enviar():
        if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID: return # Seguro anti-crasheo
        fecha_hora = time.strftime("%Y-%m-%d %H:%M:%S")
        mensaje = (
            f"🚨 *ALERTA DE SEGURIDAD - SHOGUN AI* 🚨\n\n"
            f"📅 *Fecha:* {fecha_hora}\n"
            f"⚠️ *Incidente:* {motivo}\n"
            f"🛡️ *Estatus:* Acceso bloqueado. Evidencia guardada localmente."
        )
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        payload = {"chat_id": TELEGRAM_CHAT_ID, "text": mensaje, "parse_mode": "Markdown"}
        try:
            requests.post(url, data=payload, timeout=5)
        except:
            print("❌ Error de red al enviar a Telegram")
    threading.Thread(target=tarea_enviar, daemon=True).start()

# --- CONFIGURACIÓN DE VOZ Y SFX ---
def hablar(texto):
    def tarea_voz():
        motor = pyttsx3.init()
        motor.setProperty('rate', 160)
        motor.say(texto)
        motor.runAndWait()
    threading.Thread(target=tarea_voz, daemon=True).start()

def beep_parpadeo(): threading.Thread(target=winsound.Beep, args=(1500, 100), daemon=True).start()
def sonido_exito():
    def play():
        for f in [1200, 1600, 2000]: winsound.Beep(f, 150)
    threading.Thread(target=play, daemon=True).start()
def sonido_error():
    def play():
        winsound.Beep(800, 200); winsound.Beep(400, 400)
    threading.Thread(target=play, daemon=True).start()

# --- 2. MOTOR DE VITALIDAD ---
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(max_num_faces=1, refine_landmarks=True, min_detection_confidence=0.5)

def calcular_distancia(p1, p2, w, h): return math.hypot((p2.x - p1.x) * w, (p2.y - p1.y) * h)

def calcular_ear(rostro_landmarks, w, h):
    try:
        v1_izq = calcular_distancia(rostro_landmarks[159], rostro_landmarks[145], w, h)
        v2_izq = calcular_distancia(rostro_landmarks[158], rostro_landmarks[153], w, h)
        h_izq = calcular_distancia(rostro_landmarks[33], rostro_landmarks[133], w, h)
        ear_izq = (v1_izq + v2_izq) / (2.0 * h_izq)
        v1_der = calcular_distancia(rostro_landmarks[386], rostro_landmarks[374], w, h)
        v2_der = calcular_distancia(rostro_landmarks[385], rostro_landmarks[380], w, h)
        h_der = calcular_distancia(rostro_landmarks[362], rostro_landmarks[263], w, h)
        ear_der = (v1_der + v2_der) / (2.0 * h_der)
        return (ear_izq + ear_der) / 2.0
    except: return 0.0

# --- 3. VARIABLES GLOBALES ---
frame_global = None
corriendo = True
estado_sistema = "ESPERANDO BIOMETRIA"
color_estado = (0, 255, 255)
distancia_actual = 0.0
tiempo_ia = 0.0
ear_actual = 0.0
es_humano_vivo = False
rostro_compartido = None 

# Variables del Reto
reto_completado = False
esperando_reto = False
contador_parpadeos = 0
meta_parpadeos = 3
tiempo_inicio_reto = 0.0
parpadeo_detectado = False 

# --- 4. HILO DE LA CÁMARA ---
def hilo_captura():
    global frame_global, corriendo
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    while corriendo:
        ret, frame = cap.read()
        if ret: frame_global = frame
        time.sleep(0.01)
    cap.release()
threading.Thread(target=hilo_captura, daemon=True).start()

# --- 5. CARGA DE DATOS SEGUROS ---
archivo_db = "shogun_db.pkl"
base_de_datos = {}
if os.path.exists(archivo_db):
    with open(archivo_db, "rb") as f: base_de_datos = pickle.load(f)

archivo_invalidos = "shogun_invalidos.pkl"
lista_invalidos = []
if os.path.exists(archivo_invalidos):
    with open(archivo_invalidos, "rb") as f: lista_invalidos = pickle.load(f)

def registrar_invalido(motivo, imagen_rostro=None):
    timestamp_file = time.strftime("%Y%m%d_%H%M%S")
    timestamp_log = time.strftime("%Y-%m-%d %H:%M:%S")
    if imagen_rostro is not None and imagen_rostro.size > 0:
        cv2.imwrite(f"evidencias/INTRUSO_{timestamp_file}.jpg", imagen_rostro)
    lista_invalidos.append({"fecha": timestamp_log, "motivo": motivo})
    
    with open(archivo_invalidos, "wb") as f: pickle.dump(lista_invalidos, f)
    enviar_alerta_telegram(motivo)

def exportar_reporte():
    nombre_csv = "Reporte_Seguridad_ShogunAI.csv"
    with open(nombre_csv, mode='w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=["fecha", "motivo"])
        writer.writeheader()
        writer.writerows(lista_invalidos)
    hablar("Reporte ejecutivo generado con éxito.")

# MOTOR FAISS
index_faiss = None
nombres_faiss = []
def actualizar_faiss():
    global index_faiss, nombres_faiss
    nombres_faiss = list(base_de_datos.keys())
    if len(base_de_datos) > 0:
        vectores = np.array(list(base_de_datos.values())).astype('float32')
        index_faiss = faiss.IndexFlatL2(vectores.shape[1])
        index_faiss.add(vectores)
actualizar_faiss()

# --- 6. HILO IA ---
def procesar_identificacion(rostro):
    global estado_sistema, color_estado, distancia_actual, tiempo_ia
    inicio = time.time()
    try:
        resultado = DeepFace.represent(img_path=rostro, model_name="Facenet", enforce_detection=False, align=False)
        emb_actual = np.array([resultado[0]["embedding"]]).astype('float32')
        mejor_dist = float("inf")
        identidad = "Desconocido"
        if index_faiss is not None:
            dists, idxs = index_faiss.search(emb_actual, 1) 
            mejor_dist = math.sqrt(dists[0][0])
            identidad = nombres_faiss[idxs[0][0]]
        tiempo_ia = time.time() - inicio
        distancia_actual = mejor_dist
        if mejor_dist < 10.0:
            estado_sistema = f"ACCESO: {identidad.upper()}"
            color_estado = (0, 255, 0)
            sonido_exito(); hablar(f"Acceso autorizado. Hola {identidad}")
        else:
            estado_sistema = "ACCESO DENEGADO"
            color_estado = (0, 0, 255)
            sonido_error(); hablar("Acceso denegado"); registrar_invalido("Usuario Desconocido", rostro)
    except: 
        estado_sistema = "ERROR IA"

# --- 7. HUD ---
def dibujar_hud(img, fps, ear, vivo, estado, color_est, dist, t_ia, cont, meta, esperando, t_restante):
    h, w = img.shape[:2]
    overlay = img.copy()
    cv2.rectangle(overlay, (0, 0), (300, h), (15, 15, 15), -1)
    cv2.addWeighted(overlay, 0.6, img, 0.4, 0, img)
    cv2.putText(img, "SHOGUN AI v2.5", (20, 40), 1, 1.5, (0, 255, 0), 2)
    cv2.putText(img, f"FPS: {int(fps)}", (20, 75), 1, 1.2, (255, 255, 255), 1)
    color_ear = (0, 255, 0) if vivo else (0, 0, 255)
    cv2.putText(img, f"EAR: {ear:.2f}", (20, 120), 1, 1.2, color_ear, 1)
    cv2.putText(img, "VIVO" if vivo else "SPOOF", (20, 150), 1, 1.2, color_ear, 2)
    cv2.line(img, (20, 190), (280, 190), (100, 100, 100), 1)
    cv2.putText(img, estado, (20, 260), 1, 1.3, color_est, 2)
    cv2.putText(img, f"Dist: {dist:.2f}", (20, 300), 1, 1.1, (255, 255, 255), 1)
    cv2.putText(img, f"IA: {t_ia:.2f}s", (20, 330), 1, 1.1, (255, 255, 255), 1)
    cv2.putText(img, f"DB: {len(base_de_datos)}", (20, 370), 1, 1.1, (0, 255, 0), 1)
    if esperando:
        cv2.rectangle(img, (320, 20), (620, 100), (0, 165, 255), -1) 
        cv2.putText(img, f"RETO: {meta} PARPADEOS", (330, 45), 1, 1.1, (255, 255, 255), 2)
        cv2.putText(img, f"PROGRESO: {cont}/{meta}", (330, 75), 1, 1.1, (255, 255, 255), 1)
        cv2.putText(img, f"{int(t_restante)}s", (550, 75), 1, 1.2, (0, 0, 255) if t_restante < 3 else (255, 255, 255), 2)

def dibujar_esquinas(img, x, y, w, h, color=(0, 255, 0), grosor=2, longitud=20):
    cv2.line(img, (x, y), (x+longitud, y), color, grosor)
    cv2.line(img, (x, y), (x, y+longitud), color, grosor)
    cv2.line(img, (x+w, y), (x+w-longitud, y), color, grosor)
    cv2.line(img, (x+w, y), (x+w, y+longitud), color, grosor)
    cv2.line(img, (x, y+h), (x+longitud, y+h), color, grosor)
    cv2.line(img, (x, y+h), (x, y+h-longitud), color, grosor)
    cv2.line(img, (x+w, y+h), (x+w-longitud, y+h), color, grosor)
    cv2.line(img, (x+w, y+h), (x+w, y+h-longitud), color, grosor)

# --- 8. CICLO PRINCIPAL ---
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
tiempo_anterior = time.time()

while frame_global is None: time.sleep(0.1)

while corriendo:
    frame = frame_global.copy()
    h_img, w_img = frame.shape[:2]
    tiempo_actual = time.time()
    fps = 1 / (tiempo_actual - tiempo_anterior) if (tiempo_actual - tiempo_anterior) > 0 else 0
    tiempo_anterior = tiempo_actual
    t_res = max(0, 10.0 - (tiempo_actual - tiempo_inicio_reto)) if esperando_reto else 0
    
    tecla = cv2.waitKey(1) & 0xFF
    if tecla == ord('q'): break
    if tecla == ord('e'): exportar_reporte()

    if tecla == ord('b'):
        estado_sistema = "MODO BAJAS"
        color_estado = (0, 0, 255)
        dibujar_hud(frame, fps, ear_actual, es_humano_vivo, estado_sistema, color_estado, distancia_actual, tiempo_ia, contador_parpadeos, meta_parpadeos, esperando_reto, t_res)
        cv2.imshow('Shogun AI v2.5', frame) 
        dialog = ctk.CTkInputDialog(text="Nombre a borrar:", title="Bajas")
        nom_b = dialog.get_input()
        if nom_b and nom_b in base_de_datos:
            del base_de_datos[nom_b]
            with open(archivo_db, "wb") as f: pickle.dump(base_de_datos, f)
            actualizar_faiss(); hablar(f"Borrado {nom_b}"); sonido_exito()
        estado_sistema = "ESPERANDO BIOMETRIA"

    resultados_mesh = face_mesh.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    if resultados_mesh.multi_face_landmarks:
        ear_actual = calcular_ear(resultados_mesh.multi_face_landmarks[0].landmark, w_img, h_img)
        es_humano_vivo = True if ear_actual > 0.22 else False
        if esperando_reto:
            if t_res <= 0:
                esperando_reto = False; estado_sistema = "TIMEOUT"; color_estado = (0,0,255)
                sonido_error(); registrar_invalido("Timeout Reto", rostro_compartido)
            else:
                if ear_actual < 0.18 and not parpadeo_detectado: parpadeo_detectado = True
                if ear_actual > 0.22 and parpadeo_detectado:
                    contador_parpadeos += 1; parpadeo_detectado = False; beep_parpadeo()
                if contador_parpadeos >= meta_parpadeos:
                    reto_completado = True; esperando_reto = False
    else: ear_actual = 0.0; es_humano_vivo = False

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.1, 5, minSize=(100, 100))

    for (x, y, w, h) in faces:
        dibujar_esquinas(frame, x, y, w, h)
        rostro_compartido = frame[y:y+h, x:x+w].copy()
        
        if reto_completado:
            threading.Thread(target=procesar_identificacion, args=(rostro_compartido,), daemon=True).start()
            reto_completado = False

        if tecla == ord('i'):
            if es_humano_vivo:
                meta_parpadeos = random.randint(2, 4); tiempo_inicio_reto = time.time()
                esperando_reto = True; contador_parpadeos = 0
                hablar(f"Reto activo. Parpadea {meta_parpadeos} veces")
            else:
                estado_sistema = "SPOOF DETECTADO"
                color_estado = (0,0,255)
                sonido_error(); registrar_invalido("Ataque Foto", rostro_compartido)

        if tecla == ord('r'):
            if es_humano_vivo:
                var = cv2.Laplacian(cv2.cvtColor(rostro_compartido, cv2.COLOR_BGR2GRAY), cv2.CV_64F).var()
                if var > 60:
                    dibujar_hud(frame, fps, ear_actual, es_humano_vivo, "EXTRAYENDO...", (255,255,0), 0, 0, 0, 0, False, 0)
                    cv2.imshow('Shogun AI v2.5', frame)
                    nom = ctk.CTkInputDialog(text="🧬 BIOMETRÍA\nNombre:", title="Registro").get_input()
                    if nom:
                        res = DeepFace.represent(img_path=rostro_compartido, model_name="Facenet", enforce_detection=False, align=False)
                        base_de_datos[nom] = np.array(res[0]["embedding"])
                        with open(archivo_db, "wb") as f: pickle.dump(base_de_datos, f)
                        actualizar_faiss(); sonido_exito(); hablar(f"Bienvenido {nom}")
                else:
                    hablar("Imagen borrosa. Reintenta.")

    dibujar_hud(frame, fps, ear_actual, es_humano_vivo, estado_sistema, color_estado, distancia_actual, tiempo_ia, contador_parpadeos, meta_parpadeos, esperando_reto, t_res)
    cv2.imshow('Shogun AI v2.5', frame)

cv2.destroyAllWindows()