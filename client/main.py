# main.py (versão limpa e reorganizada)
import pygame
from client.game.game_engine import Game

def main():
    pygame.init()
    game = Game()
    game.run()

if __name__ == "__main__":
    main()