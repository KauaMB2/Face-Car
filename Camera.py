import cv2 as cv  # Importa a biblioteca OpenCV para processamento de imagens e vídeos
import time  # Importa a biblioteca time para funções relacionadas ao tempo
import os  # Importa a biblioteca os para manipulação de arquivos e diretórios
from CaixaDelimitadora import CaixaDelimitadora  # Importa a classe CaixaDelimitadora do módulo CaixaDelimitadora
from Cronometro import setInterval, clearInterval  # Importa as funções setInterval e clearInterval do módulo Cronometro
import serial  # Importa a biblioteca serial para comunicação serial
from datetime import datetime  # Importa a classe datetime do módulo datetime
import tkinter as tk #Importa tkinter
from tkinter import messagebox  # Importa a função messagebox do tkinter para exibição de mensagens
import face_recognition as fr  # Importa a biblioteca face_recognition para reconhecimento facial

tempoLimiteDeInvasao = 10  # Tempo limite inicial para invasão em segundos
tempoLimiteDeSeguranca = 5  # Tempo limite inicial de segurança em segundos
cronometroDeRoubo = None  # Variável para armazenar o cronômetro de roubo
cronometroSeguranca = None  # Variável para armazenar o cronômetro de segurança

# CORES 
corVermelha = (0, 0, 255)  # Define a cor vermelha em BGR
corVerde = (0, 255, 0)  # Define a cor verde em BGR

# TEXTOS NAS IMAGENS
textFont = cv.FONT_HERSHEY_SIMPLEX  # Fonte do texto nas imagens
fontScale = 1  # Escala da fonte
textColor = (255, 255, 255)  # Cor do texto em BGR (branco)
textThickness = 2  # Espessura do texto

def mostrarMensagemDeErro(title, message):#Função para exibir error
    root = tk.Tk()#Cria janela tkinter
    root.withdraw()  # Esconde a tela principal
    messagebox.showerror(title, message)#Mostra a mensagem de erro
    root.destroy()#Apaga janela principal e deixa somente a de erro

class Camera():
    def __init__(self, portaSerialArduino):  # Inicializador da classe Camera
        self.__facesCodificadasConhecidas = []  # Lista de codificações faciais conhecidas
        self.__nomeDasFacesConhecidas = []  # Lista de nomes conhecidos
        self.__estaSeguro = True  # Estado de segurança inicial

        base_dir = os.path.dirname(os.path.abspath(__file__))  # Diretório base
        fotos_dir = os.path.join(base_dir, "fotos")  # Diretório das fotos

        try:
            for filename in os.listdir(fotos_dir):  # Percorre os arquivos no diretório de fotos
                if filename.endswith(".jpg") or filename.endswith(".png"):  # Verifica a extensão do arquivo
                    img_path = os.path.join(fotos_dir, filename)  # Caminho da imagem
                    try:
                        img = fr.load_image_file(img_path)  # Carrega a imagem
                        img = cv.cvtColor(img, cv.COLOR_BGR2RGB)  # Converte a imagem para RGB
                        facesCodificadas = fr.face_encodings(img)  # Codifica a face na imagem
                        if facesCodificadas:  # Se houver codificação
                            self.__facesCodificadasConhecidas.append(facesCodificadas[0])  # Adiciona a codificação à lista
                            self.__nomeDasFacesConhecidas.append(os.path.splitext(filename)[0])  # Adiciona o nome à lista
                    except Exception as e:
                        print(f"Erro ao processar a imagem {img_path}: {e}")
        
        except Exception as e:
            print(f"Erro ao acessar a pasta 'fotos': {e}")
            mostrarMensagemDeErro("FACE CAR - Erro", f"Erro ao acessar a pasta 'fotos': {e}")# Exibe uma mensagem de erro

        self.__tempoLimiteDeRoubo = tempoLimiteDeInvasao  # Tempo limite de roubo inicial
        self.__tempoLimiteDeSeguranca = tempoLimiteDeSeguranca  # Tempo limite de segurança inicial
        self.__portaSerialArduino = None  # Inicializa a porta serial do Arduino
        try:
            self.__portaSerialArduino = serial.Serial(portaSerialArduino, 9600, timeout=1)  # Tenta inicializar a conexão serial com o Arduino na porta especificada
            print(self.__portaSerialArduino)  # Imprime o objeto serial para depuração
            print(self.__portaSerialArduino.is_open)  # Imprime se a porta serial está aberta para confirmação
        except Exception as e:
            pass  # Passa a exceção sem tratamento, mas poderia ser melhor lidar com isso
            # mensagemDeErro = f"Não foi possível enviar a informação ao Arduino.\n\nResposta do computador: {e}"  # Código comentado para exibir mensagem de erro, caso a conexão com o Arduino falhe
            # mostrarMensagemDeErro("FACE CAR - Erro Arduino", mensagemDeErro)

    def contadorRoubo(self):
        self.__tempoLimiteDeRoubo -= 1  # Decrementa o tempo limite de roubo em 1
        print("contadorRoubo")  # Imprime "contadorRoubo" para indicar que o contador de roubo está ativo
        print(self.__tempoLimiteDeRoubo)  # Imprime o valor atual do tempo limite de roubo para depuração

    def contadorSeguranca(self):
        self.__tempoLimiteDeSeguranca -= 1  # Decrementa o tempo limite de segurança em 1
        print("contadorSeguranca")  # Imprime "contadorSeguranca" para indicar que o contador de segurança está ativo
        print(self.__tempoLimiteDeSeguranca)  # Imprime o valor atual do tempo limite de segurança para depuração


    def reconhecer(self):  # Define o método 'reconhecer' da classe
        global cronometroDeRoubo, cronometroSeguranca, corVerde, corVermelha  # Declara variáveis globais usadas para cronômetros e cores
        
        camera = cv.VideoCapture(0, cv.CAP_DSHOW)  # Inicializa a captura de vídeo da câmera padrão
        
        # Time variables
        tempoFinal = 0  # Variável para armazenar o tempo final de captura de frame
        tempoInicial = 0  # Variável para armazenar o tempo inicial de captura de frame
        
        while camera.isOpened():  # Loop que continua enquanto a câmera estiver aberta
            _, frame = camera.read()  # Lê um frame da câmera
            rgb_frame = frame[:, :, ::-1]  # Converte o frame de BGR para RGB
            
            # Find all the faces and face encodings in the current frame
            facesDetectadas = fr.face_locations(rgb_frame)  # Detecta a localização das faces no frame
            facesCodificadas = fr.face_encodings(rgb_frame, facesDetectadas)  # Obtém as codificações das faces detectadas
            
            if not facesDetectadas and self.__estaSeguro == False and cronometroSeguranca != None:  # Se não há faces detectadas e o sistema não está seguro
                clearInterval(cronometroSeguranca)  # Para o cronômetro de segurança
                cronometroSeguranca = None  # Define o cronômetro de segurança como None
                self.__tempoLimiteDeSeguranca  # (Esta linha parece desnecessária, pois não faz nada)
            
            # Show FPS
            tempoFinal = time.time()  # Obtém o tempo final para cálculo de FPS
            fps = int(1 / (tempoFinal - tempoInicial))  # Calcula o FPS como o inverso do tempo entre frames
            tempoInicial = tempoFinal  # Atualiza o tempo inicial para o próximo frame
            
            # Adiciona a informação de FPS ao frame
            cv.putText(frame, f"FPS: {(fps)}", (5, 70), textFont, fontScale, textColor, 3)  # Coloca o texto de FPS no frame
        
            for (top, right, bottom, left), face_encoding in zip(facesDetectadas, facesCodificadas):  # Itera sobre as faces detectadas e suas codificações
                # See if the face in the frame matches the known face(s)
                matches = fr.compare_faces(self.__facesCodificadasConhecidas, face_encoding)  # Compara a face detectada com as faces conhecidas
                
                if not matches:  # Se não houver correspondência com faces conhecidas
                    name = "Desconhecido"  # Define o nome como "Desconhecido"
                    confianca = 0.0  # Define a confiança como 0.0
                else:
                    # Use the known face with the smallest distance to the new face
                    face_distances = fr.face_distance(self.__facesCodificadasConhecidas, face_encoding)  # Calcula a distância das faces conhecidas para a face detectada
                    best_match_index = face_distances.argmin()  # Obtém o índice da melhor correspondência (menor distância)
                    
                    if best_match_index < len(matches) and matches[best_match_index]:  # Verifica se a melhor correspondência é válida
                        name = self.__nomeDasFacesConhecidas[best_match_index]  # Obtém o nome da melhor correspondência
                        confianca = (1 - face_distances[best_match_index]) * 100  # Calcula a confiança como um percentual
                        
                        # Formata o texto com o nome e confiança
                        texto = f"{name} - {round(confianca, 2)}%"
                        (texto_largura, texto_altura), _ = cv.getTextSize(texto, textFont, fontScale, textThickness)  # Obtém a largura e altura do texto
                        
                        # Desenha o fundo do retângulo para o texto
                        cv.rectangle(frame, (left, top - texto_altura - 10), (left + texto_largura, top), (0,0,0), -1)
                        
                        # Adiciona o texto ao frame
                        cv.putText(frame, texto, (left, top - 10), textFont, fontScale, textColor, textThickness, cv.LINE_AA)
                        
                        caixaDelimitadora = CaixaDelimitadora(frame, corVerde)  # Cria um objeto CaixaDelimitadora com cor verde
                        bbox = (left, top, right - left, bottom - top)  # Define a caixa delimitadora
                        frame = caixaDelimitadora.draw(bbox)  # Desenha a caixa delimitadora no frame
                        
                        if not self.__estaSeguro and cronometroSeguranca == None:  # Se o sistema não estiver seguro e o cronômetro de segurança não estiver definido
                            print("not self.__estaSeguro and cronometroSeguranca==None")  # Imprime mensagem de depuração
                            cronometroSeguranca = setInterval(self.contadorSeguranca, 1)  # Define um cronômetro para o método contadorSeguranca
                            self.__tempoLimiteDeSeguranca = tempoLimiteDeSeguranca  # Reinicia o tempo limite de segurança
                    else:
                        name = "Desconhecido"  # Define o nome como "Desconhecido"
                        confianca = 0.0  # Define a confiança como 0.0
                        
                        # Formata o texto com o nome e confiança
                        texto = f"{name} - {round(confianca, 2)}%"
                        (texto_largura, texto_altura), _ = cv.getTextSize(texto, textFont, fontScale, textThickness)  # Obtém a largura e altura do texto
                        
                        # Desenha o fundo do retângulo para o texto
                        cv.rectangle(frame, (left, top - texto_altura - 10), (left + texto_largura, top), (0,0,0), -1)
                        
                        # Adiciona o texto ao frame
                        cv.putText(frame, texto, (left, top - 10), textFont, fontScale, textColor, textThickness, cv.LINE_AA)
                        
                        # Desenha uma caixa ao redor da face usando CaixaDelimitadora
                        caixaDelimitadora = CaixaDelimitadora(frame, corVermelha)  # Cria um objeto CaixaDelimitadora com cor vermelha
                        bbox = (left, top, right - left, bottom - top)  # Define a caixa delimitadora
                        frame = caixaDelimitadora.draw(bbox)  # Desenha a caixa delimitadora no frame
                        
                        if self.__estaSeguro and cronometroDeRoubo == None:  # Se o sistema estiver seguro e o cronômetro de roubo não estiver definido
                            print("self.__estaSeguro and cronometroDeRoubo==None")  # Imprime mensagem de depuração
                            cronometroDeRoubo = setInterval(self.contadorRoubo, 1)  # Define um cronômetro para o método contadorRoubo
                            self.__estaSeguro = False  # Define o sistema como não seguro
                            self.__tempoLimiteDeRoubo = tempoLimiteDeInvasao  # Reinicia o tempo limite de roubo
            if self.__tempoLimiteDeRoubo == 0 and cronometroDeRoubo is not None:# Se o tempo limite de roubo for zero e o cronômetro de roubo estiver ativo
                print("self.__tempoLimiteDeRoubo==0 and cronometroDeRoubo != None")
                print("ROUBO!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
                
                DIR = os.path.dirname(os.path.abspath(__file__))  # Obtém o diretório atual do script
                
                # Adiciona a data e hora à imagem
                dataEhoraAtual = datetime.now()  # Obtém a data e hora atual
                tempoAtual = dataEhoraAtual.strftime("%Y-%m-%d %H:%M:%S")  # Formata a data e hora
                nomeDaFoto = dataEhoraAtual.strftime("%Y-%m-%d %H-%M-%S")  # Formata a data e hora para o nome do arquivo
                diretorioDosRoubos = f"{DIR}/roubos/{nomeDaFoto}.png"  # Define o caminho onde a foto será salva
                position = (10, 30)  # Posição do texto na imagem
                fotoDoRoubo = frame  # Frame atual da câmera
                # Adiciona o texto à imagem
                cv.putText(fotoDoRoubo, tempoAtual, position, textFont, fontScale, textColor, textThickness, cv.LINE_AA)
                cv.imwrite(diretorioDosRoubos, fotoDoRoubo)  # Salva a imagem com o texto
                clearInterval(cronometroDeRoubo)  # Para o cronômetro de roubo
                cronometroDeRoubo = None  # Reseta a variável do cronômetro de roubo 
                if cronometroSeguranca is not None:
                    # Se o cronômetro de segurança estiver ativo, para e reseta
                    clearInterval(cronometroSeguranca)
                    cronometroSeguranca = None
                self.__estaSeguro = True  # Define que está seguro
                try:# Tenta enviar um comando ao Arduino
                    print(self.__portaSerialArduino)
                    self.__portaSerialArduino.write(f'{1}\n'.encode())
                except Exception as e:
                    # Em caso de erro, fecha a porta serial e exibe uma mensagem de erro
                    if self.__portaSerialArduino and self.__portaSerialArduino.is_open:
                        self.__portaSerialArduino.close()
                    mostrarMensagemDeErro("FACE CAR - Erro Arduino", f"Não foi possível enviar a informação ao Arduino.\n\nResposta do computador: {e}")
                
                self.__tempoLimiteDeRoubo = tempoLimiteDeInvasao  # Reseta o tempo limite de roubo
                self.__tempoLimiteDeSeguranca = tempoLimiteDeSeguranca  # Reseta o tempo limite de segurança

            if self.__tempoLimiteDeSeguranca == 0 and cronometroSeguranca is not None:
                # Se o tempo limite de segurança for zero e o cronômetro de segurança estiver ativo
                print("self.__tempoLimiteDeSeguranca==0 and cronometroSeguranca !=None")
                self.__estaSeguro = True  # Define que está seguro
                clearInterval(cronometroSeguranca)  # Para o cronômetro de segurança
                cronometroSeguranca = None  # Reseta a variável do cronômetro de segurança
                if cronometroDeRoubo:
                    # Se o cronômetro de roubo estiver ativo, para e reseta
                    clearInterval(cronometroDeRoubo)
                    cronometroDeRoubo = None
                self.__tempoLimiteDeRoubo = tempoLimiteDeInvasao  # Reseta o tempo limite de roubo
                self.__tempoLimiteDeSeguranca = tempoLimiteDeSeguranca  # Reseta o tempo limite de segurança
            chave = cv.waitKey(1)  # ESC = 27
            if chave == 27:  # Se a tecla ESC for pressionada
                if cronometroDeRoubo:
                    clearInterval(cronometroDeRoubo)  # Para o cronômetro de roubo
                    cronometroDeRoubo = None  # Reseta a variável do cronômetro de roubo
                if cronometroSeguranca:
                    clearInterval(cronometroSeguranca)  # Para o cronômetro de segurança
                    cronometroSeguranca = None  # Reseta a variável do cronômetro de segurança
                break  # Sai do loop
            cv.imshow("Camera", frame)# Mostra o frame da câmera em uma janela chamada "Camera"
            if self.__tempoLimiteDeRoubo < 0 or self.__tempoLimiteDeSeguranca < 0:# Se algum dos tempos limites for negativo, reseta ambos e define que está seguro
                self.__tempoLimiteDeRoubo = tempoLimiteDeInvasao
                self.__tempoLimiteDeSeguranca = tempoLimiteDeSeguranca
                self.__estaSeguro = True
        if self.__portaSerialArduino and self.__portaSerialArduino.is_open:
            self.__portaSerialArduino.close()# Fecha a porta serial do Arduino, se estiver aberta
        cv.destroyAllWindows()  # Fecha todas as janelas do OpenCV

if __name__ == "__main__":
    portaSerial = input("Informe o número(Somente número. Ex: 4) da porta serial: ")
    cadastrarFace = Camera(f"{portaSerial}")
    cadastrarFace.reconhecer()
