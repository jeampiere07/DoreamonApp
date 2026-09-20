import cv2
import time
import pyttsx3
import pygame
import subprocess
import platform
import threading
import os
import signal
import tempfile
import shutil
import random

# ---------- CONFIGURACIÓN ----------
USE_LAPTOP_CAMERA = True                      # True = usar cámara integrada / False = usar cámara IP
USE_MUSIC = True                              # True = activar música de fondo
DETECTION_COOLDOWN = 10.0                     # Tiempo en segundos entre cada detección
WEB_DISPLAY_TIME = 5.0                        # Tiempo en segundos que se muestra la página
MAX_WIDTH = 640                               # Ancho máximo de la ventana
SHOW_DEBUG_BOXES = True                       # True = dibuja cajas en las caras detectadas
PERSON_CLOSE_THRESHOLD = 0.1                  # Porcentaje del frame para considerar una cara "cercana"
WEBPAGE_URL = "C:\\Users\\"  # Ruta local o link de la página web
BACKGROUND_VOLUME = 0.1                       # Volumen de la música de fondo (0.0 - 1.0)

# ---------- MODELO DE DETECCIÓN ----------
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
system = platform.system()

# ---------- FRASES ----------  #Puedes agregar más frases aquí
phrases = [                                           
    "TE AGRADECEMOS POR CUIDAR EL PLANETA", 
    "CONFÍO EN TI EN CUIDAR EL AMBIENTE",
    "TÚ SÍ PUEDES",
    "SÉ PROTECTOR DEL PLANETA",
]

def say_random_phrase():
    """Reproduce una frase motivacional aleatoria en voz alta"""
    phrase = random.choice(phrases)
    print(f"\033[36mFrase: {phrase}\033[0m")

    def tts_thread():
        local_tts = pyttsx3.init()
        local_tts.say(phrase)
        local_tts.runAndWait()
        local_tts.stop()

    threading.Thread(target=tts_thread, daemon=True).start()

# ---------- MÚSICA CON PYGAME ----------
if USE_MUSIC:
    pygame.mixer.init()
    pygame.mixer.music.load("musica.mp3")       # <<< Cambiar por tu archivo de música
    pygame.mixer.music.set_volume(BACKGROUND_VOLUME)
    pygame.mixer.music.play(-1)                 # -1 = loop infinito

# ---------- FUNCIONES ----------
def beep():
    """Hace un sonido de alerta"""
    try:
        if system == "Windows":
            import winsound
            winsound.Beep(1000, 300)            # Beep en Windows
        else:
            print('\a', end='', flush=True)     # Beep en Linux/Mac
    except:
        pass

def open_web_local(url, duration=WEB_DISPLAY_TIME):
    """Abre una página web local en Chrome y la cierra después de un tiempo"""
    def web_thread():
        temp_dir = tempfile.mkdtemp()
        try:
            print("\033[35mAbriendo página web local...\033[0m")

            say_random_phrase()

            if USE_MUSIC:
                pygame.mixer.music.set_volume(0.0)  # Silencia la música mientras se abre la página

            # ---------- Chrome según sistema operativo ----------
            if system == "Windows":
                chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
                if not os.path.exists(chrome_path):
                    chrome_path = r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
                proc = subprocess.Popen([
                    chrome_path,
                    f"--user-data-dir={temp_dir}",
                    "--incognito",
                    "--app=file:///" + url.replace("\\", "/")
                ])
            elif system == "Darwin":  # macOS
                proc = subprocess.Popen([
                    "open", "-na", "Google Chrome", "--args", "--incognito",
                    "--app=file://" + url
                ])
            else:  # Linux
                proc = subprocess.Popen([
                    "google-chrome", "--incognito",
                    "--app=file://" + url
                ])

            time.sleep(duration)

            if proc and proc.poll() is None:
                if system == "Windows":
                    proc.terminate()
                else:
                    os.kill(proc.pid, signal.SIGTERM)

            print("\033[31mPágina web cerrada\033[0m")
            if USE_MUSIC:
                pygame.mixer.music.set_volume(BACKGROUND_VOLUME)

        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

    threading.Thread(target=web_thread, daemon=True).start()

# ---------- CÁMARA ----------
CAMERA_SOURCE = 0 if USE_LAPTOP_CAMERA else "https://192.168.18.21:8080/video"  # <<< Cambiar IP si usas cámara remota
cap = cv2.VideoCapture(CAMERA_SOURCE)
if not cap.isOpened():
    raise RuntimeError("No se pudo abrir la cámara.")

last_trigger_time = 0.0
cv2.namedWindow("Program", cv2.WINDOW_NORMAL)
cv2.resizeWindow("Program", 480, 360)

# ---------- LOOP PRINCIPAL ----------
while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Redimensionar para no saturar la ventana
    height, width = frame.shape[:2]
    scale = MAX_WIDTH / max(width, height)
    frame_small = cv2.resize(frame, (int(width*scale), int(height*scale))) if scale < 1.0 else frame.copy()

    detected_close_person = False
    gray = cv2.cvtColor(frame_small, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)

    for (x, y, w, h) in faces:
        box_area = w * h
        frame_area = frame_small.shape[0] * frame_small.shape[1]
        if box_area / frame_area >= PERSON_CLOSE_THRESHOLD:
            detected_close_person = True
            print("\033[32mCara cercana detectada\033[0m")
        else:
            print("\033[33mCara lejana detectada\033[0m")

        # Dibuja caja en la cara
        if SHOW_DEBUG_BOXES:
            cv2.rectangle(frame_small, (x, y), (x+w, y+h),
                          (0,255,0) if detected_close_person else (0,255,255), 2)
            cv2.putText(frame_small, "Cara", (x, y-5), cv2.FONT_HERSHEY_SIMPLEX, 0.6,
                        (0,255,0) if detected_close_person else (0,255,255), 2)

    # Borde rojo de debug
    if SHOW_DEBUG_BOXES:
        cv2.rectangle(frame_small, (0,0), (frame_small.shape[1]-1, frame_small.shape[0]-1), (0,0,255), 2)

    # Acciones al detectar persona cercana
    now = time.time()
    if detected_close_person and (now - last_trigger_time > DETECTION_COOLDOWN):
        last_trigger_time = now
        beep()
        open_web_local(WEBPAGE_URL, WEB_DISPLAY_TIME)

    cv2.imshow("Program", frame_small)
    if cv2.waitKey(1) & 0xFF == ord("q"):  # Presionar Q para salir
        break

cap.release()
cv2.destroyAllWindows()
if USE_MUSIC:

    pygame.mixer.music.stop()
