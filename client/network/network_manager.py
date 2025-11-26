import json
import pickle
import struct
from client_connection import ClientSocket
from common.enums import PlayerAction
from exceptions import GameNetworkError, SerializationError
from common.matrix import Matrix

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

    def connect_to_server(self):
        self.conn.connect()
       
    def disconnect_from_server(self):
        self.conn.close()

    def send_input(self, input:PlayerAction):
        """ Envia a entrada do jogador para o servidor.

        Serializa a entrada e adiciona um cabeçalho com o tamanho total 
        e envia através do socket.

        Args:
            input (PlayerAction): Enum que representa a ação do jogador

        Raises:
            GameNetworkError: Se houver algum erro na conexão. 
            SerializationError: Se houver algum erro na serialização do input.
        """

        try:
            serialized_input = pickle.dumps(input) # Serializa o objeto
            header = struct.pack(">I", len(serialized_input)); # Monta um cabeçalho com o tamanho dos dados
            data = header + serialized_input
            self.conn.send(data)

        except (ConnectionError, RuntimeError) as e:
            raise GameNetworkError(f"Erro de conexão: {e}")
        
        except (pickle.PicklingError, struct.error) as e:
            raise SerializationError(f"Falha ao serializar input: {e}")

    def get_game_state(self) -> Matrix | None:
        """ Obtém o estado atual do jogo através da matriz enviada pelo servidor.

        Returns:
            Matrix | None: A matriz do jogo se recebida com sucesso, None caso contrário.

        Raises:
            GameNetworkError: Se houver algum erro na conexão. 
            SerializationError: Se os dados recebidos estiverem incompletos ou corrompidos.
        """

        HEADER_SIZE = 4

        try:
            header = self.conn.receive(HEADER_SIZE) # Tamanho em bytes da matriz a ser recebida 

            if not header:
                return None

            size = struct.unpack(">I", header)[0]
            matrix_data = self.conn.receive(size)

            if not matrix_data:
                raise RuntimeError("Conteúdo da matriz ayusente")
            
            matrix = pickle.loads(matrix_data)

            return matrix
            
        except (ConnectionError, RuntimeError) as e:
            raise GameNetworkError(f"Erro de conexão: {e}")
        
        except (pickle.UnpicklingError, struct.error) as e:
            raise SerializationError(f"Erro, dados corrompidos foram recebidos: {e}")