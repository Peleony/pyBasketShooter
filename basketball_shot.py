import sys
import math
import pygame

# Screen
WIDTH, HEIGHT = 1000, 600
FPS = 60

#Colors
COLOR_BG = (28, 30, 38)
COLOR_FLOOR = (194, 133, 76)
COLOR_BALL = (224, 90, 36)
COLOR_BALL_SEAMS = (40, 20, 10)
COLOR_HOOP = (210, 50, 20)
COLOR_BOARD = (230, 230, 230)
COLOR_NET = (200, 200, 200)
COLOR_AIM = (255, 215, 0)
COLOR_TEXT = (240, 240, 240)

#Physic constants
GRAVITY = 0.38
AIR_RESISTANCE = 0.998
BOUNCE_RESTITUTION = 0.72
FLOOR_Y = HEIGHT - 60


class BasketballGame:

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Basketball Shot Game")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Consolas", 20, bold=True)
        self.big_font = pygame.font.SysFont("Consolas", 42, bold=True)

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
        self.score = 0
        self.streak = 0
        self.scored_this_shot = False
        self.feedback_text = ""
        self.feedback_timer = 0

        #Ball starting position
        self.spawn_pos = (180, self.floor_y - 20)
        self.reset_ball()

        #Mouse drag state
        self.is_dragging = False
        self.drag_start = (0, 0)


    def reset_ball(self):
         self.ball_x, self.ball_y = self.spawn_pos
         self.ball_vx = 0.0
         self.ball_vy = 0.0
         self.ball_radius = 18
         self.ball_angel = 0.0
         self.is_in_air = False
         self.scored_this_shot = False


    def handle_events(self):
        for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()

                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_r:
                            self.streak = 0
                            self.reset_ball()

                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        if event.button == 1:  # Left mouse button
                            mx, my = pygame.mouse.get_pos()
                            dist = math.hypot(mx - self.ball_x, my - self.ball_y)
                            if dist <= self.ball_radius * 2.5:
                                self.is_dragging = True
                                self.drag_start = (mx, my)

                    elif event.type == pygame.MOUSEBUTTONUP:
                         if event.button == 1 and self.is_dragging:
                            mx, my = pygame.mouse.get_pos()
                            dx = self.drag_start[0] - mx
                            dy = self.drag_start[1] - my

                            force_multiplier = 0.16
                            self.ball_vx = dx * force_multiplier
                            self.ball_vy = dy * force_multiplier

                            speed = math.hypot(self.ball_vx, self.ball_vy)
                            if speed > 22.0:
                                 scale = 22.0 / speed
                                 self.ball_vx *= scale
                                 self.ball_vy *= scale

                            if speed > 0.5:
                                self.is_in_air = True
                            self.is_dragging = False


    def update_physics(self):
        if not self.is_in_air:
            return

        #Gravity and air resistance
        self.ball_vy += GRAVITY
        self.ball_vx *= AIR_RESISTANCE
        self.ball_vy *= AIR_RESISTANCE

        self.ball_x += self.ball_vx
        self.ball_y += self.ball_vy
        self.ball_angel += self.ball_vx * 2.0

        # Floor collision
        if self.ball_y + self.ball_radius >= self.floor_y:
            self.ball_y = self.floor_y - self.ball_radius
            self.ball_vy *= -self.ball_vy * BOUNCE_RESTITUTION
            self.ball_vx *= 0.85
            if abs(self.ball_vy) < 1.0:
                self.ball_vy = 0

        #Board collision
        if (
            self.board_y <= self.ball_y <= self.board_y + self.board_h
            and self.ball_x + self.ball_radius >= self.board_x
            and self.ball_x - self.ball_radius <= self.board_x + self.board_w
        ):
            self.ball_x = self.board_x - self.ball_radius
            self.ball_vx = -self.ball_vx * BOUNCE_RESTITUTION

        # Rim collision
        rim_points = [
            (self.rim_left, self.rim_y),
            (self.rim_right, self.rim_y),
        ]
        for px, py in rim_points:
            dist = math.hypot(self.ball_x - px, self.ball_radius - py)
            if dist < self.ball_radius + self.rim_thickness:

                overlap = (self.ball_radius + self.rim_thickness) - dist
                nx = (self.ball_x - px) / (dist or 1)
                ny = (self.ball_y - py) / (dist or 1)

                self.ball_x += nx * overlap
                self.ball_y += ny * overlap
                dot = self.ball_vx * nx + self.ball_vy * ny
                self.ball_vx = (
                    self.ball_vx -2 * dot * nx
                ) * BOUNCE_RESTITUTION
                self.ball_vy = (
                    self.ball_vy -2 * dot * ny
                ) * BOUNCE_RESTITUTION

        #Shot in detection
        hoop_min_x = self.rim_left + 6
        hoop_max_x = self.rim_right - 6
        if (
            hoop_min_x <= self.ball_x <= hoop_max_x
            and abs(self.ball_y - self.rim_y) <= 10
            and self.ball_vy > 1.2
            and not self.scored_this_shot
        ):
            self.score += 1
            self.streak += 1
            self.scored_this_shot = True
            self.feedback_text = (
                f"SWISH! (+1)  STREAK: {self.streak}"
                if abs(self.ball_vx) < 3
                else f"BUCKET! (+1)  STREAK: {self.streak}"
            )
            self.feedback_timer = FPS * 2

        # Reset ball if out or stopped
        if (
            self.ball_x > WIDTH + 50
            or self.ball_x < -50
            or (self.ball_y >= self.floor_y - self.ball_radius - 1 and abs(self.ball_vx) < 0.2 and abs(self.ball_vy) < 0.2)
        ):
            if not self.scored_this_shot and self.is_in_air:
                self.streak = 0
            self.reset_ball()

    def draw_hoop(self):
         #Pole
        pygame.draw.rect(
            self.screen,
            (80, 80, 85),
            (self.board_x + 10, self.board_y + 40, 18, HEIGHT - self.board_y),
        )
        #Backboard
        pygame.draw.rect(
            self.screen,
            (80, 80, 85),
            (self.board_x, self.board_y, self.board_w, self.board_h),
            border_radius=3
        )
        #Board square
        pygame.draw.rect(
            self.screen,
            (180, 30, 30),
            (self.board_x - 1, self.board_y + 60, 4, 40),
         )
        #Net
        net_points = [
            (self.rim_left + 4, self.rim_y),
            (self.rim_right - 4, self.rim_y),
            (self.rim_right - 14, self.rim_y + 45),
            (self.rim_left + 14, self.rim_y + 45),
        ]
        pygame.draw.polygon(self.screen, COLOR_NET, net_points, width=2)
        pygame.draw.line(
            self.screen,
            COLOR_NET,
            (self.rim_left + 18, self.rim_y),
            (self.rim_right - 24, self.rim_y + 45),
            1,
        )
        pygame.draw.line(
            self.screen,
            COLOR_NET,
            (self.rim_right - 18, self.rim_y),
            (self.rim_left + 24, self.rim_y + 45),
            1,
        )
        #Rim
        pygame.draw.line(
            self.screen,
            COLOR_HOOP,
            (self.rim_left, self.rim_y),
            (self.rim_right, self.rim_y),
            self.rim_thickness,
        )
        pygame.draw.circle(
             self.screen, COLOR_HOOP, (self.rim_left, self.rim_y), 4
        )
        pygame.draw.circle(
            self.screen, COLOR_HOOP, (self.rim_right, self.rim_y), 4
        )

    
    def draw_ball(self):
        bx, by = int(self.ball_x), int(self.ball_y)
        pygame.draw.circle(self.screen, COLOR_BALL, (bx, by), self.ball_radius)
        pygame.draw.circle(
             self.screen, COLOR_BALL_SEAMS, (bx, by), self.ball_radius, width=2
        )

        # Draw seams
        rad = math.radians(self.ball_angel)
        ex = bx = int(math.cos(rad) * (self.ball_radius - 3))
        ey = by = int(math.sin(rad) * (self.ball_radius - 3))
        pygame.draw.line(self.screen, COLOR_BALL_SEAMS, (ex, ey), (bx, by), 2)

    def draw_aim_line(self):
        if not self.is_dragging:
            return

        mx, my = pygame.mouse.get_pos()
        # Reverse the direction of the aim line

        
    def draw_ui(self):
        
        # Draw floor
        pygame.draw.rect(
            self.screen,
            COLOR_FLOOR,
            (0, self.floor_y, WIDTH, HEIGHT - self.floor_y),
        )
        pygame.draw.line(
            self.screen, (150, 100, 50), (0, self.floor_y), (WIDTH, self.floor_y), 3
        )

        # Draw free throw line
        pygame.draw.line(
            self.screen,
            (255, 255, 255),
            (self.spawn_pos[0], self.floor_y),
            (self.spawn_pos[0], self.floor_y + 12),
            3,
        )

        # Score board
        score_surf = self.font.render(
            f"SCORE: {self.score}   STREAK: {self.streak}", True, COLOR_TEXT
        )
        help_surf = self.font.render(
            "Sterowanie: Przeciagnij myszka od pilki i pusc | R = Reset",
            True,
            (160, 160, 170),
        )
        self.screen.blit(score_surf, (25, 25))
        self.screen.blit(help_surf, (25, 55))

        # Feedback message
        if self.feedback_timer > 0:
            msg_surf = self.big_font.render(
                self.feedback_text, True, (80, 255, 120)
            )
            rect = msg_surf.get_rect(center=(WIDTH // 2, 120))
            self.screen.blit(msg_surf, rect)
            self.feedback_timer -= 1

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
