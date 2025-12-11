# game/renderer.py
import pygame
from common.enums import EntityType
from client.game.config import *

class GameRenderer:
    def __init__(self, surface):
        self.surface = surface
    
    def draw_tile(self, tile, x, y, tile_size):
        """Desenha um tile específico"""
        px = x * tile_size
        py = y * tile_size
        
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
                tile_size // 10
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
                tile_size // 4
            )
    
    def draw_entity(self, x, y, image, tile_size):
        """Desenha uma entidade na posição exata de pixel informada"""
        scaled_image = pygame.transform.scale(image, (tile_size, tile_size))
        self.surface.blit(scaled_image, (x, y))
    
    
    def draw_matrix(self, matrix, tile_size):
        """Desenha somente o labirinto estático (tiles)"""
        for y, row in enumerate(matrix.matrix):
            for x, cell in enumerate(row):
                self.draw_tile(cell, x, y, tile_size)

            
    def draw_entities(self, visual_entities, tile_size, ghost_sprites,
                      pacman_sprite, entity_dirs, anim_frames):
        """
        Desenha TODAS as entidades usando:
        - posição suavizada do SmoothEntity
        - sprites da sprite-sheet
        - direções calculadas automaticamente
        - animação frame a frame
        """
        for et, smooth in visual_entities.items():
            try:
                x, y = smooth.get_pos()
            except Exception:
                continue

            # PACMAN
            if et == EntityType.PACMAN:
                sprite = pygame.transform.scale(pacman_sprite, (tile_size, tile_size))
                self.surface.blit(sprite, (x, y))
                continue

            # FANTASMAS
            name = et.name.lower()
            if name not in ghost_sprites:
                continue

            # direção calculada no Game
            direction = entity_dirs.get(et, "right")

            # frame
            frame = anim_frames.get(et, 0) % 2

            sprite = ghost_sprites[name][direction][frame]
            sprite = pygame.transform.scale(sprite, (tile_size, tile_size))

            self.surface.blit(sprite, (x, y))
