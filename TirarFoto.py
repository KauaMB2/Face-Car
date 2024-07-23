import cv2 as cv
from Cronometro import setInterval, clearInterval
import time
import os

# TEXTOS NAS IMAGENS
textFont = cv.FONT_HERSHEY_SIMPLEX  # Fonte do texto nas imagens
fontScale = 1  # Escala da fonte
textColor = (255, 255, 255)  # Cor do texto em BGR (branco)
textThickness = 2  # Espessura do texto

tempoInicialCronometro=5#Define tempo inicial do cronômetro
variavelCronometro=tempoInicialCronometro#Cria variável cronômetro

def contadorTempo():
    global variavelCronometro
    variavelCronometro -= 1

class TirarFoto:
    def __init__(self, DIR, entradaNome):
        self.__entradaNome=entradaNome
        self.__DIR=DIR
    def tirarFoto(self):
        global tempoInicialCronometro, variavelCronometro
        camera = cv.VideoCapture(0, cv.CAP_DSHOW)  # Inicializa a captura de vídeo da câmera padrão
        tempoFinal = 0  # Variável para armazenar o tempo final de captura de frame
        tempoInicial = 0  # Variável para armazenar o tempo inicial de captura de frame
        cronometroTirarFoto=setInterval(contadorTempo, 1)
        while camera.isOpened():  # Loop que continua enquanto a câmera estiver aberta
            _, frame = camera.read()  # Lê um frame da câmera
            # Mostra FPS
            tempoFinal = time.time()  # Obtém o tempo final para cálculo de FPS
            fps = int(1 / (tempoFinal - tempoInicial))  # Calcula o FPS como o inverso do tempo entre frames
            tempoInicial = tempoFinal  # Atualiza o tempo inicial para o próximo frame
            # Adiciona a informação de FPS ao frame
            cv.putText(frame, f"FPS: {(fps)}", (5, 70), textFont, fontScale, textColor, 3)  # Coloca o texto de FPS no frame
            cv.putText(frame, f"Tempo: {variavelCronometro}", (5, 100), textFont, fontScale, textColor, 3)  # Coloca o texto de tempo no frame
            chave = cv.waitKey(1)  # ESC = 27
            if chave == 27:  # Se apertou o ESC
                # Para o cronômetro que tira a foto
                clearInterval(cronometroTirarFoto)
                cronometroTirarFoto = None  # Reseta a variável do cronômetro
                variavelCronometro = tempoInicialCronometro  # Reseta a variável do cronômetro ao valor inicial
                break  # Sai do loop
            # Mostra o frame da câmera em uma janela chamada "Camera"
            cv.imshow("Camera", frame)
            if variavelCronometro == 0:  # Se o cronômetro chegou a zero
                clearInterval(cronometroTirarFoto)# Para o cronômetro que tira a foto
                cronometroTirarFoto = None  # Reseta a variável do cronômetro
                diretorioDosRoubos = f"{self.__DIR}/fotos/{self.__entradaNome}.jpg"# Define o caminho onde a foto será salva
                cv.imwrite(diretorioDosRoubos, frame)# Salva a foto no diretório especificado
                variavelCronometro = tempoInicialCronometro  # Reseta a variável do cronômetro ao valor inicial
                break  # Sai do loop
            cv.destroyAllWindows()# Fecha todas as janelas do OpenCV

if __name__ == "__main__":
    entradaNome = input("Informe o nome do usuário que será cadastrado: ")# Solicita o nome do usuário que será cadastrado
    cadastrarFace = TirarFoto(os.path.dirname(os.path.abspath(__file__)), entradaNome)# Cria uma instância da classe TirarFoto com o diretório atual e o nome do usuário
    cadastrarFace.tirarFoto()# Chama o método tirarFoto da instância criada
