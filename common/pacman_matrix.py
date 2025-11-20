from enum import Enum

# Representação e manipulação do labirinto.
class PacmanMatrix:
    def __init__(self):
        self.matrix = self.create_matrix()
    
    def create_matrix(self):
        """
            Retorna a representtação inicial da matriz (labirinto) usando objetos Cell.
        """
        return [
            [Cell(TileType.WALL), Cell(TileType.WALL), Cell(TileType.WALL), Cell(TileType.WALL), Cell(TileType.WALL), Cell(TileType.WALL), Cell(TileType.WALL), Cell(TileType.WALL)],
            [Cell(TileType.WALL), Cell(TileType.EMPTY, ItemType.PAC_DOTS), Cell(TileType.EMPTY, ItemType.PAC_DOTS), Cell(TileType.EMPTY, ItemType.PAC_DOTS), Cell(TileType.EMPTY, ItemType.POWER_PELLETS), Cell(TileType.EMPTY, ItemType.PAC_DOTS), Cell(TileType.EMPTY, ItemType.PAC_DOTS), Cell(TileType.WALL)],
            [Cell(TileType.WALL), Cell(TileType.EMPTY, ItemType.PAC_DOTS), Cell(TileType.WALL), Cell(TileType.WALL), Cell(TileType.WALL), Cell(TileType.WALL), Cell(TileType.EMPTY, ItemType.PAC_DOTS), Cell(TileType.WALL)],
            [Cell(TileType.WALL), Cell(TileType.EMPTY, ItemType.PAC_DOTS), Cell(TileType.EMPTY, ItemType.PAC_DOTS), Cell(TileType.EMPTY, entity=EntityType.PACMAN), Cell(TileType.EMPTY, ItemType.PAC_DOTS), Cell(TileType.EMPTY, ItemType.PAC_DOTS), Cell(TileType.EMPTY, ItemType.PAC_DOTS), Cell(TileType.WALL)],
            [Cell(TileType.WALL), Cell(TileType.EMPTY, ItemType.PAC_DOTS), Cell(TileType.WALL), Cell(TileType.WALL), Cell(TileType.WALL), Cell(TileType.WALL), Cell(TileType.EMPTY, ItemType.PAC_DOTS), Cell(TileType.WALL)],
            [Cell(TileType.WALL), Cell(TileType.EMPTY, ItemType.PAC_DOTS), Cell(TileType.EMPTY, ItemType.PAC_DOTS), Cell(TileType.EMPTY, ItemType.PAC_DOTS), Cell(TileType.EMPTY, ItemType.PAC_DOTS), Cell(TileType.EMPTY, ItemType.POWER_PELLETS), Cell(TileType.EMPTY, entity=EntityType.BLINKY), Cell(TileType.WALL)],
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
