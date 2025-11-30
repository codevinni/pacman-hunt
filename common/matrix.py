from .enums import TileType, ItemType, EntityType, PlayerAction
from .cell import Cell
from .maze import maze_matrix


class Matrix:
    '''
    Representa o labirinto do jogo.

    A matriz é composta por objetos `Cell`, podendo ser:
    - Parede (TileType.WALL) impede movimentação.
    - Espaço vazio (TileType.EMPTY), podendo conter itens coletáveis.

    A classe também armazena a posição de todas as entidades no jogo (Pac-Man e Fantasmas) e permite interagir com o labirinto

    Atributes:
        matrix (list[list[Cell]]): Grid 28x31 contendo as células do labirinto.
        entities (dict[EntityType, tuple[int, int]]): Dicionário contendo as posições iniciais das entidades.
    '''

    def __init__(self):
        self.matrix = self.get_matrix()
        self.entities = {
            EntityType.PACMAN: (14,23),
            EntityType.BLINKY: (12,14),
            EntityType.INKY: (13,14),
            EntityType.PINKY: (14,14),
            EntityType.CLYDE: (15,14)
        } 

    def get_matrix(self) -> list[list[Cell]]:
        '''
        Retorna a matriz do mapa previamente definida.
        '''
        return maze_matrix

    def width(self) -> int:
        '''
        Calcula e retorna a largura (número de colunas) da matriz em células.
        '''
        return len(self.matrix[0])

    def height(self) -> int:
        '''
        Calcula e retorna a altura (número de linhas) do mapa em células.
        '''
        return len(self.matrix)
    
    def get_cell(self, x: int, y: int) -> Cell | None:
        '''
        Args:
            - x (int): Coordenada horizontal da célula.
            - y (int): Coordenada vertical da célula.

        Retorna a célula na posição informada, caso exista.
        '''
        if 0 <= y < len(self.matrix) and 0 <= x < len(self.matrix[0]):
            return self.matrix[y][x]
        return None
    
    def is_valid_position(self, x: int, y: int) -> bool:
        '''
        Verifica se a posição é acessível para movimento.
        Regras:
            - Deve estar dentro dos limites do mapa
            - Não pode ser uma parede (WALL)
        
        Args:
            - x (int): Coordenada horizontal da célula.
            - y (int): Coordenada vertical da célula.
        '''
        cell = self.get_cell(x, y)

        # Verifica limites da matriz
        if not (0 <= x < self.width() and 0 <= y < self.height()):
            return None  
        
        # Verifica se a célula é caminhável
        return cell is not None and cell.is_walkable()

    def get_entity_position(self, entity: EntityType) -> tuple[int, int] | None:
        '''
        Retorna a posição atual ([x][y]) da entidade na matriz.

        Args:
            entity_type (EntityType): Tipo da entidade (PACMAN, BLINKY, PINKY, INKY, CLYDE).
        '''
        return self.entities.get(entity)

    def move_entity(self, entity: EntityType, dx: int, dy: int) -> ItemType | None:
        '''
        Move uma entidade no labirinto.
        - Apenas Pac-Man coleta PAC-DOTS e POWER-PELLETS.
        - Entidades apenas se movem se o destino for válido.

        Args:
            entity (EntityType): A entidade a ser movida (PACMAN ou fantasma).
            action (PlayerAction): A ação que determina a direção do movimento.

        Returns:
            ItemType: O item coletado (PAC_DOT ou POWER_PELLET) se houver, None caso contrário.
        '''
        position = self.entities.get(entity)
        if position is None:
            return None  # Entidade inexistente

        # Posição atual
        x, y = position

        # dx deslocamento no eixo X 
        # dy deslocamento no eixo Y 
        # nx novo X (posição futura)	
        # ny novo Y (posição futura)	
        nx, ny = x + dx, y + dy
        
        # Valida o movimento
        if not self.is_valid_position(nx, ny):  
            return None 

        cell = self.matrix[ny][nx]

        # Se for Pac-Man, permite consumir itens
        collected = None
        if entity == EntityType.PACMAN and cell.item is not None:
            collected = cell.consume_item()

        # Atualiza posição da entidade
        self.entities[entity] = (nx, ny)
        return collected  # Retorna item coletado ou None
