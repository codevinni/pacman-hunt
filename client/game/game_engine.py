# client/game/game_engine.py

from __future__ import annotations
import pygame
import time
from typing import Dict, Optional, Tuple, List
from os import *
from common.game_state import GameState
from common.enums import PlayerAction, EntityType, GameStatus
from client.game.config import *
from client.utils.sound_manager import *
from client.utils.smooth_entity import SmoothEntity
from client.utils.asset_loader import load_image, get_asset_path
from client.game.renderer import GameRenderer
from client.game.menu import GameMenu
from ..network.network_manager import NetworkManager

HUD_BOTTOM_HEIGHT = 80
NOTIFICATION_DURATION_MS = 5000


class Game:
    """
    Classe principal do cliente do jogo.
    """

    def __init__(self) -> None:
        """
        Inicializa pygame, janela, estados, assets, rede e renderizador.
        """
        pygame.init()
        self.game_state = GameState()
        self.matrix = self.game_state.matrix

        self.menu = GameMenu(self)
        self.menu_open = False
        self.fullscreen = False

        self._setup_window()

        self.font = pygame.font.Font(get_asset_path("fonts/Emulogic-zrEw.ttf"), 16)
        self.big_font = pygame.font.Font(get_asset_path("fonts/Emulogic-zrEw.ttf"), 48)

        # Smooth visual entities: pixel positions interpoladas
        self.visual_entities: Dict[EntityType, SmoothEntity] = {
            EntityType.PACMAN: SmoothEntity(14, 23, self.tile_size),
            EntityType.BLINKY: SmoothEntity(12, 14, self.tile_size),
            EntityType.INKY: SmoothEntity(13, 14, self.tile_size),
            EntityType.PINKY: SmoothEntity(14, 14, self.tile_size),
            EntityType.CLYDE: SmoothEntity(15, 14, self.tile_size),
        }

        # estados para animação e direção (por entidade)
        self.prev_grid: Dict[EntityType, Optional[Tuple[int, int]]] = {}
        self.entity_dirs: Dict[EntityType, str] = {}
        self.anim_frame: Dict[EntityType, int] = {}
        self.anim_timer: Dict[EntityType, int] = {}
        self.switch_interval = 250  # ms pacman frame switch
        self.init_entity_animation_state()

        # notificações (texto, end_timestamp_ms)
        self.notifications: List[Tuple[str, int]] = []

        # carrega sprites (pacman + fantasmas + frightened)
        self._load_assets()

        # rede
        self.network_manager = NetworkManager()
        self._setup_network()

        # renderer
        self.renderer = GameRenderer(self.screen)

        # Inicializa o gerenciador de som
        sounds_path = os.path.join(os.path.dirname(get_asset_path("sprites.png")), "..", "sounds")
        sounds_path = os.path.normpath(sounds_path)
        
        try:
            from client.game.sound_manager import SoundManager
            self.sound_manager = SoundManager(sounds_path, volume=0.7)
            print(f"Sistema de som inicializado com sucesso!")
        except Exception as e:
            print(f"Erro ao inicializar som: {e}")
            self.sound_manager = None
        # ========================

        # mapeamento de teclas -> PlayerAction
        self.key_actions = {
            pygame.K_UP: PlayerAction.UP,
            pygame.K_DOWN: PlayerAction.DOWN,
            pygame.K_LEFT: PlayerAction.LEFT,
            pygame.K_RIGHT: PlayerAction.RIGHT
        }

        self.clock = pygame.time.Clock()
        self.running = True

        # guarda scores anteriores para detectar mudanças
        self.previous_scores = dict(self.game_state.scores)
        self.pacman_lives = self.game_state.pacman_lives

    def _setup_window(self) -> None:
        """
        Cria a janela do pygame com espaço para HUD inferior e calcula offsets
        para centralizar o mapa.
        """
        info = pygame.display.Info()
        monitor_w = info.current_w
        monitor_h = info.current_h

        tiles_x = self.matrix.width()
        tiles_y = self.matrix.height()

        # escolhe tile_size considerando HUD na vertical
        self.tile_size = min(monitor_w // tiles_x, (monitor_h - HUD_BOTTOM_HEIGHT) // tiles_y)
        map_w = tiles_x * self.tile_size
        map_h = tiles_y * self.tile_size

        # usamos toda largura do monitor e altura suficiente para mapa + HUD
        self.screen = pygame.display.set_mode((monitor_w, map_h + HUD_BOTTOM_HEIGHT))
        pygame.display.set_caption("Pac-Man Hunt")

        self._compute_offsets()

    def _compute_offsets(self) -> None:
        """
        Calcula offset_x e offset_y para centralizar o mapa dentro da janela.
        Também calcula hud_y (topo do HUD inferior).
        """
        window_w, window_h = self.screen.get_size()
        map_w = self.matrix.width() * self.tile_size
        map_h = self.matrix.height() * self.tile_size

        # centralizar horizontalmente
        self.offset_x = (window_w - map_w) // 2
        # centralizar verticalmente considerando HUD embaixo
        self.offset_y = (window_h - (map_h + HUD_BOTTOM_HEIGHT)) // 2
        # posição Y onde começa o HUD inferior
        self.hud_y = self.offset_y + map_h

    def _load_assets(self) -> None:
        """
        Carrega o spritesheet e corta sprites do Pac-Man e dos fantasmas.
        Estrutura do spritesheet (conforme definido):
         - Pac-Man: linhas 0..3 (direita, esquerda, up, down) colunas 0..1
         - Fantasmas: linhas 4..7 (cada fantasma por linha) colunas 0..7 (direções)
         - Frightened blue/blink: linhas 4, colunas 8..11 (ou como definido)
        """
        sheet = load_image(get_asset_path("sprites.png"))

        # Pac-Man: linhas 0 (direita),1 (left),2 (up),3 (down); cada linha col 0 e 1
        self.pacman_sprites: Dict[str, List[pygame.Surface]] = {
            "right": [
                sheet.subsurface(pygame.Rect(0 * LARGURA_SPRITE, 0 * ALTURA_SPRITE, LARGURA_SPRITE, ALTURA_SPRITE)).copy(),
                sheet.subsurface(pygame.Rect(1 * LARGURA_SPRITE, 0 * ALTURA_SPRITE, LARGURA_SPRITE, ALTURA_SPRITE)).copy()
            ],
            "left": [
                sheet.subsurface(pygame.Rect(0 * LARGURA_SPRITE, 1 * ALTURA_SPRITE, LARGURA_SPRITE, ALTURA_SPRITE)).copy(),
                sheet.subsurface(pygame.Rect(1 * LARGURA_SPRITE, 1 * ALTURA_SPRITE, LARGURA_SPRITE, ALTURA_SPRITE)).copy()
            ],
            "up": [
                sheet.subsurface(pygame.Rect(0 * LARGURA_SPRITE, 2 * ALTURA_SPRITE, LARGURA_SPRITE, ALTURA_SPRITE)).copy(),
                sheet.subsurface(pygame.Rect(1 * LARGURA_SPRITE, 2 * ALTURA_SPRITE, LARGURA_SPRITE, ALTURA_SPRITE)).copy()
            ],
            "down": [
                sheet.subsurface(pygame.Rect(0 * LARGURA_SPRITE, 3 * ALTURA_SPRITE, LARGURA_SPRITE, ALTURA_SPRITE)).copy(),
                sheet.subsurface(pygame.Rect(1 * LARGURA_SPRITE, 3 * ALTURA_SPRITE, LARGURA_SPRITE, ALTURA_SPRITE)).copy()
            ],
        }
        # Pacman sprite default (frame 0, right)
        self.pacman_sprite = self.pacman_sprites["right"][0]

        # Fantasmas: assumimos linhas 4..7 seguem blinky,pinky,inky,clyde com colunas:
        # right cols 0-1, left cols 2-3, up cols 4-5, down cols 6-7
        GHOST_SHEET_LINE = {"blinky": 4, "pinky": 5, "inky": 6, "clyde": 7}
        self.ghost_sprites: Dict[str, Dict[str, List[pygame.Surface]]] = {}
        for name, row in GHOST_SHEET_LINE.items():
            self.ghost_sprites[name] = {
                "right": [
                    sheet.subsurface(pygame.Rect(0 * LARGURA_SPRITE, row * ALTURA_SPRITE, LARGURA_SPRITE, ALTURA_SPRITE)).copy(),
                    sheet.subsurface(pygame.Rect(1 * LARGURA_SPRITE, row * ALTURA_SPRITE, LARGURA_SPRITE, ALTURA_SPRITE)).copy()
                ],
                "left": [
                    sheet.subsurface(pygame.Rect(2 * LARGURA_SPRITE, row * ALTURA_SPRITE, LARGURA_SPRITE, ALTURA_SPRITE)).copy(),
                    sheet.subsurface(pygame.Rect(3 * LARGURA_SPRITE, row * ALTURA_SPRITE, LARGURA_SPRITE, ALTURA_SPRITE)).copy()
                ],
                "up": [
                    sheet.subsurface(pygame.Rect(4 * LARGURA_SPRITE, row * ALTURA_SPRITE, LARGURA_SPRITE, ALTURA_SPRITE)).copy(),
                    sheet.subsurface(pygame.Rect(5 * LARGURA_SPRITE, row * ALTURA_SPRITE, LARGURA_SPRITE, ALTURA_SPRITE)).copy()
                ],
                "down": [
                    sheet.subsurface(pygame.Rect(6 * LARGURA_SPRITE, row * ALTURA_SPRITE, LARGURA_SPRITE, ALTURA_SPRITE)).copy(),
                    sheet.subsurface(pygame.Rect(7 * LARGURA_SPRITE, row * ALTURA_SPRITE, LARGURA_SPRITE, ALTURA_SPRITE)).copy()
                ],
            }

        # Frightened sprites (azul and blink) assume row 4 (shared) and cols 8,9 / 10,11
        try:
            row_fb = 4
            self.frightened_blue = [
                sheet.subsurface(pygame.Rect(8 * LARGURA_SPRITE, row_fb * ALTURA_SPRITE, LARGURA_SPRITE, ALTURA_SPRITE)).copy(),
                sheet.subsurface(pygame.Rect(9 * LARGURA_SPRITE, row_fb * ALTURA_SPRITE, LARGURA_SPRITE, ALTURA_SPRITE)).copy()
            ]
            self.frightened_blink = [
                sheet.subsurface(pygame.Rect(10 * LARGURA_SPRITE, row_fb * ALTURA_SPRITE, LARGURA_SPRITE, ALTURA_SPRITE)).copy(),
                sheet.subsurface(pygame.Rect(11 * LARGURA_SPRITE, row_fb * ALTURA_SPRITE, LARGURA_SPRITE, ALTURA_SPRITE)).copy()
            ]
        except Exception:
            # fallback: duplicate blinky sprite so renderer has something
            self.frightened_blue = [self.ghost_sprites["blinky"]["left"][0]] * 2
            self.frightened_blink = [self.ghost_sprites["blinky"]["left"][0]] * 2

    def _setup_network(self) -> None:
        """
        Conecta ao servidor e tenta obter o fantasma atribuído a este cliente.
        """
        try:
            self.network_manager.connect_to_server()
            self.ghost_type = self.network_manager.get_my_ghost()
        except Exception:
            self.ghost_type = None

    def _handle_special_keys(self) -> None:
        """
        Trata teclas especiais: P para menu, F11 para fullscreen, ESC para sair (quando em menu).
        """
        keys = pygame.key.get_pressed()
        if keys[pygame.K_p]:
            self.menu_open = not self.menu_open
            pygame.time.wait(150)
        if keys[pygame.K_F11]:
            self.toggle_fullscreen()
            pygame.time.wait(150)
        if keys[pygame.K_ESCAPE] and self.menu_open:
            self.running = False

    def _handle_events(self) -> None:
        """
        Captura eventos do pygame e envia inputs de movimento ao servidor.
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            if event.type == pygame.KEYDOWN:
                if event.key in self.key_actions:
                    try:
                        self.network_manager.send_input(self.key_actions[event.key])
                    except Exception:
                        pass

    def toggle_fullscreen(self) -> None:
        """
        Alterna entre fullscreen e modo janela e recalcula offsets.
        """
        self.fullscreen = not self.fullscreen
        info = pygame.display.Info()
        if self.fullscreen:
            self.screen = pygame.display.set_mode((info.current_w, info.current_h), pygame.FULLSCREEN)
        else:
            self._setup_window()
        self._compute_offsets()

    def init_entity_animation_state(self) -> None:
        """
        Inicializa estados de animação/direção/temporizadores para todas entidades.
        """
        ENTITIES = (EntityType.PACMAN, EntityType.BLINKY, EntityType.INKY, EntityType.PINKY, EntityType.CLYDE)
        now = pygame.time.get_ticks()
        for entity in ENTITIES:
            try:
                pos = self.matrix.get_entity_position(entity)
            except Exception:
                pos = None
            self.prev_grid[entity] = (pos[0], pos[1]) if pos else None
            self.entity_dirs[entity] = "right"
            self.anim_frame[entity] = 0
            self.anim_timer[entity] = now

    def _update_animations(self) -> None:
        """
        Atualiza frames de animação (Pac-Man e fantasmas) baseado em temporizadores locais.
        """
        now = pygame.time.get_ticks()
        if now - self.anim_timer.get(EntityType.PACMAN, 0) >= self.switch_interval:
            self.anim_frame[EntityType.PACMAN] ^= 1
            # atualiza pacman_sprite para o frame atual baseado na direção
            dir_name = self.entity_dirs.get(EntityType.PACMAN, "right")
            self.pacman_sprite = self.pacman_sprites.get(dir_name, self.pacman_sprites["right"])[self.anim_frame[EntityType.PACMAN]]
            self.anim_timer[EntityType.PACMAN] = now

        for et in (EntityType.BLINKY, EntityType.INKY, EntityType.PINKY, EntityType.CLYDE):
            if now - self.anim_timer.get(et, 0) >= 180:
                self.anim_frame[et] ^= 1
                self.anim_timer[et] = now

def _update_game_state(self) -> None:
    """
    Recebe o GameState do servidor, atualiza a matriz local,
    sincroniza SmoothEntity targets e detecta mudanças de score/vidas
    para notificar o jogador.
    """
    try:
        new_state = self.network_manager.get_game_state()
    except Exception:
        new_state = None

    if not new_state:
        return

    self.game_state = new_state
    self.matrix = new_state.matrix

    game_reseted = self.game_state.pacman_lives > self.pacman_lives
    
    # detecta mudanças de pontuação e cria notificação
    for ghost, score in self.game_state.scores.items():
        old = self.previous_scores.get(ghost, 0)
        if score != old and not game_reseted:
            diff = score - old
            if diff > 0:
                self._push_notification(f"O fantasma {ghost.name.title()} eliminou o pacman")
                # ===== SOM DE MORTE DO PACMAN =====
                if self.sound_manager:
                    self.sound_manager.play_death()
                # ==================================
            else:
                self._push_notification(f"{ghost.name.title()} foi eliminado")
                # ===== SOM DE COMER FANTASMA =====
                if self.sound_manager:
                    self.sound_manager.play_eat_ghost()
                # =================================
            
    self.previous_scores = dict(self.game_state.scores)
    
    # detecta mudança de vidas do pacman
    if self.game_state.pacman_lives != self.pacman_lives:
        if self.game_state.pacman_lives < self.pacman_lives:
            self._push_notification(f"Pac-Man eliminado - Vidas restantes: {self.game_state.pacman_lives}")
            # ===== SOM DE MORTE =====
            if self.sound_manager:
                self.sound_manager.play_death()
            # ========================
        self.pacman_lives = self.game_state.pacman_lives

    # sincroniza targets e calcula direções por delta entre grids
    for ent_type, smooth in list(self.visual_entities.items()):
        try:
            grid_pos = self.matrix.get_entity_position(ent_type)
        except Exception:
            grid_pos = None

        if grid_pos:
            gx, gy = grid_pos[0], grid_pos[1]
            prev = self.prev_grid.get(ent_type)
            if prev is not None:
                ox, oy = prev
                dx = gx - ox
                dy = gy - oy
                if dx == 0 and dy == 0:
                    pass
                else:
                    if abs(dx) >= abs(dy):
                        self.entity_dirs[ent_type] = "right" if dx > 0 else "left"
                    else:
                        self.entity_dirs[ent_type] = "down" if dy > 0 else "up"
            self.prev_grid[ent_type] = (gx, gy)
            try:
                smooth.update_target(gx, gy)
            except Exception:
                self.visual_entities[ent_type] = SmoothEntity(gx, gy, self.tile_size)

    def _push_notification(self, text: str, duration_ms: int = NOTIFICATION_DURATION_MS) -> None:
        """
        Adiciona uma notificação textual que será exibida no topo por duration_ms.
        """
        end = pygame.time.get_ticks() + duration_ms
        self.notifications.append((text, end))

    def _draw_notifications(self) -> None:
        """
        Desenha notificações ativas no topo central com fundo preto semitransparente.
        """
        now = pygame.time.get_ticks()
        active: List[Tuple[str, int]] = []
        center_x = self.screen.get_width() // 2
        y = 20
        padding_x = 12
        padding_y = 6
        for msg, end in self.notifications:
            if end >= now:
                surf = self.font.render(msg, True, (255, 255, 255))
                rect_w = surf.get_width() + padding_x * 2
                rect_h = surf.get_height() + padding_y * 2
                rect_x = center_x - rect_w // 2
                rect_y = y
                overlay = pygame.Surface((rect_w, rect_h), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 180))
                self.screen.blit(overlay, (rect_x, rect_y))
                self.screen.blit(surf, (rect_x + padding_x, rect_y + padding_y))
                y += rect_h + 6
                active.append((msg, end))
        self.notifications = active

    def _draw_hud(self) -> None:
        """
        Desenha leaderboard no canto esquerdo, 'Pause (P)' no topo direito,
        e as vidas do Pac-Man centralizadas abaixo do mapa.
        """
        WHITE = (255, 255, 255)
        x_leader = 20
        y_leader = 20
        self.screen.blit(self.font.render("Leaderboard", True, WHITE), (x_leader, y_leader))
        y_leader += 40

        ordered_ghosts = [EntityType.BLINKY, EntityType.PINKY, EntityType.INKY, EntityType.CLYDE]
        ghost_names = {
            EntityType.BLINKY: "Blinky",
            EntityType.PINKY: "Pinky",
            EntityType.INKY: "Inky",
            EntityType.CLYDE: "Clyde"
        }

        for ghost in ordered_ghosts:
            name = ghost.name.lower()
            direction = self.entity_dirs.get(ghost, "right")
            frame = self.anim_frame.get(ghost, 0) % 2
            sprite = self.ghost_sprites.get(name, {}).get(direction, [None, None])[frame]
            if sprite:
                sprite_s = pygame.transform.scale(sprite, (32, 32))
                self.screen.blit(sprite_s, (x_leader, y_leader))
            score = self.game_state.scores.get(ghost, 0)
            text = f"{ghost_names[ghost]}  {score}"
            text_surf = self.font.render(text, True, WHITE)
            self.screen.blit(text_surf, (x_leader + 40, y_leader + 5))
            y_leader += 45

        # Pause label
        pause_text = self.font.render("Pause (P)", True, WHITE)
        self.screen.blit(pause_text, (self.screen.get_width() - pause_text.get_width() - 20, 20))

        # notificações no topo
        self._draw_notifications()

        # vidas do Pac-Man (centralizado na área HUD inferior)
        self._draw_pacman_lives()

    def _draw_pacman_lives(self) -> None:
        """
        Desenha ícones das vidas do Pac-Man centralizados na área do HUD inferior.
        """
        lives = self.game_state.pacman_lives
        if lives <= 0:
            return

        life_size = 32
        life_sprite = pygame.transform.scale(self.pacman_sprites["right"][0], (life_size, life_size))
        spacing = 10
        total_width = lives * life_size + (lives - 1) * spacing
        start_x = (self.screen.get_width() - total_width) // 2
        start_y = self.hud_y + (HUD_BOTTOM_HEIGHT - life_size) // 2
        for i in range(lives):
            self.screen.blit(life_sprite, (start_x + i * (life_size + spacing), start_y))

    def _draw_victory_screen(self) -> None:
        """
        Desenha overlay de vitória com o vencedor (Pac-Man ou fantasma vencedor).
        """
        w, h = self.screen.get_size()
        overlay = pygame.Surface((w, h), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        self.screen.blit(overlay, (0, 0))
        last_y = 1

        if self.game_state.status == GameStatus.PACMAN_VICTORY:
            pac = pygame.transform.scale(self.pacman_sprites["right"][0], (128, 128))
            x = (w - pac.get_width()) // 2
            y = h // 3 - pac.get_height() // 2
            self.screen.blit(pac, (x, y))
            text = self.big_font.render("O pac man venceu", True, (255, 230, 0))
            tx = (w - text.get_width()) // 2
            ty = y + pac.get_height() + 20
            self.screen.blit(text, (tx, ty))

            last_y = ty + text.get_height()

        elif self.game_state.status == GameStatus.GHOSTS_VICTORY:
            winner = self.game_state.winner
            if isinstance(winner, EntityType):
                text = self.big_font.render(f"O fantasma {winner.name.title()} venceu", True, (255, 100, 100))
            else:
                text = self.big_font.render("Os fantasmas venceram", True, (255, 100, 100))
            tx = (w - text.get_width()) // 2
            ty = h // 2 - text.get_height() // 2
            self.screen.blit(text, (tx, ty))

            last_y = ty + text.get_height() # Obter posicionamento y final do texto de vitório

        restart_timer = self.game_state.restart_game_timer
        if restart_timer < self.game_state.RESTARTING_GAME_TIME:

            restart_msg  = self.font.render("Reiniciando jogo...", True, (255, 255, 255))

            pos_x = (w - restart_msg.get_width()) // 2
            pos_y = last_y + 40

            self.screen.blit(restart_msg, (pos_x, pos_y))

    def _render(self) -> None:
        """
        Renderiza mapa, entidades, HUD, menu e telas (menu/vitória).
        """
        self.screen.fill(BLACK)
        # desenha mapa
        self.renderer.draw_matrix(self.matrix, self.tile_size, self.offset_x, self.offset_y)
        # desenha entidades (passa pacman_sprite já animado/direction-aware)
        self.renderer.draw_entities(
            visual_entities=self.visual_entities,
            tile_size=self.tile_size,
            ghost_sprites=self.ghost_sprites,
            pacman_sprite=self.pacman_sprite,
            entity_dirs=self.entity_dirs,
            anim_frames=self.anim_frame,
            game_state=self.game_state,
            offset_x=self.offset_x,
            offset_y=self.offset_y,
            frightened_blue=self.frightened_blue,
            frightened_blink=self.frightened_blink
        )

        if self.menu_open:
            self.draw_menu()
        else:
            self._draw_hud()

        if self.game_state.status in (GameStatus.PACMAN_VICTORY, GameStatus.GHOSTS_VICTORY):
            self._draw_victory_screen()

        pygame.display.update()

    def draw_menu(self) -> None:
        """
        Desenha menu de pausa (overlay com opções).
        """
        overlay = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        lines = [
            "CONFIGURACOES",
            "Pressione P para continuar",
            f"Modo de Tela: {'Fullscreen' if self.fullscreen else 'Janela'}",
            "Pressione F11 para alternar modo de tela",
            "Pressione ESC para sair do jogo"
        ]
        y = 100
        for line in lines:
            text = self.font.render(line, True, (255, 255, 255))
            x = (self.screen.get_width() - text.get_width()) // 2
            self.screen.blit(text, (x, y))
            y += 40

        def _update_sounds(self) -> None:
            if not self.sound_manager:
                return
            
            # Se o jogo acabou de começar (primeira vez que game_state tem status RUNNING)
            if not hasattr(self, '_game_started_sound_played'):
                self._game_started_sound_played = False
            
            # Toca som de início apenas uma vez
            if self.game_state.status == GameStatus.RUNNING and not self._game_started_sound_played:
                self.sound_manager.play_start()
                self._game_started_sound_played = True
            
            # Modo Frightened
            if self.game_state.is_frightened_mode():
                if not hasattr(self, '_frightened_active') or not self._frightened_active:
                    self.sound_manager.play_eat_power_pellet()
                    self._frightened_active = True
            else:
                if hasattr(self, '_frightened_active') and self._frightened_active:
                    self.sound_manager.stop_fright_mode()
                    self._frightened_active = False
            
            # Toca sirene se o jogo está rodando e não está em frightened
            if self.game_state.status == GameStatus.RUNNING and not self.game_state.is_frightened_mode():
                # Calcula o nível da sirene baseado em dots restantes (opcional)
                # Por enquanto usa nível 0
                self.sound_manager.play_siren(level=0)


    def run(self) -> None:
        """
        Loop principal do cliente.
        """
        while self.running:

            self.clock.tick(60)
            self._handle_events()
            self._handle_special_keys() 
            self._update_game_state()

            for entity in self.visual_entities.values():
                entity.update()

            self._update_animations()
            self._update_sounds() 

            self._render()
            if self.sound_manager:
                self.sound_manager.cleanup()
        pygame.quit()
