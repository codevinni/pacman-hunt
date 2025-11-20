from enum import IntEnum

# Tipos de tiles (blocos do cenário).
class TileType(IntEnum):
    EMPTY = 0
    WALL = 1

# Entidades vivas no jogo (Pac-Man e Fantasmas).
class EntityType(IntEnum):
    PACMAN = 5
    BLINKY = 6   # Vermelho: o mais agressivo e direto em sua perseguição.
    PINKY = 7    # Rosa: Tenta emboscar o Pac-Man, posicionando-se à frente dele.
    INKY = 8     # Azul: sua tática é mais complexa e às vezes imprevisível.
    CLYDE = 9    # Laranja: o mais "covarde" e muitas vezes se move para longe do Pac-Man.

# Itens coletáveis.
class ItemType(IntEnum):
    PAC_DOTS = 10
    POWER_PELLETS = 11 # Pastilhas de poder.

# Direções possíveis de movimento.
class Direction(Enum):
    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)
