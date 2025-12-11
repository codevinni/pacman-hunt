from .matrix import Matrix
from .enums import EntityType, GameStatus, ItemType, GameStatus

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
        self.winner: str = None
        self.pacman_lives = self.PACMAN_DEFAULT_LIVES

        self.scores = {
            EntityType.BLINKY: 0,
            EntityType.INKY: 0,
            EntityType.PINKY: 0,
            EntityType.CLYDE: 0
        }

    def activate_frightened_mode(self):
        """ Ativa o modo vulnerável (frightened) para os fantasmas.
            Quando o Matrix.move_entity retorna ItemType.POWER_PELLET.
        """
        self.frightened_timer = self.FRIGHTENED_MODE_DURATION

    def __is_frightened_mode(self) -> bool:
        """ Verifica se o modo frightened está ativo.

        Returns:
            bool: True se estiver ativo, False caso contrário.
        """
        return self.frightened_timer > 0

    def __decrease_frightened_timer(self):
        """ Reduz em 1 o tempo de duração do modo frightened ativado pela power pellet.
        """
        if self.frightened_timer > 0:
            self.frightened_timer -= 1

    def __decrease_pacman_life(self) -> bool:
        """ Remove uma vida do Pac-Man.
        """
        if self.pacman_lives > 0:
            self.pacman_lives -= 1
        
        return self.pacman_lives > 0
        
    def __add_score(self, ghost: EntityType, points: int) -> bool:
        """ Adiciona pontuação para um fantasma.

        Args:
            ghost (EntityType): O tipo do fantasma.
            points (int): Quantidade de pontos a adicionar.

        Returns:
            bool: True se é uma entidade válida e o ponto foi adicionado, False caso contrário.
        """
        if ghost in self.scores:
            self.scores[ghost] += points
            print(f'Score {ghost.name}: {self.scores[ghost]}')
            return True
        
        return False
 
    def update(self):
        """ Atualiza lógicas temporais do estado.
            Deve ser chamado a cada tick do loop do servidor.
        """
        # if self.status != GameStatus.RUNNING:
        #     return
        
        # Atualiza tempo do frightened
        self.__decrease_frightened_timer()
        
        # Verifica colisões
        self.__check_collisions()  
        
        # Verifica vitória
        self.__check_victory_condition()

    def __check_victory_condition(self):
        """
            Pac-Man vence se não houver mais PAC_DOTS no mapa.
        """
        # Vitória do Pac-Man: não há dots restantes
        if not self.matrix.has_remaining_pac_dots():
            return self.__handle_victory(EntityType.PACMAN)
            
        # Derrota do Pac-Man: sem vidas
        if self.pacman_lives <= 0:
            return self.__handle_victory(EntityType.CLYDE)  # Qualquer fantasma 

    def __handle_victory(self, entity: EntityType):
        """
            Define o estado de vitória baseado na entidade vencedora.
        """
        if entity == EntityType.PACMAN:
            print('Pacman ganhou')
            self.status = GameStatus.PACMAN_VICTORY
            self.winner = EntityType.PACMAN
        else:
            self.status = GameStatus.GHOSTS_VICTORY
            self.winner = self.__define_ghost_winner()
        
        return self.status

    def __define_ghost_winner(self) -> EntityType:
        """
            Determina qual fantasma tem a maior pontuação e retorna seu tipo.
        """
        if not self.scores:
            return None
        
        print('Fantasma vencedor:', max(self.scores, key=self.scores.get))

        # Encontra o fantasma com maior pontuação
        return max(self.scores, key=self.scores.get)

    def __check_collisions(self): 
        """
            Trata colisões entre Pac-Man e fantasmas.
        """
        pacman_position = self.matrix.get_entity_position(EntityType.PACMAN)

        for ghost in self.scores.keys():
            ghost_position = self.matrix.get_entity_position(ghost)

            # Vetifica se estão na mesma posição
            if pacman_position == ghost_position:
                print('Colisão detectada')
                self.__handle_collisions(ghost)
    
    def __handle_collisions(self, ghost: EntityType):
        """
            Regras da colisão:
            - Se Pac-Man estiver em frightened: mata o fantasma
            - Caso contrário: Pac-Man perde vida
        """
        # Fantasma é consumido
        if self.__is_frightened_mode():
            print('Fantasma consiumido')
            # Respawn do fantasma
            self.matrix.entities[ghost] = self.matrix.initial_positions[ghost]
        
        # Pacman é consumido
        else:   
            print('Pacman consumido')
            # Aumenta pontuação dos fantasmas
            self.__add_score(ghost, 100)  
            
            # Pac-Man perde vida
            if not self.__decrease_pacman_life():
                return self.__handle_victory(ghost)
            
            # Respawn pacman
            self.matrix.entities[EntityType.PACMAN] = self.matrix.initial_positions[EntityType.PACMAN]
                