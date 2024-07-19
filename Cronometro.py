from threading import Timer  # Importa a classe Timer do módulo threading

def setInterval(function, interval, *params, **kwparams):  # Define a função setInterval que executa uma função repetidamente com um intervalo especificado
    def setTimer(wrapper):  # Define a função setTimer para criar e iniciar um Timer
        wrapper.timer = Timer(interval, wrapper)  # Cria um Timer que chama a função wrapper após o intervalo especificado
        wrapper.timer.start()  # Inicia o Timer
    def wrapper():  # Define a função wrapper que será chamada pelo Timer
        function(*params, **kwparams)  # Chama a função especificada com os parâmetros fornecidos
        setTimer(wrapper)  # Recria o Timer para chamar a função novamente após o intervalo
    setTimer(wrapper)  # Inicializa o primeiro Timer
    return wrapper  # Retorna a função wrapper, que pode ser usada para cancelar o Timer
def clearInterval(wrapper):  # Define a função clearInterval para cancelar um Timer
    wrapper.timer.cancel()  # Cancela o Timer associado à função wrapper
