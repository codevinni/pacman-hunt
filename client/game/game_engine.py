# game/game.py
import pygame
from common.matrix import Matrix
from common.game_state import GameState
from common.enums import PlayerAction, EntityType
from client.game.config import *
from ..network.network_manager import NetworkManager
from client.utils.smooth_entity import SmoothEntity
from client.utils.asset_loader import load_image, get_asset_path
from client.game.renderer import GameRenderer

class Game:
    def __init__(self):
        self.game_state = GameState()
        self.matrix = self.game_state.matrix
        
        # Inicialização do PyGame
        pygame.init()
        self._setup_window()

        self.visual_entities = {
            EntityType.PACMAN: SmoothEntity(14, 23, self.tile_size), # Posição inicial Pacman
            EntityType.BLINKY: SmoothEntity(12, 14, self.tile_size), # Posição inicial Blinky
            EntityType.INKY: SmoothEntity(13, 14, self.tile_size),
            EntityType.PINKY: SmoothEntity(14, 14, self.tile_size),
            EntityType.CLYDE: SmoothEntity(15, 14, self.tile_size),
        }
        
        # Carregamento de assets
        self._load_assets()
        
        # Controle de tempo
        self.clock = pygame.time.Clock()
        self.last_switch_time = pygame.time.get_ticks()
        self.switch_interval = 250
        
        # Estado do jogo
        self.running = True
        self.pacman_image = self.pacman_open
        
        # Rede
        self.network_manager = NetworkManager()
        self._setup_network()
        
        # Renderizador
        self.renderer = GameRenderer(self.screen)
        
        # Mapeamento de teclas
        self.key_actions = {
            pygame.K_UP: PlayerAction.UP,
            pygame.K_DOWN: PlayerAction.DOWN,
            pygame.K_LEFT: PlayerAction.LEFT,
            pygame.K_RIGHT: PlayerAction.RIGHT
        }
    
    def _setup_window(self):
        """Configura a janela do jogo com base no tamanho do monitor"""
        info = pygame.display.Info()
        monitor_w = info.current_w
        monitor_h = info.current_h
        
        # Dimensões do labirinto
        tiles_x = self.matrix.width()
        tiles_y = self.matrix.height()
        
        # Calcula o melhor tamanho de tile possível
        tile_size = min(monitor_w // tiles_x, monitor_h // tiles_y)
        
        # Tamanho final da janela
        window_w = tiles_x * tile_size
        window_h = tiles_y * tile_size
        
        # Cria a janela
        self.screen = pygame.display.set_mode((window_w, window_h))
        pygame.display.set_caption("Pac-Man Hunt")
        self.tile_size = tile_size
    
    def _load_assets(self):
        """Carrega todas as imagens necessárias"""
        self.blinky_img = load_image(get_asset_path("blink.png"))
        self.pacman_open = load_image(get_asset_path("pacman-open.png"))
        self.pacman_close = load_image(get_asset_path("pacman-closed.png"))
        self.pacman_image = self.pacman_open
        
        # Rotaciona a imagem do Blinky
        self.blinky_img_rotated = pygame.transform.rotate(self.blinky_img, 0)
    
    def _setup_network(self):
        """Configura a conexão com o servidor"""
        self.network_manager.connect_to_server()
        self.ghost_type = self.network_manager.get_my_ghost()
    
    def _handle_events(self):
        """Processa eventos do PyGame"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            # Envia input para o servidor
            if event.type == pygame.KEYDOWN:
                if event.key in self.key_actions:
                    self.network_manager.send_input(self.key_actions[event.key])
    
    def _update_pacman_animation(self):
        """Alterna entre as imagens do Pac-Man para animação"""
        current_time = pygame.time.get_ticks()
        if current_time - self.last_switch_time >= self.switch_interval:
            self.pacman_image = (
                self.pacman_open 
                if self.pacman_image == self.pacman_close 
                else self.pacman_close
            )
            self.last_switch_time = current_time
    
    def _update_game_state(self):
        """Atualiza o estado do jogo a partir do servidor"""
        new_state = self.network_manager.get_game_state()

        if new_state:
            self.game_state = new_state
            self.matrix = self.game_state.matrix

            # Sincronia dos alvos visuais com a matriz recebida
            for entity_type, smooth_obj in self.visual_entities.items():
                grid_pos = self.matrix.get_entity_position(entity_type)
                if grid_pos:
                    smooth_obj.update_target(grid_pos[0], grid_pos[1])
        
    
    def _render(self):
        """Renderiza o jogo na tela"""
        self.screen.fill(BLACK)
        self.renderer.draw_matrix(
            self.matrix, 
            self.tile_size, 
            self.blinky_img_rotated, 
            self.pacman_image,
            self.visual_entities
        )
        pygame.display.update()
    
    def run(self):
        """Loop principal do jogo"""
        while self.running:
            self.clock.tick(60)
            
            self._handle_events()
            self._update_pacman_animation()
            self._update_game_state()

            for entity in self.visual_entities.values():
                entity.update()

            self._render()
        
        pygame.quit()