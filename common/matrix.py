from enums import TileType, ItemType, EntityType
from cell import Cell

# Representação e manipulação do labirinto.
class Matrix:
    def __init__(self):
        self.matrix = self.create_matrix()
    
    def create_matrix(self):
        """
            Retorna a representtação inicial da matriz (labirinto) usando objetos Cell.
        """
        return [
            # y = 0
            [Cell(TileType.WALL), Cell(TileType.WALL), Cell(TileType.WALL), Cell(TileType.WALL), Cell(TileType.WALL), Cell(TileType.WALL), Cell(TileType.WALL), Cell(TileType.WALL)],

            # y = 1
            [Cell(TileType.WALL), Cell(TileType.EMPTY, ItemType.PAC_DOTS), Cell(TileType.EMPTY, ItemType.PAC_DOTS), Cell(TileType.EMPTY, ItemType.PAC_DOTS), 
             Cell(TileType.EMPTY, ItemType.POWER_PELLETS), Cell(TileType.EMPTY, ItemType.PAC_DOTS), Cell(TileType.EMPTY, ItemType.PAC_DOTS), Cell(TileType.WALL)],

            # y = 2
            [Cell(TileType.WALL), Cell(TileType.EMPTY, ItemType.PAC_DOTS), Cell(TileType.WALL), Cell(TileType.WALL), Cell(TileType.WALL), Cell(TileType.WALL), 
             Cell(TileType.EMPTY, ItemType.PAC_DOTS), Cell(TileType.WALL)],

            # y = 3
            [Cell(TileType.WALL), Cell(TileType.EMPTY, ItemType.PAC_DOTS), Cell(TileType.EMPTY, ItemType.PAC_DOTS), Cell(TileType.EMPTY, entity=EntityType.PACMAN), 
             Cell(TileType.EMPTY, ItemType.PAC_DOTS), Cell(TileType.EMPTY, ItemType.PAC_DOTS), Cell(TileType.EMPTY, ItemType.PAC_DOTS), Cell(TileType.WALL)],

            # y = 4
            [Cell(TileType.WALL), Cell(TileType.EMPTY, ItemType.PAC_DOTS), Cell(TileType.WALL), Cell(TileType.WALL), Cell(TileType.WALL), Cell(TileType.WALL),
             Cell(TileType.EMPTY, ItemType.PAC_DOTS), Cell(TileType.WALL)],

            # y = 5
            [Cell(TileType.WALL), Cell(TileType.EMPTY, ItemType.PAC_DOTS), Cell(TileType.EMPTY, ItemType.PAC_DOTS), Cell(TileType.EMPTY, ItemType.PAC_DOTS),
             Cell(TileType.EMPTY, ItemType.PAC_DOTS), Cell(TileType.EMPTY, ItemType.POWER_PELLETS), Cell(TileType.EMPTY, entity=EntityType.BLINKY), Cell(TileType.WALL)],

            # y = 6
            [Cell(TileType.WALL), Cell(TileType.WALL), Cell(TileType.WALL), Cell(TileType.WALL), Cell(TileType.WALL), Cell(TileType.WALL), Cell(TileType.WALL), Cell(TileType.WALL)]
        ]

    def width(self):
        return len(self.matrix[0])

    def height(self):
        return len(self.matrix)

    def find_ghost(self, entity):
        """
            Retorna a posição atual ([x][y]) da entidade específica (Pac-Man ou Fantasma) na matriz.
        """
        pass

    def move_entity(self, entity, dx, dy):
        """
            Move a entidade (Pac-Man ou Fantasma) na direção indicada, se possível.
        """
        pass

    # Teste 
    def draw(self, surface, tile_size):
    for y, row in enumerate(self.matrix):
        for x, cell in enumerate(row):
            px = x * tile_size
            py = y * tile_size

            # Desenha parede.
            if cell.tile == TileType.WALL:
                pygame.draw.rect(surface, WALL_COLOR, (px, py, tile_size, tile_size))

            # Desenha pac-dots.
            if cell.item == ItemType.PAC_DOTS:
                pygame.draw.circle(surface, DOT_COLOR, (px + tile_size//2, py + tile_size//2), tile_size//10)

            if cell.item == ItemType.POWER_PELLETS:
                pygame.draw.circle(surface, PELLET_COLOR, (px + tile_size//2, py + tile_size//2), tile_size//4)

            # Desenha entidades.
            if cell.entity == EntityType.PACMAN:
                pygame.draw.circle(surface, YELLOW, (px + tile_size//2, py + tile_size//2), tile_size//2)

            if cell.entity == EntityType.BLINKY:
                pygame.draw.rect(surface, RED, (px, py, tile_size, tile_size))
