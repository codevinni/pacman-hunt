class GameNetworkError(Exception):
    """ Exceção base para todos os erros de rede do jogo.
    """
    def __init__(self, *args):
        super().__init__(*args)

class SerializationError(Exception):
    """ Ocorre quando falha a serialização (pickle) ou empacotamento (struct).
    """
    def __init__(self, *args):
        super().__init__(*args)