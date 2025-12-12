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
        
        Constants:
            PACMAN_DEFAULT_LIVES (int): Número inicial de vidas do Pac-Man (3).
            FRIGHTENED_MODE_DURATION (int): Duração do modo frightened em frames (600 = 10s @ 60FPS).
            DEFAULT_POINTS_EARNED (int): Pontos ganhos por fantasma ao consumir Pac-Man (200).
            DEFAULT_POINTS_LOST (int): Pontos perdidos por fantasma quando consumido (-50).
    """

    PACMAN_DEFAULT_LIVES = 3
    FRIGHTENED_MODE_DURATION = 300  # 10 segundos (considerando 60 FPS)
    DEFAULT_POINTS_EARNED = 200
    DEFAULT_POINTS_LOST = -50

    def __init__(self) -> None:
        """ 
            Inicializa um novo estado de jogo.
        """

        self.matrix = Matrix()
        self.status = GameStatus.RUNNING  
        self.frightened_timer = 0
        self.winner: str = None
        self.pacman_lives = self.PACMAN_DEFAULT_LIVES

        self.scores = {
            EntityType.BLINKY: 0,
            EntityType.INKY: 0,
            EntityType.PINKY: 0,
            EntityType.CLYDE: 0
        }

    def activate_frightened_mode(self) -> None:
        """ 
            Ativa o modo vulnerável (frightened) para os fantasmas.
            Método deve chamado quando o Pac-Man consome uma Power Pellet.
        """
        self.frightened_timer = self.FRIGHTENED_MODE_DURATION
        print("Modo Frightened ativado")

    def is_frightened_mode(self) -> bool:
        """ 
            Verifica se o modo frightened está ativo.

            Returns:
                bool: True se estiver ativo, False caso contrário.
        """
        return self.frightened_timer > 0

    def __decrease_frightened_timer(self) -> None:
        """ 
            Reduz em 1 o tempo de duração do modo frightened ativado pela Power-Pellet.
        """
        if self.frightened_timer > 0:
            self.frightened_timer -= 1

    def __decrease_pacman_life(self) -> bool:
        """ 
            Remove uma vida do Pac-Man após ser consumido por um fantasma.
        
            Returns:
                bool: True se o Pac-Man ainda tem vidas restantes após a redução,
                      False se o Pac-Man ficou sem vidas (jogo deve terminar).
        """
        if self.pacman_lives > 0:
            self.pacman_lives -= 1
        
        print("Pacman vidas restantes:", self.pacman_lives)
        return self.pacman_lives > 0
        
    def __add_score(self, ghost: EntityType, points: int) -> bool:
        """ 
            Adiciona ou subtrai pontos da pontuação de um fantasma específico.

            Args:
                ghost (EntityType): O tipo do fantasma.
                points (int): Quantidade de pontos a adicionar ou decrementar.

            Returns:
                bool: True se é uma entidade válida e o ponto foi adicionado, False caso contrário.
        """
        if ghost in self.scores:
            self.scores[ghost] += points
            print(f'Score {ghost.name}: {self.scores[ghost]}')
            return True
        
        return False
 
    def update(self) -> None:
        """ 
            Atualiza lógicas temporais do estado.
            Método chamado a cada tick do loop do servidor.
        """
        if self.status != GameStatus.RUNNING:
            return
        
        # Atualiza tempo do frightened
        if self.is_frightened_mode():
            self.__decrease_frightened_timer()
        
        # Verifica colisões
        self.__check_collision()  
        
        # Verifica vitória
        self.__check_victory_condition()

    def __check_victory_condition(self) -> GameStatus | None:
        """
           Verifica se alguma condição de término do jogo foi alcançada.
        
            Condições verificadas:
            - Vitória do Pac-Man: Não há mais PAC_DOTS no mapa
            - Vitória dos Fantasmas: Pac-Man ficou sem vidas
        
            Returns:
                Optional[GameStatus]: O novo status do jogo se houver vitória ou
                None se o jogo deve continuar.
        """
        # Vitória do Pac-Man: não há dots restantes
        if not self.matrix.has_remaining_pac_dots():
            return self.__handle_victory(EntityType.PACMAN)
            
        # Vitória dos Fantasmas: Pac-Man sem vidas
        if self.pacman_lives <= 0:
            return self.__handle_victory(EntityType.CLYDE)  # Qualquer fantasma 

    def __handle_victory(self, winning_entity: EntityType) -> GameStatus:
        """
            Processa a transição para estado de vitória e determina o vencedor final.
        
            Args:
                winning_entity (EntityType): Entidade que desencadeou a condição de vitória.
                - PACMAN para vitória do Pac-Man.
                - Qualquer fantasma para vitória dos fantasmas.

            Returns:
                GameStatus: O novo status do jogo (PACMAN_VICTORY ou GHOSTS_VICTORY).
        """
        if winning_entity == EntityType.PACMAN:
            print('Pacman ganhou')
            self.status = GameStatus.PACMAN_VICTORY
            self.winner = EntityType.PACMAN
        else:
            print('Fantasmas ganharam')
            self.status = GameStatus.GHOSTS_VICTORY
            self.winner = self.__define_ghost_winner()
        
        return self.status

    def __define_ghost_winner(self) -> EntityType: #
        """
            Determina qual fantasma individual teve o melhor desempenho.
            
            Returns:
                Optional[EntityType]: O tipo do fantasma com maior pontuação ou None se não houver pontuações.
        """
        if not self.scores:
            return None
        
        print('Fantasma vencedor:', max(self.scores, key=self.scores.get))

        # Encontra o fantasma com maior pontuação
        return max(self.scores, key=self.scores.get)

    def __check_collision(self) -> None: 
        """
            Verifica colisões entre o Pac-Man e os fantasmas ativos.
            Percorre todos os fantasmas e verifica se algum compartilha a mesma posição que o Pac-Man. 
        """
        pacman_position = self.matrix.get_entity_position(EntityType.PACMAN)
        
        # Verifica se Pac-Man existe
        if not pacman_position: 
            return

        for ghost in self.scores.keys():
            ghost_position = self.matrix.get_entity_position(ghost)
            
            # Verifica se o fantasma existe e está ativo
            if not ghost_position:
                continue

            # Verifica se estão na mesma posição
            if pacman_position == ghost_position:
                print(f'Colisão detectada entre Pac-Man e {ghost.name}')
                self.__handle_collision(ghost)  
    
    def __handle_collision(self, ghost: EntityType) -> None:
        """
            Processa as consequências de uma colisão entre Pac-Man e um fantasma.
        
            As regras da colisão dependem do estado do jogo:
            - Modo Frightened ativo: Fantasma é consumido, perde pontos e respawna.
            - Modo normal: Pac-Man perde vida, fantasma ganha pontos e Pac-Man respawna.
            
            Args:
                ghost (EntityType): O tipo do fantasma envolvido na colisão.
        """
        # Fantasma é consumido
        if self.is_frightened_mode():
            print(f'Fantasma {ghost.name} consumido')
            # Respawn do fantasma
            self.matrix.entities[ghost] = self.matrix.initial_positions[ghost]

            # Diminui a pomtuação do fantasma
            self.__add_score(ghost, self.DEFAULT_POINTS_LOST)  
        
        # Pacman é consumido
        else:   
            print('Pacman consumido')
            # Aumenta pontuação dos fantasmas
            self.__add_score(ghost, self.DEFAULT_POINTS_EARNED)  
            
            # Pac-Man perde vida
            if not self.__decrease_pacman_life():
                return self.__handle_victory(ghost)
            
            # Respawn pacman
            self.matrix.entities[EntityType.PACMAN] = self.matrix.initial_positions[EntityType.PACMAN]
    