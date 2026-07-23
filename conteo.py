import cv2
import argparse
from ultralytics import YOLO

# Configurar el paso de argumentos por consola
parser = argparse.ArgumentParser(description="Script para conteo de personas usando YOLOv8.")
parser.add_argument("video_path", help="Ruta del archivo de video a procesar")
args = parser.parse_args()

# 1. CARGAR EL MODELO DE DETECCIÓN
# Justificación de YOLO: Se elige YOLOv8n (versión nano) porque ofrece un excelente equilibrio 
# entre velocidad y precisión. Al estar altamente optimizado, permite procesar el video de 
# forma rápida (incluso en tiempo real) y es sumamente robusto para la clase "persona".
# REFERENCIA:
# https://doi.org/10.1109/ACCESS.2025.3630988
model = YOLO('yolov8n.pt') 

# 2. CONFIGURAR LECTURA DE VIDEO
video_path = args.video_path
cap = cv2.VideoCapture(video_path)

if not cap.isOpened():
    print("Error: No se pudo cargar el video. Verifica la ruta.")
    exit()

ancho = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
alto = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = int(cap.get(cv2.CAP_PROP_FPS))

# Regla: La línea de conteo debe estar en el 50% de la altura del frame
linea_y = alto // 2

# 3. CONFIGURAR ESCRITURA DE VIDEO
# Se guardará el resultado según lo exige el reto
output_path = "resultado_conteo.mp4"
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter(output_path, fourcc, fps, (ancho, alto))

# 4. VARIABLES LÓGICAS DEL CONTEO
posiciones_anteriores = {} 
ids_contados = set()
total_personas = 0

# 5. BUCLE DE PROCESAMIENTO FRAME A FRAME
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break # Fin del video

    # Aplicar Detección y Tracking
    # Justificación de ByteTrack: Se elige ByteTrack ('bytetrack.yaml') porque asocia 
    # las detecciones considerando tanto los umbrales altos como los bajos de confianza. 
    # Esto reduce drásticamente la pérdida de IDs (ID switches) cuando una persona se oculta 
    # temporalmente detrás de un poste o de otra persona, siendo ideal para un conteo fiable.
    # Se usa classes=[0] para filtrar y detectar exclusivamente personas (clase 0 en COCO).
    # REFERENCIA:
    # https://docs.ultralytics.com/modes/track#tracker-details
    resultados = model.track(frame, classes=[0], tracker="bytetrack.yaml", persist=True, verbose=False)

    # Dibujar la línea virtual de cruce en el frame
    cv2.line(frame, (0, linea_y), (ancho, linea_y), (0, 0, 255), 2)

    # Validar si hubo detecciones con ID asignado en este frame
    if resultados[0].boxes.id is not None:
        cajas = resultados[0].boxes.xyxy.cpu().numpy()
        ids = resultados[0].boxes.id.cpu().numpy().astype(int)
        confianzas = resultados[0].boxes.conf.cpu().numpy()

        for caja, track_id, conf in zip(cajas, ids, confianzas):
            x1, y1, x2, y2 = map(int, caja)
            
            # Calculamos el centro del bounding box para evaluar el cruce
            centro_x = (x1 + x2) // 2
            centro_y = (y1 + y2) // 2

            # Regla: Dibujar rectángulo, ID y confianza
            texto_label = f"ID: {track_id} | Conf: {conf:.2f}"
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(frame, texto_label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 255, 0), 2)
            
            # Dibujar un punto en el centro de la persona para visualizar mejor el track
            cv2.circle(frame, (centro_x, centro_y), 4, (255, 0, 0), -1)

            # 6. LÓGICA DE CRUCE Y CONTEO
            if track_id in posiciones_anteriores:
                y_anterior = posiciones_anteriores[track_id]
                
                # Verificamos si la persona cruzó la línea hacia arriba o hacia abajo
                cruzo_hacia_abajo = y_anterior < linea_y and centro_y >= linea_y
                cruzo_hacia_arriba = y_anterior > linea_y and centro_y <= linea_y

                # Regla: Si cruzó la línea y su ID no está en los ya contados
                if (cruzo_hacia_abajo or cruzo_hacia_arriba) and track_id not in ids_contados:
                    total_personas += 1
                    ids_contados.add(track_id) # Registramos su ID para no volver a contarlo

            # Actualizamos la posición Y actual de este ID para el próximo frame
            posiciones_anteriores[track_id] = centro_y

    # Regla: Escribir el contador en la esquina superior izquierda
    cv2.putText(frame, f"Total personas: {total_personas}", (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 255), 3)

    # Guardar el frame en el video de salida
    out.write(frame)
    
    # Mostrar el proceso en pantalla
    cv2.imshow("Conteo de Personas - YOLOv8", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# 7. LIBERACIÓN DE RECURSOS
cap.release()
out.release()
cv2.destroyAllWindows()
print(f"Procesamiento terminado. Se guardó el resultado en: {output_path}")
