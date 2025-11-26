import json
from client_connection import ClientSocket

class NetworkManager:

    __SETTINGS_FILE = "../settings.json"

    def __init__(self):

        settings = self.__load_settings()
        self.ip = settings["network"]["ip"]
        self.port = settings["network"]["port"]
        self.timeout = settings["network"]["timeout"]

        self.conn = ClientSocket(self.ip, self.port, self.timeout)

    def __load_settings(self):
        
        try:
            with open(self.__SETTINGS_FILE, 'r') as f:
                return json.load(f)
            
        except Exception as e:
            raise RuntimeError(f"Can't read configuration file: {e}")

    def send_input(input):
        """ Envia a entrada do jogador para o servidor.
        """
        pass

    def get_game_state():
        """ Obtém o estado atual do jogo através da matriz enviada pelo servidor.
        """
        pass