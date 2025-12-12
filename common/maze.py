'''
Matriz base do mapa do Pac-Man (28 x 31).
Define o labirinto original, preenchido com objetos `Cell`.
Cada célula contém:
    - Um TileType: parede ou espaço vazio
    - Opcional ItemType: pac-dots ou power-pellets
'''

from .enums import TileType, ItemType
from .cell import Cell

# Atalhos para criação de Cells
W: Cell = Cell(TileType.WALL)                     
E = lambda item=None: Cell(TileType.EMPTY, item)  # Espaço vazio opcionalmente com item

# Aliases/constantes para os membros do enum ItemType
D: ItemType = ItemType.PAC_DOT
P: ItemType = ItemType.POWER_PELLET

# Matriz que representa o labirinto: Dimensões = 28 colunas × 31 linhas
maze_matrix = [
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