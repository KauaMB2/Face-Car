import tkinter as tk #Inclui biblioteca tkinter, biblioteca para construção da Interface Gráfica e informa que será chamada de "tk"
from tkinter import * #Inclui todos os componentes da biblioteca tkinter
from tkinter import ttk #Inclui componente ttk do tkinter para botão de escolha da porta serial
from tkinter import filedialog, messagebox #Inclui função de escolha de arquivo (filedialog) e mensagem de erro (messagebox) do tkinter
import os #Inclui biblioteca com comandos do sistema operacional para leitura das pastas do computador
import shutil #Inclui biblioteca shutil, utilizada para copiar e colar arquivos. É utilizada para copiar uma foto de um novo rosto e colar na pasta fotos/
import serial.tools.list_ports #Inclui biblioteca para fazer a leitura de portas seriais do computador
from TirarFoto import TirarFoto
from TelaDeRemocao import TelaDeRemocao
from Camera import Camera #Importa biblioteca criada para abrir câmera e identificar as faces


DIR=os.path.dirname(os.path.abspath(__file__))#Diretório do arquivo que está sendo executado

#Variáveis globais para deletar as fotos da pasta fotos/
dropdownNomes=None#Variável que representa o botão com a lista dos nomes das fotos na pasta fotos/
listaNomes=None#Variável que armazena o nome de cada foto dentro da pasta fotos/

def chamarTelaDeRemocao():
    global DIR
    teladeremocao=TelaDeRemocao(DIR)
    teladeremocao.telaDeRemocao()

def salvar_imagem():# Função para salvar imagem
    nome_usuario = entradaNome.get()    # Obtém o nome do usuário a partir do campo de entrada
    if nome_usuario == "":# Verifica se o nome do usuário está vazio
        messagebox.showerror("Erro", "O nome do usuário está vazio. Digite o nome do usuário!")# Exibe uma mensagem de erro se o nome estiver vazio
        return
    arquivo_imagem = filedialog.askopenfilename(# Abre uma caixa de diálogo para selecionar uma imagem
        title="Selecione uma imagem", # Título da janela de seleção de arquivos
        filetypes=[("Arquivos de Imagem", "*.jpg;*.png;*.jpeg")] # Tipos de arquivos permitidos
    )
    if not arquivo_imagem:# Verifica se nenhum arquivo foi selecionado
        messagebox.showinfo("Info", "Nenhuma imagem selecionada.")# Exibe uma mensagem informando que nenhuma imagem foi selecionada
        return
    pasta_fotos = os.path.join(DIR, 'fotos')# Define o caminho para a pasta fotos
    if not os.path.exists(pasta_fotos):# Cria a pasta fotos se não existir
        os.makedirs(pasta_fotos)
    # Define o caminho para salvar a nova imagem
    nome_imagem = f"{nome_usuario}.jpg"  # Usa .jpg como extensão padrão
    caminho_novo = os.path.join(pasta_fotos, nome_imagem)
    try:
        shutil.copy(arquivo_imagem, caminho_novo)# Copia a imagem selecionada para o novo caminho
        messagebox.showinfo("Sucesso", f"Imagem salva como {nome_imagem} na pasta 'fotos'.")# Exibe uma mensagem de sucesso informando onde a imagem foi salva
        entradaNome.delete(0, tk.END)# Limpa o campo de entrada
    except Exception as e:
        messagebox.showerror("Erro", f"Não foi possível salvar a imagem: {e}")# Exibe uma mensagem de erro se ocorrer algum problema ao salvar a imagem
def runCamera():# Função para executar a câmera
    portaSerialSelecionada = port_var.get()# Obtém a porta serial selecionada
    cadastrarFace = Camera(f"{portaSerialSelecionada}")# Cria uma instância da classe Camera com a porta serial selecionada
    cadastrarFace.reconhecer()# Chama o método reconhecer da instância cadastrarFace para iniciar o reconhecimento facial
    # portaSerialSelecionada = port_var.get()
    # if portaSerialSelecionada:
    #     cadastrarFace = Camera(f"{portaSerialSelecionada}")
    #     cadastrarFace.reconhecer()
    # else:
    #     mensagemDeErro = "Por favor, selecione uma porta serial."
    #     mostrarTelaDeAviso("FACE CAR - AVISO", mensagemDeErro)

def pegarPortasSeriais():# Função para obter portas seriais
    portas = serial.tools.list_ports.comports()# Obtém a lista de portas seriais disponíveis
    return [port.device for port in portas]# Retorna uma lista contendo apenas os nomes das portas seriais

def atualizarPortasSeriais(event):# Função para atualizar portas seriais
    portasSeriais = pegarPortasSeriais()# Obtém a lista atualizada de portas seriais
    dropdownPortas['values'] = portasSeriais# Atualiza os valores do dropdown de portas seriais com a lista obtida

def tirarFotos():
    nomeUsuario=entradaNome.get()
    if nomeUsuario == "":# Verifica se o nome do usuário está vazio
        messagebox.showerror("Erro", "O nome do usuário está vazio. Digite o nome do usuário!")# Exibe uma mensagem de erro se o nome estiver vazio
        return
    tirarfotos=TirarFoto(DIR, nomeUsuario)
    tirarfotos.tirarFoto()

# Configuração da janela principal
janela = tk.Tk()  # Cria uma nova instância da janela principal do tkinter
img = PhotoImage(file=os.path.join(DIR, 'logo', 'Logo3-2.png'))  # Carrega a imagem para o ícone da janela
janela.iconphoto(True, img)  # Define a imagem como ícone da janela
janela.title("FACE CAR")  # Define o título da janela
janela.geometry("400x270")  # Define o tamanho da janela, com altura aumentada para acomodar o dropdown
janela.configure(bg="#027000")  # Configura a cor de fundo da janela
janela.resizable(False, False)  # Impede que a janela seja redimensionada

# Título do aplicativo
labelTitle = tk.Label(janela, text="FACE CAR", font=("calibri", 30), bg="#027000", fg="white")  # Cria um rótulo com o título do aplicativo
labelTitle.pack(side=tk.TOP)  # Adiciona o rótulo ao topo da janela

# Label e entrada para nome do usuário
labelName = tk.Label(janela, text="Digite o nome do usuário: ", font=("calibri", 12), bg="#027000", fg="white")  # Cria um rótulo para a entrada do nome do usuário
labelName.pack(side=tk.TOP)  # Adiciona o rótulo ao topo da janela

entradaNome = tk.Entry(janela, width=40)  # Cria um campo de entrada para o nome do usuário
entradaNome.pack(side=tk.TOP)  # Adiciona o campo de entrada ao topo da janela

# Frame para botões
botoesFrame = tk.Frame(janela, bg="#027000")  # Cria um frame para agrupar os botões
botoesFrame.pack(side=tk.TOP)  # Adiciona o frame ao topo da janela

# Adiciona o botão "Selecionar e Salvar Imagem"
botaoRegistrar = tk.Button(botoesFrame, text="Selecionar foto", command=salvar_imagem, bg="#028700", fg="white")  # Cria um botão para selecionar e salvar a imagem
botaoRegistrar.pack(side=tk.LEFT, pady=10, padx=5)  # Adiciona o botão ao frame e define um espaçamento vertical
botaoRegistrar = tk.Button(botoesFrame, text="Tirar foto", command=tirarFotos, bg="#028700", fg="white")  # Cria um botão para selecionar e salvar a imagem
botaoRegistrar.pack(side=tk.LEFT, pady=10, padx=5)  # Adiciona o botão ao frame e define um espaçamento vertical

# Frame para o botão da câmera e menu dropdown
cameraFrame = tk.Frame(janela, bg="#027000")  # Cria um frame para o botão da câmera e o menu dropdown
cameraFrame.pack(pady=10)  # Adiciona o frame ao frame dos botões e define um espaçamento vertical

# Botão para abrir a câmera
botaoAbrirCamera = tk.Button(cameraFrame, text="Abrir Câmera", width=15, command=runCamera, bg="#028700", fg="white")  # Cria um botão para abrir a câmera
botaoAbrirCamera.pack(side=tk.LEFT, padx=5)  # Adiciona o botão ao frame da câmera e define um espaçamento horizontal

# Dropdown para portas seriais
port_var = tk.StringVar()  # Cria uma variável para armazenar a porta serial selecionada
portasSeriais = pegarPortasSeriais()  # Obtém a lista de portas seriais disponíveis
dropdownPortas = ttk.Combobox(cameraFrame, textvariable=port_var, values=portasSeriais, width=10)  # Cria um menu dropdown para selecionar a porta serial
dropdownPortas.pack(side=tk.LEFT, padx=5)  # Adiciona o menu dropdown ao frame da câmera e define um espaçamento horizontal

# Frame para o botão da câmera e menu dropdown
removerFrame = tk.Frame(janela, bg="#027000")  # Cria um frame para o botão da câmera e o menu dropdown
removerFrame.pack(pady=15)  # Adiciona o frame ao frame dos botões e define um espaçamento vertical

# Botão para abrir a câmera
botaoRemover = tk.Button(removerFrame, text="Remover faces", width=15, command=chamarTelaDeRemocao, bg="#028700", fg="white")  # Cria um botão para abrir a câmera
botaoRemover.pack(side=tk.LEFT, padx=5)  # Adiciona o botão ao frame da câmera e define um espaçamento horizontal

# Liga o dropdown à função de atualização
dropdownPortas.bind('<Button-1>', atualizarPortasSeriais)  # Vincula a ação de clique do mouse à função de atualização das portas seriais

# Inicia o loop principal do tkinter
janela.mainloop()  # Inicia o loop principal do tkinter, que mantém a janela aberta
