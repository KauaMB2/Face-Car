import cv2 as cv  # Importa a biblioteca OpenCV e a renomeia como 'cv'

class CaixaDelimitadora:  # Define a classe CaixaDelimitadora
    def __init__(self, frame, cor):  # Método construtor da classe
        self.__frame = frame  # Inicializa a variável de instância __frame com o valor do argumento frame
        self.__cor = cor  # Inicializa a variável de instância __cor com o valor do argumento cor

    def draw(self, bbox, l=30, t=10):  # Método para desenhar uma caixa delimitadora; bbox é a caixa de limites, l é o comprimento dos cantos, e t é a espessura das linhas
        x, y, w, h = bbox  # Descompacta a caixa delimitadora em coordenadas (x, y) e dimensões (w, h)
        x1, y1 = x + w, y + h  # Calcula as coordenadas do canto inferior direito da caixa
        # Desenha o retângulo
        cv.rectangle(self.__frame, (x, y), (x + w, y + h), self.__cor, thickness=4)  # Desenha o retângulo delimitador no frame com a cor especificada e espessura 4
        # Canto Superior Esquerdo
        cv.line(self.__frame, (x, y), (x + l, y), self.__cor, t)  # Desenha uma linha horizontal na parte superior esquerda da caixa
        cv.line(self.__frame, (x, y), (x, y + l), self.__cor, t)  # Desenha uma linha vertical na parte superior esquerda da caixa
        # Canto Superior Direito
        cv.line(self.__frame, (x1, y), (x1 - l, y), self.__cor, t)  # Desenha uma linha horizontal na parte superior direita da caixa
        cv.line(self.__frame, (x1, y), (x1, y + l), self.__cor, t)  # Desenha uma linha vertical na parte superior direita da caixa
        # Canto Inferior Esquerdo
        cv.line(self.__frame, (x, y1), (x + l, y1), self.__cor, t)  # Desenha uma linha horizontal na parte inferior esquerda da caixa
        cv.line(self.__frame, (x, y1), (x, y1 - l), self.__cor, t)  # Desenha uma linha vertical na parte inferior esquerda da caixa
        # Canto Inferior Direito
        cv.line(self.__frame, (x1, y1), (x1 - l, y1), self.__cor, t)  # Desenha uma linha horizontal na parte inferior direita da caixa
        cv.line(self.__frame, (x1, y1), (x1, y1 - l), self.__cor, t)  # Desenha uma linha vertical na parte inferior direita da caixa
        return self.__frame  # Retorna o frame com a caixa delimitadora desenhada
