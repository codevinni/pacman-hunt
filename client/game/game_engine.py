# game/game.py
import pygame
from common.matrix import Matrix
from common.game_state import GameState
from common.enums import PlayerAction, EntityType
from client.game.config import *
from ..network.network_manager import NetworkManager
from client.utils.smooth_entity import SmoothEntity
from client.utils.asset_loader import load_image, get_asset_path
# para carregar sprite sheet e manipular imagens já existentes
from client.game.config import LARGURA_SPRITE, ALTURA_SPRITE
# se não tiver essas constantes no config, substitua pelos valores inteiros (ex: 32)

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
        # último grid conhecido (tupla x,y) por entidade — usado para calcular delta
        self.prev_grid = {}
        
        # direção estimada por entidade: "up","down","left","right"
        self.entity_dirs = {}
        
        # frame de animação (0 ou 1) por entidade
        self.anim_frame = {}
        
        # timers por entidade (ms)
        self.anim_timer = {}
        
        # inicializa estados de animação
        self.init_entity_animation_state()
  
        # Carregamento de assets
        self._load_assets()
        
        # Controle de tempo
        self.clock = pygame.time.Clock()
        self.last_switch_time = pygame.time.get_ticks()
        self.switch_interval = 250
        
        # Estado do jogo
        self.running = True
        
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
        """Carrega todas as imagens necessárias (suporta spritesheet se disponível)."""
        try:
            sprite_sheet = load_image(get_asset_path("sprites.png"))
        except Exception:
            sprite_sheet = None

        # prepara pacman frames
        if sprite_sheet:
            self.pacman_sprites = [
                sprite_sheet.subsurface(pygame.Rect(0 * LARGURA_SPRITE, 0 * ALTURA_SPRITE, LARGURA_SPRITE, ALTURA_SPRITE)).copy(),
                sprite_sheet.subsurface(pygame.Rect(1 * LARGURA_SPRITE, 0 * ALTURA_SPRITE, LARGURA_SPRITE, ALTURA_SPRITE)).copy()
            ]     

        # prepara sprites dos fantasmas por direção
        self.ghost_sprites = {}
        # linhas por fantasma (conforme você confirmou)
        GHOST_SHEET_LINE = {"blinky": 4, "pinky": 5, "inky": 6, "clyde": 7}
        if sprite_sheet:
            for name, line in GHOST_SHEET_LINE.items():
                    self.ghost_sprites[name] = {
                        "right": [
                            sprite_sheet.subsurface(pygame.Rect(0 * LARGURA_SPRITE, line * ALTURA_SPRITE, LARGURA_SPRITE, ALTURA_SPRITE)).copy(),
                            sprite_sheet.subsurface(pygame.Rect(1 * LARGURA_SPRITE, line * ALTURA_SPRITE, LARGURA_SPRITE, ALTURA_SPRITE)).copy()
                        ],
                        "left": [
                            sprite_sheet.subsurface(pygame.Rect(2 * LARGURA_SPRITE, line * ALTURA_SPRITE, LARGURA_SPRITE, ALTURA_SPRITE)).copy(),
                            sprite_sheet.subsurface(pygame.Rect(3 * LARGURA_SPRITE, line * ALTURA_SPRITE, LARGURA_SPRITE, ALTURA_SPRITE)).copy()
                        ],
                        "up": [
                            sprite_sheet.subsurface(pygame.Rect(4 * LARGURA_SPRITE, line * ALTURA_SPRITE, LARGURA_SPRITE, ALTURA_SPRITE)).copy(),
                            sprite_sheet.subsurface(pygame.Rect(5 * LARGURA_SPRITE, line * ALTURA_SPRITE, LARGURA_SPRITE, ALTURA_SPRITE)).copy()
                        ],
                        "down": [
                            sprite_sheet.subsurface(pygame.Rect(6 * LARGURA_SPRITE, line * ALTURA_SPRITE, LARGURA_SPRITE, ALTURA_SPRITE)).copy(),
                            sprite_sheet.subsurface(pygame.Rect(7 * LARGURA_SPRITE, line * ALTURA_SPRITE, LARGURA_SPRITE, ALTURA_SPRITE)).copy()
                        ]
                    }

    
    def _setup_network(self):
        """Configura a conexão com o servidor"""
        self.network_manager.connect_to_server()
        self.ghost_type = self.network_manager.get_my_ghost()
    
    def _handle_events(self):
        """Processa eventos do PyGame"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            if event.type == pygame.KEYDOWN:
                if event.key in self.key_actions:
                    self.network_manager.send_input(self.key_actions[event.key])
    
    def init_entity_animation_state(self):
        """Inicializa estados de direção, frames, timers e posição anterior."""
        
        ENTITIES = (
            EntityType.PACMAN,
            EntityType.BLINKY,
            EntityType.INKY,
            EntityType.PINKY,
            EntityType.CLYDE
        )

        now = pygame.time.get_ticks()

        for entity in ENTITIES:
            # tenta obter posição atual na grid
            try:
                pos = self.matrix.get_entity_position(entity)
            except Exception:
                pos = None

            # salva posição anterior
            self.prev_grid[entity] = (pos[0], pos[1]) if pos else None

            # estado inicial de animação
            self.entity_dirs[entity] = "right"
            self.anim_frame[entity] = 0
            self.anim_timer[entity] = now

    def _update_animations(self):
        """Atualiza frames de animação por entidade com timers separados."""
        now = pygame.time.get_ticks()

        # Pac-Man (caso você prefira sprite sheet, usa self.pacman_sprites)
        if now - self.anim_timer.get(EntityType.PACMAN, 0) >= self.switch_interval:
            # alterna entre pacman_sprites se existirem, senão alterna suas imagens antigas
            if hasattr(self, "pacman_sprites"):
                # usa anim_frame para index
                self.anim_frame[EntityType.PACMAN] ^= 1
                self.pacman_image = self.pacman_sprites[self.anim_frame[EntityType.PACMAN]]
            else:
                # fallback original (abre/fecha)
                self.pacman_image = (self.pacman_open if self.pacman_image == self.pacman_close else self.pacman_close)
            self.anim_timer[EntityType.PACMAN] = now

        # Fantasmas
        for et in (EntityType.BLINKY, EntityType.INKY, EntityType.PINKY, EntityType.CLYDE):
            if now - self.anim_timer.get(et, 0) >= 180:
                self.anim_frame[et] ^= 1
                self.anim_timer[et] = now


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
                    gx, gy = grid_pos[0], grid_pos[1]

                    # calcula direção pela diferença com prev_grid, se existir
                    prev = self.prev_grid.get(entity_type)
                    if prev is not None:
                        ox, oy = prev
                        dx = gx - ox
                        dy = gy - oy
                        if dx == 0 and dy == 0:
                            # sem movimento: manter direção anterior
                            pass
                        else:
                            # prioriza maior delta
                            if abs(dx) >= abs(dy):
                                self.entity_dirs[entity_type] = "right" if dx > 0 else "left"
                            else:
                                self.entity_dirs[entity_type] = "down" if dy > 0 else "up"

                    # salva prev grid
                    self.prev_grid[entity_type] = (gx, gy)

                    # atualiza target visual (SmoothEntity)
                    try:
                        smooth_obj.update_target(gx, gy)
                    except Exception:
                        # Caso smooth_obj esteja None ou falhe, tente criar
                        try:
                            self.visual_entities[entity_type] = SmoothEntity(gx, gy, self.tile_size)
                        except Exception:
                            pass

    
    def _render(self):
        """Renderiza o jogo na tela."""
        self.screen.fill(BLACK)
        self.renderer.draw_matrix(self.matrix, self.tile_size)
        self.renderer.draw_entities(
            visual_entities=self.visual_entities,
            tile_size=self.tile_size,
            ghost_sprites=self.ghost_sprites,
            pacman_sprite=self.pacman_sprites[self.anim_frame[EntityType.PACMAN]],
            entity_dirs=self.entity_dirs,
            anim_frames=self.anim_frame
        )
        pygame.display.update()

    
    def run(self):
        """Loop principal do jogo"""
        while self.running:
            self.clock.tick(60)
            self._handle_events()
            self._update_game_state()
            # atualiza targets -> SmoothEntities já têm os destinos
            for entity in self.visual_entities.values():
                entity.update()
            self._update_animations()
            self._render()
        
        pygame.quit()