from enums import TileType, ItemType, EntityType

# Representa 1 célula do labirinto.
class Cell:
    def __init__(self, tile, item=None, entity=None):
        self.tile = tile
        self.item = item
        self.entity = entity

    def is_wall(self):
        """
            Retorna True se a célula for parede.
        """
        return self.tile == TileType.WALL

    def is_walkable(self):
        """
            Retorna True se a célula pode ser atravessada por entidades.
        """
        return self.tile != TileType.WALL

    def is_empty(self):
        """
            Retorna True se não tiver item ou entidade na determinada célula.
        """
        return self.item is None and self.entity is None or self.item == TileType.EMPTY

    def has_pac_dot(self):
        """
            Retorna True se há um PAC-DOT na célula.
        """
        return self.item == ItemType.PAC_DOTS

    def has_power_pellet(self):
        """
            Retorna True se há um POWER PELLET na célula.
        """
        return self.item == ItemType.POWER_PELLETS

    def consume_item(self):
        """
            Remove o item da célula e retorna qual item foi consumido.
        """
        item = self.item
        self.item = None
        return item
    
    def set_entity(self, entity):
        """
            Insere uma entidade na célula (Pac-Man ou Fantasma).
        """
        self.entity = entity

    def remove_entity(self):
        """
            Remove qualquer entidade da célula.
        """
        self.entity = None
