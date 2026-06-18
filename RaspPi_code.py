import cv2
import numpy as np
import tflite_runtime.interpreter as tflite
import time
import RPi.GPIO as GPIO  # COMENTADO: Desativado por enquanto

# --- CONFIGURAÇÃO DO SERVO MOTOR ---
PINO_SERVO = 18 
GPIO.setmode(GPIO.BCM)
GPIO.setup(PINO_SERVO, GPIO.OUT)
servo = GPIO.PWM(PINO_SERVO, 50)
servo.start(0)

def mover_servo(angulo):
    print(f"[MOTOR] Movendo para {angulo} graus.")
    duty = 2 + (angulo / 18)
    GPIO.output(PINO_SERVO, True)
    servo.ChangeDutyCycle(duty)
    time.sleep(0.5) 
    GPIO.output(PINO_SERVO, False)
    servo.ChangeDutyCycle(0) 

# --- CONFIGURAÇÕES DO PROJETO ---
MODEL_PATH = "model.tflite"
LIMITE_CONFIANCA = 0.90  # Limite de 90% de certeza
CLASSES = ["plastico", "papel", "metal", "rejeito"]

# --- INICIALIZAR O MODELO DE IA ---
interpreter = tflite.Interpreter(model_path=MODEL_PATH)
interpreter.allocate_tensors()
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

# --- VARIÁVEIS DE CONTROLE DE ESTADO ---
ultima_classe_estavel = "vazio"
contador_confirmacao = 0
LEITURAS_NECESSARIAS = 8  # Quantas frames seguidas a IA precisa acertar para mover a rampa

# --- INICIAR A CÂMERA ---
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640) # Baixa resolução
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

print("Lixeira Inteligente Pronta na posição HOME (Horizontal)...")
mover_servo(90) # Começa na horizontal

try:
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Erro ao acessar a câmera.")
            break

       
        img = cv2.resize(frame, (224, 224))
        img = np.expand_dims(img, axis=0).astype(np.uint8)

        # Rodar a IA
        interpreter.set_tensor(input_details[0]['index'], img)
        interpreter.invoke()
        output_data = interpreter.get_tensor(output_details[0]['index'])
        
        # Pegar o índice do resultado com maior certeza
        id_classe = np.argmax(output_data[0])
        classe_detectada = CLASSES[id_classe]
        certeza = output_data[0][id_classe] / 255.0 

        # Filtro 1: Confiança alta?
        if certeza >= LIMITE_CONFIANCA:
            # Filtro 2: É o mesmo objeto que vimos no frame anterior?
            if classe_detectada == ultima_classe_estavel:
                contador_confirmacao += 1
            else:
                contador_confirmacao = 0
                ultima_classe_estavel = classe_detectada
        else:
            contador_confirmacao = 0 # Se hesitar, zera o contador

        # Se a IA detectou a mesma coisa com certeza por vários frames seguidos:
        if contador_confirmacao >= LEITURAS_NECESSARIAS:

            # Se for apenas o fundo vazio, não faz nada, continua reto
            if classe_detectada == "vazio":
                texto_status = "Aguardando objeto..."
                contador_confirmacao = 0

            # Se for RECICLÁVEL (Plástico, Papel ou Metal)
            elif classe_detectada in ["plastico", "papel", "metal"]:
                print(f"\n[SUCESSO] Confirmado {classe_detectada}! Destino: RECICLÁVEL")
                mover_servo(45) # Inclina a rampa para o lado reciclável
                print("Aguardando o objeto deslizar...")
                time.sleep(3.0) # Espera 3 segundos com a rampa aberta

                print("Retornando para a posição HOME...")
                mover_servo(90) # Volta para a horizontal
                time.sleep(1.0) # Tempo de estabilização
                contador_confirmacao = 0 # Reseta para a próxima leitura

            # Se for REJEITO (Não reciclável)
            elif classe_detectada == "rejeito":
                print(f"\n[SUCESSO] Confirmado Rejeito! Destino: NÃO RECICLÁVEL")
                mover_servo(135) # Inclina a rampa para o outro lado
                print("Aguardando o objeto deslizar...")
                time.sleep(3.0)

                print("Retornando para a posição HOME...")
                mover_servo(90)
                time.sleep(1.0)
                contador_confirmacao = 0
                
        # Interface visual do VNC
        texto_tela = f"Vendo: {classe_detectada} ({certeza*100:.0f}%) | Conf: {contador_confirmacao}"
        cv2.putText(frame, texto_tela, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.imshow("Lixeira Inteligente", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

except KeyboardInterrupt:
    print("\nDesligando lixeira...")
finally:
    cap.release()
    cv2.destroyAllWindows()
    servo.stop()       
    GPIO.cleanup()        
