# Lixeira Inteligente 🗂️♻️

## Descrição

Esse projeto surge como uma solução prática para realizar a triagem de resíduos entre recicláveis e não-recicláveis. O sistema inteligente utiliza visão computacional e aprendizado de máquina para classificar e separar automaticamente o lixo no compartimentos apropriado. O sistema combina o reconhecimento de imagem baseado em Raspberry Pi com um mecanismo servo para a triagem automatizada.

## Características

* Classificação de resíduos em tempo real usando o modelo TensorFlow Lite
* Mecanismo de triagem automatizado com seletor de caixas controlado por servomotor
* Detecção de resíduos em 5 categorias : Vidro, Metal, Papel, Plástico e Lixo Comum
* Feedback visual com transmissão ao vivo da câmera e confiança na classificação
* Detecção inteligente de centro - processa apenas objetos colocados na área designada.
* Integração com Arduino para controle preciso de servos.
* Sistema de votação - analisa objetos em um intervalo de 5 segundos para classificação precisa.

## 🛠️ Requisitos de hardware

### Configuração do Raspberry Pi

* Raspberry Pi 3B+
* Webcam USB
* Cartão SD (32 GB)
* Fonte de alimentação (5V, 2A)
* Servo motor (SG90)

### Componentes físicos

* Lixeiras para coleta de lixo (2x)
* Estrutura de montagem para câmera e servo
* Sistema de calha

## Autores

* **Matheus Pereira** - matheusmendesdpereira@gmail.com
* **Gabriel Dalla Costa** - glanderdahldallacosta@gmail.com
* **Kalyl** - personalsafekalyl@hotmail.com
* **Luana Raskopf Stürmer** - luanaraskopf@gmail.com


