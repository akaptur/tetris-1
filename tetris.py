import os, sys, pygame, random
from pygame.locals import *
from random import choice

pygame.init()

class Button:
    # On-screen button, with optional text on top of it
    def __init__(self, text, location_xy):
        # store attributes on object
        self.text = text
        self.location_xy = location_xy

        # create the button object
        self.buttonbg = pygame.Surface([screen_width-edge_tetris-2*margin, button_height])
        self.buttonbg.fill(lightblue)
        self.buttonbg = self.buttonbg.convert_alpha()

        # get the rectangle for the whole button
        self.rect = self.buttonbg.get_rect()
        self.rect = pygame.Rect(add_tuples(self.rect, (self.location_xy[0], self.location_xy[1], 0, 0)))    

        # add the text
        basicFont = pygame.font.SysFont(None, button_text_size)
        self.text = basicFont.render(self.text, True, black)
        self.textrect = self.text.get_rect()

        # position the button text so it is in the center of the button object
        self.textrect.centerx = (screen_width+edge_tetris) / 2
        self.textrect.centery = self.location_xy[1] + button_height / 2

    def show_button(self):
        background.blit(self.buttonbg, self.location_xy)
        background.blit(self.text, self.textrect)

class Block(pygame.sprite.Sprite):
    instances = []

    # Initialise, move and stop a tetris block
    def __init__(self, color, width, height):
        # Track this instance
        self.instances.append(self)

        pygame.sprite.Sprite.__init__(self) #call Sprite initializer
        self.image = pygame.Surface([width, height])
        self.image.fill(color)
        self.image.set_colorkey(white)

        # Draw the ellipse
        pygame.draw.ellipse(self.image,color,[0,0,width,height])

        # Fetch the rectangle object that has the dimensions of the 
        # image. The position of this object is updated
        # by setting the values of rect.x and rect.y
        self.rect = self.image.get_rect()

        self.stopped = False

    def update(self):
        checkIfEndOfScreen(self)
        checkCollision(self)

        print self.rect

        if self.stopped != True and self in moving_list:
            # Move block down by some pixels
            self.rect.y += 42

    def rotate(self):
        pass

    def stop(self):
        self.stopped = True

class Piece():
    

def checkCollision(movingsprite):
    # movingsprite.rect.y += 42
    col = pygame.sprite.spritecollideany(movingsprite, placed_list, False)
    # movingsprite.rect.y -= 42
    if not col:
        # If no collisions, we don't do anything
        pass
    else:
        stop_object(movingsprite)

def stop_object(movingsprite):
    for instance in Block.instances:
        # Stop the sprite from moving
        instance.stop()

        # Move all sprites from the moving group to the placed group
        moving_list.remove(instance)
        placed_list.add(instance)

def checkIfEndOfScreen(movingsprite):
    if movingsprite.rect.y >= (screen_height - block_size):
        stop_object(movingsprite)

def start_game():
    global game_in_progress
    global moving_list
    global placed_list

    game_in_progress = True

    # Create 2 lists to hold all tetris blocks on the screen
    moving_list = pygame.sprite.Group()
    placed_list = pygame.sprite.Group()

def new_piece(piecename):

    thisname = piecename
    thisshape = pieces[piecename]['shape']
    thiscolor = pieces[piecename]['color']

    # Create the first block
    prep_new_block(0, 0, thiscolor)

    # Manually define tbar shape
    if thisname == 'tbar':
        prep_new_block(42, 0, thiscolor)
        prep_new_block(84, 0, thiscolor)
        prep_new_block(42, -42, thiscolor)
    else:
    # The other shapes can follow a ruleset from left to right
        pos_x = 0
        pos_y = 0

        for char in thisshape:
            if char == 'r': pos_x += 42
            if char == 'u': pos_y -= 42
            if char == 'd': pos_y += 42
            if char == 'l': pos_x -= 42

            prep_new_block(pos_x, pos_y, thiscolor)



def prep_new_block(x_adj, y_adj, color):
    # Create tetris block (object)
    block = Block(color, 42, 42)

    # Set block location
    block.rect.x = ( edge_tetris / 2 ) - ( block_size / 2 ) + x_adj
    block.rect.y = 0 + y_adj

    # Add block to list
    moving_list.add(block)

def add_tuples(a, b):
    # This function adds two tuples together, and returns their sum as the output (as if they were matrices)
    (ax, ay, aw, ah) = a
    (bx, by, bw, bh) = b
    return (ax+bx, ay+by, aw+bw, ah+bh)

def load_image(name, colorkey=None):
    # This function takes the name of an image and the 'colorkey' as inputs.
    # (Colorkey is used to represent the color of the image that is transparent)

    # Create a full pathname to the file.
    fullname = os.path.join('assets', name)

    # Try and load the file
    try:
        image = pygame.image.load(fullname)

    # If file not found, throw an error
    except pygame.error, message:
        print 'Cannot load image:', name
        raise SystemExit, message

    # Make a new copy of a Surface, and convert it so that its color format and depth match the display
    # This speeds up the blitting of the image later on
    image = image.convert()

    # Finally, if the user provided a colorkey, then set it to provide the effect of transparency
    if colorkey is not None:
        if colorkey is -1:
            colorkey = image.get_at((0,0))
        image.set_colorkey(colorkey, RLEACCEL)

    # Return the image, and the rectangular dimensions of the image
    return image, image.get_rect()

def load_sound(name):
    class NoneSound:
        def play(self): pass
    if not pygame.mixer:
        return NoneSound()
    fullname = os.path.join('data', name)
    try:
        sound = pygame.mixer.Sound(fullname)
    except pygame.error, message:
        print 'Cannot load sound:', wav
        raise SystemExit, message
    return sound

# Define dimensions
edge_tetris = 420
screen_width = 600
screen_height = 630
margin = 20
button_height = 40
button_text_size = 48
block_size = 42

# Global variables
game_in_progress = False

# Types of pieces
pieces = {}
pieces['long'] = { 'name': 'long', 'shape': 'rrr', 'color': (0, 175, 230) }
pieces['cornerright'] = { 'name': 'cornerright', 'shape': 'drr', 'color': (10, 115, 185) }
pieces['cornerleft'] = { 'name': 'cornerright', 'shape': 'rru', 'color': (250, 162, 57) }
pieces['square'] = { 'name': 'square', 'shape': 'rdl', 'color': (225, 225, 25) }
pieces['zigleft'] = { 'name': 'zigleft', 'shape': 'rur', 'color': (0, 170, 80) }
pieces['zigright'] = { 'name': 'zigright', 'shape': 'rdr', 'color': (210, 50, 40) }
pieces['tbar'] = { 'name': 'tbar', 'shape': '', 'color': (130, 90, 160) }


# Colours
black = (0,0,0)
white = (255, 255, 255)
lightblue = (150, 204, 255)

# Size of window
size = width, height = screen_width, screen_height
screen = pygame.display.set_mode(size)
pygame.display.set_caption('Tetris')

# Set background image
background = pygame.image.load('assets/background.gif').convert()

# Define action buttons
btn_start = Button('Start', (edge_tetris+margin, 420))
btn_exit = Button('Exit', (edge_tetris+margin, 500))

# Show action buttons
btn_start.show_button()
btn_exit.show_button()

# Define clock
clock = pygame.time.Clock()

gravity_delay = pygame.USEREVENT + 1
pygame.time.set_timer(pygame.USEREVENT + 1, 200)

random.seed(9879789)

# Constant loop to check for events
while 1:
    # Ensure game does not run faster than 60 frames/second
    clock.tick(60)

    for event in pygame.event.get():
        if event.type == pygame.QUIT: sys.exit()

        # handle mouse clicks
        if pygame.mouse.get_pressed()[0]:

            # Start button
            if btn_start.rect.collidepoint(pygame.mouse.get_pos()):
                start_game()

            # Exit button
            if btn_exit.rect.collidepoint(pygame.mouse.get_pos()):
                pygame.quit()

        if event.type == pygame.USEREVENT + 1:
            if game_in_progress == True:
                moving_list.update()
                print

    if game_in_progress:
        if not moving_list:
            # Create random new piece if there aren't any moving
            thepiece = random.choice(pieces.keys())
            new_piece(thepiece)

    # Draw everything
    screen.blit(background, (0, 0))
    if game_in_progress == True:
        moving_list.draw(screen)
        placed_list.draw(screen)
    pygame.display.flip()
