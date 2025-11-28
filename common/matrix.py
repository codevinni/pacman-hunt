from .enums import TileType, ItemType, EntityType
from .cell import Cell

# Representação e manipulação do labirinto.
class Matrix:
    def __init__(self):
        self.matrix = self.create_matrix()
        self.entities = {
            EntityType.PACMAN: (14,23),
            EntityType.BLINKY: (12,14),
            EntityType.INKY: (13,14),
            EntityType.PINKY: (14,14),
            EntityType.CLYDE: (15,14)
        } 

    def create_matrix(self):
        """
            Retorna a representação inicial da matriz (labirinto) usando objetos Cell.
        """
        W = Cell(TileType.WALL)
        E = lambda item=None: Cell(TileType.EMPTY, item)
        D = ItemType.PAC_DOTS
        P = ItemType.POWER_PELLETS
        
        # Mapa 28x31
        return [

            [W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W],
        
            [W, E(D), E(D), E(D), E(D), E(D), E(D), E(D), E(D), E(D), E(D), E(D), E(D), W, W, E(D), E(D), E(D), E(D), E(D), E(D), E(D), E(D), E(D), E(D), E(D), E(D), W],
            [W, E(D), W, W, W, W, E(D), W, W, W, W, W, E(D), W, W, E(D), W, W, W, W, W, E(D), W, W, W, W, E(D), W],
            [W, E(P), W, W, W, W, E(D), W, W, W, W, W, E(D), W, W, E(D), W, W, W, W, W, E(D), W, W, W, W, E(P), W],
            [W, E(D), W, W, W, W, E(D), W, W, W, W, W, E(D), W, W, E(D), W, W, W, W, W, E(D), W, W, W, W, E(D), W],
            [W, E(D), E(D), E(D), E(D), E(D), E(D), E(D), E(D), E(D), E(D), E(D), E(D), E(D), E(D), E(D), E(D), E(D), E(D), E(D), E(D), E(D), E(D), E(D), E(D), E(D), E(D), W],
            [W, E(D), W, W, W, W, E(D), W, W, E(D), W, W, W, W, W, W, W, W, E(D), W, W, E(D), W, W, W, W, E(D), W],
            [W, E(D), W, W, W, W, E(D), W, W, E(D), W, W, W, W, W, W, W, W, E(D), W, W, E(D), W, W, W, W, E(D), W],
            [W, E(D), E(D), E(D), E(D), E(D), E(D), W, W, E(D), E(D), E(D), E(D), W, W, E(D), E(D), E(D), E(D), W, W, E(D), E(D), E(D), E(D), E(D), E(D), W],
            
            [W, W, W, W, W, W, E(D), W, W, W, W, W, E(D), W, W, E(D), W, W, W, W, W, E(D), W, W, W, W, W, W],
            [W, W, W, W, W, W, E(D), W, W, W, W, W, E(D), W, W, E(D), W, W, W, W, W, E(D), W, W, W, W, W, W],
            [W, W, W, W, W, W, E(D), W, W, E(D), E(D), E(D), E(D), E(D), E(D), E(D), E(D), E(D), E(D), W, W, E(D), W, W, W, W, W, W],
           
            # Início da área dos ghosts
            [W, W, W, W, W, W, E(D), W, W, E(D), W, W, W, E(), E(), W, W, W, E(D), W, W, E(D), W, W, W, W, W, W],
            [W, W, W, W, W, W, E(D), W, W, E(D), W, E(), E(), E(), E(), E(), E(), W, E(D), W, W, E(D), W, W, W, W, W, W],
            
            # Túnel (meio do mapa)
            [E(D), E(D), E(D), E(D), E(D), E(D), E(D), E(D), E(D), E(D), W, E(), E(), E(), E(), E(), E(), W, E(D), E(D), E(D), E(D), E(D), E(D), E(D), E(D), E(D), E(D)],
            
            # Restante da área dos ghosts
            [W, W, W, W, W, W, E(D), W, W, E(D), W, E(), E(), E(), E(), E(), E(), W, E(D), W, W, E(D), W, W, W, W, W, W],
            [W, W, W, W, W, W, E(D), W, W, E(D), W, W, W, W, W, W, W, W, E(D), W, W, E(D), W, W, W, W, W, W],
            
            [W, W, W, W, W, W, E(D), W, W, E(D), E(D), E(D), E(D), E(D), E(D), E(D), E(D), E(D), E(D), W, W, E(D), W, W, W, W, W, W],
            [W, W, W, W, W, W, E(D), W, W, E(D), W, W, W, W, W, W, W, W, E(D), W, W, E(D), W, W, W, W, W, W],
            [W, W, W, W, W, W, E(D), W, W, E(D), W, W, W, W, W, W, W, W, E(D), W, W, E(D), W, W, W, W, W, W],
            
            [W, E(D), E(D), E(D), E(D), E(D), E(D), E(D), E(D), E(D), E(D), E(D), E(D), W, W, E(D), E(D), E(D), E(D), E(D), E(D), E(D), E(D), E(D), E(D), E(D), E(D), W],
            [W, E(D), W, W, W, W, E(D), W, W, W, W, W, E(D), W, W, E(D), W, W, W, W, W, E(D), W, W, W, W, E(D), W],
            [W, E(D), W, W, W, W, E(D), W, W, W, W, W, E(D), W, W, E(D), W, W, W, W, W, E(D), W, W, W, W, E(D), W],
            [W, E(P), E(D), E(D), W, W, E(D), E(D), E(D), E(D), E(D), E(D), E(D), E(D), E(D), E(D), E(D), E(D), E(D), E(D), E(D), E(D), W, W, E(D), E(D), E(P), W],
            [W, W, W, E(D), W, W, E(D), W, W, E(D), W, W, W, W, W, W, W, W, E(D), W, W, E(D), W, W, E(D), W, W, W],
            [W, W, W, E(D), W, W, E(D), W, W, E(D), W, W, W, W, W, W, W, W, E(D), W, W, E(D), W, W, E(D), W, W, W],
            [W, E(D), E(D), E(D), E(D), E(D), E(D), W, W, E(D), E(D), E(D), E(D), W, W, E(D), E(D), E(D), E(D), W, W, E(D), E(D), E(D), E(D), E(D), E(D), W],
            [W, E(D), W, W, W, W, W, W, W, W, W, W, E(D), W, W, E(D), W, W, W, W, W, W, W, W, W, W, E(D), W],
            [W, E(D), W, W, W, W, W, W, W, W, W, W, E(D), W, W, E(D), W, W, W, W, W, W, W, W, W, W, E(D), W],
            [W, E(D), E(D), E(D), E(D), E(D), E(D), E(D), E(D), E(D), E(D), E(D), E(D), E(D), E(D), E(D), E(D), E(D), E(D), E(D), E(D), E(D), E(D), E(D), E(D), E(D), E(D), W],
        
            [W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W]
        ]

    def width(self):
        return len(self.matrix[0])

    def height(self):
        return len(self.matrix)
    
    def get_cell(self, x, y):
        """
            Acesso seguro à célula.
        """
        if 0 <= y < len(self.matrix) and 0 <= x < len(self.matrix[0]):
            return self.matrix[y][x]
        return None
    
    def is_valid_position(self, x, y):
        """
            Verifica se posição existe e é transitável
        """
        cell = self.get_cell(x, y)
        return cell is not None and cell.can_walk_through()

    def get_entity_position(self, entity_type):
        """
            Retorna a posição atual ([x][y]) da entidade específica (Pac-Man ou Fantasma) na matriz.
        """
        return self.entities.get(entity_type)
    
    def find_ghost(self, entity):
        # Compat: procura na tabela de entidades
        return self.entities.get(entity)
    
    def move_entity(self, entity, dx, dy):
        pos = self.entities.get(entity)
        if pos is None:
            return

        x, y = pos
        nx, ny = x + dx, y + dy

        # Fora dos limites
        if nx < 0 or ny < 0 or nx >= self.width() or ny >= self.height():
            return

        target = self.matrix[ny][nx]

        # Parede
        if target.tile == TileType.WALL:
            return

        # Consumir item se houver
        if target.item is not None:
            target.consume_item()

        # Atualiza posição
        self.entities[entity] = (nx, ny)
