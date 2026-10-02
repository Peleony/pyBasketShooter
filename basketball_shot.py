import sys
import math
import pygame

WIDTH, HEIGHT = 1000, 600
FPS = 60


#Physic constants
GRAVITY = 0.38
AIR_RESISTANCE = 0.998
FLOOR_Y = HEIGHT - 60


class BasketballGame:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Basketball Shot Game")
        self.clock = pygame.time.Clock()

        # Basket properties
        self.floor_y = HEIGHT - 60
        self.board_x = WIDTH - 120
        self.board_y = 160
        self.board_w = 12
        self.board_h = 130

        self.rim_y = self.board_y + 90
        self.rim_left = self.board_x - 70
        self.rim_right = self.board_x - 5
        self.rim_thickness = 5

        #Game state

        #Ball starting position

        #Mouse drag state

    def reset_ball(self):

    def handle_events(self):
        for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()

    def update_physics(self):

    def draw_hoop(self):

    def draw_ball(self):

    def draw_aim_line(self):

    def draw_ui(self):

    def run(self):
        while True:
            self.handle_events()
            self.update_physics()

            self.screen.fill((COLOR_BG))
            self.draw_ui()
            self.draw_hoop()
            self.draw_aim_line()
            self.draw_ball()

            pygame.display.flip()
            self.clock.tick(FPS)


if __name__ == "__main__":
    game = BasketballGame()
    game.run()
