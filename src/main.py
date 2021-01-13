__docformat__ = "reStructuredText"

import pymunk, pymunk.pygame_util, pygame, random

class Camera(object):
    """
    This class implements a simple camera that can pan through the level
    """
    def __init__(self, x = 0, y = 0, w=400, h = 600) -> None:
        self.x = x
        self.y = y
        self.w = w
        self.h = h

    def translate(self, pos):
        return (pos[0]-self.x,pos[1]-self.y)

    def outOfBounds(self, pos):
        if (pos[0] > self.w-self.x or pos[0] < 0-self.x
                or pos[1] > self.h-self.y or pos[1] < 0-self.y):
            return True
        else:
            return False

class Thing(object):
    """
    This class implements a generic pymunk object that can be written to the pygame window
    """
    def __init__(self, game, mass = 1.0, moment = 1666, bodyType = pymunk.Body.DYNAMIC) -> None:
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

class Circle(Thing):
    """
    This class implements a pymunk circle that can be displayed on a pygame window
    """
    def __init__(self, game, radius = 80, color = pygame.Color(0,0,255,1), mass = 1, moment = 1666, bodyType = pymunk.Body.DYNAMIC) -> None:
        super().__init__(game, mass=mass, moment=moment, bodyType=bodyType)
        self.radius = radius
        self.color = color 
        self._poly = pymunk.Circle(self._body,radius)
        self._game._space.add(self._body,self._poly)

    def draw(self):
        if self.visible:
            pygame.draw.circle(self._game._screen,self.color,self._body.position,self.radius)

class Platform(Thing):
    """
    This class implements a static platform
    """
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

class RainDrop(Thing):
    """
    Raindrop
    """
    def __init__(self,game, maxTime):
        super().__init__(game, 0.02)
        self.radius = 2
        self.color = pygame.Color(0,0,255,1)
        self._poly = pymunk.Circle(self._body,self.radius)
        self._maxTime = maxTime
        self._startTime = pygame.time.get_ticks()
        self.destroy = False
        self._game._space.add(self._body,self._poly)
        self.setPos(random.randint(0,400),0)
        self._body.apply_force_at_local_point((0,self._game._space.gravity[1]*1))
    def update(self):
        t = pygame.time.get_ticks()
        dt= t - self._startTime
        if (dt > self._maxTime):
            self.destroy = True

        if self._game.camera.outOfBounds(self.getPos()):
            self.destroy = True


    def draw(self):
        if self.visible:
            pygame.draw.circle(self._game._screen,self.color,self._body.position,self.radius)
    def delete(self):
        self._game._space.remove(self._body,self._poly)

class Rain(object):
    def __init__(self,game,maxDrops = 10,maxTime = 15000, dropRate=400):
        self.dropList = [RainDrop(game, maxTime)]
        self.lastSpawn = pygame.time.get_ticks()
        self.maxDrops = maxDrops
        self.maxTime = maxTime
        self.dropRate = dropRate
        self.game = game
        self.raining = True

    def update(self):
        t = pygame.time.get_ticks()
        dt= t - self.lastSpawn
        print(len(self.dropList))

        if self.raining:
            if (len(self.dropList) < self.maxDrops and dt > self.dropRate):
                self.dropList.append(RainDrop(self.game, self.maxTime))
                self.lastSpawn = t


        for raindrop in self.dropList:
            raindrop.update()
            if (raindrop.destroy == True):
                self.dropList.remove(raindrop)
                raindrop.delete()
                del raindrop
            else:
                raindrop.draw()

class RiseToFall(object):
    """
    riseToFall game class
    """

    def __init__(self) -> None:
        # create space
        self._space = pymunk.Space()
        self._space.gravity = 0,100

        # initialize pygame
        pygame.init()
        self._screen = pygame.display.set_mode((400,600))
        self._clock = pygame.time.Clock()

        # set caption
        pygame.display.set_caption("rise to fall")

        self._running = True

        self._shapes = []

        box = Platform(self, (100,140), (150,160))
        self._shapes.append(box)
        # font = pygame.font.SysFont("Arial",16)

        self.rain = Rain(self)

        self.camera = Camera()

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
                shape = Circle(self, 10)
                shape.setPos(random.randint(0,400),0)
                shape.color = pygame.Color(255,0,255,1)
                self._shapes.append(shape)
                self._space.gravity = (self._space.gravity[0]*-1,self._space.gravity[1]*-1)
                self.rain.raining = not self.rain.raining

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
            self.rain.update()
            pygame.display.flip()
        

if __name__ == "__main__":
    game = RiseToFall()
    game._createBox()
    game.run()
