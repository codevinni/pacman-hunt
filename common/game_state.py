from .matrix import Matrix
from .enums import EntityType, GameStatus

class GameState:
    """
    Representa o estado completo do jogo.
    Encapsula todos os dados necessários para que o cliente renderize um frame do jogo. 

    Attributes:
        matrix (Matrix): O estado do mapa.
        status (GameStatus): O estado atual do jogo.
        frightened_timer (int): Contador de frames para o modo frightened (ativadeo pela Power Pellet).
        pacman_lives (int): Quantidade de vidas restantes do Pac-Man.
        scores (dict[EntityType, int]): Placar de pontuação dos fantasmas.
        winner (str): Nome do vencedor (para exibição).
    """

    PACMAN_DEFAULT_LIVES = 3
    FRIGHTENED_MODE_DURATION = 600  # 10 segundos (considerando 60 FPS)

    def __init__(self):
        """ Inicializa um novo estado de jogo
        """

        self.matrix = Matrix()
    
        self.status = GameStatus.WAITING_PLAYERS
        self.frightened_timer = 0
        self.winner:str = None
        
        self.pacman_lives = self.PACMAN_DEFAULT_LIVES

        self.scores = {
            EntityType.BLINKY: 0,
            EntityType.INKY: 0,
            EntityType.PINKY: 0,
            EntityType.CLYDE: 0
        }

    def activate_frightened_mode(self):
        """ Ativa o modo vulnerável (frightened) para os fantasmas.
        """
        self.frightened_timer = self.FRIGHTENED_MODE_DURATION

    def is_frightened_mode(self) -> bool:
        """ Verifica se o modo frightened está ativo.

        Returns:
            bool: True se estiver ativo, False caso contrário.
        """
        return self.frightened_timer > 0

    def decrease_frightened_timer(self):
        """ Reduz em 1 o tempo de duração do modo frightened ativado pela power pellet.
        """
        if self.frightened_timer > 0:
            self.frightened_timer -= 1

    def decrease_pacman_life(self) -> bool:
        """ Remove uma vida do Pac-Man.
        """
        if self.pacman_lives > 0:
            self.pacman_lives -= 1

    def add_score(self, ghost: EntityType, points: int) -> bool:
        """ Adiciona pontuação para um fantasma.

        Args:
            ghost (EntityType): O tipo do fantasma.
            points (int): Quantidade de pontos a adicionar.

        Returns:
            bool: True se é uma entidade válida e o ponto foi adicionado, False caso contrário.
        """
        if ghost in self.scores:
            self.scores[ghost] += points
            return True
        
        return False
 
    def update(self):
        """ Atualiza lógicas temporais do estado.
            Deve ser chamado a cada tick do loop do servidor.
        """
        #self.decrease_frightened_timer()
        pass

    def check_victory_condition(self):
        pass