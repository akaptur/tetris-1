import os, sys, pygame, random, pdb
from pygame.locals import *
from random import choice

pygame.mixer.pre_init(44100, -16, 1, 512)
pygame.init()

class Game(object):
    def __init__(self, initial_level = 0):
        # Define dimensions
        self.edge_tetris = 420
        self.screen_width = 600
        self.screen_height = 756
        self.margin = 20
        self.button_height = 40
        self.button_text_size = 48
        self.small_text_size = 24
        self.block_size = 42

        # State of the game
        self.draw = True
        self.allows_clicks = True
        self.game_in_progress = False
        self.paused = False
        self.game_over_var = False
        self.score = 0
        self.level = 0
        self.initial_level = initial_level
        self.earned_level = 0
        self.lines_completed = 0
        self.speed = 550

        # Colours
        self.black = (0, 0, 0)
        self.lightblue = (150, 204, 255)
        self.white = (255, 255, 255)

        # List of all the rows that blocks can be in (y axis)
        self.rows = [42, 84, 126, 168, 210, 252, 294, 336, 378, 420, 462, 504, 546, 588, 630, 672, 714]

        self.animate_row = { }
        for i in self.rows:
            self.animate_row.update({i: ''})
        self.rows_cleared = 0

        # Sounds
        self.music = os.path.join('assets', 'music_a.wav')
        pygame.mixer.init()
        self.bgmusic = pygame.mixer.music
        self.bgmusic.load(self.music)
        self.clear_sound = load_sound('4-clear.wav')

        # Types of pieces
        self.pieces = {}
        self.pieces['long'] = { 'name': 'long', 'color': 'cyan', 'rotation_1' : ( (-42, 0), (0, 0), (42, 0), (84, 0) ), 'rotation_2' : ( (0, -42), (0, 0), (0, 42), (0, 84) ), 'rotation_3' : ( (-42, 0), (0, 0), (42, 0), (84, 0) ), 'rotation_4' : ( (0, -42), (0, 0), (0, 42), (0, 84) ) }
        self.pieces['cornerright'] = { 'name': 'cornerright', 'color': 'blue', 'rotation_1' : ( (42, -42), (-42, 0), (0, 0), (42, 0) ), 'rotation_2' : ( (-42, -42), (-42, 0), (-42, 42), (0, 42) ), 'rotation_3' : ( (-42, -42), (-42, 0), (42, -42), (0, -42) ), 'rotation_4' : ( (0, -42), (42, -42), (42, 0), (42, 42) ) }
        self.pieces['cornerleft'] = { 'name': 'cornerleft', 'color': 'orange', 'rotation_1' : ( (-42, -42), (-42, 0), (0, 0), (42, 0) ), 'rotation_2' : ( (0, 42), (0, 0), (0, -42), (42, -42) ), 'rotation_3' : ( (-42, 0), (0, 0), (42, 0), (42, 42) ), 'rotation_4' : ( (-42, 42), (0, 42), (0, 0), (0, -42) ) }
        self.pieces['square'] = { 'name': 'square', 'color': 'yellow', 'rotation_1' : ( (0, -42), (0, 0), (42, -42), (42, 0) ), 'rotation_2' : ( (0, -42), (0, 0), (42, -42), (42, 0) ), 'rotation_3' : ( (0, -42), (0, 0), (42, -42), (42, 0) ), 'rotation_4' : ( (0, -42), (0, 0), (42, -42), (42, 0) ) }
        self.pieces['zigleft'] = { 'name': 'zigleft', 'color': 'green', 'rotation_1' : ( (-42, 0), (0, 0), (0, -42), (42, -42) ), 'rotation_2' : ( (0, -42), (0, 0), (42, 0), (42, 42) ), 'rotation_3' : ( (-42, 0), (0, 0), (0, -42), (42, -42) ), 'rotation_4' : ( (0, -42), (0, 0), (42, 0), (42, 42) ) }
        self.pieces['zigright'] = { 'name': 'zigright', 'color': 'red', 'rotation_1' : ( (-42, -42), (0, -42), (0, 0), (42, 0) ), 'rotation_2' : ( (0, 42), (0, 0), (42, 0), (42, -42) ), 'rotation_3' : ( (-42, -42), (0, -42), (0, 0), (42, 0) ), 'rotation_4' : ( (0, 42), (0, 0), (42, 0), (42, -42) ) }
        self.pieces['tbar'] = { 'name': 'tbar', 'color': 'purple', 'rotation_1' : ( (-42, 0), (0, 0), (42, 0), (0, -42) ), 'rotation_2' : ( (0, -42), (0, 0), (0, 42), (42, 0) ), 'rotation_3' : ( (-42, 0), (0, 0), (42, 0), (0, 42) ), 'rotation_4' : ( (0, -42), (0, 0), (0, 42), (-42, 0) ) }

        # Size of window
        size = width, height = self.screen_width, self.screen_height
        self.screen = pygame.display.set_mode(size)
        pygame.display.set_caption('Tetris')

        # Set background image
        self.background = pygame.image.load('assets/background.gif').convert()

        # Set foreground image
        self.foreground, self.transparent = None, (1, 2, 3)
        self.foreground = pygame.Surface(self.screen.get_size())
        self.foreground.fill(self.transparent)
        self.foreground.set_colorkey(self.transparent)

        self.basicFont = pygame.font.Font(None, self.button_text_size)
        self.smallFont = pygame.font.Font(None, self.small_text_size)

        # Background to be used to overwrite old scores
        self.score_bg = pygame.Surface((180,100))
        self.score_bg.fill(self.white)
        self.score_bg_rect = self.score_bg.get_rect()
        self.score_bg_rect.x += 420

    def start_game(self):
        self.game_in_progress = True

        # Create 2 lists to hold all tetris blocks on the screen
        self.moving_list = pygame.sprite.Group()
        self.placed_list = pygame.sprite.Group()

        # Create a sprite group for each of the rows we care about
        self.placed_row = [pygame.sprite.Group()] * (714 + 1)
        for i in self.rows:
            self.placed_row[i] = pygame.sprite.Group()

        # Play music
        self.bgmusic.play(-1)

        # Show score
        self.update_score()
        self.calculate_level()

    def restart(self):
        main()

    def game_over(self):
        global text
        self.game_in_progress = False
        self.game_over_var = True
        self.bgmusic.stop()

        text = "GAME OVER!"
        text = game.basicFont.render(text, True, game.black)
        textpos = text.get_rect()
        textpos.centerx = self.background.get_rect().centerx
        textpos.centery = self.background.get_rect().centery
        self.foreground.blit(text, textpos)

        # Show start over button
        btn_restart.show_button()

    def clear_row(self, thisrow):
        # Play the sound
        self.clear_sound.play()

        # Remove all sprites in row from the placed list
        for sprite in iter(self.placed_row[thisrow]):
            self.placed_list.remove(sprite)

        # Create a surface for the animation
            self.animate_row.update( { thisrow : '1' } )

        # And then clear this row
        self.placed_row[thisrow].empty()

        # Now shift all higher sprites down one row
        # We work through the rows in reverse order (from bottom to top, so we only move each sprite once)
        rows_reverse = self.rows[::-1]

        for row in rows_reverse:
            for sprite in iter(self.placed_row[row]):
                if sprite.rect.y != thisrow and sprite.rect.y < thisrow:
                    self.placed_row[sprite.rect.y].remove(sprite)
                    self.placed_row[sprite.rect.y + 42].add(sprite)
                    sprite.rect.y += 42

        self.rows_cleared += 1

    def animate_rows(self):
        animate_surface = None
        animate_surface = pygame.Surface(self.screen.get_size())
        animate_surface.fill(self.transparent)
        animate_surface.set_colorkey(self.transparent)

        # Load the images
        f1 = pygame.image.load("assets/flash1.bmp")
        f2 = pygame.image.load("assets/flash2.bmp")
        f1rect, f2rect = f1.get_rect(), f2.get_rect()

        sprite_list = {}

        # Generate sprites for each animation row
        for row in self.animate_row:
            if self.animate_row[row] == '1':
                sprite_list[row] = { 'f1': f1rect.copy(), 'f2': f2rect.copy() }

                # Position the images
                sprite_list[row]['f1'].y, sprite_list[row]['f2'].y = row, row

                #Draw animation
                animate_surface.blit(f1, sprite_list[row]['f1'])

        # Animate
        self.screen.blit(animate_surface, (0, 0))
        pygame.display.flip()
        pygame.time.wait(50)

        for row in self.animate_row:
            if self.animate_row[row] == '1':
                #Draw animation 2
                animate_surface.blit(f2, sprite_list[row]['f2'])

        # Second animation
        self.screen.blit(animate_surface, (0, 0))
        pygame.display.flip()
        pygame.time.wait(50)

        # Clear animation row list
        for i in self.rows:
            self.animate_row.update({i: ''})

        # Update the counter of rows cleared this game
        self.lines_completed += self.rows_cleared

        self.rows_cleared = 0

    def force_redraw(self):
        self.screen.blit(self.background, (0, 0))
        self.moving_list.draw(self.screen)
        self.placed_list.draw(self.screen)
        pygame.display.flip()

    def update_score(self):
        points_map = { 1: 40, 2: 100, 3: 300, 4: 1200 }
        if self.rows_cleared > 0:
            self.score += ( points_map[self.rows_cleared] * ( self.level + 1) )

        # First draw over the area with a white filled rectangle
        game.background.blit(self.score_bg, self.score_bg_rect)

        # Now draw over again with the updated score
        self.scoretext = self.smallFont.render("Score: " + str(self.score), True, self.black)
        self.scoretextrect = self.scoretext.get_rect()
        self.scoretextrect.x, self.scoretextrect.y = 440, 50
        game.background.blit(self.scoretext, self.scoretextrect)

    def calculate_level(self):
        if self.lines_completed <= 0:
            self.earned_level = 1
        
        elif self.lines_completed >= 1 and self.lines_completed <= 90:
            self.earned_level = 1 + ( ( self.lines_completed - 1) / 10 )

        elif self.lines_completed >= 91:
            self.earned_level = 10

        self.level = max(self.initial_level, self.earned_level)
        self.speed = 550 - (self.level * 50)

        self.leveltext = self.smallFont.render("Level: " + str(self.level), True, self.black)
        self.leveltextrect = self.leveltext.get_rect()
        self.leveltextrect.x, self.leveltextrect.y = 440, 20
        game.background.blit(self.leveltext, self.leveltextrect)

class Button(object):
    # On-screen button, with optional text on top of it
    def __init__(self, text, location_xy):
        # store attributes on object
        self.text = text
        self.location_xy = location_xy

        # create the button object
        self.buttonbg = pygame.Surface([game.screen_width-game.edge_tetris-2*game.margin, game.button_height])
        self.buttonbg.fill(game.lightblue)

        # get the rectangle for the whole button
        self.rect = self.buttonbg.get_rect()
        self.rect = pygame.Rect(add_tuples(self.rect, (self.location_xy[0], self.location_xy[1], 0, 0)))    

        # add the text
        self.text = game.basicFont.render(self.text, True, game.black)
        self.textrect = self.text.get_rect()

        # position the button text so it is in the center of the button object
        self.textrect.centerx = (game.screen_width+game.edge_tetris) / 2
        self.textrect.centery = self.location_xy[1] + game.button_height / 2

    def show_button(self):
        game.background.blit(self.buttonbg, self.location_xy)
        game.background.blit(self.text, self.textrect)

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
        pygame.sprite.Group.__init__(self) #call Sprite initializer

        self.chosenpiece = chosenPiece
        self.rotation = rotation

        # Create random new piece if there aren't any moving
        if self.chosenpiece == '':
            self.chosenpiece = random.choice(game.pieces.keys())

        thisrotation = game.pieces[self.chosenpiece]['rotation' + "_" + str(self.rotation)]
        thiscolor = game.pieces[self.chosenpiece]['color']

        # Create pieces according to their specs
        for x, y in thisrotation:
            self.prep_new_block(x, y, thiscolor)

        # Adjust the positions to be correct
        # First, we adjust for height (y)
        n_pos_x = { }
        n_pos_y = []
        for sprite in game.moving_list:
            n_pos_x[sprite.rect.x] = 1
            n_pos_y.append(sprite.rect.y)

        y_difference = pos_y - max(n_pos_y)

        if y_difference > 0:
            for sprite in game.moving_list:
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
        for sprite in game.moving_list:
            new_x = sprite.rect.x + x_difference
            sprite.rect.x = new_x
            f_pos_x.append(new_x)

        # Check if over left edge
        if min(f_pos_x) < 0:
            for sprite in game.moving_list:
                sprite.rect.x += -min(f_pos_x)

        # Check if over right edge
        if max(f_pos_x) >= 420:
            for sprite in game.moving_list:
                sprite.rect.x -= 42

    def prep_new_block(self, x_adj, y_adj, color):
        # Create tetris block (object)
        block = Block(color, 42, 42)

        # Set block location
        block.rect.x = ( game.edge_tetris / 2 ) - ( game.block_size / 2 ) + x_adj - game.block_size/2
        block.rect.y = 0 + y_adj

        # Add block to list
        game.moving_list.add(block)

    def update(self, updateType, direction = ''):
        if updateType == "move":

            for sprite in game.moving_list:
                if direction == '':
                    sprite.rect.y += 42
                elif direction == 'right':
                    sprite.rect.x += 42
                elif direction == 'left':
                    sprite.rect.x -= 42

            # Move to bottom when space is pushed       
            if direction == 'to_bottom':
                self.move_to_bottom()
                        
            self.checkCollide(direction)

        if updateType == "moveBack":
            for sprite in game.moving_list:
                # If a vertical collision happens on the top row, it's game over!
                if sprite.rect.y <= 42:
                    game.game_over()

                # Otherwise, bump it up one
                sprite.rect.y -= 42

        if updateType == "reverse":
            for sprite in game.moving_list:
                if direction == "left":
                    sprite.rect.x += 42
                elif direction == "right":
                    sprite.rect.x -= 42

        if updateType == 'checkEdges':
            for sprite in game.moving_list:
                if sprite.rect.x < 0:
                    self.update("reverse", "left")
                if sprite.rect.x >= 420:
                    self.update("reverse", "right")

    def move_to_bottom(self):
        col = self.has_sprite_collided()
        y_list = []
        for sprite in game.moving_list:
            y_list.append(sprite.rect.y)
        if not col and len(y_list) >= 4:
            if max(y_list) <= 642:
                self.update('move')
                self.move_to_bottom()

    def checkCollide(self, direction):
            self.checkCollision(direction)
            self.checkIfEndOfScreen()
            self.update('checkEdges')

    def checkIfEndOfScreen(self):
        for sprite in game.moving_list:
            if sprite.rect.y >= (game.screen_height - game.block_size):
                self.stop()

    def checkCollision(self, direction = ''):
        col = self.has_sprite_collided()

        if not col:
            # This ensures that when clearing rows, the pieces are drawn before the clearing animation
            if direction == '':
                game.force_redraw()

        elif direction == '':
            self.update("moveBack")
            self.stop()

        elif direction == 'left' or direction == 'right':
            self.update("reverse", direction)

    def has_sprite_collided(self):
        col = None
        col = pygame.sprite.groupcollide(game.moving_list, game.placed_list, False, False)
        return col

    def stop(self):
        for sprite in game.moving_list:
            game.placed_list.add(sprite)

            # Add it to the row group
            game.placed_row[sprite.rect.y].add(sprite)
         
        game.moving_list.empty()

    def rotate(self, direction = 'clockwise'):
        # Rotation will be achieved by deleting the current piece, and creating a new one rotated 90 degrees
        # First, get x and y coordinates of all blocks in piece
        y_list = []
        x_list = { }
        for sprite in game.moving_list:
            x_list[sprite.rect.x] = 1
            y_list.append(sprite.rect.y)

        # Get highest value of y (lowest position on screen)
        y_low = max(y_list)
        
        # Get unique values of x
        x_values = x_list.keys()

        x_mid = ( max(x_values) + min(x_values) ) / 2

        # Now delete the existing piece, and check the current rotation
        game.moving_list.empty()

        if direction == 'clockwise':
            if self.rotation <= 3:
                self.rotation += 1
            else:
                self.rotation = 1
        else:
            if self.rotation == 1:
                self.rotation = 4
            else:
                self.rotation -= 1

        # Finally, create the new piece
        piece = Piece(self.chosenpiece, self.rotation, x_mid, y_low)

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

def round_down(x, base=42):
    return int(base * round(float(x)/base))

def main():
    global game, btn_start, btn_pause, btn_exit, btn_restart
    game = Game()

    # Define action buttons
    btn_start = Button('Start', (game.edge_tetris+game.margin, 420))
    btn_pause = Button('Pause', (game.edge_tetris+game.margin, 420))
    btn_exit = Button('Exit', (game.edge_tetris+game.margin, 500))
    btn_restart = Button('Restart', (game.edge_tetris+game.margin, 420))

    # Show action buttons
    btn_start.show_button()
    btn_exit.show_button()

    # Define clock
    clock = pygame.time.Clock()
    pygame.time.set_timer(pygame.USEREVENT + 1, game.speed)

    # Force a seed (order of pieces), for debugging
    # random.seed(9879789)

    # Constant loop to check for events (the game loop)
    while 1:
        # Ensure game does not run faster than 60 frames/second
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT: sys.exit()

            # handle mouse clicks
            if pygame.mouse.get_pressed()[0] and game.allows_clicks:

                # Prevent multiple clicks
                game.allows_clicks = False
                pygame.time.set_timer(pygame.USEREVENT + 2, 300)

                # Start/pause button
                if btn_start.rect.collidepoint(pygame.mouse.get_pos()):

                    if game.game_in_progress == False:

                        # If game over, restart the game
                        if game.game_over_var:
                            game.restart()

                        # Otherwise, just start
                        game.start_game()
                        btn_pause.show_button()

                    elif game.paused:
                        game.paused = False
                        btn_pause.show_button()
                        game.bgmusic.unpause()

                    else:
                        game.paused = True
                        btn_start.show_button()
                        game.bgmusic.pause()

                # Exit button
                if btn_exit.rect.collidepoint(pygame.mouse.get_pos()):
                    pygame.quit()

            # Check if piece exists
            try:
                a = piece.chosenpiece
            except NameError:
                pass
            else:
                if not game.paused and game.game_in_progress:

                    # Handle keyboard presses
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_UP: # UP Arrow
                            piece.rotate()
                            if piece.has_sprite_collided():
                                piece.rotate('counterclockwise')

                        if event.key == pygame.K_DOWN: # DOWN Arrow
                            piece.update("move")
                        if event.key == pygame.K_RIGHT: # RIGHT Arrow
                            piece.update("move", "right")
                        if event.key == pygame.K_LEFT: # LEFT Arrow
                            piece.update("move", "left")
                        if event.key == pygame.K_SPACE: # Space Bar
                            piece.update("move", "to_bottom")

                    if event.type == pygame.USEREVENT + 1:
                        if game.game_in_progress == True:
                            game.draw = False
                            piece.update("move")
                            game.draw = True

            if event.type == pygame.USEREVENT + 2:
                    game.allows_clicks = True      

        if game.game_in_progress:
            if not game.moving_list:
                # Create new piece
                piece = Piece()

        # Check if 10 in a row
        if game.game_in_progress:
            for i in game.rows:
                if len(game.placed_row[i]) == 10:
                    game.clear_row(i)

        if game.rows_cleared > 0:
            # Update score
            game.update_score()

            # Animate row clearing
            game.animate_rows()

            # Recalculate level
            game.calculate_level()

            # Recalibrate clock
            pygame.time.set_timer(pygame.USEREVENT + 1, game.speed)

        # Draw everything
        game.screen.blit(game.background, (0, 0))

        if game.game_in_progress and game.draw:
            game.moving_list.draw(game.screen)
            game.placed_list.draw(game.screen)

        if game.game_over_var:
            game.screen.blit(game.foreground, (0, 0))

        pygame.display.flip()

if __name__ == "__main__":
    main()