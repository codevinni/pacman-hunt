import pygame 

# Classe de buffer para controlar movimentos
# -----------------------------------------------------------
# O fantasma estava se movendo na velocidade que você aperta a tecla enquanto pacman tinha velocidade fixa.
# Com o buffer aplicado, os dois estão a 180ms como no jogo original
# -----------------------------------------------------------

class MovementBuffer:
    def __init__(self, interval=180):
        self.interval = interval
        self.last_move = pygame.time.get_ticks()
        self.queued_move = None
    
    def queue_move(self, dx, dy):
        # -----------------------------------------------------------
        # Põe o movimento no buffer
        # -----------------------------------------------------------
        self.queued_move = (dx, dy)
    
    def try_execute(self, matrix, entity_type):
        # -----------------------------------------------------------
        # Executa se o intervalo já passou
        # -----------------------------------------------------------
        current_time = pygame.time.get_ticks()
        if self.queued_move and current_time - self.last_move >= self.interval:
            dx, dy = self.queued_move
            matrix.move_entity(entity_type, dx, dy)
            self.queued_move = None
            self.last_move = current_time
            return True
        return False

