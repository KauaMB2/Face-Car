import cv2 as cv
import time
import os
from CaixaDelimitadora import CaixaDelimitadora
from Cronometro import setInterval, clearInterval
import serial
from datetime import datetime
import tkinter as tk
from tkinter import messagebox


initialInvasionLimitTime = 5
initialSafeLimitTime = 5
cronometroDeRoubo = None
cronometroSeguranca = None

# CORES
corVermelha = (0, 0, 255)
corVerde = (0, 255, 0)

# TEXTOS NAS IMAGENS
textFont = cv.FONT_HERSHEY_SIMPLEX
fontScale = 1
textColor = (255, 255, 255)  # White color in BGR
textThickness = 2


def mostrarMensagemDeErro(title, message):
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    messagebox.showerror(title, message)
    root.destroy()


class Camera():
    def __init__(self, portaSerialArduino):
        self.__haar_cascade = cv.CascadeClassifier(r'cascades\haarcascade_frontalface_default.xml')
        self.__pessoas = os.listdir("fotos")
        self.__reconhecedorDeFaces = cv.face.LBPHFaceRecognizer_create()
        self.__reconhecedorDeFaces.read(r'classificadores\faceTrained.yml')
        self.__tempoLimiteDeRoubo = initialInvasionLimitTime
        self.__tempoLimiteDeSeguranca = initialSafeLimitTime
        self.__portaSerialArduino=None
        try:
            self.__portaSerialArduino = serial.Serial(portaSerialArduino, 9600, timeout=1)
            print(self.__portaSerialArduino)
            print(self.__portaSerialArduino.is_open)
        except Exception as e:
            mensagemDeErro = f"Não foi possível enviar a informação ao Arduino.\n\nResposta do computador: {e}"
            mostrarMensagemDeErro("FACE CAR - Erro Arduino", mensagemDeErro)
        self.__estaSeguro = True

    def contadorRoubo(self):
        self.__tempoLimiteDeRoubo -= 1
        print("contadorRoubo")
        print(self.__tempoLimiteDeRoubo)

    def contadorSeguranca(self):
        self.__tempoLimiteDeSeguranca -= 1
        print("contadorSeguranca")
        print(self.__tempoLimiteDeSeguranca)

    def reconhecer(self):
        global cronometroDeRoubo, cronometroSeguranca, corVerde, corVermelha
        camera = cv.VideoCapture(0, cv.CAP_DSHOW)
        # Time variables
        tempoFinal = 0
        tempoInicial = 0
        while camera.isOpened():
            _, frame = camera.read()
            gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
            facesDetectadas = self.__haar_cascade.detectMultiScale(gray, 1.1, 4)
            if len(facesDetectadas) == 0 and self.__estaSeguro == False:
                self.__estaSeguro = True
            # Show FPS
            tempoFinal = time.time()
            fps = int(1 / (tempoFinal - tempoInicial))
            tempoInicial = tempoFinal
            cv.putText(frame, f"FPS: {(fps)}", (5, 70), textFont, fontScale, textColor, 3)  # putText(frame,text,(positionX,positionY),font,tamanho,(B,G,R),espessura)
            for (x, y, w, h) in facesDetectadas:
                facesCortadas = gray[y:y + h, x:x + h]
                faceNome, confianca = self.__reconhecedorDeFaces.predict(facesCortadas)
                if len(self.__pessoas) != 0:
                    # print(f'faceNome = {self.__pessoas[faceNome]} with a confianca of {confianca}')
                    texto = f"{self.__pessoas[faceNome]} - {round(confianca, 2)}%"
                    (texto_largura, texto_altura), _ = cv.getTextSize(texto, textFont, fontScale, textThickness)  # Get the largura and altura of the text box
                    cv.rectangle(frame, (x, y - texto_altura - 10), (x + texto_largura, y), (0, 0, 0), -1)  # Draw the rectangle background for the text
                    threshold = 50  # Minimun percentage of confianca to show image
                    if confianca > threshold and confianca < 60:
                        cv.putText(frame, texto, (x, y - 5), textFont, fontScale, corVerde, textThickness)  # Put the text on top of the rectangle
                        caixaDelimitadora = CaixaDelimitadora(frame, corVerde)
                        frame = caixaDelimitadora.draw((x, y, w, h))
                        if not self.__estaSeguro and cronometroSeguranca == None:
                            print("not self.__estaSeguro and cronometroSeguranca==None")
                            cronometroSeguranca = setInterval(self.contadorSeguranca, 1)
                            self.__tempoLimiteDeRoubo = initialInvasionLimitTime
                            self.__tempoLimiteDeSeguranca = initialSafeLimitTime
                    else:
                        cv.putText(frame, texto, (x, y - 5), cv.FONT_HERSHEY_COMPLEX, 0.9, corVermelha, thickness=2)  # Put the text on top of the rectangle
                        caixaDelimitadora = CaixaDelimitadora(frame, corVermelha)
                        frame = caixaDelimitadora.draw((x, y, w, h))
                        if self.__estaSeguro and cronometroDeRoubo == None:
                            print("self.__estaSeguro and cronometroDeRoubo==None")
                            cronometroDeRoubo = setInterval(self.contadorRoubo, 1)
                            self.__estaSeguro = False
                            self.__tempoLimiteDeRoubo = initialInvasionLimitTime
                            self.__tempoLimiteDeSeguranca = initialSafeLimitTime

            if self.__tempoLimiteDeRoubo == 0 and cronometroDeRoubo != None:
                print("self.__tempoLimiteDeRoubo==0 and cronometroDeRoubo != None")
                print("ROUBO!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
                DIR = os.path.dirname(os.path.abspath(__file__))
                # Add date and time to the image
                dataEhoraAtual = datetime.now()
                tempoAtual = dataEhoraAtual.strftime("%Y-%m-%d %H:%M:%S")
                nomeDaFoto = dataEhoraAtual.strftime("%Y-%m-%d %H-%M-%S")
                diretorioDosRoubos = f"{DIR}/roubos/{nomeDaFoto}.png"
                position = (10, 30)  # Bottom left corner of the image
                fotoDoRoubo = frame
                # Adding text to the image
                cv.putText(fotoDoRoubo, tempoAtual, position, textFont, fontScale, textColor, textThickness, cv.LINE_AA)
                cv.imwrite(diretorioDosRoubos, fotoDoRoubo)
                clearInterval(cronometroDeRoubo)
                cronometroDeRoubo = None
                try:
                    print(self.__portaSerialArduino)
                    self.__portaSerialArduino.write(f'{255}\n'.encode())
                except Exception as e:
                    if self.__portaSerialArduino and self.__portaSerialArduino.is_open:
                        self.__portaSerialArduino.close()
                    mensagemDeErro = f"Não foi possível enviar a informação ao Arduino.\n\nResposta do computador: {e}"
                    mostrarMensagemDeErro("FACE CAR - Erro Arduino", mensagemDeErro)
                self.__tempoLimiteDeRoubo = initialInvasionLimitTime
                self.__tempoLimiteDeSeguranca = initialSafeLimitTime
            if self.__tempoLimiteDeSeguranca == 0 and cronometroSeguranca != None:
                print("self.__tempoLimiteDeSeguranca==0 and cronometroSeguranca !=None")
                self.__estaSeguro = True
                if cronometroDeRoubo:
                    clearInterval(cronometroDeRoubo)
                    cronometroDeRoubo = None
                if cronometroSeguranca:
                    clearInterval(cronometroSeguranca)
                    cronometroSeguranca = None
                self.__estaSeguro = True
                self.__tempoLimiteDeRoubo = initialInvasionLimitTime
                self.__tempoLimiteDeSeguranca = initialSafeLimitTime
            key = cv.waitKey(1)  # ESC = 27
            if key == 27:  # Se apertou o ESC
                if cronometroDeRoubo:
                    clearInterval(cronometroDeRoubo)
                    cronometroDeRoubo = None
                if cronometroSeguranca:
                    clearInterval(cronometroSeguranca)
                    cronometroSeguranca = None
                break
            cv.imshow("Camera", frame)
        if self.__portaSerialArduino and self.__portaSerialArduino.is_open:
            self.__portaSerialArduino.close()
        cv.destroyAllWindows()

if __name__ == "__main__":
    portaSerial = input("Informe o número(Somente número. Ex: 4) da porta serial: ")
    cadastrarFace = Camera(f"{portaSerial}")
    cadastrarFace.reconhecer()
