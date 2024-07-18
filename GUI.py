import tkinter as tk
from tkinter import *
from tkinter import ttk
from tkinter import messagebox
import os
from CadastrarFace import CadastrarFace
from Treinamento import Treinamento
from Camera import Camera
import serial.tools.list_ports

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

def runCamera():
    portaSerialSelecionada = port_var.get()
    if portaSerialSelecionada:
        cadastrarFace = Camera(f"{portaSerialSelecionada}")
        cadastrarFace.reconhecer()
    else:
        mensagemDeErro=f"Por favor, selecione uma porta serial."
        mostrarTelaDeAviso("FACE CAR - AVISO", mensagemDeErro)

def start_training():
    treinamento = Treinamento()
    treinamento.createTrain()

def cadastrarUsuario():
    global textoDeErro  # Declare textoDeErro as global
    nomeUsuario = inputName.get()
    if textoDeErro:
        textoDeErro.pack_forget()  # Remove the label if it's currently visible
    if nomeUsuario == "":
        textoDeErro = tk.Label(janela, text="O nome do usuário está vazio. Digite o nome do usuário!", bg="#00FFF7", fg="red")
        textoDeErro.pack(side=tk.TOP)
        return
    cadastrarFace = CadastrarFace(nomeUsuario)
    cadastrarFace.TirarFotos()

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

labelName = tk.Label(janela, text="Digite o nome da usuário: ", font=("calibri", 12), bg="#027000", fg="white")
labelName.pack(side=tk.TOP)

inputName = tk.Entry(janela, width=40)
inputName.pack(side=tk.TOP)

botoesFrame = tk.Frame(janela, bg="#027000")
botoesFrame.pack(side=tk.TOP)

botaoRegistrar = tk.Button(botoesFrame, text="Cadastrar nova face", width=20, command=cadastrarUsuario, bg="#028700", fg="white")
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

botaoTreinamento = tk.Button(botoesFrame, text="Treinar IA", width=30, command=start_training, bg="#028700", fg="white")
botaoTreinamento.pack(pady=10)

janela.mainloop()
