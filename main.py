import asyncio
import pygame

pygame.init()
pygame.display.set_mode((990, 540))
clock = pygame.time.Clock()

async def main():
    count = 60

    while count:
        print(f"{count}: Hello from Pygame")
        count -= 1
        clock.tick(60)
        pygame.display.update()
        await asyncio.sleep(0)  # You must include this statement in your main loop. Keep the argument at 0.     

    pygame.quit()

asyncio.run(main())