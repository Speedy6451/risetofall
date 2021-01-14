__docformat__ = "reStructuredText"

import pymunk, pymunk.pygame_util, pygame, random, json

class Camera(object):
    """
    This class implements a simple camera that can pan through the level
    """
    def __init__(self, x = 0, y = 0, w=400, h = 600) -> None:
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.tracking = None
        self.speed = 0.05

    def translate(self, pos):
        return (pos[0]-self.x,pos[1]-self.y)

    def outOfBounds(self, pos):
        if (pos[0]-self.y >self.h or pos[0]-self.y < 0 
                or pos[1]-self.x >self.w or pos[1]-self.x < 0):
            return True
        else:
            return False

    def track(self, thing):
        self.tracking = thing

    def update(self):
        if self.tracking:
            target = self.tracking.getPos()
            target = (target[0]-(self.w/2),target[1]-(self.h/2))

            self.x += (target[0]-self.x)*self.speed
            self.y += (target[1]-self.y)*self.speed

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

    def setPosList(self, pos):
        self._body.position = pos

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
            pygame.draw.circle(self._game._screen,self.color,self._game.camera.translate(self._body.position),self.radius)

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
            pygame.draw.line(self._game._screen, self.color, self._game.camera.translate(self._pos1), self._game.camera.translate(self._pos2), self._width)

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
        self._body.position = self._game.camera.translate((random.randint(0,self._game.windowSize[0]),0))
        self._body.apply_force_at_local_point((0,self._game._space.gravity[1]*1))
        self._poly.collision_type = 4
    def update(self):
        t = pygame.time.get_ticks()
        dt= t - self._startTime
        if (dt > self._maxTime):
            self.destroy = True

        if self._game.camera.outOfBounds(self.getPos()):
            self.destroy = True


    def draw(self):
        if self.visible:
            pygame.draw.circle(self._game._screen,self.color,self._game.camera.translate(self._body.position),self.radius)
    def delete(self):
        self._game._space.remove(self._body,self._poly)

class Rain(object):
    def rainCollisionHandler(self, arbiter, space, data):
        return False

    def __init__(self,game,maxDrops = 10,maxTime = 15000, dropRate=400):
        self.dropList = [RainDrop(game, maxTime)]
        self.lastSpawn = pygame.time.get_ticks()
        self.maxDrops = maxDrops
        self.maxTime = maxTime
        self.dropRate = dropRate
        self.game = game
        self.raining = True

        self.collisionHandler = game._space.add_collision_handler(3,4)
        self.collisionHandler.begin = self.rainCollisionHandler

    def update(self):
        t = pygame.time.get_ticks()
        dt= t - self.lastSpawn

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

class Level(object):
    """
    Level class
    Creates and destroys a level from a JSON file.
    """
    
    def platformCollisionHandler(self, arbiter, space, data):
        self._game.player.canJump = True
        return True

    def __init__(self, levelFilePath: str, game):
        self._levelFilePath = levelFilePath
        self._levelFile = open(self._levelFilePath, 'r')
        self.level = json.load(self._levelFile)
        self._game = game

        self.collisionHandler = game._space.add_collision_handler(3,5)
        self.collisionHandler.begin = self.platformCollisionHandler

    def start(self):
        for platform in self.level['platforms']:
            box = Platform(self._game,platform['pos1'],platform['pos2'],platform['width'] or 4,platform['color'] or (0,0,0,1))
            box._poly.collision_type = 5
            self._game._shapes.append(box)

class Player(Circle):
    """
    Player class
    implements the player that can move and jump
    """
    def __init__(self, game):
        super().__init__(game, 13, (255,0,0,1))
        self.setPos(random.randint(0,self._game.windowSize[0]),0)
        self._poly.collision_type = 3
        self.moveRight = False
        self.moveLeft = False
        self.setPosList(self._game.level.level['playerSpawn'])
        self.canJump = True

    def jump(self):
        if self.canJump:
            self._body.apply_force_at_local_point((0,-15000))
            self.canJump = False

    def draw(self):
        super().draw()
        print(self.getPos())
        if self.getPos()[1] > 1500:
            self.setPosList(self._game.level.level['playerSpawn'])
            pass 
        if self.moveLeft:
            self._body.apply_force_at_local_point((-200,0))
        if self.moveRight:
            self._body.apply_force_at_local_point((200,0))


class Mouse(Thing):
    """
    Mouse class
    allows the player to interact with the rain
    """
    def __init__(self,game):
        super().__init__(game)
        self._body = pymunk.Body(body_type=pymunk.Body.STATIC)
        self._poly = pymunk.Circle(self._body,60)
        self._game._space.add(self._body,self._poly)

    def draw(self):
        mouse = pygame.mouse.get_pos()
        self.setPos(mouse[0],mouse[1])
        pygame.draw.circle(self._game._screen,(0,0,0,1),self._body.position,6)

class RiseToFall(object):
    """
    riseToFall game class
    """

    def __init__(self) -> None:
        # create space
        self._space = pymunk.Space()
        self._space.gravity = 0,300
        self.windowSize = (400,600)

        # initialize pygame
        pygame.init()
        self._screen = pygame.display.set_mode(self.windowSize, pygame.RESIZABLE)
        self._clock = pygame.time.Clock()


        # set caption
        pygame.display.set_caption("rise to fall")

        self._running = True

        self._shapes = []

        box = Platform(self, (100,140), (150,160))
        self._shapes.append(box)
        # font = pygame.font.SysFont("Arial",16)


        self.camera = Camera(w=self.windowSize[0],h=self.windowSize[1])


        self.rain = Rain(self)

        self._shapes.append(Mouse(self))


        self.level = Level('levels/testlevel.json',self)
        self.level.start()
        self.player = Player(self)
        self._shapes.append(self.player)
        self.camera.track(self.player)

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
            if event.type == pygame.KEYDOWN and event.key == pygame.K_a and self.player:
                self.player.moveLeft = True
            if event.type == pygame.KEYDOWN and event.key == pygame.K_d and self.player:
                self.player.moveRight = True
            if event.type == pygame.KEYUP and event.key == pygame.K_a and self.player:
                self.player.moveLeft = False
            if event.type == pygame.KEYUP and event.key == pygame.K_d and self.player:
                self.player.moveRight = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_w and self.player:
                self.player.jump()
            if event.type == pygame.VIDEORESIZE:
                self._screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
                self.camera.h = event.h
                self.camera.w = event.w
                


    def _drawEntities(self):
        for shape in self._shapes:
            shape.draw()

    def run(self):
        while self._running:
            self._processEvents();
            self.camera.update()
            self._space.step(0.02)
            self._screen.fill(pygame.Color("white"))
            # self._space.debug_draw(self._print_options)
            self.rain.update()
            self._drawEntities()
            pygame.display.flip()
        

if __name__ == "__main__":
    game = RiseToFall()
    game._createBox()
    game.run()
