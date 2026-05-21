import cv2
import numpy as np
import tflite_runtime.interpreter as tflite
import time
# import RPi.GPIO as GPIO  # COMENTADO: Desativado por enquanto

# --- CONFIGURAÇÃO DO SERVO MOTOR (COMENTADO) ---
# PINO_SERVO = 18 
# GPIO.setmode(GPIO.BCM)
# GPIO.setup(PINO_SERVO, GPIO.OUT)
# servo = GPIO.PWM(PINO_SERVO, 50)
# servo.start(0)

def mover_servo(angulo):
    """ Função para mover o servo (Desativada temporariamente) """
    print(f"[MOTOR] Simulação: Movendo motor para {angulo} graus.")
    # duty = 2 + (angulo / 18)
    # GPIO.output(PINO_SERVO, True)
    # servo.ChangeDutyCycle(duty)
    # time.sleep(0.5) 
    # GPIO.output(PINO_SERVO, False)
    # servo.ChangeDutyCycle(0) 

# --- CARREGAR O MODELO TFLITE QUANTIZADO ---
MODEL_PATH = "model.tflite" 

interpreter = tflite.Interpreter(model_path=MODEL_PATH)
interpreter.allocate_tensors()

input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

# Mapeamento das classes exatamente na ordem do Teachable Machine
CLASSES = ["plastico", "papel", "metal", "rejeito"]

# --- INICIAR A CÂMERA ---
cap = cv2.VideoCapture(0)

print("Lixeira Inteligente Pronta! Aproxime o objeto...")

try:
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # O Teachable Machine usa imagens 224x224
        img = cv2.resize(frame, (224, 224))
        img = np.expand_dims(img, axis=0)
        
        # Converter para o formato que o modelo Quantized espera (UINT8)
        img = img.astype(np.uint8)

        # Rodar a IA
        interpreter.set_tensor(input_details[0]['index'], img)
        interpreter.invoke()
        output_data = interpreter.get_tensor(output_details[0]['index'])
        
        # Pegar o índice do resultado com maior certeza
        id_classe = np.argmax(output_data[0])
        classe_detectada = CLASSES[id_classe]
        certeza = output_data[0][id_classe] / 255.0 

        # Só toma uma ação se a IA tiver mais de 95% de certeza
        if certeza > 0.95:
            texto = f"{classe_detectada} ({certeza*100:.1f}%)"
            
            # --- LÓGICA DE MOVIMENTO DO SERVO ---
            if classe_detectada == "plastico":
                print("Detectado: Plástico ->Abre o lixo reciclavel")
                mover_servo(0) 
            elif classe_detectada == "papel":
                print("Detectado: Papel -> Abre o lixo reciclavel")
                mover_servo(0) 
            elif classe_detectada == "metal":
                print("Detectado: Metal -> Abre o lixo reciclavel")
                mover_servo(0)
            elif classe_detectada == "rejeito":
                print("Detectado: Rejeito -> Abre o lixo comum")
                mover_servo(90)
        else:
            texto = "Analisando..."

        # Mostrar na tela do VNC o que a IA está vendo
        cv2.putText(frame, texto, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.imshow("Lixeira Inteligente", frame)

        # Se apertar 'q' na janela da câmera, fecha o programa
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

except KeyboardInterrupt:
    print("\nDesligando lixeira...")

finally:
    cap.release()
    cv2.destroyAllWindows()
    # servo.stop()          # COMENTADO
    # GPIO.cleanup()        # COMENTADO
