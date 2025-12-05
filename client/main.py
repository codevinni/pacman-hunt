import pygame
import os
from common.matrix import Matrix
from common.game_state import GameState
from common.enums import EntityType, PlayerAction
from .game.config import *

from .network.network_manager import NetworkManager

# Função para carregar uma imagem e verificar sua existência
def load_image(path):
    if not os.path.exists(path):
        raise FileNotFoundError(f"Imagem não encontrada: {path}")
    return pygame.image.load(path).convert_alpha()

# Função para obter o caminho do diretório de assets
def get_asset_path(filename):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    assets_sprites = os.path.normpath(os.path.join(base_dir, "..", "assets", "sprites"))
    return os.path.join(assets_sprites, filename)

# Função para alternar entre as imagens do Pac-Man
def switch_pacman_image(current_image, open_image, closed_image, last_switch_time, switch_interval):
    current_time = pygame.time.get_ticks()
    if current_time - last_switch_time >= switch_interval:
        current_image = open_image if current_image == closed_image else closed_image
        last_switch_time = current_time
    return current_image, last_switch_time

# Função para desenhar um tile específico
def draw_tile(surface, tile, x, y, tile_size):
    px = x * tile_size
    py = y * tile_size

    # Parede
    try:
        is_wall = tile.is_wall()
    except Exception:
        is_wall = getattr(tile, 'tile', None) == 1
    if is_wall:
        pygame.draw.rect(surface, WALL_COLOR, (px, py, tile_size, tile_size))

    # Pac-Dot
    try:
        has_dot = tile.has_pac_dot()
    except Exception:
        has_dot = getattr(tile, 'item', None) == 10
    if has_dot:
        pygame.draw.circle(surface, DOT_COLOR, (px + tile_size // 2, py + tile_size // 2), tile_size // 10)

    # Power Pellet
    try:
        has_pellet = tile.has_power_pellet()
    except Exception:
        has_pellet = getattr(tile, 'item', None) == 11
    if has_pellet:
        pygame.draw.circle(surface, PELLET_COLOR, (px + tile_size // 2, py + tile_size // 2), tile_size // 4)

# Função para desenhar o mapa completo
def draw_matrix(surface, matrix, tile_size, blinky_img, pacman_image):
    for y, row in enumerate(matrix.matrix):
        for x, cell in enumerate(row):
            draw_tile(surface, cell, x, y, tile_size)

    # Desenha as entidades (Pac-Man e Blinky)
    draw_entity(surface, matrix, EntityType.PACMAN, pacman_image, tile_size)
    draw_entity(surface, matrix, EntityType.BLINKY, blinky_img, tile_size)

# Função para desenhar uma entidade no mapa
def draw_entity(surface, matrix, entity_type, image, tile_size):
    entity_pos = matrix.get_entity_position(entity_type)
    if entity_pos:
        px, py = entity_pos[0] * tile_size, entity_pos[1] * tile_size
        scaled_image = pygame.transform.scale(image, (tile_size, tile_size))
        surface.blit(scaled_image, (px, py))

# Função para mover o Blinky
def move_blinky(matrix, dx, dy):
    matrix.move_entity(EntityType.BLINKY, dx, dy)

def main():
    pygame.init()
    game_state = GameState()
    matrix = game_state.matrix

    # -----------------------------
    # DETECTA TAMANHO DO MONITOR
    # -----------------------------
    info = pygame.display.Info()
    monitor_w = info.current_w
    monitor_h = info.current_h

    # Dimensões do labirinto
    tiles_x = matrix.width()
    tiles_y = matrix.height()

    # Melhor tamanho possível
    tile_size = min(monitor_w // tiles_x, monitor_h // tiles_y)

    # Tamanho final da janela
    window_w = tiles_x * tile_size
    window_h = tiles_y * tile_size

    # -----------------------------
    # CRIA JANELA AUTOMÁTICA
    # -----------------------------
    screen = pygame.display.set_mode((window_w, window_h))
    pygame.display.set_caption("Pac-Man Hunt")

    # Carrega as imagens
    blinky_img = load_image(get_asset_path("blink.png"))
    pacman_open = load_image(get_asset_path("pacman-open.png"))
    pacman_close = load_image(get_asset_path("pacman-closed.png"))
    
    clock = pygame.time.Clock()
    running = True
    
    # Controle do tempo para alternar entre as imagens do Pac-Man
    last_switch_time = pygame.time.get_ticks()
    pacman_image = pacman_open
    switch_interval = 250
    
    # Velocidade do movimento do pacman
    last_ia_move = pygame.time.get_ticks()
    move_interval = 180
    
    imagem_rotacionada = pygame.transform.rotate(blinky_img, 0)
    
    '''
    OBS: É SOMENTE UM ESBOÇO PARA INTEGRAÇÃO DO CLIENTE AO PYGAME.
    TRATEM EXCEÇÕES E ERROS, ESTÁ TUDO COMENTADO NA CLASSE
    '''
    network_manager = NetworkManager()
    network_manager.connect_to_server()

    # PARA CARREGAR SPRITES EQUIVALENTES
    GHOST = network_manager.get_my_ghost()

    # MAPEAMENTO DAS AÇÕES DO PYGAME, PARA AS QUE DEFINIMOS
    key_actions = {
            pygame.K_UP: PlayerAction.UP,
            pygame.K_DOWN: PlayerAction.DOWN,
            pygame.K_LEFT: PlayerAction.LEFT,
            pygame.K_RIGHT: PlayerAction.RIGHT
    }

    # -----------------------------
    # LOOP PRINCIPAL DO JOGO
    # -----------------------------
    while running:

        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # Enviando input para o servidor.
            if event.type == pygame.KEYDOWN:
                if event.key in key_actions:
                    network_manager.send_input(key_actions[event.key])
        

        # Verifica se é hora de alternar a imagem do Pac-Man
        pacman_image, last_switch_time = switch_pacman_image(
            pacman_image, pacman_open, pacman_close, last_switch_time, switch_interval
        )

        # OBTEM A MATRIZ 
        game_state = network_manager.get_game_state()
        matrix = game_state.matrix

        # Renderização
        screen.fill(BLACK)
        draw_matrix(screen, matrix, tile_size, imagem_rotacionada, pacman_image)
        pygame.display.update()

    pygame.quit()

if __name__ == "__main__":
    main()