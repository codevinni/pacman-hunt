import os
import json
from .server_connection import ServerSocket

class ServerManager:
    """
        Gerencia a configuração e inicialização do servidor de jogo.

        Responsável por carregar as configurações do arquivo 'settings.json' e iniciar a instância do ServerSocket.
    """
    __SETTINGS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'settings.json')

    def __init__(self):
        """
            Inicializa o ServerManager.

            Carrega as configurações de IP, porta e timeout e cria a instância de ServerSocket.
        """
        settings = self.__load_settings()
        self.ip = settings["network"]["ip"]
        self.port = settings["network"]["port"]
        self.timeout = settings["network"]["timeout"]

        self.conn = ServerSocket(self.ip, self.port, self.timeout)

    def __load_settings(self):
        """
            Carrega as configurações de rede do arquivo 'settings.json'.

            Returns:
                dict: Um dicionário contendo as configurações carregadas.

            Raises:
                RuntimeError: Se o arquivo de configuração não puder ser lido.
        """
        try:
            with open(self.__SETTINGS_FILE, 'r') as f:
                return json.load(f)
        except Exception as e:
            tried_path = os.path.abspath(self.__SETTINGS_FILE)
            raise RuntimeError(f"Can't read configuration file: {e}. Tried path: {tried_path}")
        
    def run(self):
        """
            Inicia a execução do loop principal do servidor.

            Chama o método start() da instância ServerSocket.
        """
        print(f"Servidor iniciado em {self.ip}:{self.port}")
        self.conn.start()