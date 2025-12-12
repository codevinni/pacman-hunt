import pygame

class GameMenu:
    def __init__(self, game):
        self.game = game
        self.active = False
        self.options = [
            "Alternar modo de tela",
            "Sair do jogo"
        ]

        self.selected = 0

    def toggle(self):
        self.active = not self.active

    def update(self, events):
        if not self.active:
            return

        for ev in events:
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_UP:
                    self.selected = (self.selected - 1) % len(self.options)

                elif ev.key == pygame.K_DOWN:
                    self.selected = (self.selected + 1) % len(self.options)

                elif ev.key == pygame.K_RETURN:
                    # Executar ação
                    if self.selected == 0:
                        self.game.toggle_fullscreen()
                    elif self.selected == 1:
                        self.game.running = False

    def draw(self, surf):
        if not self.active:
            return

        w, h = surf.get_size()

        # fundo escuro
        shade = pygame.Surface((w, h), pygame.SRCALPHA)
        shade.fill((0, 0, 0, 180))
        surf.blit(shade, (0, 0))

        # renderiza opções
        y = h // 2 - 60

        for i, text in enumerate(self.options):
            color = (255, 255, 0) if i == self.selected else (255, 255, 255)
            label = self.font.render(text, True, color)
            surf.blit(label, (w // 2 - label.get_width() // 2, y))
            y += 40
            


import pygame