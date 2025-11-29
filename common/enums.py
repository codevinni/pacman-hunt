from enum import IntEnum, Enum, auto

# Tipos de tiles (blocos do cenário).
class TileType(IntEnum):
    EMPTY = 0
    WALL = 1
    DOOR = 2        # Porta da área do fantasma
    TUNNEL = 3      # Passagem lateral do mapa

# Entidades vivas no jogo (Pac-Man e Fantasmas).
class EntityType(IntEnum):
    PACMAN = 5
    BLINKY = 6  
    PINKY = 7    
    INKY = 8     
    CLYDE = 9    

# Itens coletáveis.
class ItemType(IntEnum):
    PAC_DOT = 10
    POWER_PELLET = 11

# Ações (inputs) do jogador.
class PlayerAction(Enum):
    UP = auto()
    DOWN = auto()
    LEFT = auto()
    RIGHT = auto()
    