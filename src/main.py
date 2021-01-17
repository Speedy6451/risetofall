__docformat__ = "reStructuredText"

import pymunk, pymunk.pygame_util, pygame, random, json

class Camera(object):
    """
    This class implements a simple camera that can pan through the level and track an object
    """
    def __init__(self, x = 0, y = 0, w=400, h = 600) -> None:
        self.x = x # cam x offset
        self.y = y # cam y offset
        self.w = w # cam width
        self.h = h # cam height
        self.tracking = None # tracking target
        self.speed = 0.05 # tracking speed (get 5% closer to target every frame)

    def translate(self, pos):
        """
        This function translates the given coordinate to give a camera pan effect
        """
        return (int(pos[0]-self.x),int(pos[1]-self.y))

    def outOfBounds(self, pos):
        """
        This function checks if the given coordinate is currently visible. It is used to despawn objects
        """
        if (pos[0]-self.y >self.h or pos[0]-self.y < 0
                or pos[1]-self.x >self.w or pos[1]-self.x < 0):
            return True
        else:
            return False

    def track(self, thing):
        """
        This function sets the tracking target
        """
        self.tracking = thing

    def update(self):
        """
        This function is called every frame, and pans toward the given target.
        """
        if self.tracking:
            target = self.tracking.getPos()
            target = (target[0]-(self.w/2),target[1]-(self.h/2)) # find offset from target

            self.x += (target[0]-self.x)*self.speed # pan toward target at given speed
            self.y += (target[1]-self.y)*self.speed

class Thing(object):
    """
    This class implements a generic pymunk object that can be written to the pygame window
    """
    def __init__(self, game, mass = 1.0, moment = 1666, bodyType = pymunk.Body.DYNAMIC) -> None:
        self._mass = mass # weight 
        self._moment = moment # rotational inertia
        self._bodyType = bodyType # fixed/moving
        self._body = pymunk.Body(self._mass,self._moment,self._bodyType) # body (physics object)
        self._body.position = (400, 0) # position
        self.visible = True
        self._game = game # game object

    def setPos(self, x,y):
        """
        This function sets the object's position given an x and y coordinate
        """
        self._body.position = (x,y)

    def setPosList(self, pos):
        """
        This function sets the object's position given a coordinate list
        """
        self._body.position = pos

    def getPos(self):
        """
        This function returns the current position as a list
        """
        return (self._body.position)

    def draw(self):
        """
        This function draws the object
        It is empty by default as a Thing object has no visual form
        """
        pass

class Circle(Thing):
    """
    This class implements a pymunk circle that can be displayed on a pygame window
    """
    def __init__(self, game, radius = 80, color = pygame.Color(0,0,255,1), mass = 1, moment = 1666, bodyType = pymunk.Body.DYNAMIC) -> None:
        super().__init__(game, mass=mass, moment=moment, bodyType=bodyType)
        self.radius = radius # circle radius
        self.color = color  # circle color
        self._poly = pymunk.Circle(self._body,radius) # physics shape
        self._game._space.add(self._body,self._poly) # add self to physics simulation

    def draw(self):
        """
        This function draws the circle every frame
        """
        if self.visible:
            pygame.draw.circle(self._game._screen,self.color,self._game.camera.translate(self._body.position),self.radius)

class Platform(Thing):
    """
    This class implements a static platform
    """
    def __init__(self, game, pos1 = (20,40), pos2 = (40,40), width = 5, color = pygame.Color(0,0,0,1)) -> None:
        super().__init__(game, bodyType=pymunk.Body.DYNAMIC)
        self._body = pymunk.Body(body_type=pymunk.Body.STATIC) # Creates static body (unmovable)
        self.color = color # line color
        self._pos1 = pos1 # line point 1
        self._pos2 = pos2 # line point 2
        self._width = width # line width
        self._poly = pymunk.Segment(self._body,pos1,pos2,width) # create physics shape
        self._game._space.add(self._body,self._poly) # add self to simulation

    def draw(self):
        """
        This function draws the platform every frame
        """
        if self.visible:
            pygame.draw.line(self._game._screen, self.color, self._game.camera.translate(self._pos1), self._game.camera.translate(self._pos2), self._width)

class RainDrop(Thing):
    """
    Raindrop class
    """
    def __init__(self,game, maxTime):
        super().__init__(game, 0.02) # mass of 0.02
        self.radius = 2 # raindrop radius 2px
        self.color = pygame.Color(0,0,255,1) # raindrop color blue
        self._poly = pymunk.Circle(self._body,self.radius) # create physics object
        self._maxTime = maxTime # death timer
        self._startTime = pygame.time.get_ticks() # creation time
        self.destroy = False # death flag
        self._game._space.add(self._body,self._poly) # add self to simulation
        self._body.position = self._game.camera.translate((random.randint(0,self._game.windowSize[0]),0)) # spawn randomly at top of screen
        self._body.apply_force_at_local_point((0,self._game._space.gravity[1]*1)) # push raindrop downward
        self._poly.collision_type = 4 # set type so as not to interact with the player
    def update(self):
        """
        This function is called every frame and checks if the raindrop should die because it is out of bounds, or it is too old.
        """
        t = pygame.time.get_ticks()
        dt= t - self._startTime # calculate delta from creation
        if (dt > self._maxTime): # kill if too old
            self.destroy = True

        if self._game.camera.outOfBounds(self.getPos()): # kill if offscreen
            self.destroy = True

    def draw(self):
        """
        This function draws the raindrop each frame
        """
        if self.visible:
            pygame.draw.circle(self._game._screen,self.color,self._game.camera.translate(self._body.position),self.radius)
    def delete(self):
        """
        This  function removes the raindrop from the physics simulation
        """
        self._game._space.remove(self._body,self._poly)

class Rain(object):
    def rainCollisionHandler(self, arbiter, space, data):
        """
        This function activates when rain hits the player and ensures they do not interact
        """
        return False

    def __init__(self,game,maxDrops = 10,maxTime = 15000, dropRate=400):
        self.dropList = [RainDrop(game, maxTime)] # list of raindrops
        self.lastSpawn = pygame.time.get_ticks() # time last raindrop was spawned
        self.maxDrops = maxDrops # maximum raindrops at a time
        self.maxTime = maxTime # maximun time a raindrop can exist
        self.dropRate = dropRate # milliseconds between raindrops
        self.game = game # game object 
        self.raining = True # toggle new rain

        self.collisionHandler = game._space.add_collision_handler(3,4) # keeps raindrops from interacting with the player
        self.collisionHandler.begin = self.rainCollisionHandler

    def update(self):
        """
        This function is called every frame and is what creates and destroys raindrops
        """
        t = pygame.time.get_ticks()
        dt= t - self.lastSpawn # delta since last drop spawned

        if self.raining:
            if (len(self.dropList) < self.maxDrops and dt > self.dropRate): # create a raindrop if there is room, and the time has passed
                self.dropList.append(RainDrop(self.game, self.maxTime))  # create drop
                self.lastSpawn = t # reset counter


        for raindrop in self.dropList:
            raindrop.update() # make drops check if they should die
            if (raindrop.destroy == True): # delete drops whose time has come
                self.dropList.remove(raindrop)
                raindrop.delete()
                del raindrop
            else:
                raindrop.draw() # draw all alive drops

class Level(object):
    """
    Level class
    Creates and destroys a level from a JSON file.
    """
    
    def platformCollisionHandler(self, arbiter, space, data): # allow player to jump again on collision with platform
        self._game.player.canJump = True
        return True # make player collide

    def __init__(self, levelFilePath: str, game):
        self._levelFilePath = levelFilePath # filepath to level json
        self._levelFile = open(self._levelFilePath, 'r') # open level
        self.level = json.load(self._levelFile) # load to python object
        self._game = game # game object

        self.collisionHandler = game._space.add_collision_handler(3,5) # allow player to jump on collision
        self.collisionHandler.begin = self.platformCollisionHandler

    def start(self):
        """
        This function starts the level, and spawns in all level objects
        """
        for platform in self.level['platforms']:
            box = Platform(self._game,platform['pos1'],platform['pos2'],platform['width'] or 4,platform['color'] or (0,0,0,1)) # create platform object based on data
            box._poly.collision_type = 5 # specify as a platform collision type
            self._game._shapes.append(box) # add object to the game

class Player(Circle):
    """
    Player class
    implements the player that can move and jump
    """
    def __init__(self, game):
        super().__init__(game, 13, (255,0,0,1))
        self._poly.collision_type = 3 # specify to collide as a player
        self.moveRight = False # is d pressed
        self.moveLeft = False # is a pressed 
        self.setPosList(self._game.level.level['playerSpawn']) # set position to level start
        self.canJump = True # can the player jump

    def jump(self):
        """
        This function makes the player jump if it can
        """
        if self.canJump: # if the player can jump
            self._body.apply_force_at_local_point((0,-15000)) # shove the player up
            self.canJump = False # the player can no longer jump

    def draw(self):
        """
        This function is called every frame and draws the player
        """
        super().draw()
        if self.getPos()[1] > 1500 or self.getPos()[1]  < -500: # respawn the player if fallen out of map
            self.setPosList(self._game.level.level['playerSpawn']) # go to spawnpoint
        if self.moveLeft: # is a pressed
            self._body.apply_force_at_local_point((-200,0)) # shove player left
        if self.moveRight: # is d pressed
            self._body.apply_force_at_local_point((200,0)) # shove player right

class Mouse(Thing):
    """
    Mouse class
    allows the player to interact with the rain
    """
    def __init__(self,game):
        super().__init__(game)
        self._body = pymunk.Body(body_type=pymunk.Body.STATIC) # unaffected by gravity
        self._poly = pymunk.Circle(self._body,6) # create physics shape
        self._game._space.add(self._body,self._poly) # add to simulation

    def draw(self):
        """
        This function is called every frame and draws the mouse to the screen. It also ensures the mouse is on the mouse
        """
        mouse = pygame.mouse.get_pos() # get mouse position
        self.setPosList(mouse) # go to mouse
        pygame.draw.circle(self._game._screen,(0,0,0,1),(int(self._body.position[0]),int(self._body.position[1])),6)

class RiseToFall(object):
    """
    riseToFall game class
    """

    def __init__(self) -> None:
        # create space
        self._space = pymunk.Space() # physics arena
        self._space.gravity = 0,300 # gravity
        self.windowSize = (400,600) # size of window w,h

        # initialize pygame
        pygame.init()
        self._screen = pygame.display.set_mode(self.windowSize, pygame.RESIZABLE) # set window size and enable resizing

        self.clock = pygame.time.Clock()

        # set caption
        pygame.display.set_caption("rise to fall")

        self._running = True

        self._shapes = [] # list of objects

        # font = pygame.font.SysFont("Arial",16) # font


        self.camera = Camera(w=self.windowSize[0],h=self.windowSize[1]) # initialize camera

        self.rain = Rain(self) # initialize rain

        self._shapes.append(Mouse(self)) # initialize mouse


        # load and start the first level
        self.level = Level('levels/testlevel.json',self)
        self.level.start()

        # create player
        self.player = Player(self)
        self._shapes.append(self.player)
        self.camera.track(self.player) 

    def _processEvents(self):
        """
        This function is called every frame and handles events such as keyboard input
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT: # close button on window
                self._running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE: # exit if escape pressed
                self._running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE: # invert gravity on spacebar
                self._space.gravity = (self._space.gravity[0]*-1,self._space.gravity[1]*-1)
                self.rain.raining = not self.rain.raining
            if event.type == pygame.KEYDOWN and event.key == pygame.K_a and self.player: # begin moving left
                self.player.moveLeft = True
            if event.type == pygame.KEYDOWN and event.key == pygame.K_d and self.player: # begin moving right
                self.player.moveRight = True
            if event.type == pygame.KEYUP and event.key == pygame.K_a and self.player: # stop moving left
                self.player.moveLeft = False
            if event.type == pygame.KEYUP and event.key == pygame.K_d and self.player: # stop moving right
                self.player.moveRight = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_w and self.player: # jump
                self.player.jump()
            if event.type == pygame.VIDEORESIZE: # resize if window moved
                self._screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
                self.camera.h = event.h
                self.camera.w = event.w

    def _drawEntities(self):
        """
        This function is called every frame and draws all objects 
        """
        for shape in self._shapes:
            shape.draw()

    def run(self):
        """
        Main game loop
        """
        while self._running:
            self._processEvents() # process keyboard input
            self.camera.update() # make camera pan
            self._screen.fill(pygame.Color("white")) # clear screen
            self.rain.update() # process rain
            self._drawEntities() # draw entities
            pygame.display.flip() # write to screen
            self._space.step(0.02) # increment simulation
            self.clock.tick(60)
        

if __name__ == "__main__": # run game if called directly
    game = RiseToFall()
    game.run()
