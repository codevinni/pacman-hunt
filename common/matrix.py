from .enums import TileType, ItemType, EntityType
from .cell import Cell
from .maze import maze_matrix, W, E


class Matrix:
    """
        Representa o labirinto do jogo.

        A matriz é composta por objetos `Cell`, podendo ser:
        - Parede (TileType.WALL) impede movimentação.
        - Espaço vazio (TileType.EMPTY), podendo conter itens coletáveis.

        A classe também armazena a posição de todas as entidades no jogo (Pac-Man e Fantasmas) e permite interagir com o labirinto

        Atributes:
            matrix (list[list[Cell]]): Grid 28x31 contendo as células do labirinto.
            entities (dict[EntityType, tuple[int, int]]): Dicionário contendo as posições iniciais das entidades.
            self.initial_positions: dict[EntityType, tuple[int, int]]: Posições iniciais das entidades para respawn. 
    """

    def __init__(self):
        self.matrix = self.get_matrix()

        # Posições atuais das entidades
        self.entities = {
            EntityType.PACMAN: (14,23),
            EntityType.BLINKY: (12,14),
            EntityType.INKY: (13,14),
            EntityType.PINKY: (14,14),
            EntityType.CLYDE: (15,14)
        } 

        # Posições iniciais das entidades
        self.initial_positions = self.entities.copy()

    def get_matrix(self) -> list[list[Cell]]:
        """
            Retorna a matriz do mapa predefinida.
            
            Returns:
                list[list[Cell]]: Grade contendo todas as células do labirinto.
        """
        return maze_matrix

    def width(self) -> int:
        """
            Calcula e retorna a largura da matriz.
            
            Returns:
                int: Número de colunas na matriz.
        """
        return len(self.matrix[0])

    def height(self) -> int:
        """
            Calcula a altura da matriz.
            
            Returns:
                int: Número de linhas na matriz.
        """
        return len(self.matrix)
    
    def get_cell(self, x: int, y: int) -> Cell | None:
        """
            Retorna a célula na posição informada, caso a mesma exista.
            
            Args:
                x (int): Coordenada horizontal da célula.
                y (int): Coordenada vertical da célula.

            Returns:
                Cell | None: A célula na posição (x, y), ou None se a posição estiver fora dos limites da matriz.
        """
        if 0 <= y < len(self.matrix) and 0 <= x < len(self.matrix[0]):
            return self.matrix[y][x]
        return None
    
    def is_valid_position(self, x: int, y: int) -> bool:
        """
            Verifica se a posição é acessível para movimento.
            Regras:
                - Deve estar dentro dos limites do mapa.
                - Não pode ser uma parede (WALL).
            
            Args:
                x (int): Coordenada horizontal da célula.
                y (int): Coordenada vertical da célula.
            
            Returns:
                bool: True se a posição é válida para movimento, False caso contrário.
        """
        cell = self.get_cell(x, y)

        # Verifica limites da matriz
        if not (0 <= x < self.width() and 0 <= y < self.height()):
            return False  
        
        # Verifica se a célula é caminhável
        return cell is not None and cell.is_walkable()

    def get_entity_position(self, entity: EntityType) -> tuple[int, int] | None:
        """
            Retorna a posição atual ([x][y]) da entidade na matriz.

            Args:
                entity (EntityType): Tipo da entidade (PACMAN, BLINKY, PINKY, INKY, CLYDE).

            Returns:
                tuple[int,int] | None: Coordenadas (x, y) ou None se não existir.
        """
        return self.entities.get(entity)

    def move_entity(self, entity: EntityType, dx: int, dy: int) -> ItemType | None:
        """
            Move uma entidade no labirinto e processa possíveis interações.
            O movimento só é realizado se a posição de destino for válida. 
            Apenas o Pac-Man pode coletar itens (PAC_DOT ou POWER_PELLET). 
            
            Args:
                entity (EntityType): A entidade a ser movida (PACMAN ou fantasma).
                dx (int): Deslocamento no eixo X (-1: esquerda, 0: nenhum, 1: direita).
                dy (int): Deslocamento no eixo Y (-1: cima, 0: nenhum, 1: baixo).
                
            Returns:
                ItemType | None: 
                    - ItemType.PAC_DOT se o Pac-Man coletou um pac-dot.
                    - ItemType.POWER_PELLET se o Pac-Man coletou uma power pellet.
                    - None se nenhum item foi coletado ou se a entidade não é o Pac-Man.
        """
        position = self.entities.get(entity)
        if position is None:
            return None  # Entidade inexistente

        # Posição atual
        x, y = position

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
    
    def has_remaining_pac_dots(self) -> bool:
        """
            Verifica se ainda existem PAC-DOTS coletáveis no mapa.
            Percorre toda a matriz em busca de células que contenham PAC_DOT. 
        
            Returns:
                bool: True se houver pelo menos um PAC_DOT no mapa, False caso contrário.
        """
        for row in self.matrix:
            for cell in row:
                if cell.has_pac_dot():
                    return True
        return False
    
    def open_ghost_area(self):
        """
            Abre a área dos fantasmas redefinindo-o para uma célula (Cell) do tipo TileType.EMPTY (E)
        """
        self.matrix[12][13] = E()
        self.matrix[12][14] = E()
        
    def close_ghost_area(self):
        """
            Fecha a área dos fantasmas redefinindo-o para uma célula (Cell) do tipo TileType.WALL (W)
        """
        self.matrix[12][13] = W
        self.matrix[12][14] = W