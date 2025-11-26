import socket

class ClientSocket:
    """
    Define um cliente para conexões de socket TCP/IP.

    Gerencia conexão, envio de dados, recebimento e encerramento de uma conexão. 

    Attributes:
        ip (str): O endereço IP do servidor de destino.
        port (int): A porta TCP do servidor de destino.
    """

    def __init__(self, server_ip:str, server_port:int):
        self.ip = server_ip
        self.port = server_port
        self.sock = None

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def connect(self):
        """Cria o socket e conecta ao servidor.
        
        Raises:
            RuntimeError: Se o cliente já estiver conectado.
            ConnectionError: Se ocorrer um erro de rede ao tentar conectar.
        """

        if self.sock:
            raise RuntimeError("Already connected.")

        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((self.ip, self.port))
        except socket.error as e:
            raise ConnectionError(f"Error while connecting: {e}")

    def send(self, data:bytes):
        """ Envia dados para o servidor.

        Args:
            data (bytes): Os dados a serem enviados.

        Raises:
            ConnectionError: Se o socket não estiver conectado.
            RuntimeError: Se ocorrer um erro durante o envio.
        """

        if not self.sock:
            raise ConnectionError("Not connected.")

        try:
            self.sock.sendall(data)
        except Exception as e:
            raise RuntimeError(f"Error while sending data: {e}")

    def receive(self) -> bytes:
        """ Recebe dados do servidor. Lê até 1024 bytes do buffer do socket.

        Returns:
            bytes: Os dados recebidos do servidor.

        Raises:
            ConnectionError: Se o socket não estiver conectado.
            RuntimeError: Se ocorrer um erro durante o recebimento.
        """

        if not self.sock:
            raise ConnectionError("Not connected.")

        try:
            data = self.sock.recv(1024)
            return data
        except Exception as e:
            raise RuntimeError(f"Error while receiving data: {e}")

    def close(self):
        """ Fecha a conexão do socket.
        """

        if self.sock:
            try:
                self.sock.close()
            finally:
                self.sock = None