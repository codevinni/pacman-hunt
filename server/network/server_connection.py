import time
import pickle
import socket
import struct
import threading 
from common.game_state import GameState            
from common.enums import EntityType, PlayerAction 

from ..pacman import PacmanIA

class ServerSocket:
    """
        Define o servidor para conexões de socket TCP/IP.

        Gerencia o loop de aceitação de clientes, a comunicação thread-safe
        com os clientes e a lógica de jogo (PacmanIA, GameState).
    """
    def __init__(self, server_ip:str, server_port:int, timeout: float = None):
        """
            Inicializa o ServerSocket.

            Args:
                server_ip (str): O endereço IP para o servidor escutar.
                server_port (int): A porta TCP para o servidor escutar.
                timeout (float, optional): Timeout para operações de socket. Padrão é None.
        """
        self.ip = server_ip
        self.port = server_port
        self.timeout = timeout

        self.game_state = GameState()
        self.pacman_ai = PacmanIA()
        self.pacman_running = False

        # Flags para controlar thread de update do jogo
        self.game_running = True
        self.game_update_thread = None

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
            Inicializa o socket do servidor, bind e listen, e entra no loop principal de aceitação de conexões.

            O loop é protegido por um bloco try/except/finally para garantir
            um desligamento limpo em caso de interrupção (Ctrl+C).

            Raises:
                Exception: Se o bind/listen falhar (tratado com print).
                KeyboardInterrupt: Capturada para iniciar o processo de desligamento (shutdown).
        """
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        try:
            self.server_socket.bind((self.ip, self.port))
            self.server_socket.listen()
        except:
            return print("\nNão foi possível iniciar o servidor!\n")

        try:
            # Inicia thread de atualização do jogo (game_state)
            self.game_update_thread = threading.Thread(target=self.__game_update_loop)
            self.game_update_thread.daemon = True
            self.game_update_thread.start()

            while True:
                client, addr = self.server_socket.accept()
                print(f"Nova conexão de {addr}")

                client_handler = threading.Thread(target=self.handle_client, args=(client,))
                client_handler.daemon = True # Usado para desligamento rápido
                client_handler.start()

        except KeyboardInterrupt: 
            print("\nServidor encerrando por interrupção do usuário (Ctrl+C).")
        finally:
            self.__shutdown() # Método de desligamento

    def __game_update_loop(self):
        """
            Thread dedicada à atualização contínua do estado do jogo.
            Responsável por manter a lógica do jogo funcionando independentemente das operações de rede.
        """
        # Intervalo entre atualizações em segundos
        UPDATE_INTERVAL = 0.05
        
        # Loop principal de atualização do jogo
        while self.game_running:
            with self.lock:
                # Executa uma atualização completa do estado do jogo
                self.game_state.update()
                
            time.sleep(UPDATE_INTERVAL)

    def __shutdown(self):
        """
            Executa o desligamento limpo do servidor.

            Garante que o socket de escuta seja fechado.
        """
        self.game_running = False
    
        # Aguarda a thread de atualização do jogo finalizar, com timeout de 2 segundos
        if self.game_update_thread:
            self.game_update_thread.join(timeout=2.0)

            if self.server_socket:
                self.server_socket.close()

        print("Servidor desligado com sucesso")

    def __receive_all(self, client_socket, num_bytes:int) -> bytes | None:
        """
            Método auxiliar para garantir que todos os bytes solicitados sejam lidos do socket.

            Define um timeout temporário de 1.0s para evitar bloqueio infinito.

            Args:
                client_socket (socket): O socket do qual receber os dados.
                num_bytes (int): O número exato de bytes a serem lidos.

            Returns:
                bytes | None: Os dados lidos, ou None se a conexão for fechada ou ocorrer timeout sem dados.
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
            Atribui um fantasma disponível ao cliente de forma thread-safe.

            Se não houver fantasmas disponíveis, atribui como espectador (None).

            Args:
                client_socket (socket): O socket do cliente.

            Returns:
                EntityType | None: O tipo de fantasma atribuído ou None se for espectador.
        """
        assigned_ghost = None

        with self.lock:
            if self.available_ghosts:
                assigned_ghost = self.available_ghosts.pop(0)
                self.clients[client_socket] = assigned_ghost

                # TODO: Implementar a lógica para colocar entidade na matriz inicial aqui
            else:
                self.clients[client_socket] = None

        return assigned_ghost

    def __move_pacman(self):
        """
            Thread de controle da inteligência artificial do Pac-Man.

            O Pac-Man se move em intervalos de 0.2 segundos, usando a IA para atualizar sua posição na matriz de forma thread-safe.
        """
        while self.pacman_running:

            with self.lock:
                self.pacman_ai.update(self.game_state)

            time.sleep(0.2)

    def __game_state_sending(self, client_socket):
        """
            Thread de envio contínuo do estado atual do jogo para o cliente.

            Args:
                client_socket (socket): O socket do cliente para o qual enviar dados.

            Raises:
                ConnectionResetError, BrokenPipeError: Capturadas para encerrar
                a thread de envio quando o cliente desconecta abruptamente.
        """
        COOLDOWN = 0.05

        while True:
            try:
                self.send_game_state(client_socket)
                time.sleep(COOLDOWN)
            except (ConnectionResetError, BrokenPipeError) as e:
                # O cliente fechou a conexão de forma inesperada.
                print(f"Erro de conexão inesperada durante o envio do estado do jogo ({e}). Encerrando thread de envio.")
                break # Sai do loop, e a thread __game_state_sending termina

    def __ghost_movement(self, assigned_ghost, client_context):
        """
            Executa o loop de movimento contínuo para o fantasma de um cliente.

            Esta função verifica periodicamente a última direção solicitada pelo cliente (`current_action`)
            e aplica o movimento na matriz do jogo. O movimento persiste na mesma direção até que:
            1. O cliente envie uma nova direção.
            2. O fantasma encontre um obstáculo, momento em que a ação é resetada para None.

            O acesso ao estado do jogo (`self.game_state`) é protegido por `self.lock` para garantir
            a integridade dos dados em ambiente multithread.

            Args:
                assigned_ghost (EntityType): O tipo de fantasma (BLINKY, PINKY, etc.) controlado.
                client_context (dict): Dicionário compartilhado para sincronização entre a thread de recebimento
                                    e esta thread de movimento. Deve conter:
                                    - 'running' (bool): Controle de execução do loop.
                                    - 'current_action' (PlayerAction | None): A direção atual do movimento.
        """
        movement_map = { # Mapeamento de ações para deltas (x, y)
            PlayerAction.UP: (0, -1),
            PlayerAction.RIGHT: (1, 0),
            PlayerAction.DOWN: (0, 1),
            PlayerAction.LEFT: (-1, 0),
        }

        MOVE_INTERVAL = 0.2

        while client_context['running']:
            action = client_context['current_action']

            if action and action in movement_map:
                dx, dy = movement_map[action]

                with self.lock:
                    # Verifica posição do fantasma
                    current_pos = self.game_state.matrix.get_entity_position(assigned_ghost)

                    if current_pos:
                        nx, ny = current_pos[0] + dx, current_pos[1] + dy

                        # Verifica se a próxima posição é válida
                        if self.game_state.matrix.is_valid_position(nx, ny):
                            # Se livre, move
                            self.game_state.matrix.move_entity(assigned_ghost, dx, dy)
                        else:
                            # Se bateu na parede, para o movimento contínuo
                            client_context['current_action'] = None
            time.sleep(MOVE_INTERVAL)

    def handle_client(self, client_socket):
        """
            Lida com a comunicação e lógica de jogo para um cliente específico.

            Este método roda em uma thread separada e é responsável por:
            1. Atribuir o fantasma.
            2. Iniciar threads de envio de estado de jogo e movimento do Pac-Man (se aplicável).
            3. Loop principal de recebimento de comandos do jogador (PlayerAction).
            4. Tratar desconexões abruptas (`ConnectionResetError`, `BrokenPipeError`).

            Args:
                client_socket (socket): O socket conectado do cliente.
            
            Raises:
                ConnectionResetError, BrokenPipeError: Capturadas no loop principal
                para sinalizar desconexão abrupta e iniciar a remoção formal.
                Exception: Capturada para erros inesperados na comunicação.
        """
        assigned_ghost = self.__assign_ghost(client_socket)

        # Envia atribuição de fantasma (ou espectador)
        try:
            self.send_data(client_socket, assigned_ghost)
        except Exception as e:
            print(f"Erro ao enviar atribuição para cliente: {e}")
            self.remove_client(client_socket)
            return
        
        # Thread que envia o estado do jogo constantemente
        game_state_sender = threading.Thread(target=self.__game_state_sending, args=(client_socket,))
        game_state_sender.daemon = True # Usado para desligamento rápido
        game_state_sender.start()

        # Thread que inicia o PacMan
        if assigned_ghost and not self.pacman_running:
            self.pacman_running = True
            pacman_mover = threading.Thread(target=self.__move_pacman)
            pacman_mover.daemon = True # Usado para desligamento rápido
            pacman_mover.start()

        client_context = {
            'running': True,          # Controla o loop da thread de movimento
            'current_action': None    # Armazena a última tecla válida pressionada
        }

        # Se o cliente controla um fantasma, inicia a thread de movimento dele
        if assigned_ghost:
            ghost_mover = threading.Thread(target=self.__ghost_movement, args=(assigned_ghost, client_context))
            ghost_mover.daemon = True
            ghost_mover.start()

        # Loop de controle de movimento e envio de estado
        while True:
            try:
                # Recebe a entrada do cliente (movimentação)
                client_input_data: PlayerAction = self.receive_data(client_socket)

                if assigned_ghost and client_input_data:
                    # print(f"Fantasma {assigned_ghost.name} mudou direção para: {client_input_data.name}")
                    # Atualiza a direção na thread de movimento
                    client_context['current_action'] = client_input_data

                # Pausa para não consumir 100% da CPU
                time.sleep(0.01)

            except (ConnectionResetError, BrokenPipeError): 
                print("Cliente desconectado (Reset ou Broken Pipe)")
                break
            except Exception as e:
                print(f"Erro na comunicação com o cliente: {e}")
                break
        
        client_context['running'] = False
        self.remove_client(client_socket)
            
    def send_game_state(self, client_socket):
        """
            Serializa o game_state usando pickle e envia para o cliente.
            
            Protocolo: [4 bytes (tamanho do payload)] + [payload (game_state serializado)]

            Args:
                client_socket (socket): O socket do cliente de destino.

            Raises:
                Exception: Propaga exceções de conexão ou struct.pack/pickle.
        """
        with self.lock:
            # Serializa o objeto GameState completo para incluir as entidades
            payload = pickle.dumps(self.game_state)
        
        self.send_data(client_socket, payload)
    
    def send_data(self, client_socket, data):
        """
            Empacota e envia os dados (GameState ou EntityType) com o prefixo de 4 bytes do tamanho.

            Args:
                client_socket (socket): O socket do cliente de destino.
                data (any | bytes | None): Os dados a serem serializados e enviados. Pode ser um objeto (serializado via pickle) ou bytes (para dados já serializados).

            Raises:
                socket.error: Se ocorrer um erro de conexão durante `sendall`.
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
            Recebe e deserializa uma mensagem (PlayerAction) do cliente, lidando com o 
            protocolo de cabeçalho (tamanho).

            Protocolo: [4 bytes Big-Endian Size] + [Payload (pickle-dumps de PlayerAction)]

            Args:
                client_socket (socket): O socket do qual receber os dados.

            Returns:
                PlayerAction | None: A ação do jogador deserializada, ou None se a conexão for fechada 
                ou o cliente enviar um payload de tamanho zero.

            Raises:
                ConnectionResetError: Se a conexão for interrompida, o cabeçalho for inválido, 
                ou ocorrer erro na deserialização (pickle).
        """
        HEADER_SIZE = 4 # Tamanho do cabeçalho de empacotamento (em bytes)

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
            Remove o cliente da lista de ativos, libera o fantasma atribuído (se houver)
            e fecha o socket de forma thread-safe.

            Args:
                client_socket (socket): O socket do cliente a ser removido.
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