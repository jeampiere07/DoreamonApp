# Sensor de Cámara con Detección de Rostros

Este proyecto utiliza **OpenCV** para detectar rostros en tiempo real desde una cámara (integrada o IP).  
Cuando una persona se acerca a la cámara:  
- Se reproduce una **frase motivacional en voz alta**.  
- Se emite un **sonido de alerta (beep)**.  
- Se abre una **página web local** en Google Chrome durante algunos segundos.  
- Opcionalmente, se reproduce **música de fondo**. 

---

## Características
- Detección de rostros con HaarCascade.
- Diferencia entre persona **cercana** y **lejana**.
- Reproduce frases aleatorias con **pyttsx3**.
- Abre una página web automáticamente.
- Música de fondo configurable.
- Compatible con **Windows, Linux y macOS**.

---

## Configuración
En el archivo principal (`main.py`) puedes editar:

- `USE_LAPTOP_CAMERA` → `True` para cámara integrada / `False` para cámara IP.  
- `WEBPAGE_URL` → Ruta local de la página a mostrar.  
- `BACKGROUND_VOLUME` → Volumen de la música de fondo.  
- `DETECTION_COOLDOWN` → Tiempo entre detecciones (segundos).  
- `phrases` → Lista de frases motivacionales.  

---

## Ejecución

1. Instalar dependencias:
   ```bash
   pip install -r requirements.txt