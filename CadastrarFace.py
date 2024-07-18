import cv2
import numpy as np
import tkinter as tk
import time
from tkinter import *
import os
from CaixaDelimitadora import CaixaDelimitadora

#COR
greenColor=(0,255,0)

class CadastrarFace():
    def __init__(self, nomeUsuario):
        self.__haarcascade_face = cv2.CascadeClassifier("cascades/haarcascade_frontalface_default.xml")
        self.__amostra = 1
        self.__numeroAmostras = 5000
        self.__largura = 220
        self.__altura = 220
        self.__nomeUsuario=nomeUsuario
    def TirarFotos(self):
        camera = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        tempoFinal=0
        tempoInicial=0
        while True:
            _, video = camera.read()
            imagemCinza = cv2.cvtColor(video, cv2.COLOR_BGR2GRAY)
            detectar_face = self.__haarcascade_face.detectMultiScale(imagemCinza, scaleFactor=1.5, minSize=(100, 100))
            tempoFinal=time.time()
            fps=int(1/(tempoFinal-tempoInicial))
            tempoInicial=tempoFinal
            if not os.path.exists(f'fotos/{self.__nomeUsuario}'):
                os.makedirs(f'fotos/{self.__nomeUsuario}')

            for (x, y, w, h) in detectar_face:
                caixaDelimitadora=CaixaDelimitadora(video, greenColor)
                caixaDelimitadora.draw((x, y, w, h))
                if np.average(imagemCinza) > 30:#Verifica se a média dos valores dos pixels da imagem em escala de cinza (imagemCinza) é maior que 100. Essa verificação é usada para garantir que a imagem tenha um brilho suficiente antes de salvar a imagem da face detectada.
                    imagemFace = cv2.resize(imagemCinza[y:y + h, x:x + w], (self.__largura, self.__altura))
                    dirr = f"fotos/{self.__nomeUsuario}/{self.__amostra}.jpg"
                    cv2.imwrite(dirr, imagemFace)
                    print("foto " + str(self.__amostra) + " capturada com sucesso!")
                    self.__amostra += 1
            cv2.putText(video,f"FPS: {fps}",(5,40),cv2.FONT_HERSHEY_PLAIN,2,(0,200,0),3)#putText(frame,text,(positionX,positionY),font,tamanho,(B,G,R),espessura)
            cv2.putText(video,f"Amostras: {self.__amostra}/{self.__numeroAmostras}",(5,70),cv2.FONT_HERSHEY_PLAIN,2,(0,200,0),3)#putText(frame,text,(positionX,positionY),font,tamanho,(B,G,R),espessura)
            cv2.imshow("Video", video)

            if cv2.waitKey(1) == ord("q"):
                break

            if self.__amostra >= self.__numeroAmostras + 1:
                break

        print("Imagens da face capturadas com sucesso!")

        camera.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    nomeUsuario = input("Digite o nome do usuário: ")
    if nomeUsuario:
        cadastrarFace=CadastrarFace(nomeUsuario)
        cadastrarFace.TirarFotos()
