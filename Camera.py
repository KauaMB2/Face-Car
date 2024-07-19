import cv2 as cv
import time
import os
from CaixaDelimitadora import CaixaDelimitadora
from Cronometro import setInterval, clearInterval
import serial
from datetime import datetime
import tkinter as tk
from tkinter import messagebox
import face_recognition as fr

initialInvasionLimitTime = 10
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
        self.__known_face_encodings = []
        self.__known_face_names = []
        self.__estaSeguro = True

        base_dir = os.path.dirname(os.path.abspath(__file__))
        fotos_dir = os.path.join(base_dir, "fotos")

        try:
            for filename in os.listdir(fotos_dir):
                if filename.endswith(".jpg") or filename.endswith(".png"):  # Adicione mais extensões se necessário
                    img_path = os.path.join(fotos_dir, filename)
                    try:
                        img = fr.load_image_file(img_path)
                        img = cv.cvtColor(img, cv.COLOR_BGR2RGB)
                        face_encodings = fr.face_encodings(img)
                        if face_encodings:
                            self.__known_face_encodings.append(face_encodings[0])
                            self.__known_face_names.append(os.path.splitext(filename)[0])  # Use o nome do arquivo sem a extensão como nome
                    except Exception as e:
                        print(f"Erro ao processar a imagem {img_path}: {e}")
        
        except Exception as e:
            print(f"Erro ao acessar a pasta 'fotos': {e}")
            mostrarMensagemDeErro("FACE CAR - Erro", f"Erro ao acessar a pasta 'fotos': {e}")

        self.__tempoLimiteDeRoubo = initialInvasionLimitTime
        self.__tempoLimiteDeSeguranca = initialSafeLimitTime
        self.__portaSerialArduino = None
        try:
            self.__portaSerialArduino = serial.Serial(portaSerialArduino, 9600, timeout=1)
            print(self.__portaSerialArduino)
            print(self.__portaSerialArduino.is_open)
        except Exception as e:
            pass
            # mensagemDeErro = f"Não foi possível enviar a informação ao Arduino.\n\nResposta do computador: {e}"
            # mostrarMensagemDeErro("FACE CAR - Erro Arduino", mensagemDeErro)

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
            rgb_frame = frame[:, :, ::-1]
            # Find all the faces and face encodings in the current frame
            facesDetectadas = fr.face_locations(rgb_frame)
            facesCodificacoes = fr.face_encodings(rgb_frame, facesDetectadas)
            if not facesDetectadas and self.__estaSeguro == False and cronometroSeguranca!=None:
                clearInterval(cronometroSeguranca)
                cronometroSeguranca=None
                self.__tempoLimiteDeSeguranca
            # Show FPS
            tempoFinal = time.time()
            fps = int(1 / (tempoFinal - tempoInicial))
            tempoInicial = tempoFinal
            cv.putText(frame, f"FPS: {(fps)}", (5, 70), textFont, fontScale, textColor, 3)  # putText(frame,text,(positionX,positionY),font,tamanho,(B,G,R),espessura)

            for (top, right, bottom, left), face_encoding in zip(facesDetectadas, facesCodificacoes):
                # See if the face in the frame matches the known face(s)
                matches = fr.compare_faces(self.__known_face_encodings, face_encoding)
                if not matches:
                    name = "Desconhecido"
                    confianca = 0.0
                else:
                    # Use the known face with the smallest distance to the new face
                    face_distances = fr.face_distance(self.__known_face_encodings, face_encoding)
                    best_match_index = face_distances.argmin()
                    if best_match_index < len(matches) and matches[best_match_index]:
                        name = self.__known_face_names[best_match_index]
                        confianca = (1 - face_distances[best_match_index]) * 100
                        texto = f"{name} - {round(confianca, 2)}%"
                        (texto_largura, texto_altura), _ = cv.getTextSize(texto, textFont, fontScale, textThickness)  # Get the width and height of the text box
                        # Draw the rectangle background for the text above the box
                        cv.rectangle(frame, (left, top - texto_altura - 10), (left + texto_largura, top), (0,0,0), -1)
                        # Put text above the box
                        cv.putText(frame, texto, (left, top - 10), textFont, fontScale, textColor, textThickness, cv.LINE_AA)
                        caixaDelimitadora = CaixaDelimitadora(frame, corVerde)
                        bbox = (left, top, right - left, bottom - top)
                        frame = caixaDelimitadora.draw(bbox)
                        if not self.__estaSeguro and cronometroSeguranca == None:
                            print("not self.__estaSeguro and cronometroSeguranca==None")
                            cronometroSeguranca = setInterval(self.contadorSeguranca, 1)
                            self.__tempoLimiteDeSeguranca = initialSafeLimitTime
                    else:
                        name = "Desconhecido"
                        confianca = 0.0
                        # New way to display name and confidence
                        texto = f"{name} - {round(confianca, 2)}%"
                        (texto_largura, texto_altura), _ = cv.getTextSize(texto, textFont, fontScale, textThickness)  # Get the width and height of the text box
                        # Draw the rectangle background for the text above the box
                        cv.rectangle(frame, (left, top - texto_altura - 10), (left + texto_largura, top), (0,0,0), -1)
                        # Put text above the box
                        cv.putText(frame, texto, (left, top - 10), textFont, fontScale, textColor, textThickness, cv.LINE_AA)
                        # Draw a box around the face using CaixaDelimitadora
                        caixaDelimitadora = CaixaDelimitadora(frame, corVermelha)
                        bbox = (left, top, right - left, bottom - top)
                        frame = caixaDelimitadora.draw(bbox)
                        if self.__estaSeguro and cronometroDeRoubo == None:
                            print("self.__estaSeguro and cronometroDeRoubo==None")
                            cronometroDeRoubo = setInterval(self.contadorRoubo, 1)
                            self.__estaSeguro = False
                            self.__tempoLimiteDeRoubo = initialInvasionLimitTime
            if self.__tempoLimiteDeRoubo == 0 and cronometroDeRoubo is not None:
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
                if cronometroSeguranca != None:
                    clearInterval(cronometroSeguranca)
                    cronometroSeguranca = None
                self.__estaSeguro=True
                try:
                    print(self.__portaSerialArduino)
                    self.__portaSerialArduino.write(f'{1}\n'.encode())
                except Exception as e:
                    if self.__portaSerialArduino and self.__portaSerialArduino.is_open:
                        self.__portaSerialArduino.close()
                    mensagemDeErro = f"Não foi possível enviar a informação ao Arduino.\n\nResposta do computador: {e}"
                    mostrarMensagemDeErro("FACE CAR - Erro Arduino", mensagemDeErro)
                self.__tempoLimiteDeRoubo = initialInvasionLimitTime
                self.__tempoLimiteDeSeguranca = initialSafeLimitTime

            if self.__tempoLimiteDeSeguranca == 0 and cronometroSeguranca is not None:
                print("self.__tempoLimiteDeSeguranca==0 and cronometroSeguranca !=None")
                self.__estaSeguro = True
                clearInterval(cronometroSeguranca)
                cronometroSeguranca = None
                if cronometroDeRoubo:
                    clearInterval(cronometroDeRoubo)
                    cronometroDeRoubo = None
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
            if self.__tempoLimiteDeRoubo<0 or self.__tempoLimiteDeSeguranca<0:
                self.__tempoLimiteDeRoubo=initialInvasionLimitTime
                self.__tempoLimiteDeSeguranca=initialSafeLimitTime
                self.__estaSeguro=True



        if self.__portaSerialArduino and self.__portaSerialArduino.is_open:
            self.__portaSerialArduino.close()
        cv.destroyAllWindows()

if __name__ == "__main__":
    portaSerial = input("Informe o número(Somente número. Ex: 4) da porta serial: ")
    cadastrarFace = Camera(f"{portaSerial}")
    cadastrarFace.reconhecer()
