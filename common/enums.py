"""
    Enumerações do jogo Pac-Man Hunt.
    Define:
    - Tipos de tiles (blocos do mapa)
    - Entidades vivas (Pac-Man e Fantasmas)
    - Tipos de itens coletáveis (PAC-DOT e POWER-PELLET)
    - Ações do jogador em coordenadas de movimento
"""

from enum import IntEnum, Enum, auto

class TileType(IntEnum):
    """
        Representa o tipo de bloco presente no labirinto.

        Values:
            EMPTY: Espaço livre onde entidades podem se mover.
            WALL: Parede, impede movimento de entidades.
            DOOR: Porta da casa dos fantasmas (Ghost House).
            TUNNEL: Caminho lateral que conecta bordas do mapa.
    """
    EMPTY = 0
    WALL = 1
    DOOR = 2
    TUNNEL = 3

class EntityType(IntEnum):
    """
        Tipos de entidades vivas que podem existir no jogo.

        Values:
            PACMAN: Jogador principal.
            BLINKY: Fantasma vermelho.
            PINKY: Fantasma rosa.
            INKY: Fantasma azul.
            CLYDE: Fantasma laranja.
    """
    PACMAN = 5
    BLINKY = 6
    PINKY = 7
    INKY = 8
    CLYDE = 9

class ItemType(IntEnum):
    """
        Representa os itens que podem estar presentes em uma célula.

        Values:
            PAC_DOT: Pequeno ponto comestível.
            POWER_PELLET: Habilita Pac-Man a consumir fantasmas temporariamente.
    """
    PAC_DOT = 10
    POWER_PELLET = 11

class PlayerAction(Enum):
    """
        Direções que o jogador pode mover Pac-Man.
        Cada ação armazena um deslocamento (dx, dy) aplicado no movimento.
    """
    UP = auto()
    DOWN = auto()
    LEFT = auto()
    RIGHT = auto()

class GameStatus(Enum):
    """
        Define os estados possíveis da partida.
    """
    WAITING_PLAYERS = auto() 
    RUNNING = auto()
    PACMAN_VICTORY = auto() 
    GHOSTS_VICTORY = auto()