import pymunk, pymunk.pygame_util, pygame

space = pymunk.Space()
space.gravity = 0,-1000

body = pymunk.Body(1,1666)
body.position = 50,100

poly = pymunk.Poly.create_box(body)

space.add(body, poly)

pygame.init()
screen = pygame.display.set_mode([400,600])
clock = pygame.time.Clock()
running = True
# font = pygame.font.SysFont("Arial",16)


print_options = pymunk.pygame_util.DrawOptions(screen)

while True:
    space.step(0.02)
    space.debug_draw(print_options)
