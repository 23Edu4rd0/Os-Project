import os 

class Contador:
    @staticmethod
    def caminho_arquivo():
        pasta = os.path.join(os.environ["LOCALAPPDATA"], "ProjetoOs")
        if not os.path.exists(pasta):
            os.makedirs(pasta)
        return os.path.join(pasta, "contador.txt")
    
    @staticmethod
    def ler_contador():
        caminho = Contador.caminho_arquivo()
        if not os.path.exists(caminho):
            with open(caminho, 'w') as f:
                f.write('0')
            return 0
        with open(caminho, 'r') as f:
            conteudo = f.read().strip()
            if conteudo == '':
                return 0
            return int(conteudo)
    @staticmethod
    def salvar_contador(valor):
        caminho = Contador.caminho_arquivo()
        with open(caminho, 'w') as f:
            f.write(str(valor))
            
   