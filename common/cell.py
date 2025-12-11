from .enums import TileType, ItemType

class Cell:
    '''
        Representa uma única célula do labirinto no jogo.

        Uma célula possui:
        - Um tipo de terreno (tile), podendo ser parede ou espaço vazio.
        - Um item opcional, como PAC-DOT, POWER-PELLET ou nenhum.

        A classe fornece métodos auxiliares para verificar o estado da célula e consumir itens quando presente.
    '''

    def __init__(self, tile, item=None):
        '''
            Inicializa uma célula com um tipo de terreno e possível item.

            Args:
                tile : Tipo da célula (EMPTY ou WALL).
                item : Item presente (PAC_DOT, POWER_PELLET ou None).
        '''
        self.tile = tile     # TileType.EMPTY ou TileType.WALL.
        self.item = item     # ItemType.PAC_DOT, POWER_PELLET ou None.

    def is_wall(self) -> bool:
        '''
            Verifica se a célula é uma parede.
            Returns: True se a célula for do tipo WALL.
        '''
        return self.tile == TileType.WALL

    def is_walkable(self) -> bool:
        '''
            Verifica se a célula pode ser atravessada por entidades.
            Returns: True se a célula não for WALL.
        '''
        return self.tile != TileType.WALL

    def is_empty(self) -> bool:
        '''
            Verifica se não há item armazenado na célula.
            Returns: True se não houver item.
        '''
        return self.item is None or self.item == TileType.EMPTY

    def has_pac_dot(self) -> bool:
        '''
            Verifica se há um PAC-DOT na célula.
            Returns: True se o item presente for PAC_DOT.
        '''
        return self.item == ItemType.PAC_DOT

    def has_power_pellet(self) -> bool:
        '''
            Verifica se há um POWER-PELLET na célula.
            Returns: True se o item presente for POWER_PELLET.
        '''
        return self.item == ItemType.POWER_PELLET

    def consume_item(self) -> ItemType | None:
        '''
            Consome o item presente na célula.
            O item é removido e retornado, permitindo que o chamador saiba qual item foi consumido.

            Returns: O item consumido ou None se não havia item.
        '''
        item = self.item
        self.item = None
        return item
