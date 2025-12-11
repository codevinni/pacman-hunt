# game/game.py
import pygame, os
from common.matrix import Matrix
from common.game_state import GameState
from common.enums import PlayerAction, EntityType
from client.game.config import *
from ..network.network_manager import NetworkManager
from client.utils.smooth_entity import SmoothEntity
from client.utils.asset_loader import load_image, get_asset_path
from client.game.config import LARGURA_SPRITE, ALTURA_SPRITE
from client.game.menu import GameMenu

from client.game.renderer import GameRenderer

HUD_BOTTOM_HEIGHT = 80   # altura reservada abaixo do mapa

class Game:
    def __init__(self):
        self.game_state = GameState()
        self.matrix = self.game_state.matrix
        self.menu = GameMenu(self)
        pygame.init()
        self._setup_window()
        self.menu_open = False
        self.fullscreen = False
        self.font = pygame.font.Font(get_asset_path("fonts/Emulogic-zrEw.ttf"), 16)

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
        info = pygame.display.Info()
        monitor_w = info.current_w
        monitor_h = info.current_h
        
        tiles_x = self.matrix.width()
        tiles_y = self.matrix.height()

        self.tile_size = min(monitor_w // tiles_x, monitor_h // tiles_y)
        window_w = tiles_x * self.tile_size
        window_h = tiles_y * self.tile_size + HUD_BOTTOM_HEIGHT

        
        self.screen = pygame.display.set_mode((monitor_w, monitor_h)) 
        pygame.display.set_caption("Pac-Man Hunt")

        self._compute_offsets()

    def _load_assets(self):
        sheet = load_image(get_asset_path("sprites.png"))

        # Pac-Man usa linha 0
        self.pacman_sprites = [
            sheet.subsurface(pygame.Rect(0 * LARGURA_SPRITE, 0 * ALTURA_SPRITE, LARGURA_SPRITE, ALTURA_SPRITE)).copy(),
            sheet.subsurface(pygame.Rect(1 * LARGURA_SPRITE, 0 * ALTURA_SPRITE, LARGURA_SPRITE, ALTURA_SPRITE)).copy(),
        ]

        # Constante: pacman_image começa no frame 0
        self.pacman_image = self.pacman_sprites[0]

        # SPRITES DOS FANTASMAS
        GHOST_SHEET_LINE = {
            "blinky": 4,
            "pinky": 5,
            "inky": 6,
            "clyde": 7,
        }

        self.ghost_sprites = {}

        for name, row in GHOST_SHEET_LINE.items():
            self.ghost_sprites[name] = {
                "right": [
                    sheet.subsurface(pygame.Rect(0 * LARGURA_SPRITE, row * ALTURA_SPRITE, LARGURA_SPRITE, ALTURA_SPRITE)).copy(),
                    sheet.subsurface(pygame.Rect(1 * LARGURA_SPRITE, row * ALTURA_SPRITE, LARGURA_SPRITE, ALTURA_SPRITE)).copy(),
                ],
                "left": [
                    sheet.subsurface(pygame.Rect(2 * LARGURA_SPRITE, row * ALTURA_SPRITE, LARGURA_SPRITE, ALTURA_SPRITE)).copy(),
                    sheet.subsurface(pygame.Rect(3 * LARGURA_SPRITE, row * ALTURA_SPRITE, LARGURA_SPRITE, ALTURA_SPRITE)).copy(),
                ],
                "up": [
                    sheet.subsurface(pygame.Rect(4 * LARGURA_SPRITE, row * ALTURA_SPRITE, LARGURA_SPRITE, ALTURA_SPRITE)).copy(),
                    sheet.subsurface(pygame.Rect(5 * LARGURA_SPRITE, row * ALTURA_SPRITE, LARGURA_SPRITE, ALTURA_SPRITE)).copy(),
                ],
                "down": [
                    sheet.subsurface(pygame.Rect(6 * LARGURA_SPRITE, row * ALTURA_SPRITE, LARGURA_SPRITE, ALTURA_SPRITE)).copy(),
                    sheet.subsurface(pygame.Rect(7 * LARGURA_SPRITE, row * ALTURA_SPRITE, LARGURA_SPRITE, ALTURA_SPRITE)).copy(),
                ],
            }

    def _setup_network(self):
        """Configura a conexão com o servidor"""
        self.network_manager.connect_to_server()
        self.ghost_type = self.network_manager.get_my_ghost()
    
    def _handle_special_keys(self):
        """Gerencia teclas especiais (menu, fullscreen, sair)."""
        keys = pygame.key.get_pressed()

        # Abre/fecha menu
        if keys[pygame.K_p]:
            self.menu_open = not self.menu_open
            pygame.time.wait(150)  # evita repeat de toggle

        # Tela cheia (F11)
        if keys[pygame.K_F11]:
            self.toggle_fullscreen()
            pygame.time.wait(150)

        # Sair
        if keys[pygame.K_ESCAPE] and self.menu_open:
            self.running = False

    def _handle_events(self):
        """Processa eventos do PyGame"""
        for event in pygame.event.get():
            
            if event.type == pygame.QUIT:
                self.running = False
                

            if event.type == pygame.KEYDOWN:
                if event.key in self.key_actions:
                    self.network_manager.send_input(self.key_actions[event.key])
   
    def toggle_fullscreen(self):
        """Alterna entre fullscreen e janela."""
        self.fullscreen = not self.fullscreen

        if self.fullscreen:
            pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        else:
            # volta ao modo janela calculado pelo setup_window
            self._setup_window()
        
        self._compute_offsets()

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

    def _compute_offsets(self):
        """
        Calcula o deslocamento (offset) para centralizar o mapa na janela.
        """
        window_w, window_h = self.screen.get_size()
        map_w = self.matrix.width() * self.tile_size
        map_h = self.matrix.height() * self.tile_size

        self.offset_x = (window_w - map_w) // 2
        self.offset_y = (window_h - map_h) // 2
 
    def _render(self):
        """Renderiza o jogo na tela."""
        self.screen.fill(BLACK)
        self.renderer.draw_matrix(self.matrix, self.tile_size, self.offset_x, self.offset_y)
        self.renderer.draw_entities(
                    visual_entities=self.visual_entities,
                    tile_size=self.tile_size,
                    ghost_sprites=self.ghost_sprites,
                    pacman_sprite=self.pacman_sprites[self.anim_frame[EntityType.PACMAN]],
                    entity_dirs=self.entity_dirs,
                    anim_frames=self.anim_frame,
                    offset_x=self.offset_x,
                    offset_y=self.offset_y
                )

        if self.menu_open:
            self.draw_menu()
            pygame.display.update()
            return
        self._draw_hud()
        pygame.display.update()

    def draw_menu(self):
        """Desenha o menu de pausa."""
        overlay = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))  # Fundo semitransparente
        self.screen.blit(overlay, (0, 0))

        lines = [
            "MENU DE OPÇÕES",
            "",
            f"Modo de Tela: {'Fullscreen' if self.fullscreen else 'Janela'}",
            "Pressione F11 para alternar",
            "",
            "Pressione ESC para sair do jogo",
            "Pressione P para continuar",
        ]

        y = 100
        for text in lines:
            rendered = self.font.render(text, True, (255, 255, 255))
            x = (self.screen.get_width() - rendered.get_width()) // 2
            self.screen.blit(rendered, (x, y))
            y += 40
     
    def _draw_hud(self):
        """
        Desenha o HUD:
        - Leaderboards (esquerda)
        - Pause (direita, topo)
        - Vidas do Pac-Man (abaixo do mapa)
        """

        WHITE = (255, 255, 255)

        # ============= LEADERBOARD (ESQUERDA) =============
        x_leader = 20
        y_leader = 20

        # Título
        label = self.font.render("Leaderboard", True, WHITE)
        self.screen.blit(label, (x_leader, y_leader))
        y_leader += 40

        # lista de fantasmas em ordem fixa
        ordered_ghosts = [
            EntityType.BLINKY,
            EntityType.PINKY,
            EntityType.INKY,
            EntityType.CLYDE
        ]

        ghost_names = {
            EntityType.BLINKY: "Blinky",
            EntityType.PINKY:  "Pinky",
            EntityType.INKY:   "Inky",
            EntityType.CLYDE:  "Clyde"
        }

        for ghost in ordered_ghosts:
            # pega sprite animado atual
            name = ghost.name.lower()
            direction = self.entity_dirs.get(ghost, "right")
            frame = self.anim_frame.get(ghost, 0) % 2
            sprite = self.ghost_sprites[name][direction][frame]
            sprite = pygame.transform.scale(sprite, (32, 32))

            self.screen.blit(sprite, (x_leader, y_leader))

            # nome + pontuação
            score = self.game_state.scores.get(ghost, 0)
            text = f"{ghost_names[ghost]}  {score}"
            text_surf = self.font.render(text, True, WHITE)
            self.screen.blit(text_surf, (x_leader + 40, y_leader + 5))

            y_leader += 45

        # ============= PAUSE (DIREITA) =============
        pause_text = self.font.render("Pause (P)", True, WHITE)
        pause_x = self.screen.get_width() - pause_text.get_width() - 20
        pause_y = 20
        self.screen.blit(pause_text, (pause_x, pause_y))

        # ============= VIDAS DO PAC-MAN (ABAIXO DO MAPA) =============

        # distância do mapa
        hud_space = 20
        bottom_y = self.offset_y + self.matrix.height() * self.tile_size + hud_space

        life_icon = pygame.transform.scale(self.pacman_sprites[0], (32, 32))

        lives = self.game_state.pacman_lives

        for i in range(lives):
            lx = self.offset_x + i * 40
            self.screen.blit(life_icon, (lx, bottom_y))

    def _draw_pacman_lives(self):
        lives = self.game_state.pacman_lives

        # posição inicial
        start_x = self.offset_x + 20
        start_y = self.offset_y + self.matrix.height() * self.tile_size + 20

        life_sprite = pygame.transform.scale(
            self.pacman_sprites[0],
            (self.tile_size, self.tile_size)
        )

        for i in range(lives):
            self.screen.blit(life_sprite, (start_x + i * (self.tile_size + 10), start_y))

    
    def run(self):
        """Loop principal do jogo"""
        while self.running:
            self.clock.tick(60)
            self._handle_events()
            self._handle_special_keys()
            self._update_game_state()
            # atualiza targets -> SmoothEntities já têm os destinos
            for entity in self.visual_entities.values():
                entity.update()
            self._update_animations()
            self._render()
        
        pygame.quit()