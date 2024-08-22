# ~ Imports ~ #
import pygame
from random import shuffle, randrange
from os import path as osPath
from copy import deepcopy
from json import load as jsonLoad
from json import dump as jsonDump
from subprocess import run as subprocessRun

# Inits
pygame.init()
clock = pygame.time.Clock()

# Create window
(display_width,display_height) = (256,224)

display = pygame.display.set_mode((3*display_width, 3*display_height))
pygame.display.set_caption('PyTetris')
icon = pygame.image.load('images/gui/icon.png').convert_alpha()
pygame.display.set_icon(icon)

# Load assets
screen = pygame.image.load('images/gui/bg.png').convert()
paused_overlay = pygame.image.load('images/gui/paused.png').convert_alpha()
death_overlay = pygame.image.load('images/gui/gameOver.png').convert_alpha()
pivot_sprite = pygame.image.load(f'images/pieces/pivot.png').convert_alpha()
lvl_up_particle = pygame.image.load('images/gui/lvlUpParticle.png').convert_alpha()

pieces = [
    pygame.image.load('images/pieces/0.png').convert_alpha(),
    pygame.image.load('images/pieces/1.png').convert_alpha(),
    pygame.image.load('images/pieces/2.png').convert_alpha(),
    pygame.image.load('images/pieces/ghost.png').convert_alpha()
]

def getGraphValues(image_path):
    img = pygame.image.load('images/curves/'+image_path)
    img = img.convert()
    width, height = img.get_size()
    pixel_counts = []
    for x in range(width):
        pixel_counts.append(0)
        for y in range(height):
            color = img.get_at((x,y))
            if color != (255,255,255,255):
                pixel_counts[x] += 1
    return pixel_counts

spreadParticleSizeCurve = getGraphValues('spreadParticleSize.png')
moveShapeAnimCurve = getGraphValues('moveShapeAnim.png')

# - Load controls - #
controls = {
    'left rotate': [pygame.K_z],
    'right rotate': [pygame.K_UP],
    'move left': [pygame.K_LEFT],
    'move right': [pygame.K_RIGHT],
    'soft down': [pygame.K_DOWN],
    'hard down': [pygame.K_SPACE],
    'toggle pivot indicator': [pygame.K_d],
    'hold': [pygame.K_c],
    'pause': [pygame.K_RETURN],
    'reset': [pygame.K_r],
    'quit': [pygame.K_ESCAPE],
    'toggle ghost': [pygame.K_g],
    'dementia': [pygame.K_x]
}

if osPath.isfile('controls.json'):
    jsonControls = jsonLoad(open('controls.json','r'))
    for id in controls.keys():
        if id in jsonControls.keys():
            keys = jsonControls[id]
            temp = []
            for key in keys:
                try:
                    temp.append(pygame.key.key_code(key))
                except ValueError as e:
                    raise ValueError(f"Key string not recognized by Pygame: '{key}'") from e
                controls[id] = temp
else:
    with open('controls.json','w') as file:
        convertedControls = deepcopy(controls)
        for k,v in controls.items():
            temp = []
            for key in v:
                temp.append(pygame.key.name(key))
            convertedControls[k] = temp
        jsonDump(convertedControls,file)
# - Load controls - #
# Define variables

frameRate = 60
show_ghost = True

holding_input = False
holding_down = False
left_collided = False
right_collided = False
running = True
closed = False
paused = False
reset = False
dementia = True
AREpaused = False
AREpauseLength = 0
linesCleared = 0
demeter = 0

showPivot = True

holdAnimFrames = -1
holdAnim_mode = 'current to hold'
# possible modes: 'current to hold', 'swap'
holdAnim_oldCurrentPos = (0,0)
holdAnim_newCurrentPos = (0,0)
holdAnim_oldCurrentRot = 0

nextAnimFrames = -1

offset = pygame.Vector2(0,0)
lastOffset = pygame.Vector2(0,0)
deltaTime = 0
springConstant = 500
damping = 10
velocity = pygame.Vector2(0,0)

lines = 0
lvl = 0
speed = 48

doParticles = True
spreadParticles = []

# Map storage
tileMap = []
def clearMap():
    global tileMap
    tileMap = []
    for row in range(20):
        column = []
        for x in range(10):
            column.append('')
        tileMap.append(column)
clearMap()
    
def setTileonMap(x,y, value):
    try:
        tileMap[y][x] = value
        return value
    except IndexError:
        return (x,y)

def getTileonMap(x,y):
    try:
        if y < 0 or x < 0:
            return 'OUT'
        else:
            return tileMap[y][x]
    except IndexError:
        return 'OUT'
    
def rotateTable(table):
    return [[*r][::-1] for r in zip(*table)]

# Rendering
stamps = []
def drawStamps():
    for i in range(len(stamps)):
        if not dementia or i < demeter/10+10:
            stamps[i][1].image.set_alpha(round(max(0,(demeter/10+10)-i)*32))
            screen.blit(stamps[i][1].image, stamps[i][0])
        if not dementia:
            stamps[i][1].image.set_alpha(255)
            screen.blit(stamps[i][1].image,stamps[i][0])

TotalAREpauseLength = 60
AREFlashes = 3
flash_stamps = []
def flashStamps():
    for pos, sprite in flash_stamps:
        if AREpauseLength <= (TotalAREpauseLength/(2*AREFlashes)) or (AREpauseLength > (TotalAREpauseLength/(2*AREFlashes))*2 and AREpauseLength <= (TotalAREpauseLength/(2*AREFlashes))*3) or (AREpauseLength > (TotalAREpauseLength/(2*AREFlashes))*4 and AREpauseLength <= (TotalAREpauseLength/(2*AREFlashes))*5):
            if not dementia:
                screen.blit(sprite.image, pos)
        else:
            pygame.draw.rect(screen, 'white', (pos[0], pos[1], 8, 8))

# Draw Text
def writeNums(pos: tuple, num: int, length: int,color=(255,255,255)):
    full_num = str(num)
    full_num = (length-len(full_num))*'0'+full_num
    i = 0
    for c in full_num:
        text = pygame.image.load(f'images/text/{c}.png').convert_alpha()
        text.fill(color, special_flags=pygame.BLEND_RGB_MULT)
        screen.blit(text, (pos[0]+8*i,pos[1]))
        i += 1

class SpreadParticles:
    class Particle:
        def __init__(self,x,y,xv,yv,gs,img,c=(255,255,255)) -> None:
            self.x = x
            self.y = y
            self.x_vel = xv
            self.y_vel = yv
            self.gravity_scale = gs * randrange(1,2)
            self.img = img
            self.color = c
            self.age = 0
            self.gravity = randrange(2,7)
        def draw(self,surface: pygame.Surface):
            self.age += 1
            self.gravity -= self.gravity_scale
            self.x += self.x_vel
            self.y += self.y_vel * self.gravity
            colored = self.img.copy()
            colored.fill(self.color,special_flags=pygame.BLEND_RGB_MULT)
            sized = pygame.transform.scale(colored, ((spreadParticleSizeCurve[self.age]*0.01)*self.img.get_width(),(spreadParticleSizeCurve[self.age]*0.01)*self.img.get_height()))
            surface.blit(sized,(self.x-(sized.get_width()//2),self.y-(sized.get_height()//2))) 
    def __init__(self,amount,start_x,start_y,gravity_scale,img,color=(255,255,255)) -> None:
        self.particles = []
        for i in range(amount):
            self.particles.append(self.Particle(start_x,start_y,randrange(-4,4),randrange(-2,0),gravity_scale,img,color))
    def draw(self,surface):
        for particle in self.particles:
            if particle.age >= 89:
                self.particles.pop(self.particles.index(particle))
            else:
                particle.draw(surface)

# Shapes and pieces
all_shapes = {}
class Shapes:
    class shape:
        # The individual blocks that make up a shape
        class __piece:
            def __init__(self,image,id,localx,localy,pieceid) -> None:
                self.sprite = pygame.sprite.Sprite()
                self.sprite.image = pygame.image.load(f'images/pieces/{image}.png').convert_alpha()
                self.sprite.rect = self.sprite.image.get_rect()
                self.pieceid = pieceid
                self.id = id
                self.localx = localx
                self.localy = localy
                self.center = False
                
        def __init__(self,id: str,piece_sprite: str,hitbox: str) -> None:
            self.id = id
            self.hitbox = hitbox
            self.base_hitbox = hitbox
            self.piece_sprite = piece_sprite
            self.rotation = 0
            self.x = 4
            self.y = 0
            self.centerPieceId = None
            self.makePieces()
            if id[0] != 'G':
                all_shapes[id] = self
                self.gui_sprite = pygame.surface.Surface((33,42), pygame.SRCALPHA)
                shape_sprite = pygame.surface.Surface((8*self.width,8*self.height), pygame.SRCALPHA)
                for piece in self.pieces:
                    shape_sprite.blit(piece.sprite.image,(8*piece.localx,8*piece.localy))
                rect = shape_sprite.get_rect()
                rect.center = (17,25)
                self.gui_sprite.blit(shape_sprite,rect)

                
        def makePieces(self):
            self.piecesGroup = pygame.sprite.Group()
            self.pieces = []
            maxWidth = 0
            x = 0
            y = 0
            for c in self.hitbox:
                if c.isdigit():
                    piece = self.__piece(self.piece_sprite,c,x,y,self.id)
                    piece.globalx = self.x + x
                    piece.globaly = self.y + y
                    self.pieces.append(piece)
                    self.piecesGroup.add(piece.sprite)
                    x += 1
                elif c == ' ':
                    x += 1
                elif c == '-':
                    y += 1
                    x = 0
                elif c == 'x':
                    self.centerPieceId = self.pieces[-1].id
                maxWidth = max(maxWidth,x)
            self.width = maxWidth
            self.height = self.hitbox.count('-')+1
        
        def getCenterPiece(self):
            for piece in self.pieces:
                if piece.id == self.centerPieceId: return piece

        def rotate(self,dir):
            oldCenterPieceLocalX = None
            oldCenterPieceLocalY = None
            if self.centerPieceId:
                centerPiece = self.getCenterPiece()
                oldCenterPieceLocalX = centerPiece.localx
                oldCenterPieceLocalY = centerPiece.localy
            self.rotation = self.rotation + dir
            if self.rotation < 0:
                self.rotation = 3
            elif self.rotation > 3:
                self.rotation = 0
            new_hitbox = []
            for line in self.base_hitbox.split('-'):
                new_hitbox.append([])
                for c in line:
                    if c.isdigit() or c == ' ':
                        new_hitbox[-1].append(c)
            for i in range(self.rotation):
                new_hitbox = rotateTable(new_hitbox)
            str_hitbox = ''
            for line in new_hitbox:
                for c in line:
                    str_hitbox += c
                str_hitbox += '-'
            str_hitbox = str_hitbox.removesuffix('-')
            self.hitbox = str_hitbox
            self.makePieces()
            if self.centerPieceId:
                centerPiece = self.getCenterPiece()
                self.x += (oldCenterPieceLocalX - centerPiece.localx)
                self.y += (oldCenterPieceLocalY - centerPiece.localy)
            
        def draw(self):
            if showPivot and self.getCenterPiece():
                self.getCenterPiece().sprite.image.blit(pivot_sprite,(0,0),special_flags=pygame.BLEND_RGBA_MIN)
            elif self.getCenterPiece():
                self.getCenterPiece().sprite.image = pygame.image.load(f'images/pieces/{self.piece_sprite}.png').convert_alpha()
            for piece in self.pieces:
                piece.sprite.rect.x = 96+(8*(self.x+piece.localx))
                piece.sprite.rect.y = 40+(8*(self.y+piece.localy))
            self.piecesGroup.draw(screen)
            
        def stamp(self):
            for piece in self.pieces:
                s = piece.sprite
                s.globalx = self.x+piece.localx
                s.globaly = self.y+piece.localy
                setTileonMap(self.x+piece.localx,self.y+piece.localy,self.id)
            self.makePieces()
            
    I = shape('I','1','01x23')
    J = shape('J','0','01x2-  3')
    L = shape('L','2','01x2-3  ')
    O = shape('O','1','01-23')
    S = shape('S','0',' 0x1-23 ')
    T = shape('T','1','01x2- 3 ')
    Z = shape('Z','2','01x - 23')

    def __makeBag():
        out = list(all_shapes.values())
        shuffle(out)
        return out
    
    bag = []

    def fromBag() -> shape:
        if len(Shapes.bag) == 0:
            Shapes.bag = Shapes.__makeBag()
        return Shapes.bag.pop(0)


def getInp(control_scheme):
    keys = pygame.key.get_pressed()
    for key in controls[control_scheme]:
        if keys[key]:
            return True
    return False

def shakeScreen(force: pygame.Vector2):
    global offset,lastOffset,deltaTime,springConstant,damping,velocity
    if force.magnitude() == 0:
        velocity += (-springConstant*offset - damping * velocity) * deltaTime
    else:
        velocity = force * deltaTime

    if velocity.magnitude() < 0.01:
        velocity = pygame.Vector2(0,0)
        offset = pygame.Vector2(0,0)

    offset += velocity * deltaTime

# Clearing Lines
def clearLine(y: int):
    global linesCleared,AREpaused,AREpauseLength,stamps,lines,lvl,speed,demeter,thud
    thud = 0
    linesCleared += 1
    AREpaused = True
    AREpauseLength = TotalAREpauseLength
    tileMap.pop(y)
    empty = []
    for i in range(10):
        empty.append('')
    tileMap.insert(0,empty)
    temp = []
    for pos,piece in stamps:
        if piece.globaly <= y:
            thud += 2
        if piece.globaly != y:
            temp.append((pos,piece))
        else:
            flash_stamps.append((pos,piece))
    stamps = temp
    lines += 1

    demeter += 2
    
    if demeter > 80:
        demeter = demeter

    if lines % 10 == 0:
        lvl += 1
        if doParticles:
            spreadParticles.append(SpreadParticles(25,screen.get_width()//2,screen.get_height()//2,0.2,lvl_up_particle))
        if lvl < 9:
            speed -= 3
        elif lvl == 9:
            speed -= 2
        elif lvl in [10,13,16,19,29]:
            speed -= 1
        if lvl > 99:
            lvl = 99
            speed = 48
    if lines > 999:
        lines = 999

def getCollision():
    global ghostShape,ghostCollided,collided,left_collided,right_collided

    collided = False
    ghostCollided = False
    left_collided = False
    right_collided = False

    ghostShape.x = currentShape.x
    ghostShape.y = currentShape.y-1
    ghostShape.rotation = currentShape.rotation-1
    ghostShape.rotate(1)

    while not ghostCollided:
        ghostShape.y += 1
        if ghostShape.y == (20-ghostShape.height):
            ghostCollided = True
        else:
            tempMap = deepcopy(tileMap)
            for piece in ghostShape.pieces:
                x = ghostShape.x+piece.localx
                y = ghostShape.y+piece.localy
                tempMap[y][x] = 'x'
            x = 0
            y = 0
            for row in tempMap:
                for c in row:
                    if c == 'x':
                        if not (tempMap[y+1][x] in 'x '):
                            ghostCollided = True
                            break
                    x += 1
                y += 1
                x = 0
            del tempMap
    
    tempMap = deepcopy(tileMap)
    for piece in currentShape.pieces:
        x = currentShape.x+piece.localx
        y = currentShape.y+piece.localy
        tempMap[y][x] = 'x'
    x = 0
    y = 0
    for row in tempMap:
        for c in row:
            if c == 'x':
                try:
                    if currentShape.y == (20-currentShape.height):
                            collided = True
                    elif not (tempMap[y+1][x] in 'x '):
                        collided = True
                except: collided = True
                
                try:
                    if currentShape.x <= 0:
                        left_collided = True
                    elif not (tempMap[y][x-1] in 'x '):
                        left_collided = True
                except: left_collided = True

                try:
                    if currentShape.x >= 10-currentShape.width:
                        right_collided = True
                    elif not (tempMap[y][x+1] in 'x '):
                        right_collided = True
                except: right_collided = True
            x += 1
        y += 1
        x = 0
    del tempMap

replay = True

# - Timers - #
class Timer:
    def __init__(self, duration) -> None:
        self.duration = duration
        self.finished = False

        self.startTime = 0
        self.active = False

    def activate(self):
        self.active = True
        self.finished = False
        self.startTime = pygame.time.get_ticks()

    def deactivate(self):
        self.active = False
        self.finished = True
        self.startTime = 0

    def update(self):
        currentTime = pygame.time.get_ticks()
        if self.active and currentTime - self.startTime >= (self.duration*(1000/60)):
            self.deactivate()

timers = {
    'fall': Timer(speed),
    'move': Timer(16),
    'soft down': Timer(2),
    "demeter": Timer(0.5*60)
}
# - Timers - #

# Main game loop
while replay:
    clearMap()
    stamps = []
    flash_stamps = []
    left_collided = False
    right_collided = False
    holding_input = False
    holding_down = False
    running = True
    reset = False
    closed = False
    paused = False
    dementia = True
    AREpaused = False
    AREpauseLength = 0
    linesCleared = 0
    demeter = 0

    offset = pygame.Vector2(0,0)
    lastOffset = pygame.Vector2(0,0)
    deltaTime = 0
    thud = 0

    spreadParticles = []

    holdAnimFrames = -1
    holdAnim_mode = 'current to hold'
    # possible modes: 'current to hold', 'swap'
    holdAnim_oldCurrentPos = (0,0)
    holdAnim_newCurrentPos = (0,0)
    holdAnim_oldCurrentRot = 0

    nextAnimFrames = -1

    lines = 0
    lvl = 0
    speed = 48
    Shapes.bag = []
    currentShape = Shapes.fromBag()
    currentShape.x = 4
    currentShape.y = 0
    currentShape.rotation = 1
    currentShape.rotate(-1)
    nextShape = Shapes.fromBag()
    nextShape.x = 4
    nextShape.y = 0
    nextShape.rotation = 1
    nextShape.rotate(-1)
    holdShape = None
    holdCount = 0
    ghostShape = Shapes.shape('G'+currentShape.id,'ghost',currentShape.hitbox)

    timers['fall'].activate()
    timers['move'].deactivate()
    timers['soft down'].deactivate()
    timers['demeter'].deactivate()
    while running and (not reset):  
        deltaTime = clock.tick(frameRate) / 1000
        if not paused:
            for timer in timers.values():
                timer.update()
        for event in pygame.event.get():
            # Detect window closed
            if event.type == pygame.QUIT:
                closed = True
                replay = False
            if event.type == pygame.KEYDOWN:
                if event.key in controls['dementia']:
                    if not AREpaused:
                        dementia = not dementia
                        if (not dementia) and demeter <= 0:
                            dementia = True
                            demeter = 0

                if event.key in controls['toggle pivot indicator']:
                    showPivot = not showPivot
                if event.key in controls['pause']:
                    paused = not paused
                if event.key in controls['reset']:
                    subprocessRun(["python",osPath.abspath(__file__)])
                    exit()
                if event.key in controls['quit']:
                    closed = True
                    replay = False
                if event.key in controls['toggle ghost']:
                    show_ghost = not show_ghost
                    demeter += 100
                if (not paused) and (not AREpaused) and (holdAnimFrames < 0 and nextAnimFrames < 0) and event.key in controls['left rotate'] and currentShape.getCenterPiece():
                    currentShape.rotate(-1)
                    i = True
                    out = False
                    for piece in currentShape.pieces:
                        if getTileonMap(currentShape.x+piece.localx,currentShape.y+piece.localy) == 'OUT' or getTileonMap(currentShape.x+piece.localx,currentShape.y+piece.localy) != '':
                            i = False
                            out = getTileonMap(currentShape.x+piece.localx,currentShape.y+piece.localy) == 'OUT'
                            break
                    if (not i) and out:
                        oldX = currentShape.x
                        ii = False
                        for piece in currentShape.pieces:
                            if currentShape.x+piece.localx >= 10:
                                currentShape.x = 10-currentShape.width
                                ii = True
                                break
                            elif currentShape.x+piece.localx <= -1:
                                currentShape.x = 0
                                ii = True
                                break
                        if ii:
                            i = True
                            for piece in currentShape.pieces:
                                if getTileonMap(currentShape.x+piece.localx,currentShape.y+piece.localy) == 'OUT' or getTileonMap(currentShape.x+piece.localx,currentShape.y+piece.localy) != '':
                                    i = False
                                    break
                            if not i:
                                currentShape.x = oldX
                    if i:
                        getCollision()
                    else:
                        currentShape.rotate(1)
                        getCollision()
                if (not paused) and (not AREpaused) and (holdAnimFrames < 0 and nextAnimFrames < 0) and event.key in controls['right rotate'] and currentShape.getCenterPiece():
                    currentShape.rotate(1)
                    i = True
                    out = False
                    for piece in currentShape.pieces:
                        if getTileonMap(currentShape.x+piece.localx,currentShape.y+piece.localy) == 'OUT' or getTileonMap(currentShape.x+piece.localx,currentShape.y+piece.localy) != '':
                            i = False
                            out = getTileonMap(currentShape.x+piece.localx,currentShape.y+piece.localy) == 'OUT'
                            break
                    if (not i) and out:
                        oldX = currentShape.x
                        ii = False
                        for piece in currentShape.pieces:
                            if currentShape.x+piece.localx >= 10:
                                currentShape.x = 10-currentShape.width
                                ii = True
                                break
                            elif currentShape.x+piece.localx <= -1:
                                currentShape.x = 0
                                ii = True
                                break
                        if ii:
                            i = True
                            for piece in currentShape.pieces:
                                if getTileonMap(currentShape.x+piece.localx,currentShape.y+piece.localy) == 'OUT' or getTileonMap(currentShape.x+piece.localx,currentShape.y+piece.localy) != '':
                                    i = False
                                    break
                            if not i:
                                currentShape.x = oldX
                    if i:
                        getCollision()
                    else:
                        currentShape.rotate(-1)
                        getCollision()
                if (not paused) and (not AREpaused) and (holdAnimFrames < 0 and nextAnimFrames < 0) and event.key in controls['hold'] and holdCount == 0:
                    if holdShape == None:
                        holdAnim_mode = 'current to hold'
                        holdAnim_oldCurrentPos = (96+(8*(currentShape.x))+2,40+(8*(currentShape.y))+10)
                        holdAnim_oldCurrentRot = currentShape.rotation
                        currentShape.x = 4
                        currentShape.y = 0
                        currentShape.rotation = 1
                        currentShape.rotate(-1)
                        holdShape = currentShape
                        nextShape.x = 4
                        nextShape.y = 0
                        nextShape.rotation = 1
                        nextShape.rotate(-1)
                        currentShape = nextShape
                        ghostShape = Shapes.shape('G'+currentShape.id,'ghost',currentShape.hitbox)
                        nextShape = Shapes.fromBag()
                        nextAnimFrames = len(moveShapeAnimCurve)
                    else:
                        holdAnim_mode = 'swap'
                        holdAnim_oldCurrentPos = (96+(8*(currentShape.x))+2,40+(8*(currentShape.y))+10)
                        holdAnim_oldCurrentRot = currentShape.rotation
                        currentShape.x = 4
                        currentShape.y = 0
                        holdAnim_newCurrentPos = (96+(8*(currentShape.x))+2,40+(8*(currentShape.y))+10)
                        currentShape.rotation = 1
                        currentShape.rotate(-1)
                        holdShape.x = 4
                        holdShape.y = 0
                        holdShape.rotation = 1
                        holdShape.rotate(-1)
                        temp = currentShape
                        currentShape = holdShape
                        holdShape = temp
                        del temp
                        ghostShape = Shapes.shape('G'+currentShape.id,'ghost',currentShape.hitbox)
                    holdCount += 1
                    getCollision()
                    holdAnimFrames = len(moveShapeAnimCurve)
        if (not paused) and (not AREpaused) and (holdAnimFrames < 0 and nextAnimFrames < 0):
            # Input
            if (not getInp('move left')) and (not getInp('move right')):
                holding_input = False
                timers['move'].deactivate()
            if getInp('move left') and (not getInp('move right')) and (not left_collided) and timers['move'].finished:
                currentShape.x -= 1
                getCollision()
                if holding_input == False:
                    timers['move'].duration = 16
                else:
                    timers['move'].duration = 6
                timers['move'].activate()
                holding_input = True
            if getInp('move right') and (not getInp('move left')) and (not right_collided) and timers['move'].finished:
                currentShape.x += 1
                getCollision()
                if holding_input == False:
                    timers['move'].duration = 16
                else:
                    timers['move'].duration = 6
                timers['move'].activate()
                holding_input = True
            if holding_down and not (getInp('soft down') or getInp('hard down')):
                holding_down = False
            if ((not holding_down) and getInp('soft down')) and currentShape.y + currentShape.height < 20 and not collided:
                shakeScreen(pygame.Vector2(0,50))
                if (timers['soft down'].finished or speed == 1):
                    currentShape.y += 1
                    getCollision()
                    timers['soft down'].duration = 2
                    timers['soft down'].activate()
                    timers['fall'].activate()
            if ((not holding_down) and getInp('hard down')) and currentShape.y < ghostShape.y and not collided:
                currentShape.y = ghostShape.y
                shakeScreen(pygame.Vector2(0,100))
                getCollision()

        # Rendering
        screen = pygame.image.load('images/gui/bg.png').convert_alpha()
        screen.fill('black')
        if not AREpaused:
            stamps = []
            y = 0
            for row in tileMap:
                x = 0
                for tile in row:
                    if tile != '':
                        sprite = pygame.sprite.Sprite()
                        sprite.image = pygame.image.load(f'images/pieces/{all_shapes[tile].piece_sprite}.png').convert_alpha()
                        sprite.rect = sprite.image.get_rect()
                        sprite.globaly = y
                        stamps.append(((96+8*x,40+8*y),sprite))
                    x += 1
                y += 1
        drawStamps()
        if AREpaused:
            flashStamps()
        # Test game over
        for c in tileMap[0]:
            if c != '':
                running = False
                break
        if nextAnimFrames < 0:
            screen.blit(nextShape.gui_sprite,(191+2,95+10))
        else:
            nextShapeGui_scaled = pygame.transform.scale(nextShape.gui_sprite.copy(),pygame.Vector2(33,42)*(0.01*moveShapeAnimCurve[nextAnimFrames-1]))
            screen.blit(nextShapeGui_scaled,pygame.Vector2(193+15.5,105+21)-(pygame.Vector2(nextShapeGui_scaled.get_size())/2))
        if holdAnimFrames < 0:
            if holdShape != None:
                screen.blit(holdShape.gui_sprite,(80-holdShape.gui_sprite.get_width(),95))
            if nextAnimFrames < 0:
                if show_ghost:
                    ghostShape.draw()
                currentShape.draw()

        layer3 = pygame.surface.Surface((256,224), pygame.SRCALPHA)
        layer1 = pygame.image.load('images/gui/bg.png').convert_alpha()
        screen.blit(layer1,(0,0))
        screen.blit(layer3,(0,0))
        writeNums((59-11,72),lines,3)
        writeNums((204,72),lvl,2)

        if doParticles:
            for _spreadParticles in spreadParticles:
                if len(_spreadParticles.particles) == 0:
                    spreadParticles.remove(_spreadParticles)
                else:
                    if (not paused) and running:
                        _spreadParticles.draw(screen)

        if not paused and holdAnimFrames >= 0:
            if holdAnimFrames > 0:
                if holdAnim_mode == 'current to hold':
                    diff = pygame.Vector2(holdAnim_oldCurrentPos) - pygame.Vector2(80-holdShape.gui_sprite.get_width(),95)
                    rotDiff = 0
                    if holdAnim_oldCurrentRot >= 2:
                        rotDiff = (90*holdAnim_oldCurrentRot)
                    else:
                        rotDiff = (-90*holdAnim_oldCurrentRot)
                    rotated = pygame.transform.rotate(holdShape.gui_sprite.copy(), (moveShapeAnimCurve[len(moveShapeAnimCurve)-(holdAnimFrames)]*0.01)*rotDiff)
                    screen.blit(rotated,holdAnim_oldCurrentPos - ((moveShapeAnimCurve[holdAnimFrames-1]*0.01)*diff))
                elif holdAnim_mode == 'swap':
                    diff = pygame.Vector2(holdAnim_oldCurrentPos) - pygame.Vector2(80-holdShape.gui_sprite.get_width(),95)
                    rotDiff = 0
                    if holdAnim_oldCurrentRot >= 2:
                        rotDiff = (90*holdAnim_oldCurrentRot)
                    else:
                        rotDiff = (-90*holdAnim_oldCurrentRot)
                    rotated = pygame.transform.rotate(holdShape.gui_sprite.copy(), (moveShapeAnimCurve[len(moveShapeAnimCurve)-(holdAnimFrames)]*0.01)*rotDiff)
                    screen.blit(rotated,holdAnim_oldCurrentPos - ((moveShapeAnimCurve[holdAnimFrames-1]*0.01)*diff))
                    diff = pygame.Vector2(80-holdShape.gui_sprite.get_width(),95) - pygame.Vector2(holdAnim_newCurrentPos)
                    screen.blit(currentShape.gui_sprite,pygame.Vector2(80-holdShape.gui_sprite.get_width(),95) - ((moveShapeAnimCurve[holdAnimFrames-1]*0.01)*diff))
            holdAnimFrames -= 1
        if not paused and nextAnimFrames >= 0:
            if nextAnimFrames > 0:
                diff = pygame.Vector2(193,105) - (130,50)
                screen.blit(currentShape.gui_sprite.copy(),(193,105) - ((moveShapeAnimCurve[nextAnimFrames-1]*0.01)*diff))
            else:
                timers['fall'].duration = speed
                timers['fall'].activate()
            nextAnimFrames -= 1

        pygame.draw.rect(screen,"#f6b93b", pygame.Rect(96, 211, demeter, 9))

        if paused and running:
            screen.blit(paused_overlay,(0,0))
        if not running:
            screen.blit(death_overlay,(0,0))

        scaled = pygame.transform.scale(screen, display.get_size())
        shakeScreen(pygame.Vector2(0,0))
        display.fill('black')
        display.blit(scaled, (-8*(display.get_width()//screen.get_width())+offset[0]*100, offset[1]*100-50))
        pygame.display.flip()

        if (not paused) and (not AREpaused):
            if not dementia and demeter > 0:
                if timers['demeter'].finished:
                    timers['demeter'].activate()
                    demeter -= 2
            if demeter <= 0:
                demeter = 0
                dementia = True
            # Collision and line clearing
            getCollision()

            i = 0
            cleared_count = 0
            for row in tileMap:
                cleared = True
                for x in row:
                    if x == '':
                        cleared = False
                        break
                if cleared:
                    clearLine(i)
                    cleared_count += 1
                    shakeScreen(pygame.Vector2(0,thud*10))
                i += 1


            if collided and (timers['fall'].finished or getInp('hard down')):
                currentShape.stamp()
                nextShape.x = 4
                nextShape.y = 0
                nextShape.rotation = 1
                nextShape.rotate(-1)
                currentShape = nextShape
                ghostShape = Shapes.shape('G'+currentShape.id,'ghost',currentShape.hitbox)
                nextShape = Shapes.fromBag()
                nextAnimFrames = len(moveShapeAnimCurve)
                holdCount = 0
                if getInp('soft down') or getInp('hard down'):
                    holding_down = True
            elif timers['fall'].finished and (holdAnimFrames < 0 and nextAnimFrames < 0) and not ((not holding_down) and (getInp('soft down') or getInp('hard down'))):
                currentShape.y += 1
                timers['fall'].duration = speed
                timers['fall'].activate()
        if AREpaused and AREpauseLength > 0:
            AREpauseLength -= 1
            if AREpauseLength == 0:
                AREpaused = False
                temp = []
                topBadY = 20
                for stamp in flash_stamps:
                    y = stamp[1].globaly
                    if y < topBadY:
                        topBadY = y
                for pos,piece in stamps:
                    if piece.globaly < topBadY:
                        piece.globaly += linesCleared
                        temp.append(((pos[0],pos[1]+8*linesCleared),piece))
                    else:
                        temp.append((pos,piece))
                flash_stamps = []
                stamps = temp
                linesCleared = 0
        if closed:
            running = False
    # Window closed logic
    else:
        game_over = True
        while (game_over and not closed) and not reset:
            for event in pygame.event.get():
                # Detect window closed
                if event.type == pygame.QUIT:
                    game_over = False
                    replay = False
                if event.type == pygame.KEYDOWN:
                    if event.key in controls['quit']:
                        closed = True
                        replay = False
                    if event.key == pygame.K_RETURN:
                        game_over = False
else:
    print('crashed :(') # we love how this is still here lmao