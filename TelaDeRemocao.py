import os
import tkinter as tk
from tkinter import *
from tkinter import ttk

class TelaDeRemocao:
    def __init__(self, DIR):
        self.__DIR=DIR

    def removerImage(self):
        selected_image = dropdownNomes.get()# Obtenha a imagem selecionada no dropdown
        if selected_image:
            image_path = os.path.join(self.__DIR, "fotos", selected_image)
            if os.path.exists(image_path):
                os.remove(image_path)  # Remove a imagem selecionada
                listaNomes.remove(selected_image)# Atualiza o dropdown após a remoção
                dropdownNomes['values'] = listaNomes
                dropdownNomes.set('')  # Limpa a seleção atual

    def telaDeRemocao(self):
        global dropdownNomes, listaNomes  # Declarar variáveis globais para uso em removerImage
        root = tk.Tk()
        root.title("Remover face")
        root.geometry("400x200")  # Increased height to accommodate dropdown
        root.configure(bg="#027000")
        root.resizable(False, False)
        
        # Adicionar um label separado para o título
        title_label = tk.Label(root, text="Remover face", font=("calibri", 30), bg="#027000", fg="white")
        title_label.pack(side=tk.TOP)

        labelName = tk.Label(root, text="Selecione a face que deseja apagar.", font=("calibri", 12), bg="#027000", fg="white")
        labelName.pack(side=tk.TOP, pady=(10, 5))

        nomesDasFotos = os.path.join(self.__DIR, "fotos")
        listaNomes = [filename for filename in os.listdir(nomesDasFotos) if os.path.isfile(os.path.join(nomesDasFotos, filename))]
        dropdownNomes = ttk.Combobox(root, values=listaNomes, width=30)  # Cria um menu dropdown para selecionar a imagem
        dropdownNomes.pack(side=tk.TOP, padx=5, pady=5)  # Adiciona o menu dropdown ao frame da câmera e define um espaçamento horizontal

        botoesFrame = tk.Frame(root, bg="#027000")
        botoesFrame.pack(side=tk.TOP, pady=(10, 5))

        # Adiciona o botão "Remover imagem selecionada"
        botaoRegistrar = tk.Button(botoesFrame, text="Remover imagem selecionada", command=self.removerImage, bg="#028700", fg="white")
        botaoRegistrar.pack(pady=10)

        root.mainloop()

if __name__ == "__main__":
    teladeremocao = TelaDeRemocao(os.path.dirname(os.path.abspath(__file__)))
    teladeremocao.telaDeRemocao()