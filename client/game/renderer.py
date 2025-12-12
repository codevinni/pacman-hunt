import pygame
from common.enums import EntityType
from client.game.config import *


class GameRenderer:
    """
    Responsável por todo o desenho do jogo:
    - labirinto
    - entidades (Pac-Man, fantasmas)
    - sprites animados
    """

    def __init__(self, surface):
        self.surface = surface

    def draw_tile(self, tile, x, y, tile_size, offset_x=0, offset_y=0):
        """
        Desenha um tile (parede, pac-dot, power pellet).
        """
        px = offset_x + x * tile_size
        py = offset_y + y * tile_size

        # Parede
        try:
            is_wall = tile.is_wall()
        except:
            is_wall = getattr(tile, "tile", None) == 1

        if is_wall:
            pygame.draw.rect(self.surface, WALL_COLOR, (px, py, tile_size, tile_size))

        # Pac-dot
        try:
            has_dot = tile.has_pac_dot()
        except:
            has_dot = getattr(tile, "item", None) == 10

        if has_dot:
            pygame.draw.circle(
                self.surface,
                DOT_COLOR,
                (px + tile_size // 2, py + tile_size // 2),
                max(1, tile_size // 10),
            )

        # Power pellet
        try:
            has_pellet = tile.has_power_pellet()
        except:
            has_pellet = getattr(tile, "item", None) == 11

        if has_pellet:
            pygame.draw.circle(
                self.surface,
                PELLET_COLOR,
                (px + tile_size // 2, py + tile_size // 2),
                max(2, tile_size // 4),
            )

    def draw_entity(self, x, y, image, tile_size, offset_x=0, offset_y=0, center=False):
        """
        Desenha uma entidade baseada em coordenadas pixeladas já suavizadas.
        """
        if image is None:
            return

        px = offset_x + x
        py = offset_y + y

        if center:
            px -= tile_size // 2
            py -= tile_size // 2

        sprite = pygame.transform.scale(image, (tile_size, tile_size))
        self.surface.blit(sprite, (px, py))

    def draw_matrix(self, matrix, tile_size, offset_x=0, offset_y=0):
        """
        Desenha o labirinto completo.
        """
        for y, row in enumerate(matrix.matrix):
            for x, cell in enumerate(row):
                self.draw_tile(cell, x, y, tile_size, offset_x, offset_y)

    def draw_entities(
        self,
        visual_entities,
        tile_size,
        ghost_sprites,
        pacman_sprite,
        entity_dirs,
        anim_frames,
        game_state,
        offset_x,
        offset_y,
        frightened_blue,
        frightened_blink,
    ):
        """
        Desenha todas as entidades: Pac-Man e Fantasmas.

        Usa:
        - entity_dirs para direção atual
        - anim_frames para index de animação
        - frightened_timer para decidir cor do fantasma
        """

        for et, smooth in visual_entities.items():
            try:
                x, y = smooth.get_pos()
            except:
                continue

            # --------------------
            # Desenhar Pac-Man
            # --------------------
            if et == EntityType.PACMAN:
                self.draw_entity(x, y, pacman_sprite, tile_size, offset_x, offset_y)
                continue

            # --------------------
            # Desenhar fantasmas
            # --------------------
            name = et.name.lower()

            if name not in ghost_sprites:
                continue

            direction = entity_dirs.get(et, "right")
            frame = anim_frames.get(et, 0) % 2

            # Modo frightened
            if game_state.is_frightened_mode():

                remaining = game_state.frightened_timer
                total = game_state.FRIGHTENED_MODE_DURATION

                # último quarto → piscar
                if remaining < total * 0.25:
                    if (remaining // 10) % 2 == 0:
                        sprite = frightened_blue[frame]
                    else:
                        sprite = frightened_blink[frame]
                else:
                    sprite = frightened_blue[frame]

            else:
                # Fantasma normal
                sprite = ghost_sprites[name][direction][frame]

            self.draw_entity(x, y, sprite, tile_size, offset_x, offset_y)
