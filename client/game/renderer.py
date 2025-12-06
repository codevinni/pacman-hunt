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
    
    def draw_entity(self, matrix, entity_type, image, tile_size):
        """Desenha uma entidade no mapa"""
        entity_pos = matrix.get_entity_position(entity_type)
        if entity_pos:
            px, py = entity_pos[0] * tile_size, entity_pos[1] * tile_size
            scaled_image = pygame.transform.scale(image, (tile_size, tile_size))
            self.surface.blit(scaled_image, (px, py))
    
    def draw_matrix(self, matrix, tile_size, blinky_img, pacman_image):
        """Desenha o mapa completo com todas as entidades"""
        # Desenha os tiles
        for y, row in enumerate(matrix.matrix):
            for x, cell in enumerate(row):
                self.draw_tile(cell, x, y, tile_size)
        
        # Desenha as entidades
        self.draw_entity(matrix, EntityType.PACMAN, pacman_image, tile_size)
        self.draw_entity(matrix, EntityType.BLINKY, blinky_img, tile_size)