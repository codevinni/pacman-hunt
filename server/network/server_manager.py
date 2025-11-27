import os
import json
from .server_connection import ServerSocket

class ServerManager:
    __SETTINGS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'settings.json')

    def __init__(self):
        settings = self.__load_settings()
        self.ip = settings["network"]["ip"]
        self.port = settings["network"]["port"]
        self.timeout = settings["network"]["timeout"]

        self.conn = ServerSocket(self.ip, self.port, self.timeout)

    def __load_settings(self):
        try:
            with open(self.__SETTINGS_FILE, 'r') as f:
                return json.load(f)
        except Exception as e:
            tried_path = os.path.abspath(self.__SETTINGS_FILE)
            raise RuntimeError(f"Can't read configuration file: {e}. Tried path: {tried_path}")
        
    def run(self):
        print(f"Servidor iniciado em {self.ip}:{self.port}")
        self.conn.start()

'''
if __name__ == "__main__":
    # 1. Cria uma instância do ServerManager
    manager = ServerManager()
    
    # 2. Chama o método run, que por sua vez chama ServerSocket.start()
    #    Este método contém o loop infinito (while True) que mantém o servidor ativo.
    manager.run()
'''