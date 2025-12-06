# game/utils/asset_loader.py
import pygame
import os

def load_image(path):
    """Carrega uma imagem e verifica sua existência"""
    if not os.path.exists(path):
        raise FileNotFoundError(f"Imagem não encontrada: {path}")
    return pygame.image.load(path).convert_alpha()

def get_asset_path(filename):
    """Obtém o caminho completo para um arquivo de asset"""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    assets_sprites = os.path.normpath(
        os.path.join(base_dir, "..", "..", "assets", "sprites")
    )
    return os.path.join(assets_sprites, filename)