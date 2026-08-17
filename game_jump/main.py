import asyncio
import math
import random
from array import array

import pygame


WIDTH, HEIGHT = 960, 540
GROUND_Y = 440
PLAYER_START_X = 120
TARGET_SCORE = 10

START = "START"
PLAYING = "PLAYING"
WIN = "WIN"
GAME_OVER = "GAME_OVER"


def make_beep(frequency=440, duration_ms=120, volume=0.12):
    """Create a short tone for simple sound effects."""
    sample_rate = 22050
    total_samples = int(sample_rate * duration_ms / 1000)
    sound_buffer = array("h")

    for i in range(total_samples):
        time_value = i / sample_rate
        wave = math.sin(2 * math.pi * frequency * time_value)
        sample = int(32767 * volume * wave)
        sound_buffer.append(sample)

    return pygame.mixer.Sound(buffer=sound_buffer)


class Player(pygame.sprite.Sprite):
    """The playable character on the left side of the screen."""

    def __init__(self):
        super().__init__()
        self.width = 42
        self.height = 56
        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.rect.x = PLAYER_START_X
        self.rect.bottom = GROUND_Y
        self.velocity_y = 0
        self.on_ground = True
        self.draw_sprite()

    def draw_sprite(self):
        image = self.image
        image.fill((0, 0, 0, 0))

        # Hat
        pygame.draw.rect(image, (212, 34, 31), (6, 0, 30, 10))
        pygame.draw.rect(image, (255, 255, 255), (9, 8, 24, 5))

        # Face
        pygame.draw.rect(image, (250, 216, 177), (10, 12, 22, 18))
        pygame.draw.rect(image, (0, 0, 0), (15, 18, 3, 3))
        pygame.draw.rect(image, (0, 0, 0), (24, 18, 3, 3))
        pygame.draw.rect(image, (255, 100, 100), (16, 24, 10, 4))

        # Mustache and nose
        pygame.draw.rect(image, (110, 75, 40), (14, 22, 14, 3))
        pygame.draw.rect(image, (250, 216, 177), (20, 23, 3, 3))

        # Body
        pygame.draw.rect(image, (52, 92, 235), (9, 30, 24, 18))
        pygame.draw.rect(image, (245, 205, 47), (12, 38, 18, 5))

        # Arms / gloves
        pygame.draw.rect(image, (250, 216, 177), (5, 34, 4, 12))
        pygame.draw.rect(image, (250, 216, 177), (33, 34, 4, 12))

        # Legs and shoes
        pygame.draw.rect(image, (95, 92, 240), (12, 48, 7, 8))
        pygame.draw.rect(image, (95, 92, 240), (23, 48, 7, 8))
        pygame.draw.rect(image, (160, 82, 60), (9, 56, 10, 4))
        pygame.draw.rect(image, (160, 82, 60), (23, 56, 10, 4))

    def jump(self):
        if self.on_ground:
            self.velocity_y = -700
            self.on_ground = False

    def update(self, dt):
        self.velocity_y += 1700 * dt
        self.rect.y += self.velocity_y * dt

        if self.rect.bottom >= GROUND_Y:
            self.rect.bottom = GROUND_Y
            self.velocity_y = 0
            self.on_ground = True


class Barrel(pygame.sprite.Sprite):
    """Rolling barrels that move from right to left."""

    def __init__(self, speed):
        super().__init__()
        self.width = 30
        self.height = 36
        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.rect.x = WIDTH + random.randint(20, 120)
        self.rect.bottom = GROUND_Y
        self.speed = speed
        self.scored = False
        self.draw_sprite()

    def draw_sprite(self):
        image = self.image
        image.fill((0, 0, 0, 0))

        # Wooden barrel body
        pygame.draw.rect(image, (150, 92, 44), (2, 4, 26, 28))
        pygame.draw.rect(image, (118, 71, 33), (4, 0, 22, 10))

        # Red bands
        pygame.draw.rect(image, (190, 33, 33), (4, 12, 22, 5))
        pygame.draw.rect(image, (190, 33, 33), (4, 22, 22, 5))

        # Metal highlights
        pygame.draw.rect(image, (220, 170, 110), (8, 6, 14, 2))
        pygame.draw.rect(image, (220, 170, 110), (8, 18, 14, 2))
        pygame.draw.rect(image, (220, 170, 110), (8, 30, 14, 2))

    def update(self, dt):
        self.rect.x -= self.speed * dt


class Game:
    """Main game logic and state."""

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("DONKEY KONG - BARREL SURVIVAL")

        self.clock = pygame.time.Clock()
        self.running = True
        self.game_state = START
        self.score = 0

        self.player = Player()
        self.barrels = pygame.sprite.Group()
        self.spawn_timer = 1.2
        self.next_spawn_delay = 1.2

        self.title_font = pygame.font.SysFont("arialblack", 44)
        self.subtitle_font = pygame.font.SysFont("arialblack", 24)
        self.hud_font = pygame.font.SysFont("arialblack", 28)

        try:
            pygame.mixer.init()
            self.jump_sound = make_beep(660, 120, 0.12)
            self.score_sound = make_beep(880, 90, 0.10)
            self.hit_sound = make_beep(180, 220, 0.18)
            self.win_sound = make_beep(1046, 220, 0.14)
        except Exception:
            self.jump_sound = None
            self.score_sound = None
            self.hit_sound = None
            self.win_sound = None

    def reset_game(self):
        self.score = 0
        self.player = Player()
        self.barrels.empty()
        self.spawn_timer = 1.0
        self.next_spawn_delay = random.uniform(1.0, 2.0)

    def start_game(self):
        self.reset_game()
        self.game_state = PLAYING

    def play_sound(self, sound):
        if sound is not None:
            try:
                sound.play()
            except Exception:
                pass

    def spawn_barrel(self):
        speed = 200 + min(self.score * 15, 150)
        barrel = Barrel(speed)
        self.barrels.add(barrel)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if self.game_state == START:
                    self.start_game()
                elif self.game_state in (WIN, GAME_OVER):
                    self.reset_game()
                    self.game_state = PLAYING
                elif self.game_state == PLAYING and event.key == pygame.K_SPACE:
                    self.player.jump()
                    self.play_sound(self.jump_sound)

    def update(self, dt):
        if self.game_state == PLAYING:
            self.player.update(dt)

            self.spawn_timer -= dt
            if self.spawn_timer <= 0:
                self.spawn_barrel()
                self.spawn_timer = random.uniform(1.0, 2.1)

            for barrel in list(self.barrels):
                barrel.update(dt)

                if not barrel.scored and barrel.rect.right < self.player.rect.left:
                    barrel.scored = True
                    self.score += 1
                    self.play_sound(self.score_sound)

                if barrel.rect.right < -50:
                    barrel.kill()

            collisions = pygame.sprite.spritecollide(self.player, self.barrels, False)
            if collisions:
                self.game_state = GAME_OVER
                self.play_sound(self.hit_sound)

            if self.score >= TARGET_SCORE:
                self.game_state = WIN
                self.play_sound(self.win_sound)

    def draw_background(self):
        sky = (120, 190, 255)
        self.screen.fill(sky)

        # Clouds
        for x in (80, 320, 520, 760):
            pygame.draw.ellipse(self.screen, (255, 255, 255), (x, 70, 110, 40))
            pygame.draw.ellipse(self.screen, (255, 255, 255), (x + 25, 48, 90, 48))
            pygame.draw.ellipse(self.screen, (255, 255, 255), (x + 70, 68, 70, 36))

        # Hills
        pygame.draw.ellipse(self.screen, (94, 196, 96), (-40, 300, 240, 180))
        pygame.draw.ellipse(self.screen, (65, 170, 70), (180, 330, 310, 170))
        pygame.draw.ellipse(self.screen, (94, 196, 96), (440, 290, 300, 200))
        pygame.draw.ellipse(self.screen, (79, 180, 80), (680, 320, 330, 180))

        # Ground
        pygame.draw.rect(self.screen, (129, 92, 49), (0, GROUND_Y, WIDTH, HEIGHT - GROUND_Y))
        pygame.draw.rect(self.screen, (95, 148, 78), (0, GROUND_Y, WIDTH, 18))

        for x in range(0, WIDTH + 20, 34):
            pygame.draw.rect(self.screen, (174, 135, 83), (x, GROUND_Y + 20, 28, 18))
            pygame.draw.rect(self.screen, (148, 120, 68), (x + 5, GROUND_Y + 22, 18, 12))
            pygame.draw.rect(self.screen, (201, 165, 103), (x + 6, GROUND_Y + 28, 14, 3))

    def draw_hud(self):
        score_text = self.hud_font.render(f"BARRELS CLEARED: {self.score}/{TARGET_SCORE}", True, (255, 255, 255))
        score_rect = score_text.get_rect(center=(WIDTH // 2, 30))
        pygame.draw.rect(self.screen, (0, 0, 0, 120), (score_rect.x - 18, score_rect.y - 10, score_rect.width + 36, score_rect.height + 20))
        self.screen.blit(score_text, score_rect)

    def draw_start_screen(self):
        title_text = self.title_font.render("DONKEY KONG - BARREL SURVIVAL", True, (255, 215, 0))
        subtitle_text = self.subtitle_font.render("PRESS ANY KEY TO START", True, (255, 255, 255))

        title_rect = title_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 30))
        subtitle_rect = subtitle_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 40))

        pygame.draw.rect(self.screen, (30, 30, 30, 160), (150, 170, 660, 180))
        self.screen.blit(title_text, title_rect)
        self.screen.blit(subtitle_text, subtitle_rect)

    def draw_end_screen(self, message):
        panel = pygame.Surface((540, 180), pygame.SRCALPHA)
        panel.fill((0, 0, 0, 150))
        self.screen.blit(panel, (210, 170))

        title = self.title_font.render(message, True, (255, 255, 255))
        subtitle = self.subtitle_font.render("PRESS ANY KEY TO PLAY AGAIN", True, (255, 220, 100))

        title_rect = title.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 20))
        subtitle_rect = subtitle.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 40))

        self.screen.blit(title, title_rect)
        self.screen.blit(subtitle, subtitle_rect)

    def draw(self):
        self.draw_background()

        if self.game_state == START:
            self.draw_start_screen()
        elif self.game_state in (PLAYING, WIN, GAME_OVER):
            self.draw_hud()
            self.barrels.draw(self.screen)
            self.screen.blit(self.player.image, self.player.rect)

            if self.game_state == WIN:
                self.draw_end_screen("YOU WIN!")
            elif self.game_state == GAME_OVER:
                self.draw_end_screen("GAME OVER")

    async def run(self):
        while self.running:
            dt = self.clock.tick(60) / 1000.0
            self.handle_events()
            self.update(dt)
            self.draw()
            pygame.display.flip()
            await asyncio.sleep(0)

        pygame.quit()


async def main():
    game = Game()
    await game.run()


if __name__ == "__main__":
    asyncio.run(main())
