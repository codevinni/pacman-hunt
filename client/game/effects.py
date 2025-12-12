# game/effects.py
import pygame

class AnimationManager:
    """Gerencia todas as animações do jogo"""
    
    def __init__(self, screen, font_path):
        self.screen = screen
        self.font_path = font_path
        self.active_effects = []
        self.ghost_fright_active = False
        self.ghost_fright_timer = 0
        self.ghost_fright_duration = 300  # 5 segundos a 60 FPS
        self.blinking_phase = False
        
        # Estado do jogo
        self.game_started = False
        self.start_timer = 0
        self.start_duration = 90  # 1.5 segundos
        
        # Morte do Pac-Man
        self.death_text = None
        self.death_timer = 0
        self.death_duration = 120  # 2 segundos
        
        # Vitória
        self.victory_animation = None
        self.victory_timer = 0
        self.victory_duration = 300  # 5 segundos (5 piscadas de 1 segundo cada)
    
    def update(self):
        """Atualiza todas as animações"""
        # Atualiza timer do susto dos fantasmas
        if self.ghost_fright_active:
            self.ghost_fright_timer -= 1
            if self.ghost_fright_timer <= 0:
                self.ghost_fright_active = False
            else:
                # Alterna entre azul e branco nos últimos 30% do tempo
                if self.ghost_fright_timer < self.ghost_fright_duration * 0.3:
                    self.blinking_phase = (self.ghost_fright_timer // 10) % 2 == 0
        
        # Atualiza animação de início
        if not self.game_started:
            self.start_timer += 1
            if self.start_timer >= self.start_duration:
                self.game_started = True
        
        # Atualiza animação de morte
        if self.death_text:
            self.death_timer += 1
            if self.death_timer >= self.death_duration:
                self.death_text = None
        
        # Atualiza animação de vitória
        if self.victory_animation:
            self.victory_timer += 1
            # Para após 5 piscadas completas
            if self.victory_timer >= self.victory_duration:
                self.victory_animation = None
    
    def activate_ghost_fright(self):
        """Ativa o modo de susto dos fantasmas"""
        self.ghost_fright_active = True
        self.ghost_fright_timer = self.ghost_fright_duration
        self.blinking_phase = False
    
    def get_ghost_sprite_index(self):
        """
        Retorna o índice do sprite para fantasmas assustados
        Returns: 'blue' para azul, 'white' para branco, None para normal
        """
        if not self.ghost_fright_active:
            return None
        
        if self.blinking_phase:
            return 'white'  # Branco (piscando)
        else:
            return 'blue'   # Azul
    
    def show_start_text(self):
        """Mostra texto START no início do jogo"""
        self.game_started = False
        self.start_timer = 0
    
    def show_death_text(self, ghost_name, points):
        """Mostra texto quando Pac-Man morre"""
        self.death_text = f"O fantasma {ghost_name} pontou: +{points}"
        self.death_timer = 0
    
    def show_victory(self, winner_type, winner_name, winner_sprite):
        """Mostra animação de vitória"""
        self.victory_animation = {
            'type': winner_type,
            'name': winner_name,
            'sprite': winner_sprite
        }
        self.victory_timer = 0
    
    def draw_effects(self, offset_x=0, offset_y=0):
        """Desenha todos os efeitos visuais na tela"""
        screen_w, screen_h = self.screen.get_size()
        
        # Texto START
        if not self.game_started:
            font = pygame.font.Font(self.font_path, 48)
            text = font.render("START", True, (255, 255, 255))
            
            # Calcula alpha (fade out nos últimos 30 frames)
            alpha = 255
            if self.start_timer > self.start_duration - 30:
                alpha = int(255 * (1 - (self.start_timer - (self.start_duration - 30)) / 30))
            
            text.set_alpha(alpha)
            text_rect = text.get_rect(center=(screen_w // 2, screen_h // 2))
            self.screen.blit(text, text_rect)
        
        # Texto de morte
        if self.death_text:
            font = pygame.font.Font(self.font_path, 24)
            text = font.render(self.death_text, True, (255, 255, 255))
            
            # Fade out
            alpha = 255
            if self.death_timer > self.death_duration - 30:
                alpha = int(255 * (1 - (self.death_timer - (self.death_duration - 30)) / 30))
            
            text.set_alpha(alpha)
            text_rect = text.get_rect(center=(screen_w // 2, offset_y + screen_h // 2 + 100))
            self.screen.blit(text, text_rect)
        
        # Animação de vitória
        if self.victory_animation:
            # Determina o texto
            if self.victory_animation['type'] == 'pacman':
                victory_text = "VITÓRIA DO PAC-MAN"
            else:
                victory_text = f"VITÓRIA DO {self.victory_animation['name'].upper()}"
            
            # Fonte grande
            big_font = pygame.font.Font(self.font_path, 72)
            
            # Alterna entre amarelo e branco (5 piscadas = 10 alternâncias de 0.5s cada)
            # Cada piscada completa: 1 segundo (0.5s amarelo, 0.5s branco)
            color_phase = (self.victory_timer // 30) % 2  # Muda a cada 0.5 segundos (30 frames)
            color = (255, 255, 0) if color_phase == 0 else (255, 255, 255)  # Amarelo/Branco
            
            # Renderiza texto
            text = big_font.render(victory_text, True, color)
            text_rect = text.get_rect(center=(screen_w // 2, screen_h // 2 - 50))
            self.screen.blit(text, text_rect)
            
            # Desenha sprite do vencedor
            if self.victory_animation['sprite']:
                sprite_rect = self.victory_animation['sprite'].get_rect(center=(screen_w // 2, screen_h // 2 + 50))
                self.screen.blit(self.victory_animation['sprite'], sprite_rect)