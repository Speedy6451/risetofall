__docformat__ = "reStructuredText"

import pymunk, pymunk.pygame_util, pygame

class riseToFall(object):
    """
    riseToFall game class
    """

    def __init__(self) -> None:
        # create space
        self._space = pymunk.Space()
        self._space.gravity = 0,10

        # initialize pygame
        pygame.init()
        self._screen = pygame.display.set_mode((400,600))
        self._clock = pygame.time.Clock()

        # set caption
        pygame.display.set_caption("rise to fall")

        self._running = True
        # font = pygame.font.SysFont("Arial",16)

        # set draw options
        self._print_options = pymunk.pygame_util.DrawOptions(self._screen)

    def _createBox(self):
        body = pymunk.Body(1,1666)
        body.position = 50,100

        poly = pymunk.Poly.create_box(body)

        self._space.add(body, poly)

    def _processEvents(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self._running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self._running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                self._createBox()

    def run(self):
        while self._running:
            self._processEvents();
            self._space.step(0.02)
            self._screen.fill(pygame.Color("white"))
            self._space.debug_draw(self._print_options)
            pygame.display.flip()
        

if __name__ == "__main__":
    game = riseToFall()
    game._createBox()
    game.run()
