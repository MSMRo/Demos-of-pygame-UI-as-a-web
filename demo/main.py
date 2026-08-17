import asyncio
import sys
import pygame

pygame.init()
WIDTH, HEIGHT = 990, 540
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Contador - Demo Pygame")
clock = pygame.time.Clock()


async def main():
    count = 0
    font = pygame.font.SysFont(None, 96)
    btn_font = pygame.font.SysFont(None, 36)

    increase_rect = pygame.Rect(WIDTH // 2 + 80, HEIGHT - 140, 160, 60)
    decrease_rect = pygame.Rect(WIDTH // 2 - 240, HEIGHT - 140, 160, 60)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if increase_rect.collidepoint(event.pos):
                    count += 1
                elif decrease_rect.collidepoint(event.pos):
                    count -= 1

        # Draw
        screen.fill((30, 30, 30))

        # Counter display
        txt = font.render(str(count), True, (255, 255, 255))
        txt_rect = txt.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        screen.blit(txt, txt_rect)

        # Increase button
        pygame.draw.rect(screen, (70, 130, 180), increase_rect, border_radius=8)
        inc_label = btn_font.render("Aumentar", True, (255, 255, 255))
        inc_rect = inc_label.get_rect(center=increase_rect.center)
        screen.blit(inc_label, inc_rect)

        # Decrease button
        pygame.draw.rect(screen, (180, 70, 70), decrease_rect, border_radius=8)
        dec_label = btn_font.render("Disminuir", True, (255, 255, 255))
        dec_rect = dec_label.get_rect(center=decrease_rect.center)
        screen.blit(dec_label, dec_rect)

        pygame.display.flip()
        clock.tick(60)
        await asyncio.sleep(0)

    pygame.quit()
    sys.exit(0)


if __name__ == '__main__':
    asyncio.run(main())