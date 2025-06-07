import pygame

pygame.init

run = True
screen = pygame.display.set_mode([1000, 1000])
pygame.display.set_caption("Kaffespil")
clock = pygame.time.Clock()

while run:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
            
    deltaInSeconds = clock.tick(60) / 1000

    screen.fill([255, 255, 255])



    pygame.display.update()