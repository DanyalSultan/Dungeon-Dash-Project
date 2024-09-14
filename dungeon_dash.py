# dungeondash.py

# Imports
import pygame, random, sys, time, psycopg2
from database import cursor, connection
from login import useremail

# Set 2D vectors
vector = pygame.math.Vector2

# Initialise pygame
pygame.init()

# Setup display
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 736
display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Dungeon Dash")
icon = pygame.image.load("logo.png")
pygame.display.set_icon(icon)

# Set FPS and clock
FPS = 60
clock = pygame.time.Clock()

class Game():
    """A class to manage gameplay"""

    def __init__(self, monster_group, platform_group, weapon):

        # Set game values 
        self.score = 0
        self.frame_count = 0
        self.time = 0
        self.monster_creation_time = 5
        
        # Attach groups and sprites
        self.player = player
        self.monster_group = monster_group
        self.platform_group = platform_group
        self.weapon = weapon
        self.chest = chest_group

        # Set fonts
        self.title_font = pygame.font.Font("GabtonMalgora.otf", 44)
        self.HUD_font = pygame.font.Font("ranille.ttf", 24)
        self.email = useremail

    def update(self):
        """Update the game"""
        self.timer()
        #self.draw_hud()
        self.add_monster()
        self.damage_decider()
        self.check_collisions()
        self.check_game_over(self.email)
        
        # Minus 5 defence every second
        if self.frame_count % FPS == 0:
            self.player.defence -= 5
        
        # Player starts losing health if defence reaches 0
        if self.player.defence <= 0:
            self.player.defence = 0 
            if self.frame_count % FPS == 0:
                self.player.health -= 20

        # Make sure health never goes over 100
        if self.player.health >= 100:
            self.player.health = 100
    
    def damage_decider(self):
        self.current_damage = int((self.time*0.1*self.time) + 75 - self.player.defence)
        if self.current_damage <= 0:
            self.current_damage = 0
 
    def draw_hud(self):
        """A function to draw the HUD"""
        # Set colours
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.GREEN = (50, 200, 25)
        self.RED = (235, 62, 23)
        self.YELLOW = (255, 242, 0)
        self.BLUE = (0, 180, 255)

        # Set text
        score_text = self.HUD_font.render("Score: " + str(self.score), True, self.GREEN)
        score_rect = score_text.get_rect()
        score_rect.topleft = (10, WINDOW_HEIGHT - 50)

        health_text = self.HUD_font.render("Health: " + str(self.player.health), True, self.RED)
        health_rect = health_text.get_rect()
        health_rect.topleft = (10, WINDOW_HEIGHT - 25)

        title_text = self.title_font.render("Dungeon Dash", True, self.BLACK)
        title_rect = title_text.get_rect()
        title_rect.center = (WINDOW_WIDTH//2, WINDOW_HEIGHT - 25)

        timer_text = self.HUD_font.render("Time: " + str(self.time), True, self.WHITE)
        timer_rect = timer_text.get_rect()
        timer_rect.topright = (WINDOW_WIDTH - 10, WINDOW_HEIGHT - 25)

        defence_text = self.HUD_font.render("Defence: " + str(self.player.defence), True, self.BLUE)
        defence_rect = defence_text.get_rect()
        defence_rect.topleft = (250, WINDOW_HEIGHT - 37.5)

        display_surface.blit(score_text, score_rect)
        display_surface.blit(health_text, health_rect)
        display_surface.blit(title_text, title_rect)
        display_surface.blit(timer_text, timer_rect)
        display_surface.blit(defence_text, defence_rect)

    def add_monster(self):
        """Add a monster to the game"""
        # Check to add a zombie every second
        if self.frame_count % FPS == 0:
            # Only add a zombie if zombie creation time has passed
            if self.time % self.monster_creation_time == 0:
                self.monster_creation_time = self.monster_creation_time - 1
                if self.monster_creation_time <= 1:
                    self.monster_creation_time = 2
                monster = Monster(self.platform_group)
                self.monster_group.add(monster)
                

    def check_collisions(self):
        """Check collisions that affect gameplay"""
        #See if weapon collided with monster
        collision_dict = pygame.sprite.spritecollide(self.weapon, self.monster_group, True)
        if collision_dict:
            for monster in collision_dict:
                monster.is_dead = True
                monster.animate_death = True
                # The monster is dead
                if monster.is_dead == True:
                    monster.kill()
                    self.score += 25
                    self.player.health += 1
        
        # See if a monster collided with player
        collision_list = pygame.sprite.spritecollide(self.player, self.monster_group, False)
        if collision_list:
            for monster in collision_list:
                # Take damage from the monster
                self.player.health -= self.current_damage 
                self.draw_hitmarker()
                # Move the player to not continually take damage
                self.player.position.x -= 256 
                self.player.rect.bottomleft = self.player.position

        # See if player collided with chest
        collision_with_chest = pygame.sprite.spritecollide(self.player, self.chest, False)
        if collision_with_chest:
            for chest in collision_with_chest:
                chest.kill()
            player.defence += random.randint(4, 20)


        # Player collisions
        # Collision check between player and platforms when falling
        if self.player.velocity.y > 0:
            collided_platforms = pygame.sprite.spritecollide(self.player, self.platform_group, False, pygame.sprite.collide_mask)
            if collided_platforms:
                self.player.position.y = collided_platforms[0].rect.top + 10
                self.player.velocity.y = 0

        # Collision check between player and platform if jumping up
        if self.player.velocity.y < 0:
            collided_platforms = pygame.sprite.spritecollide(self.player, self.platform_group, False, pygame.sprite.collide_mask)
            if collided_platforms:
                self.player.velocity.y = 0
                while pygame.sprite.spritecollide(self.player, self.platform_group, False):
                    self.player.position.y += 1
                    self.player.rect.bottomleft = self.player.position

    def draw_hitmarker(self):
        if self.current_damage < 25:
            hitmarker = Hitmarker(self.YELLOW, self.player.rect)
        else:
            hitmarker = Hitmarker(self.RED, self.player.rect)

    def check_game_over(self, email):
        """Check to see if the player lost the game"""
        if self.player.health <= 0 or len(self.monster_group) >= 18:
            self.player.health = 0
            if self.player.velocity.x > 0:
                self.player.velocity = vector(0, 0)
                self.player.animate_death_right = True
            else:
                self.player.velocity = vector(0, 0)
                self.player.animate_death_left = True

            if self.player.gameover:
                self.pause_game("Game Over! Final score: " + str(self.score), "Press 'Enter' to play again...")
                cursor.execute("SELECT high_score FROM player WHERE email=(%s)", (email,))
                highscore = cursor.fetchone()
                stringhighscore = str(highscore)
                stringhighscore = stringhighscore.replace(",", "")
                stringhighscore = stringhighscore.replace("(", "")
                stringhighscore = stringhighscore.replace("'", "")
                stringhighscore = stringhighscore.replace(")", "")

                if int(self.score) > int(stringhighscore):  
                    cursor.execute("UPDATE player SET high_score=(%s) WHERE email=(%s)", ((str(self.score), (email,)))) #Update high score field
                    connection.commit()
                    print("1 Field appended successfully")

                self.reset_game()
            

    def pause_game(self, main_text, sub_text):
        """Pause the game"""
        global running

        #pygame.mixer.music.pause()

        # Create main pause text
        main_text = self.title_font.render(main_text, True, self.RED)
        main_rect = main_text.get_rect()
        main_rect.center = (WINDOW_WIDTH//2, WINDOW_HEIGHT//2)

        # Create sub pause text
        sub_text = self.title_font.render(sub_text, True, self.GREEN)
        sub_rect = sub_text.get_rect()
        sub_rect.center = (WINDOW_WIDTH//2, WINDOW_HEIGHT//2 + 64)

        # Display the pause text
        display_surface.fill(self.BLACK)
        display_surface.blit(main_text, main_rect)
        display_surface.blit(sub_text, sub_rect)
        pygame.display.update()

        # Pause the game until user hits enter or quits
        is_paused = True
        while is_paused:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    # User wants to continue
                    if event.key == pygame.K_RETURN:
                        is_paused = False
                # User wants to quit
                if event.type == pygame.QUIT:
                    is_paused = False
                    running = False

    def reset_game(self):
        """Reset the game"""
        self.score = 0
        self.time = 0

        # Reset the player
        self.player.reset()
        Chest.reset(chest)


        # Empty sprite groups
        self.monster_group.empty()

    def timer(self):
        """A timer to determine how much time has passed and what to do at certain times"""
        # Update the timer every second
        self.frame_count += 1
        if self.frame_count % FPS == 0:
            self.time += 1
            self.frame_count = 0

class Player(pygame.sprite.Sprite):
    """A class for the player object"""
    def __init__(self, x, y, platform_group):
        super().__init__()
        # Constants
        self.FRICTION = 0.2
        self.GRAVITY = 0.8
        self.INITIAL_VELOCITY = 1.5
        self.INITIAL_HEALTH = 100
        self.JUMP_SPEED = 18
        self.INITIAL_X = x
        self.INITIAL_Y = y
        self.INITIAL_DEFENCE = 15
        self.gameover = False

        # Variables
        self.health = self.INITIAL_HEALTH
        self.position = vector(self.INITIAL_X, self.INITIAL_Y)
        self.velocity = vector(0, 0)
        self.acceleration = vector(0, 0)
        self.defence = self.INITIAL_DEFENCE
        self.monster_group = monster_group

        # Animation frames
        self.idle_right_frames = []
        self.idle_left_frames = []
        self.move_right_frames = []
        self.move_left_frames = []
        self.jump_right_frames = []
        self.jump_left_frames = []
        self.dead_right_frames = []
        self.dead_left_frames = []

        # idle frames
        self.idle_right_frames.append(pygame.transform.scale(pygame.image.load("player_frames/Idle__000.png"), (64, 64)))
        self.idle_right_frames.append(pygame.transform.scale(pygame.image.load("player_frames/Idle__001.png"), (64, 64)))
        self.idle_right_frames.append(pygame.transform.scale(pygame.image.load("player_frames/Idle__002.png"), (64, 64)))
        self.idle_right_frames.append(pygame.transform.scale(pygame.image.load("player_frames/Idle__003.png"), (64, 64)))
        self.idle_right_frames.append(pygame.transform.scale(pygame.image.load("player_frames/Idle__004.png"), (64, 64)))
        self.idle_right_frames.append(pygame.transform.scale(pygame.image.load("player_frames/Idle__005.png"), (64, 64)))
        self.idle_right_frames.append(pygame.transform.scale(pygame.image.load("player_frames/Idle__006.png"), (64, 64)))
        self.idle_right_frames.append(pygame.transform.scale(pygame.image.load("player_frames/Idle__007.png"), (64, 64)))
        self.idle_right_frames.append(pygame.transform.scale(pygame.image.load("player_frames/Idle__008.png"), (64, 64)))
        self.idle_right_frames.append(pygame.transform.scale(pygame.image.load("player_frames/Idle__009.png"), (64, 64)))

        for frame in self.idle_right_frames:
            self.idle_left_frames.append(pygame.transform.flip(frame, True, False))

        # move frames
        self.move_right_frames.append(pygame.transform.scale(pygame.image.load("player_frames/Run__001.png"), (64, 64)))
        self.move_right_frames.append(pygame.transform.scale(pygame.image.load("player_frames/Run__001.png"), (64, 64)))
        self.move_right_frames.append(pygame.transform.scale(pygame.image.load("player_frames/Run__002.png"), (64, 64)))
        self.move_right_frames.append(pygame.transform.scale(pygame.image.load("player_frames/Run__003.png"), (64, 64)))
        self.move_right_frames.append(pygame.transform.scale(pygame.image.load("player_frames/Run__004.png"), (64, 64)))
        self.move_right_frames.append(pygame.transform.scale(pygame.image.load("player_frames/Run__005.png"), (64, 64)))
        self.move_right_frames.append(pygame.transform.scale(pygame.image.load("player_frames/Run__006.png"), (64, 64)))
        self.move_right_frames.append(pygame.transform.scale(pygame.image.load("player_frames/Run__007.png"), (64, 64)))
        self.move_right_frames.append(pygame.transform.scale(pygame.image.load("player_frames/Run__008.png"), (64, 64)))
        self.move_right_frames.append(pygame.transform.scale(pygame.image.load("player_frames/Run__009.png"), (64, 64)))

        for frame in self.move_right_frames:
            self.move_left_frames.append(pygame.transform.flip(frame, True, False))

        # jump frames
        self.jump_right_frames.append(pygame.transform.scale(pygame.image.load("player_frames/Jump__000.png"), (64, 64)))
        self.jump_right_frames.append(pygame.transform.scale(pygame.image.load("player_frames/Jump__001.png"), (64, 64)))
        self.jump_right_frames.append(pygame.transform.scale(pygame.image.load("player_frames/Jump__002.png"), (64, 64)))
        self.jump_right_frames.append(pygame.transform.scale(pygame.image.load("player_frames/Jump__003.png"), (64, 64)))
        self.jump_right_frames.append(pygame.transform.scale(pygame.image.load("player_frames/Jump__004.png"), (64, 64)))
        self.jump_right_frames.append(pygame.transform.scale(pygame.image.load("player_frames/Jump__005.png"), (64, 64)))
        self.jump_right_frames.append(pygame.transform.scale(pygame.image.load("player_frames/Jump__006.png"), (64, 64)))
        self.jump_right_frames.append(pygame.transform.scale(pygame.image.load("player_frames/Jump__007.png"), (64, 64)))
        self.jump_right_frames.append(pygame.transform.scale(pygame.image.load("player_frames/Jump__008.png"), (64, 64)))
        self.jump_right_frames.append(pygame.transform.scale(pygame.image.load("player_frames/Jump__009.png"), (64, 64)))

        for frame in self.jump_right_frames:
            self.jump_left_frames.append(pygame.transform.flip(frame, True, False))

        # dead frames
        self.dead_right_frames.append(pygame.transform.scale(pygame.image.load("player_frames/Dead__000.png"), (64, 64)))
        self.dead_right_frames.append(pygame.transform.scale(pygame.image.load("player_frames/Dead__001.png"), (64, 64)))
        self.dead_right_frames.append(pygame.transform.scale(pygame.image.load("player_frames/Dead__002.png"), (64, 64)))
        self.dead_right_frames.append(pygame.transform.scale(pygame.image.load("player_frames/Dead__003.png"), (64, 64)))
        self.dead_right_frames.append(pygame.transform.scale(pygame.image.load("player_frames/Dead__004.png"), (64, 64)))
        self.dead_right_frames.append(pygame.transform.scale(pygame.image.load("player_frames/Dead__005.png"), (64, 64)))
        self.dead_right_frames.append(pygame.transform.scale(pygame.image.load("player_frames/Dead__006.png"), (64, 64)))
        self.dead_right_frames.append(pygame.transform.scale(pygame.image.load("player_frames/Dead__007.png"), (64, 64)))
        self.dead_right_frames.append(pygame.transform.scale(pygame.image.load("player_frames/Dead__008.png"), (64, 64)))
        self.dead_right_frames.append(pygame.transform.scale(pygame.image.load("player_frames/Dead__009.png"), (64, 64)))

        for frame in self.move_right_frames:
            self.dead_left_frames.append(pygame.transform.flip(frame, True, False))

        # Load image and get rect
        self.current_frame = 0
        self.image = self.idle_right_frames[0]
        self.rect = self.image.get_rect()
        self.rect.bottomleft = (x, y)

        #Attach sprite groups
        self.platform_group = platform_group

        # Animation booleans
        self.animate_jump = False
        self.animate_death_right = False
        self.animate_death_left = False

        # Load sounds

        # Kinematics vectors
        self.position = vector(self.INITIAL_X, self.INITIAL_Y)
        self.velocity = vector(0, 0)
        self.acceleration = vector(0, self.GRAVITY)


    def update(self):
        self.move()
        self.check_animations()

        # Player mask
        self.mask = pygame.mask.from_surface(self.image)
        mask_outline = self.mask.outline()


    def move(self):
        # Set acceleration vector
        self.acceleration = vector(0, self.GRAVITY)

        # If user is pressing a key, set the x-component of acceleration to be non-zero
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.acceleration.x = -1*self.INITIAL_VELOCITY
            self.animate(self.move_left_frames, 0.5)
        elif keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.acceleration.x = self.INITIAL_VELOCITY
            self.animate(self.move_right_frames, 0.5)
        else:
            if self.velocity.x > 0:
                self.animate(self.idle_right_frames, 0.5)
            else:
                self.animate(self.idle_left_frames, 0.5)

        # Calculate new kinematics values
        self.acceleration.x -= self.velocity.x*self.FRICTION
        self.velocity += self.acceleration
        self.position += self.velocity + 0.5*self.acceleration
        
        # Update rect based on kinematic calculations
        if self.position.x <= 0:
            self.position.x = 0
            print(self.position.x)
        elif self.position.x >= WINDOW_WIDTH - 20:
            self.position.x = WINDOW_WIDTH - 20
            print(self.position.x)

        self.rect.bottomleft = self.position


    def check_animations(self):
        """Check to see if jump/attack animations should run"""
        # Animate the player jump
        if self.animate_jump:
            if self.velocity.x > 0:
                self.animate(self.jump_right_frames, 0.1)
            else:
                self.animate(self.jump_left_frames, 0.1)
        # Animate player death
        if self.animate_death_right:
            self.animate(self.dead_right_frames, 0.001)
        elif self.animate_death_left:
            self.animate(self.dead_left_frames, 0.001)
    

    def jump(self):
        """Jump upwards if on a platform"""
        # Only jump if on a platform
        if pygame.sprite.spritecollide(self, self.platform_group, False):
            self.velocity.y = -1*self.JUMP_SPEED
            self.animate_jump = True
            

    def reset(self):
        """Reset the player's position"""
        self.velocity = vector(0, 0)
        self.position = vector(self.INITIAL_X, self.INITIAL_Y)
        self.rect.bottomleft = self.position
        self.health = self.INITIAL_HEALTH
        self.acceleration = vector(0, 0)
        self.defence = self.INITIAL_DEFENCE
        self.monster_group = monster_group
        self.image = self.idle_right_frames[0]
        self.gameover = False
        self.animate_jump = False
        self.animate_death_right = False
        self.animate_death_left = False       

    
    def animate(self, sprite_list, speed):
        """Animate the player's actions"""
        if self.current_frame < len(sprite_list) - 1:
            self.current_frame += speed
        else:
            self.current_frame = 0
            # End jump animation
            if self.animate_jump:
                self.animate_jump = False
            
            # End death animation
            if self.animate_death_right or self.animate_death_left:
                self.animate_death_right = False
                self.animate_death_left = False
                self.gameover = True

        self.image = sprite_list[int(self.current_frame)]

class Weapon(pygame.sprite.Sprite):
    def __init__(self, weapon_group):
        super().__init__()
        self.image = pygame.transform.scale(pygame.image.load("Weapon1.png"), (32,32))
        self.rect = self.image.get_rect()
        self.rect.center = (player.rect.centerx - 32, player.rect.centery)
        weapon_group.add(self)
        pass

    def update(self):
        self.rect.center = (player.rect.centerx - 32, player.rect.centery)
        if player.velocity.x > 0:
            self.image = pygame.transform.scale(pygame.image.load("Weapon1.png"), (32,32))
            self.rect.center = (player.rect.centerx + 32, player.rect.centery)
        else:
            self.image = pygame.transform.flip(pygame.transform.scale(pygame.image.load("Weapon1.png"), (32,32)), True, False)
            self.rect.center = (player.rect.centerx - 32, player.rect.centery)

class GUI(pygame.sprite.Sprite):
    """A class for the GUI""" 
    def __init__(self, x, y, image_int, main_group, platform_group=""):
        """Initialise the GUI"""
        super().__init__()
        # Load in correct image and add it to the correct sub group
        # Stone
        if image_int == 1:
            self.image = pygame.transform.scale(pygame.image.load("stone1.png").convert(), (32, 32)) # Stone block
        elif image_int == 2:
            self.image = pygame.transform.scale(pygame.image.load("stone2.png").convert_alpha(), (32, 32)) # Stone top
            platform_group.add(self)
        elif image_int == 3:
            self.image = pygame.transform.scale(pygame.image.load("stone3.png").convert_alpha(), (32, 32)) # Edge facing left
            platform_group.add(self)
        elif image_int == 4:
            self.image = pygame.transform.scale(pygame.image.load("stone2.png").convert_alpha(), (32, 32)) # Stone top
            platform_group.add(self)
        elif image_int == 5:
            self.image = pygame.transform.scale(pygame.image.load("stone4.png").convert_alpha(), (32, 32)) # Edge facing right
            platform_group.add(self)

        # Add every image to the main group
        main_group.add(self)

        # Get the rect of the image and position within grid
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

    def camera_scroll(self, scrollamount):
        """A function to scroll the world"""
        self.rect.x += scrollamount

class Monster(pygame.sprite.Sprite):
    def __init__(self, platform_group):
        super().__init__()

        # Set constant variables
        self.GRAVITY = 3
        self.INITIAL_HEALTH = 100
        
        # Set variables
        self.health = self.INITIAL_HEALTH
        self.velocity = vector(0, 0)
        self.acceleration = vector(0, 0)
        self.monster_group = monster_group

        # Animation frames
        self.run_right_frames = []
        self.run_left_frames = []
        self.die_right_frames = []
        self.die_left_frames = []

        monstertype = random.randint(1,3)

        # move frames
        if monstertype == 1:
            self.run_right_frames.append(pygame.transform.scale(pygame.image.load("monster_walking 1/Minotaur_01_Walking_001.png"), (64, 64)))
            self.run_right_frames.append(pygame.transform.scale(pygame.image.load("monster_walking 1/Minotaur_01_Walking_002.png"), (64, 64)))
            self.run_right_frames.append(pygame.transform.scale(pygame.image.load("monster_walking 1/Minotaur_01_Walking_003.png"), (64, 64)))
            self.run_right_frames.append(pygame.transform.scale(pygame.image.load("monster_walking 1/Minotaur_01_Walking_004.png"), (64, 64)))
            self.run_right_frames.append(pygame.transform.scale(pygame.image.load("monster_walking 1/Minotaur_01_Walking_005.png"), (64, 64)))
            self.run_right_frames.append(pygame.transform.scale(pygame.image.load("monster_walking 1/Minotaur_01_Walking_006.png"), (64, 64)))
            self.run_right_frames.append(pygame.transform.scale(pygame.image.load("monster_walking 1/Minotaur_01_Walking_007.png"), (64, 64)))
            self.run_right_frames.append(pygame.transform.scale(pygame.image.load("monster_walking 1/Minotaur_01_Walking_008.png"), (64, 64)))
            self.run_right_frames.append(pygame.transform.scale(pygame.image.load("monster_walking 1/Minotaur_01_Walking_009.png"), (64, 64)))
            self.run_right_frames.append(pygame.transform.scale(pygame.image.load("monster_walking 1/Minotaur_01_Walking_010.png"), (64, 64)))
            self.run_right_frames.append(pygame.transform.scale(pygame.image.load("monster_walking 1/Minotaur_01_Walking_011.png"), (64, 64)))
            self.run_right_frames.append(pygame.transform.scale(pygame.image.load("monster_walking 1/Minotaur_01_Walking_012.png"), (64, 64)))
            self.run_right_frames.append(pygame.transform.scale(pygame.image.load("monster_walking 1/Minotaur_01_Walking_013.png"), (64, 64)))
            self.run_right_frames.append(pygame.transform.scale(pygame.image.load("monster_walking 1/Minotaur_01_Walking_014.png"), (64, 64)))
            self.run_right_frames.append(pygame.transform.scale(pygame.image.load("monster_walking 1/Minotaur_01_Walking_015.png"), (64, 64)))
            self.run_right_frames.append(pygame.transform.scale(pygame.image.load("monster_walking 1/Minotaur_01_Walking_016.png"), (64, 64)))
            self.run_right_frames.append(pygame.transform.scale(pygame.image.load("monster_walking 1/Minotaur_01_Walking_017.png"), (64, 64)))

            for frame in self.run_right_frames:
                self.run_left_frames.append(pygame.transform.flip(frame, True, False))

        elif monstertype == 2:
            self.run_right_frames.append(pygame.transform.scale(pygame.image.load("monster_walking 2/Minotaur_02_Walking_001.png"), (64, 64)))
            self.run_right_frames.append(pygame.transform.scale(pygame.image.load("monster_walking 2/Minotaur_02_Walking_002.png"), (64, 64)))
            self.run_right_frames.append(pygame.transform.scale(pygame.image.load("monster_walking 2/Minotaur_02_Walking_003.png"), (64, 64)))
            self.run_right_frames.append(pygame.transform.scale(pygame.image.load("monster_walking 2/Minotaur_02_Walking_004.png"), (64, 64)))
            self.run_right_frames.append(pygame.transform.scale(pygame.image.load("monster_walking 2/Minotaur_02_Walking_005.png"), (64, 64)))
            self.run_right_frames.append(pygame.transform.scale(pygame.image.load("monster_walking 2/Minotaur_02_Walking_006.png"), (64, 64)))
            self.run_right_frames.append(pygame.transform.scale(pygame.image.load("monster_walking 2/Minotaur_02_Walking_007.png"), (64, 64)))
            self.run_right_frames.append(pygame.transform.scale(pygame.image.load("monster_walking 2/Minotaur_02_Walking_008.png"), (64, 64)))
            self.run_right_frames.append(pygame.transform.scale(pygame.image.load("monster_walking 2/Minotaur_02_Walking_009.png"), (64, 64)))
            self.run_right_frames.append(pygame.transform.scale(pygame.image.load("monster_walking 2/Minotaur_02_Walking_010.png"), (64, 64)))
            self.run_right_frames.append(pygame.transform.scale(pygame.image.load("monster_walking 2/Minotaur_02_Walking_011.png"), (64, 64)))
            self.run_right_frames.append(pygame.transform.scale(pygame.image.load("monster_walking 2/Minotaur_02_Walking_012.png"), (64, 64)))
            self.run_right_frames.append(pygame.transform.scale(pygame.image.load("monster_walking 2/Minotaur_02_Walking_013.png"), (64, 64)))
            self.run_right_frames.append(pygame.transform.scale(pygame.image.load("monster_walking 2/Minotaur_02_Walking_014.png"), (64, 64)))
            self.run_right_frames.append(pygame.transform.scale(pygame.image.load("monster_walking 2/Minotaur_02_Walking_015.png"), (64, 64)))
            self.run_right_frames.append(pygame.transform.scale(pygame.image.load("monster_walking 2/Minotaur_02_Walking_016.png"), (64, 64)))
            self.run_right_frames.append(pygame.transform.scale(pygame.image.load("monster_walking 2/Minotaur_02_Walking_017.png"), (64, 64)))

            for frame in self.run_right_frames:
                self.run_left_frames.append(pygame.transform.flip(frame, True, False))

        elif monstertype == 3:
            self.run_right_frames.append(pygame.transform.scale(pygame.image.load("monster_walking 3/Minotaur_03_Walking_001.png"), (64, 64)))
            self.run_right_frames.append(pygame.transform.scale(pygame.image.load("monster_walking 3/Minotaur_03_Walking_002.png"), (64, 64)))
            self.run_right_frames.append(pygame.transform.scale(pygame.image.load("monster_walking 3/Minotaur_03_Walking_003.png"), (64, 64)))
            self.run_right_frames.append(pygame.transform.scale(pygame.image.load("monster_walking 3/Minotaur_03_Walking_004.png"), (64, 64)))
            self.run_right_frames.append(pygame.transform.scale(pygame.image.load("monster_walking 3/Minotaur_03_Walking_005.png"), (64, 64)))
            self.run_right_frames.append(pygame.transform.scale(pygame.image.load("monster_walking 3/Minotaur_03_Walking_006.png"), (64, 64)))
            self.run_right_frames.append(pygame.transform.scale(pygame.image.load("monster_walking 3/Minotaur_03_Walking_007.png"), (64, 64)))
            self.run_right_frames.append(pygame.transform.scale(pygame.image.load("monster_walking 3/Minotaur_03_Walking_008.png"), (64, 64)))
            self.run_right_frames.append(pygame.transform.scale(pygame.image.load("monster_walking 3/Minotaur_03_Walking_009.png"), (64, 64)))
            self.run_right_frames.append(pygame.transform.scale(pygame.image.load("monster_walking 3/Minotaur_03_Walking_010.png"), (64, 64)))
            self.run_right_frames.append(pygame.transform.scale(pygame.image.load("monster_walking 3/Minotaur_03_Walking_011.png"), (64, 64)))
            self.run_right_frames.append(pygame.transform.scale(pygame.image.load("monster_walking 3/Minotaur_03_Walking_012.png"), (64, 64)))
            self.run_right_frames.append(pygame.transform.scale(pygame.image.load("monster_walking 3/Minotaur_03_Walking_013.png"), (64, 64)))
            self.run_right_frames.append(pygame.transform.scale(pygame.image.load("monster_walking 3/Minotaur_03_Walking_014.png"), (64, 64)))
            self.run_right_frames.append(pygame.transform.scale(pygame.image.load("monster_walking 3/Minotaur_03_Walking_015.png"), (64, 64)))
            self.run_right_frames.append(pygame.transform.scale(pygame.image.load("monster_walking 3/Minotaur_03_Walking_016.png"), (64, 64)))
            self.run_right_frames.append(pygame.transform.scale(pygame.image.load("monster_walking 3/Minotaur_03_Walking_017.png"), (64, 64)))

            for frame in self.run_right_frames:
                self.run_left_frames.append(pygame.transform.flip(frame, True, False))

        self.current_frame = 0

        self.image = self.run_right_frames[self.current_frame]

        self.rect = self.image.get_rect()
        self.rect.bottomleft = (random.randint(100, WINDOW_WIDTH - 100), -100)
        

        # Attach sprite groups
        self.platform_group = platform_group

        # Set animation booleans
        self.animate_death = False

        # Load sounds

        # Kinematics vectors
        self.position = vector(self.rect.x, self.rect.y)
        self.velocity = vector(random.randint(-8, 8), 0)
        if self.velocity.x == 0:
            self.velocity = vector(random.randint(1, 8), 0)
        self.acceleration = vector(0, self.GRAVITY)

        # Initial monster values
        self.is_dead = False
        self.round_time = 0
        self.frame_count = 0

    def update(self):
        """Update the monster"""
        self.pathfind()
        self.check_collisions()
        self.check_animations()
        self.check_dead()
        
        # Monster mask
        self.mask = pygame.mask.from_surface(self.image)
        mask_outline = self.mask.outline()
        pygame.draw.lines(self.image, (255, 0, 0), True, mask_outline) # Draw the monster collision box
        
    def pathfind(self):
        """Move the monster"""
        # Calculate new kinematics values: (4, 1) + (2, 8) = (6, 9)
        self.animate(self.run_right_frames, 0.5)
        self.velocity += self.acceleration
        self.position += self.velocity + 0.5*self.acceleration

        self.rect.bottomleft = self.position

        if self.position.x >= WINDOW_WIDTH - 20:
            self.velocity = vector(-self.velocity.x, 0)
        elif self.position.x <= 0:
            self.velocity = vector(abs(self.velocity.x), 0)

        

    def check_collisions(self):
        """Check for collisions with platforms"""
        # Collision check between monster and platforms when falling
        collided_platforms = pygame.sprite.spritecollide(self, self.platform_group, False)
        if collided_platforms:
            self.position.y = collided_platforms[0].rect.top + 5
            self.velocity.y = 0

    def check_animations(self):
        """Check for death animation"""
        # Animate the zombie death
        if self.animate_death:
            self.animate(self.die_right_frames, .095)

        # Switch direction of animation
        if self.velocity.x > 0:
            self.image = self.run_right_frames[int(self.current_frame)]
        else:
            self.image = self.run_left_frames[int(self.current_frame)]
            

    def animate(self, sprite_list, speed):
        """Animate the Monsters actions"""
        if self.current_frame < len(sprite_list) - 1:
            self.current_frame += speed
        else:
            self.current_frame = 0
            # End the death animation
            if self.animate_death:
                self.current_frame = len(sprite_list) - 1
                self.animate_death = False

        self.image = sprite_list[int(self.current_frame)]
    

    def check_dead(self):
        if self.health <= 0:
            self.monster_group.remove(self)
            self.score += 25

class Hitmarker(pygame.sprite.Sprite):
    def __init__(self, colour, player_rect):
        super().__init__()
        self.damage = game.current_damage
        self.damage_text = str(self.damage)
        self.title_font = pygame.font.Font("sunny-spells.otf", 48)

        # Create main pause text
        hitmarker_text = self.title_font.render(self.damage_text, True, colour)
        hitmarker_rect = hitmarker_text.get_rect()
        hitmarker_rect.center = (player_rect.x + 32, player_rect.y - 5)

        display_surface.blit(hitmarker_text, hitmarker_rect)

class Chest(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.transform.scale(pygame.image.load("chest.png"), (64, 64))
        self.rect = self.image.get_rect()
        self.rect.bottomleft = (x, y)
    
    def update(self):
        if len(chest_group) == 0:
            self.reset()

    def reset(self):
        for i in range(len(tile_map)):
        # Loop through the 40 elements in a given list (cols) (j moves us across the map)
            for j in range(len(tile_map[i])):
                if tile_map[i][j] == 7:
                    if random.randint(1, 30) == 1:
                        chest = Chest(j*32, i*32 + 64)
                        chest_group.add(chest)

# Create sprite groups
main_tile_group = pygame.sprite.Group()
platform_group = pygame.sprite.Group()

player_group = pygame.sprite.Group()
chest_group = pygame.sprite.Group()

monster_group = pygame.sprite.Group()
weapon_group = pygame.sprite.Group()

# Create tile map
# 0 => air, 1-5 => stone, 6 => player, 7 => chests
# 23 rows and 40 columns
tile_map = [
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 0],
    [4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 7, 7, 7, 7, 7, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 7, 7, 7, 7, 7, 0],
    [4, 4, 4, 4, 4, 5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 4, 4, 4, 4, 4],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 0, 0, 0, 0, 0, 0, 0, 0, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 0],
    [4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 5, 0, 0, 0, 0, 0, 0, 0, 0, 3, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 7, 7, 6, 7, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 4, 4, 5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 0],
    [2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
]

# Generate Tile objects from the tile map
# Loop through the 23 lists (rows) in the tile map (i moves us down the map)
for i in range(len(tile_map)):
    # Loop through the 40 elements in a given list (cols) (j moves us across the map)
    for j in range(len(tile_map[i])):
        # Stone
        if tile_map[i][j] == 1:
            GUI(j*32, i*32, 1, main_tile_group, platform_group)
        elif tile_map[i][j] == 2:
            GUI(j*32, i*32, 2, main_tile_group, platform_group)
        elif tile_map[i][j] == 3:
            GUI(j*32, i*32, 3, main_tile_group, platform_group)
        elif tile_map[i][j] == 4:
            GUI(j*32, i*32, 4, main_tile_group, platform_group)
        elif tile_map[i][j] == 5:
            GUI(j*32, i*32, 5, main_tile_group, platform_group)
        
        # Player
        elif tile_map[i][j] == 6:
            player = Player(j*32, i*32 + 64, platform_group)
            player_group.add(player)

        # Chest
        elif tile_map[i][j] == 7:
            if random.randint(1, 30) == 1:
                chest = Chest(j*32, i*32 + 64)
                chest_group.add(chest)

# Load in a background image (we must resize)
background_image = pygame.transform.scale(pygame.image.load("Background.png"), (1280, 736))
background_rect = background_image.get_rect()
background_rect.topleft = (0, 0)

# Create the game
weapon = Weapon(weapon_group)
game = Game(monster_group, platform_group, weapon)
game.draw_hud()
game.pause_game("Dungeon Dash", "Press 'Enter' to Begin")

# The main game loop
running = True
while running:
    # Check to see if the user wants to quit
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            sys.exit()
        if event.type == pygame.KEYDOWN:
            # Player wants to jump
            if event.key == pygame.K_SPACE:
                player.jump()

    # Blit the background
    display_surface.blit(background_image, background_rect)

    # Draw tiles
    main_tile_group.update()
    main_tile_group.draw(display_surface)

    platform_group.update()
    platform_group.draw(display_surface)

    # Update and draw sprite groups
    chest_group.update()
    chest_group.draw(display_surface)

    player_group.update()
    player_group.draw(display_surface)

    monster_group.update()
    monster_group.draw(display_surface)

    weapon_group.update()
    weapon_group.draw(display_surface)

    # Create, Update and draw the game
    game.update()
    game.draw_hud()
    #weapon.update()
    chest.update()

    # Update the display and tick the clock
    pygame.display.update()
    clock.tick(FPS)

# End the game
pygame.quit()


