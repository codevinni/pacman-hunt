import time
import pickle
import socket
import struct
import threading 
from common.matrix import Matrix            
from common.enums import EntityType, PlayerAction 

from ..pacman import PacmanIA

class ServerSocket:
    """
        Define o servidor para conexões de socket TCP/IP.
    """
    def __init__(self, server_ip:str, server_port:int, timeout: float = None):
        self.ip = server_ip
        self.port = server_port
        self.timeout = timeout

        self.matrix = Matrix()
        self.pacman_ai = PacmanIA()
        self.pacman_running = False

        self.server_socket = None
        self.clients = {}

        # Sincronização: Lock para acesso thread-safe aos recursos compartilhados
        self.lock = threading.Lock()

        self.available_ghosts = [
            EntityType.BLINKY,
            EntityType.INKY,
            EntityType.PINKY,
            EntityType.CLYDE
        ]
    
    def start(self):
        """
            Inicializa e inicia o servidor.
        """
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        try:
            self.server_socket.bind((self.ip, self.port))
            self.server_socket.listen()
        except:
            return print("\nNão foi possível iniciar o servidor!\n")

        while True:
            client, addr = self.server_socket.accept()
            print(f"Nova conexão de {addr}")

            client_handler = threading.Thread(target=self.handle_client, args=(client,))
            client_handler.start()

    def __receive_all(self, client_socket, num_bytes:int) -> bytes | None:
        """
            Método auxiliar para garantir que todos os bytes solicitados sejam lidos.
        """
        data = b""
        client_socket.settimeout(1.0)
        try:
            while len(data) < num_bytes:
                packet = client_socket.recv(num_bytes - len(data))
                if not packet:
                    # Conexão fechada
                    return None
                data += packet
            return data
        except socket.timeout:
            # Retorna o que foi lido até o timeout
            return data if data else None
        finally:
            client_socket.settimeout(None) # Remove timeout

    def __assign_ghost(self, client_socket):
        """
            Atribui um fantasma disponível ao cliente e retorna o tipo de fantasma.
            Se não houver fantasmas disponíveis, atribui como espectador (None).
        """
        assigned_ghost = None

        with self.lock:
            if self.available_ghosts:
                assigned_ghost = self.available_ghosts.pop(0)
                self.clients[client_socket] = assigned_ghost

                # TODO: Implementar a lógica para colocar entidade na matriz inicial aqui
                # self.matrix.set_entity_position(assigned_ghost, x_inicial, y_inicial)
            else:
                self.clients[client_socket] = None

        return assigned_ghost

    def __move_pacman(self):
    
        while self.pacman_running:

            with self.lock:
                self.pacman_ai.update(self.matrix)

            time.sleep(0.2)

    def __map_sending(self, client_socket):

        COOLDOWN = 0.05

        while True:
            self.send_matrix(client_socket)
            time.sleep(COOLDOWN)

    def handle_client(self, client_socket):
        """
            Lida com a comunicação de um cliente conectado.
        """
        assigned_ghost = self.__assign_ghost(client_socket)

        # 1. Envia atribuição de fantasma (ou espectador)
        try:
            self.send_data(client_socket, assigned_ghost)
        except Exception as e:
            print(f"Erro ao enviar atribuição para cliente: {e}")
            self.remove_client(client_socket)
            return
        
        # 2. Cria outra thread para enviar o mapa constantemente
        map_sender = threading.Thread(target=self.__map_sending, args=(client_socket,))
        map_sender.start()

        # 3. Cria outra thread para iniciar o PacMan
        if assigned_ghost and not self.pacman_running:
            self.pacman_running = True
            pacman_mover = threading.Thread(target=self.__move_pacman)
            pacman_mover.start()

        # Loop de controle de movimento e envio de estado
        while True:
            try:
                # 4. Receber a entrada do cliente (movimentação)
                client_input_data: PlayerAction = self.receive_data(client_socket)

                if assigned_ghost and client_input_data:
                    # Se o cliente é um jogador e enviou uma ação
                    print(f"Fantasma {assigned_ghost.name} recebeu ação: {client_input_data.name}")

                    movement_map = {
                        PlayerAction.UP: (0, -1),
                        PlayerAction.RIGHT: (1, 0),
                        PlayerAction.DOWN: (0, 1),
                        PlayerAction.LEFT: (-1,0),
                    }

                    delta_x, delta_y = movement_map[client_input_data]

                    # Movimenta o fantasminha baseando no input
                    with self.lock:
                        self.matrix.move_entity(assigned_ghost, delta_x, delta_y)

                # Pausa para controle de taxa de atualização
                time.sleep(0.05)

            except ConnectionResetError:
                print("Cliente desconectado")
                break
            except Exception as e:
                print(f"Erro na comunicação com o cliente: {e}")
                break
        
        self.remove_client(client_socket)
            
    def send_matrix(self, client_socket):
        """
            Serializa a matriz usando pickle e envia o cliente com o prefixo de tamanjo.
            Protocolo: [4 bytes (tamanho do payload)] + [payload (matriz serializada)]
        """
        with self.lock:
            # Serializa o objeto Matrix completo para incluir as entidades
            payload = pickle.dumps(self.matrix)
        
        self.send_data(client_socket, payload)
    
    def send_data(self, client_socket, data):
        """
            Envia os dados (que podem ser a matriz ou o EntityType) com o prefixo de 4 bytes do tamanho.
        """
        if data is None:
            payload = pickle.dumps(None)
        elif isinstance(data, bytes):
            payload = data
        else:
            payload = pickle.dumps(data)
        
        size = struct.pack("!I", len(payload))

        client_socket.sendall(size + payload)

    def receive_data(self,client_socket) -> PlayerAction | None:
        """
            Recebe os dados do cliente (entrada/input) seguindo o protocolo:
            [4 bytes Big-Endian Size] + [Payload (pickle-dumps de PlayerAction)]
        """
        HEADER_SIZE = 4

        # Tenta receber o cabeçalho (tamanho)
        header = self.__receive_all(client_socket, HEADER_SIZE)

        if header is None:
            # Conexão fechada ou timeout sem dados
            return None

        if len(header) != HEADER_SIZE:
            # Se leu só uma parte, é um erro de conexão ou protocolo
            raise ConnectionResetError("Conexão interrompida durante a leitura do cabeçalho.")
            
        try:
            # Desempacota o tamanho
            size = struct.unpack("!I", header)[0]

            # Se tamanho igual a zero (cliente enviou None ou um objeto vazio), retorna None
            if size == 0:
                return None

            # Recebe o payload completo
            payload = self.__receive_all(client_socket, size)

            if not payload or len(payload) != size:
                raise ConnectionResetError("Conexão interrompida ou payload incompleto.")

            # Deserializa o payload (PlayerAction)
            data = pickle.loads(payload)
            return data
        except Exception as e:
            # Erro de desempacotamento/deserialização
            raise ConnectionResetError(f"Erro ao receber ou processar dados do cliente: {e}")

    def remove_client(self, client_socket):
        """
            Remove o cliente e libera o fantasma atribuído (se houver).
        """
        with self.lock:
            if client_socket in self.clients:
                assigned_ghost = self.clients.pop(client_socket)

                if assigned_ghost is not None:
                    # Libera o fanstasma para outros jogadores
                    self.available_ghosts.append(assigned_ghost)
                    # TODO: Implementar a lógica para remover a entidade da matriz ou movê-la

                client_socket.close()
                print("Cliente removido e fantasma liberado (se aplicável).")

                if len(self.available_ghosts) == 4:
                    self.pacman_running = False