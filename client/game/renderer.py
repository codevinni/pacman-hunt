# game/renderer.py
import pygame
from common.enums import EntityType
from client.game.config import *

class GameRenderer:
    def __init__(self, surface):
        self.surface = surface

    # -------------------------------------------------------------------------
    # DESENHA UM TILE DO MAPA (com offset aplicado opcionalmente)
    # -------------------------------------------------------------------------
    def draw_tile(self, tile, x, y, tile_size, offset_x=0, offset_y=0):
        """
        x, y: coordenadas em tiles (col, row)
        offset_x, offset_y: deslocamento em pixels aplicado (opcional)
        """
        px = offset_x + x * tile_size
        py = offset_y + y * tile_size

        # Parede
        try:
            is_wall = tile.is_wall()
        except Exception:
            is_wall = getattr(tile, 'tile', None) == 1

        if is_wall:
            pygame.draw.rect(
                self.surface,
                WALL_COLOR,
                (px, py, tile_size, tile_size)
            )

        # Pac-Dot
        try:
            has_dot = tile.has_pac_dot()
        except Exception:
            has_dot = getattr(tile, 'item', None) == 10
        if has_dot:
            pygame.draw.circle(
                self.surface,
                DOT_COLOR,
                (px + tile_size // 2, py + tile_size // 2),
                max(1, tile_size // 10)
            )

        # Power Pellet
        try:
            has_pellet = tile.has_power_pellet()
        except Exception:
            has_pellet = getattr(tile, 'item', None) == 11
        if has_pellet:
            pygame.draw.circle(
                self.surface,
                PELLET_COLOR,
                (px + tile_size // 2, py + tile_size // 2),
                max(2, tile_size // 4)
            )

    # -------------------------------------------------------------------------
    # DESENHA UMA ENTIDADE (já com offset opcional)
    # -------------------------------------------------------------------------
    def draw_entity(self, x, y, image, tile_size, offset_x=0, offset_y=0, center=False):
        """
        x,y: posição em pixels (normalmente SmoothEntity.get_pos())
        offset_x/offset_y: deslocamento em pixels (opcional)
        center: se True, considera (x,y) como o centro da sprite e ajusta top-left
        """
        if image is None:
            return False

        px = offset_x + x
        py = offset_y + y

        surf = pygame.transform.scale(image, (tile_size, tile_size))

        if center:
            draw_x = int(px - tile_size // 2)
            draw_y = int(py - tile_size // 2)
        else:
            draw_x = int(px)
            draw_y = int(py)

        self.surface.blit(surf, (draw_x, draw_y))
        return True

    # -------------------------------------------------------------------------
    # DESENHA SOMENTE O MAPA (tiles) — offset opcional
    # -------------------------------------------------------------------------
    def draw_matrix(self, matrix, tile_size, offset_x=0, offset_y=0):
        """
        Desenha o labirinto. offset_x/offset_y são opcionais e defaultam a 0,
        assim chamadas antigas (sem offset) continuam funcionando.
        """
        for y, row in enumerate(matrix.matrix):
            for x, cell in enumerate(row):
                try:
                    self.draw_tile(cell, x, y, tile_size, offset_x, offset_y)
                except Exception:
                    # Proteção para evitar crash por célula inesperada
                    continue

    # -------------------------------------------------------------------------
    # DESENHA TODAS AS ENTIDADES (com offset opcional, sprites e animação)
    # -------------------------------------------------------------------------
    def draw_entities(
        self,
        visual_entities,
        tile_size,
        ghost_sprites,
        pacman_sprite,
        entity_dirs,
        anim_frames,
        offset_x=0,
        offset_y=0,
        center_sprites=False
    ):
        """
        Desenha entidades dadas em visual_entities (dicionário EntityType -> SmoothEntity).
        Parâmetros offset_x/offset_y são opcionais:
          - se não passados, comportamento idêntico ao antigo (sem offset).
          - se passados, deslocam todo o desenho do mapa e entidades.
        center_sprites: se True centraliza cada sprite no ponto retornado por SmoothEntity.get_pos()
        """
        if not visual_entities:
            return

        for et, smooth in visual_entities.items():
            try:
                x, y = smooth.get_pos()
            except Exception:
                continue

            # PAC-MAN
            if et == EntityType.PACMAN:
                # pacman_sprite pode ser None — cheque
                if pacman_sprite:
                    self.draw_entity(x, y, pacman_sprite, tile_size, offset_x, offset_y, center=center_sprites)
                continue

            # FANTASMAS
            name = et.name.lower()
            if name not in ghost_sprites:
                continue

            direction = entity_dirs.get(et, "right")
            frame = anim_frames.get(et, 0) % 2

            try:
                sprite = ghost_sprites[name][direction][frame]
            except Exception:
                # fallback para evitar crash
                try:
                    sprite = ghost_sprites[name]["right"][0]
                except Exception:
                    sprite = None

            if sprite:
                self.draw_entity(x, y, sprite, tile_size, offset_x, offset_y, center=center_sprites)
