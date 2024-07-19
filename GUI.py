import tkinter as tk
from tkinter import *
from tkinter import ttk
from tkinter import filedialog, messagebox
import os
import shutil
import serial.tools.list_ports
from Camera import Camera

# Global variables
textoDeErro = None

def mostrarTelaDeAviso(title, message):
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    messagebox.showinfo(title, message)
    root.destroy()

def mostrarMensagemDeErro(title, message):
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    messagebox.showerror(title, message)
    root.destroy()

def salvar_imagem():
    nome_usuario = inputName.get()
    if nome_usuario == "":
        messagebox.showerror("Erro", "O nome do usuário está vazio. Digite o nome do usuário!")
        return
    
    # Abre uma caixa de diálogo para selecionar uma imagem
    arquivo_imagem = filedialog.askopenfilename(
        title="Selecione uma imagem",
        filetypes=[("Arquivos de Imagem", "*.jpg;*.png;*.jpeg")]
    )
    
    if not arquivo_imagem:
        messagebox.showinfo("Info", "Nenhuma imagem selecionada.")
        return
    
    # Define o caminho para a pasta fotos
    pasta_fotos = os.path.join(os.path.dirname(__file__), 'fotos')
    
    # Cria a pasta fotos se não existir
    if not os.path.exists(pasta_fotos):
        os.makedirs(pasta_fotos)
    
    # Define o caminho para salvar a nova imagem
    nome_imagem = f"{nome_usuario}.jpg"  # Usa .jpg como extensão padrão
    caminho_novo = os.path.join(pasta_fotos, nome_imagem)
    
    try:
        shutil.copy(arquivo_imagem, caminho_novo)
        messagebox.showinfo("Sucesso", f"Imagem salva como {nome_imagem} na pasta 'fotos'.")
        inputName.delete(0, tk.END)  # Limpa o campo de entrada
    except Exception as e:
        messagebox.showerror("Erro", f"Não foi possível salvar a imagem: {e}")

def runCamera():
    portaSerialSelecionada = port_var.get()
    cadastrarFace = Camera(f"{portaSerialSelecionada}")
    cadastrarFace.reconhecer()
    # portaSerialSelecionada = port_var.get()
    # if portaSerialSelecionada:
    #     cadastrarFace = Camera(f"{portaSerialSelecionada}")
    #     cadastrarFace.reconhecer()
    # else:
    #     mensagemDeErro = "Por favor, selecione uma porta serial."
    #     mostrarTelaDeAviso("FACE CAR - AVISO", mensagemDeErro)

def get_serial_ports():
    ports = serial.tools.list_ports.comports()
    return [port.device for port in ports]

def update_serial_ports(event):
    serial_ports = get_serial_ports()
    port_dropdown['values'] = serial_ports

janela = tk.Tk()
img = PhotoImage(file=os.path.join(os.path.dirname(__file__), 'logo', 'Logo3-2.png'))
janela.iconphoto(False, img)
janela.title("FACE CAR")
janela.geometry("400x270")  # Increased height to accommodate dropdown
janela.configure(bg="#027000")
janela.resizable(False, False)

labelTitle = tk.Label(janela, text="FACE CAR", font=("calibri", 30), bg="#027000", fg="white")
labelTitle.pack(side=tk.TOP)

labelName = tk.Label(janela, text="Digite o nome do usuário: ", font=("calibri", 12), bg="#027000", fg="white")
labelName.pack(side=tk.TOP)

inputName = tk.Entry(janela, width=40)
inputName.pack(side=tk.TOP)

botoesFrame = tk.Frame(janela, bg="#027000")
botoesFrame.pack(side=tk.TOP)

# Adiciona o botão "Selecionar e Salvar Imagem" antes do botão "Abrir Câmera"
botaoRegistrar = tk.Button(botoesFrame, text="Selecionar e Salvar Imagem", command=salvar_imagem, bg="#028700", fg="white")
botaoRegistrar.pack(pady=10)

# Create a frame to hold the camera button and dropdown menu
cameraFrame = tk.Frame(botoesFrame, bg="#027000")
cameraFrame.pack(pady=10)

botaoAbrirCamera = tk.Button(cameraFrame, text="Abrir Câmera", width=15, command=runCamera, bg="#028700", fg="white")
botaoAbrirCamera.pack(side=tk.LEFT, padx=5)

# Dropdown for serial ports
port_var = tk.StringVar()
serial_ports = get_serial_ports()
port_dropdown = ttk.Combobox(cameraFrame, textvariable=port_var, values=serial_ports, width=10)
port_dropdown.pack(side=tk.LEFT, padx=5)

# Link the dropdown to the update function
port_dropdown.bind('<Button-1>', update_serial_ports)

janela.mainloop()
