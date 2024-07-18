import cv2 as cv
import os
import numpy as np

class Treinamento():
    def __init__(self):
        # Get the list of self.__people (directories) in the 'fotos' folder
        self.__people = os.listdir("./fotos")
        # Get the directory of the current script
        self.__DIR = os.path.dirname(__file__)
        # Create the full path to the 'fotos' folder
        self.__diretorioDasFotos = os.path.join(self.__DIR, './fotos')
        self.__features = []
        self.__labels = []
        # Load the Haar cascade classifier
        self.__haar_cascade = cv.CascadeClassifier('./cascades/haarcascade_frontalface_default.xml')

    def createTrain(self):
        for person in self.__people:
            path = os.path.join(self.__diretorioDasFotos, person)
            label = self.__people.index(person)
            print(path, label, person)
            for img in os.listdir(path):
                diretorioDaImagem = os.path.join(path, img)
                arrayDeImagens = cv.imread(diretorioDaImagem)
                if arrayDeImagens is None:
                    print(f"Failed to read {diretorioDaImagem}")
                    continue
                imagemCinza = cv.cvtColor(arrayDeImagens, cv.COLOR_BGR2GRAY)
                facesDetectadas = self.__haar_cascade.detectMultiScale(imagemCinza, scaleFactor=1.1, minNeighbors=4)
                for (x, y, w, h) in facesDetectadas:
                    facesCortadas = imagemCinza[y:y + h, x:x + w]
                    self.__features.append(facesCortadas)
                    self.__labels.append(label)
                    print(f'label = {label}')
                    print(f'facesCortadas = {facesCortadas}')
        print(f'features = {self.__features}')
        print(f'labels = {self.__labels}')
        print(f'Length of the features = {len(self.__features)}')
        print(f'Length of the labels = {len(self.__labels)}')

        self.__features = np.array(self.__features, dtype='object')
        self.__labels = np.array(self.__labels)

        # Create the LBPH face recognizer
        reconhecedorDeFaces = cv.face.LBPHreconhecedorDeFaces_create()
        # Train the recognizer using the self.__features and self.__labels
        reconhecedorDeFaces.train(self.__features, self.__labels)
        # Save the trained model
        reconhecedorDeFaces.save(os.path.join(self.__DIR, 'classificadores', 'faceTrained.yml'))
        # Save the self.__features and self.__labels arrays
        np.save(os.path.join(self.__DIR, './features.npy'), self.__features)
        np.save(os.path.join(self.__DIR, './labels.npy'), self.__labels)

if __name__ == "__main__":
    treinamento=Treinamento()
    treinamento.createTrain()