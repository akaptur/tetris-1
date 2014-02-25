import os, sys, pygame, random, pdb
from pygame.locals import *
from random import choice

# Global variables that need to be declared early (e.g. used in game loop)
global game_in_progress, paused, game_over_var, piece

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

        # get the rectangle for the whole button
        self.rect = self.buttonbg.get_rect()
        self.rect = pygame.Rect(add_tuples(self.rect, (self.location_xy[0], self.location_xy[1], 0, 0)))    

        # add the text
        self.text = basicFont.render(self.text, True, black)
        self.textrect = self.text.get_rect()

        # position the button text so it is in the center of the button object
        self.textrect.centerx = (screen_width+edge_tetris) / 2
        self.textrect.centery = self.location_xy[1] + button_height / 2

    def show_button(self):
        background.blit(self.buttonbg, self.location_xy)
        background.blit(self.text, self.textrect)

class IterRegistry(type):
    def __iter__(cls):
        return iter(cls._registry)

class Block(pygame.sprite.Sprite):
    __metaclass__ = IterRegistry
    _registry = []

    # Initialise, move and stop a tetris block
    def __init__(self, color, width, height):
        # Track this instance
        self._registry.append(self)

        pygame.sprite.Sprite.__init__(self) #call Sprite initializer
        self.image = pygame.Surface([width, height])

        # Fetch the rectangle object that has the dimensions of the 
        # image. The position of this object is updated
        # by setting the values of rect.x and rect.y
        self.image, self.rect = load_image(color + '.bmp', -1)

class Piece(pygame.sprite.Group):
    def __init__(self, chosenPiece = '', rotation = 1, pos_x = 210, pos_y = 0):
        # Create list of blocks in piece
        self.blocks = []

        pygame.sprite.Group.__init__(self) #call Sprite initializer

        self.chosenpiece = chosenPiece
        self.rotation = rotation

        # Create random new piece if there aren't any moving
        if self.chosenpiece == '':
            self.chosenpiece = random.choice(pieces.keys())

        thisrotation = pieces[self.chosenpiece]['rotation' + "_" + str(self.rotation)]
        thiscolor = pieces[self.chosenpiece]['color']

        # Create pieces according to their specs
        for x, y in thisrotation:
            self.prep_new_block(x, y, thiscolor)

        # Adjust the positions to be correct
        # First, we adjust for height (y)
        n_pos_x = { }
        n_pos_y = []
        for sprite in moving_list:
            n_pos_x[sprite.rect.x] = 1
            n_pos_y.append(sprite.rect.y)

        y_difference = pos_y - max(n_pos_y)

        if y_difference > 0:
            for sprite in moving_list:
                sprite.rect.y += y_difference

        # Next, we adjust for horizontal placement (x)
        pos_x = round_down(pos_x)

        # Get unique values of x, find midpoint
        n_x_values = n_pos_x.keys()
        x_mid = ( max(n_x_values) + min(n_x_values) ) / 2
        x_mid = round_down(x_mid)

        # See difference between old midpoint and new midpoint
        x_difference = pos_x - x_mid

        # Finally, make the adjustments, also double check if over an edge
        f_pos_x = []
        for sprite in moving_list:
            new_x = sprite.rect.x + x_difference
            sprite.rect.x = new_x
            f_pos_x.append(new_x)

        # Check if over left edge
        if min(f_pos_x) < 0:
            for sprite in moving_list:
                sprite.rect.x += -min(f_pos_x)

        # Check if over right edge
        if max(f_pos_x) >= 420:
            for sprite in moving_list:
                sprite.rect.x -= 42

    def prep_new_block(self, x_adj, y_adj, color):
        # Create tetris block (object)
        block = Block(color, 42, 42)

        # Set block location
        block.rect.x = ( edge_tetris / 2 ) - ( block_size / 2 ) + x_adj - block_size/2
        block.rect.y = 0 + y_adj

        # Add block to list
        moving_list.add(block)

    def update(self, updateType, direction = ''):
        if updateType == "move":

            for sprite in moving_list:
                if direction == '':
                    sprite.rect.y += 42
                if direction == 'right':
                    sprite.rect.x += 42
                if direction == 'left':
                    sprite.rect.x -= 42

            self.checkCollide(direction)

        if updateType == "moveBack":
            for sprite in moving_list:
                # If a vertical collision happens on the top row, it's game over!
                if sprite.rect.y <= 42:
                    game_over()

                # Otherwise, bump it up one
                sprite.rect.y -= 42

        if updateType == "reverse":
            for sprite in moving_list:
                if direction == "left":
                    sprite.rect.x += 42
                elif direction == "right":
                    sprite.rect.x -= 42

        if updateType == 'checkEdges':
            for sprite in moving_list:
                if sprite.rect.x < 0:
                    self.update("reverse", "left")
                if sprite.rect.x >= 420:
                    self.update("reverse", "right")

    def checkCollide(self, direction):
            self.checkCollision(direction)
            self.checkIfEndOfScreen()
            self.update('checkEdges')

    def checkIfEndOfScreen(self):
        for sprite in moving_list:
            if sprite.rect.y >= (screen_height - block_size):
                self.stop()

    def checkCollision(self, direction = ''):
        col = None
        col = pygame.sprite.groupcollide(moving_list, placed_list, False, False)

        if not col:
            pass

        elif direction == '':
            self.update("moveBack")
            self.stop()

        elif direction == 'left' or direction == 'right':
            self.update("reverse", direction)

    def stop(self):
        for sprite in moving_list:
            placed_list.add(sprite)

            # Add it to the row group
            placed_row[sprite.rect.y].add(sprite)
         
        moving_list.empty()

    def rotate(self):
        # Rotation will be achieved by deleting the current piece, and creating a new one rotated 90 degrees

        # First, get x and y coordinates of all blocks in piece
        y_list = []
        x_list = { }
        for sprite in moving_list:
            x_list[sprite.rect.x] = 1
            y_list.append(sprite.rect.y)

        # Get highest value of y (lowest position on screen)
        y_low = max(y_list)
        
        # Get unique values of x
        x_values = x_list.keys()

        x_mid = ( max(x_values) + min(x_values) ) / 2

        # Now delete the existing piece, and check the current rotation
        moving_list.empty()

        if self.rotation <= 3:
            self.rotation += 1
        else:
            self.rotation = 1

        # Finally, create the new piece
        piece = Piece(self.chosenpiece, self.rotation, x_mid, y_low)

def stop_object(movingsprite):
    for instance in Block.instances:
        # Stop the sprite from moving
        instance.stop()

        # Move all sprites from the moving group to the placed group
        moving_list.remove(instance)
        placed_list.add(instance)

def clear_row(thisrow):
    # Remove all sprites in row from the placed list
    for sprite in iter(placed_row[thisrow]):
        placed_list.remove(sprite)

    # Create a surface for the animation
        animate_row.update( { thisrow : '1' } )

    # And then clear this row
    placed_row[thisrow].empty()

    # Now shift all higher sprites down one row
    # We work through the rows in reverse order (from bottom to top, so we only move each sprite once)
    rows_reverse = rows[::-1]

    for row in rows_reverse:
        for sprite in iter(placed_row[row]):
            if sprite.rect.y != thisrow and sprite.rect.y < thisrow:
                placed_row[sprite.rect.y].remove(sprite)
                placed_row[sprite.rect.y + 42].add(sprite)
                sprite.rect.y += 42

def animate_rows():
    animate_surface = None
    animate_surface = pygame.Surface(screen.get_size())
    animate_surface.fill(transparent)
    animate_surface.set_colorkey(transparent)

    # Load the images
    f1 = pygame.image.load("assets/flash1.bmp")
    f2 = pygame.image.load("assets/flash2.bmp")
    f1rect, f2rect = f1.get_rect(), f2.get_rect()

    sprite_list = {}
    sprites = []

    # Generate sprites for each animation row
    for row in animate_row:
        if animate_row[row] == '1':
            sprite_list[row] = { 'f1': f1rect.copy(), 'f2': f2rect.copy() }

            # Position the images
            sprite_list[row]['f1'].y, sprite_list[row]['f2'].y = row, row

            print sprite_list[row]['f1']

            #Draw animation
            animate_surface.blit(f1, sprite_list[row]['f1'])

    # Animate
    screen.blit(animate_surface, (0, 0))
    pygame.display.flip()
    pygame.time.wait(50)

    for row in animate_row:
        if animate_row[row] == '1':
            #Draw animation 2
            animate_surface.blit(f2, sprite_list[row]['f2'])

    # Second animation
    screen.blit(animate_surface, (0, 0))
    pygame.display.flip()
    pygame.time.wait(50)

    # Clear animation row list
    for i in rows:
        animate_row.update({i: ''})

def start_game():
    global moving_list
    global placed_list
    global placed_row
    global game_in_progress

    game_in_progress = True

    # Create 2 lists to hold all tetris blocks on the screen
    moving_list = pygame.sprite.Group()
    placed_list = pygame.sprite.Group()

    # Create a sprite group for each of the rows we care about
    placed_row = [pygame.sprite.Group()] * (714 + 1)
    for i in rows:
        placed_row[i] = pygame.sprite.Group()

    # Play music
    bgmusic.play(-1)

def game_over():
    global game_in_progress, text, game_over_var, foreground
    game_in_progress = False
    game_over_var = True
    bgmusic.stop()

    text = "GAME OVER!"
    text = basicFont.render(text, True, black)
    textpos = text.get_rect()
    textpos.centerx = background.get_rect().centerx
    textpos.centery = background.get_rect().centery
    foreground.blit(text, textpos)

    # Show start over button
    btn_restart.show_button()

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
    fullname = os.path.join('assets', name)
    print fullname
    try:
        sound = pygame.mixer.Sound(fullname)
    except pygame.error, message:
        print 'Cannot load sound:', wav
        raise SystemExit, message
    return sound

def force_redraw():
    screen.blit(background, (0, 0))
    moving_list.draw(screen)
    placed_list.draw(screen)
    pygame.display.flip()

def restart():
    main()

def round_down(x, base=42):
    return int(base * round(float(x)/base))

def main():
    global edge_tetris, screen_width, screen_height, margin, button_height, button_text_size, block_size
    global game_in_progress, paused, game_over_var, draw, allows_clicks
    global rows, bgmusic, music, pieces, black, lightblue, screen, background, foreground, transparent, basicFont
    global btn_start, btn_exit, btn_pause, btn_restart, piece, animate_row, row_cleared

    # Define dimensions
    edge_tetris = 420
    screen_width = 600
    screen_height = 756
    margin = 20
    button_height = 40
    button_text_size = 48
    block_size = 42

    # List of all the rows that blocks can be in (y axis)
    rows = [42, 84, 126, 168, 210, 252, 294, 336, 378, 420, 462, 504, 546, 588, 630, 672, 714]

    # Global variables
    game_in_progress = False
    paused = False
    game_over_var = False
    draw = True
    allows_clicks = True
    animate_row = { }
    for i in rows:
        animate_row.update({i: ''})
    row_cleared = False

    # Sounds
    music = os.path.join('assets', 'music_a.wav')
    pygame.mixer.init()
    bgmusic = pygame.mixer.music
    bgmusic.load(music)

    # Types of pieces
    pieces = {}
    pieces['long'] = { 'name': 'long', 'color': 'cyan', 'rotation_1' : ( (-42, 0), (0, 0), (42, 0), (84, 0) ), 'rotation_2' : ( (0, -42), (0, 0), (0, 42), (0, 84) ), 'rotation_3' : ( (-42, 0), (0, 0), (42, 0), (84, 0) ), 'rotation_4' : ( (0, -42), (0, 0), (0, 42), (0, 84) ) }
    pieces['cornerright'] = { 'name': 'cornerright', 'color': 'blue', 'rotation_1' : ( (42, -42), (-42, 0), (0, 0), (42, 0) ), 'rotation_2' : ( (-42, -42), (-42, 0), (-42, 42), (0, 42) ), 'rotation_3' : ( (-42, -42), (-42, 0), (42, -42), (0, -42) ), 'rotation_4' : ( (0, -42), (42, -42), (42, 0), (42, 42) ) }
    pieces['cornerleft'] = { 'name': 'cornerleft', 'color': 'orange', 'rotation_1' : ( (-42, -42), (-42, 0), (0, 0), (42, 0) ), 'rotation_2' : ( (0, 42), (0, 0), (0, -42), (42, -42) ), 'rotation_3' : ( (-42, 0), (0, 0), (42, 0), (42, 42) ), 'rotation_4' : ( (-42, 42), (0, 42), (0, 0), (0, -42) ) }
    pieces['square'] = { 'name': 'square', 'color': 'yellow', 'rotation_1' : ( (0, -42), (0, 0), (42, -42), (42, 0) ), 'rotation_2' : ( (0, -42), (0, 0), (42, -42), (42, 0) ), 'rotation_3' : ( (0, -42), (0, 0), (42, -42), (42, 0) ), 'rotation_4' : ( (0, -42), (0, 0), (42, -42), (42, 0) ) }
    pieces['zigleft'] = { 'name': 'zigleft', 'color': 'green', 'rotation_1' : ( (-42, 0), (0, 0), (0, -42), (42, -42) ), 'rotation_2' : ( (0, -42), (0, 0), (42, 0), (42, 42) ), 'rotation_3' : ( (-42, 0), (0, 0), (0, -42), (42, -42) ), 'rotation_4' : ( (0, -42), (0, 0), (42, 0), (42, 42) ) }
    pieces['zigright'] = { 'name': 'zigright', 'color': 'red', 'rotation_1' : ( (-42, -42), (0, -42), (0, 0), (42, 0) ), 'rotation_2' : ( (0, 42), (0, 0), (42, 0), (42, -42) ), 'rotation_3' : ( (-42, -42), (0, -42), (0, 0), (42, 0) ), 'rotation_4' : ( (0, 42), (0, 0), (42, 0), (42, -42) ) }
    pieces['tbar'] = { 'name': 'tbar', 'color': 'purple', 'rotation_1' : ( (-42, 0), (0, 0), (42, 0), (0, -42) ), 'rotation_2' : ( (0, -42), (0, 0), (0, 42), (42, 0) ), 'rotation_3' : ( (-42, 0), (0, 0), (42, 0), (0, 42) ), 'rotation_4' : ( (0, -42), (0, 0), (0, 42), (-42, 0) ) }

    # Colours
    black = (0,0,0)
    lightblue = (150, 204, 255)

    # Size of window
    size = width, height = screen_width, screen_height
    screen = pygame.display.set_mode(size)
    pygame.display.set_caption('Tetris')

    # Set background image
    background = pygame.image.load('assets/background.gif').convert()

    # Set foreground image
    foreground, transparent = None, (1, 2, 3)
    foreground = pygame.Surface(screen.get_size())
    foreground.fill(transparent)
    foreground.set_colorkey(transparent)

    # Set fonts
    basicFont = pygame.font.SysFont(None, button_text_size)

    # Define action buttons
    btn_start = Button('Start', (edge_tetris+margin, 420))
    btn_pause = Button('Pause', (edge_tetris+margin, 420))
    btn_exit = Button('Exit', (edge_tetris+margin, 500))
    btn_restart = Button('Restart', (edge_tetris+margin, 420))

    # Show action buttons
    btn_start.show_button()
    btn_exit.show_button()

    # Define clock
    clock = pygame.time.Clock()

    gravity_delay = pygame.USEREVENT + 1
    pygame.time.set_timer(pygame.USEREVENT + 1, 500)

    # Force a seed (order of pieces), for debugging
    # random.seed(9879789)

    # Constant loop to check for events (the game loop)
    while 1:
        # Ensure game does not run faster than 60 frames/second
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT: sys.exit()

            # handle mouse clicks
            if pygame.mouse.get_pressed()[0] and allows_clicks:

                # Prevent multiple clicks
                allows_clicks = False
                pygame.time.set_timer(pygame.USEREVENT + 2, 300)

                # Start/pause button
                if btn_start.rect.collidepoint(pygame.mouse.get_pos()):

                    if game_in_progress == False:
                        # If game over, restart the game
                        if game_over_var:
                            restart()

                        # Otherwise, just start
                        start_game()
                        btn_pause.show_button()
                    elif paused:
                        paused = False
                        btn_pause.show_button()
                        bgmusic.unpause()
                    elif game_over_var:
                        restart()
                    else:
                        paused = True
                        btn_start.show_button()
                        bgmusic.pause()

                # Exit button
                if btn_exit.rect.collidepoint(pygame.mouse.get_pos()):
                    pygame.quit()

            if not paused and game_in_progress:

                # Handle keyboard presses
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP: # UP Arrow
                        piece.rotate()
                    if event.key == pygame.K_DOWN: # DOWN Arrow
                        piece.update("move")
                    if event.key == pygame.K_RIGHT: # RIGHT Arrow
                        piece.update("move", "right")
                    if event.key == pygame.K_LEFT: # LEFT Arrow
                        piece.update("move", "left")

                if event.type == pygame.USEREVENT + 1:
                    if game_in_progress == True:
                        draw = False
                        piece.update("move")
                        draw = True

            if event.type == pygame.USEREVENT + 2:
                    allows_clicks = True      

        if game_in_progress:
            if not moving_list:
                # Create new piece
                piece = Piece()

        # Check if 10 in a row
        if game_in_progress:
            for i in rows:
                if len(placed_row[i]) == 10:
                    clear_row(i)
                    row_cleared = True

        if row_cleared:
            # Animate row clearing
            animate_rows()
            row_cleared = False

        # Draw everything
        screen.blit(background, (0, 0))
        if game_in_progress and draw:
            moving_list.draw(screen)
            placed_list.draw(screen)

        if game_over_var:
            screen.blit(foreground, (0, 0))

        pygame.display.flip()

if __name__ == "__main__":
    main()
