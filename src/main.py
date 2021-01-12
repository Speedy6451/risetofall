__docformat__ = "reStructuredText"

import pymunk, pymunk.pygame_util, pygame, random

class camera(object):
    def __init__(self, x = 0, y = 0) -> None:
        self.x = x
        self.y = y

    def translate(self, pos):
        return (pos[0]-self.x,pos[1]-self.y)

class thing(object):
    def __init__(self, game, mass = 1, moment = 1666, bodyType = pymunk.Body.DYNAMIC) -> None:
        self._mass = mass # weight 
        self._moment = moment # rotational inertia
        self._bodyType = bodyType # fixed/moving
        self._body = pymunk.Body(self._mass,self._moment,self._bodyType)
        self._body.position = (400, 0)
        self.visible = True
        self._game = game # game object

    def setPos(self, x,y):
        self._body.position = (x,y)

    def getPos(self):
        return (self._body.position)

    def draw(self):
        pass

class circle(thing):
    def __init__(self, game, radius = 80, color = pygame.Color(0,0,255,1), mass = 1, moment = 1666, bodyType = pymunk.Body.DYNAMIC) -> None:
        super().__init__(game, mass=mass, moment=moment, bodyType=bodyType)
        self.radius = radius
        self.color = color 
        self._poly = pymunk.Circle(self._body,radius)
        self._game._space.add(self._body,self._poly)

    def draw(self):
        if self.visible:
            pygame.draw.circle(self._game._screen,self.color,self._body.position,self.radius)

class platform(thing):
    def __init__(self, game, pos1 = (20,40), pos2 = (40,40), width = 5, color = pygame.Color(0,0,0,1)) -> None:
        super().__init__(game, bodyType=pymunk.Body.DYNAMIC)
        self._body = pymunk.Body(body_type=pymunk.Body.STATIC)
        self.color = color 
        self._pos1 = pos1
        self._pos2 = pos2
        self._width = width
        self._poly = pymunk.Segment(self._body,pos1,pos2,width)
        self._game._space.add(self._body,self._poly)

    def draw(self):
        if self.visible:
            pygame.draw.line(self._game._screen, self.color, self._pos1, self._pos2, self._width)

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

        self._shapes = []

        box = platform(self, (100,140), (150,160))
        self._shapes.append(box)
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
                #self._createBox()
                shape = circle(self, 10)
                shape.setPos(random.randint(0,400),0)
                shape.color = pygame.Color(255,0,255,1)
                self._shapes.append(shape)

    def _drawEntities(self):
        for shape in self._shapes:
            shape.draw()

    def run(self):
        while self._running:
            self._processEvents();
            self._space.step(0.02)
            self._screen.fill(pygame.Color("white"))
            # self._space.debug_draw(self._print_options)
            self._drawEntities()
            pygame.display.flip()
        

if __name__ == "__main__":
    game = riseToFall()
    game._createBox()
    game.run()
