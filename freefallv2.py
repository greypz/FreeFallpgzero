# === Imports and Constants ===
import random
import math
import time
from pgzero.actor import Actor
from pgzero.rect import Rect
from pgzero.loaders import sounds, images
from pgzero import music

WIDTH = 560
HEIGHT = 700

settings_inputs = {"duration": "120", "sfx_volume": "30", "bgm_volume": "20"}
active_input = None
game_status = 'menu'

# === Player Class ===
class Player:
    def __init__(self, x, y):
        self.actor = Actor('mainslow1', (x, y))
        self.slow_frames = ['mainslow1', 'mainslow2']
        self.fast_frame = 'mainfast'
        self.slow_index = 0
        self.slow_counter = 0
        self.SLOW_SPEED = 15
        self.move_speed = 4
        self.state = 'slow'

    def reset(self, x, y):
        self.actor.pos = (x, y)
        self.state = 'slow'
        self.slow_index = 0
        self.slow_counter = 0
        self.actor.image = self.slow_frames[0]

    def update(self):
        if keyboard.w and self.actor.y < 350:
            self.state = 'fast'
        else:
            self.state = 'slow'
        if keyboard.a and self.actor.x > 5:
            self.actor.x -= self.move_speed
        if keyboard.d and self.actor.x < WIDTH - self.actor.width / 2:
            self.actor.x += self.move_speed
        if self.state == 'slow' and self.actor.y > 150:
            self.slow_counter += 1
            if self.slow_counter >= self.SLOW_SPEED:
                self.slow_counter = 0
                self.slow_index = (self.slow_index + 1) % len(self.slow_frames)
            self.actor.image = self.slow_frames[self.slow_index]
            self.actor.y -= 2
        elif self.state == 'fast':
            self.actor.image = self.fast_frame
            self.actor.y += 1
            self.slow_counter = 0
            self.slow_index = 0

    def draw(self):
        self.actor.draw()

    def collide(self, rect):
        return self.actor.colliderect(rect)

    def scroll_speed(self):
        return -int((self.actor.y - 100) / 10) - 3

    def is_fast(self):
        return self.state == 'fast'

# === Assets and Game State Variables ===
player = Player(265, 150)
bg_image = images.cloudybg

crate_image = images.crate
supply_image = images.supply_drop
sound_effect = sounds.phaserup3
wining_sound = sounds.wining_sound

platforms = []
bg_scroll = 0
MAX_PLATFORMS = 4
counter = True

timer_seconds = int(settings_inputs['duration'])
start_time = time.time()
cumulative_elapsed = 0
last_update_time = time.time()
current_time = timer_seconds
win_message = None

play_rect = Rect((0,0),(0,0))
settings_rect = Rect((0,0),(0,0))
back_rect = Rect((0,0),(0,0))
settings_key_rects = {}

# === Game Control Functions ===
def reset_game():
    global bg_scroll, platforms, start_time, current_time, timer_seconds, game_status, win_message, cumulative_elapsed, last_update_time
    bg_scroll = -bg_image.get_height()
    platforms.clear()
    player.reset(265, 150)
    timer_seconds = int(settings_inputs['duration'])
    start_time = time.time()
    last_update_time = start_time
    cumulative_elapsed = 0
    current_time = timer_seconds
    win_message = None
    music.set_volume(int(settings_inputs['bgm_volume']) / 100)
    sound_effect.set_volume(int(settings_inputs['sfx_volume']) / 100)
    wining_sound.set_volume(int(settings_inputs['sfx_volume']) / 100)
    music.play('bond_bg_music')
    game_status = 'game'

# === Main Draw Function ===
def draw():
    screen.clear()
    if game_status == 'menu':
        draw_menu()
    elif game_status == 'settings':
        draw_settings()
    elif game_status == 'game':
        draw_game()

# === Menu Drawing ===
def draw_menu():
    global play_rect, settings_rect
    screen.fill((30,30,30))
    screen.draw.text("Main Menu", center=(WIDTH//2, HEIGHT//4), fontsize=60, color="white")
    play_rect = Rect((WIDTH//2-50, HEIGHT//2-20), (100,40))
    screen.draw.text("Play", center=(WIDTH//2, HEIGHT//2), fontsize=50, color="green")
    settings_rect = Rect((WIDTH//2-80, HEIGHT//2+60), (160,40))
    screen.draw.text("Settings", center=(WIDTH//2, HEIGHT//2+80), fontsize=50, color="cyan")

# === Settings Screen Drawing ===
def draw_settings():
    global back_rect, settings_key_rects
    screen.fill((40,40,40))
    back_rect = Rect((20,20), (80,40))
    screen.draw.text("< Back", topleft=(20,20), fontsize=30, color="white")
    labels = ["Duration (s):", "SFX Volume (0-100):", "BGM Volume (0-100):"]
    keys = ["duration","sfx_volume","bgm_volume"]
    base_y = HEIGHT // 3
    settings_key_rects.clear()
    for i,label in enumerate(labels):
        y = base_y + i * 60
        screen.draw.text(label, topleft=(50,y), fontsize=25, color="white")
        box = Rect((WIDTH//2, y), (200,40))
        color = "white" if active_input == keys[i] else "gray"
        screen.draw.rect(box, color)
        screen.draw.text(settings_inputs[keys[i]], topleft=(box.x+5,box.y+5), fontsize=25, color="cyan")
        settings_key_rects[keys[i]] = box

# === Game Screen Drawing ===
def draw_game():
    bg_h = bg_image.get_height()
    for i in range(math.ceil(HEIGHT/bg_h) + 2):
        screen.blit(bg_image, (0, i * bg_h + bg_scroll))
    for p in platforms:
        screen.blit(p['surf'], p['rect'])
    player.draw()
    screen.draw.text(str(current_time), topleft=(510,30), fontsize=25, color="black")
    if win_message:
        screen.draw.text(win_message, center=(WIDTH//2,HEIGHT//2), fontsize=60, color="black")

# === Game Update Logic ===
def update():
    global bg_scroll, current_time, win_message, counter, cumulative_elapsed, last_update_time
    if game_status != 'game': return
    if win_message:
        if keyboard.space: reset_game()
        return
    scroll_speed = player.scroll_speed()
    bg_scroll += scroll_speed
    if bg_scroll <= -bg_image.get_height(): bg_scroll = 0
    if len(platforms) < MAX_PLATFORMS:
        attempts = 0
        while attempts < 10:
            px = random.randint(0,4) * 140 + 25
            base_y = random.randint(HEIGHT, HEIGHT + 200)
            offset = 300 if not counter else 0
            counter = not counter
            py = base_y + offset
            surf = crate_image if random.random() < 0.5 else supply_image
            rect = surf.get_rect(center=(px, py))
            if not any(r['rect'].colliderect(rect.inflate(-20,-20)) for r in platforms):
                platforms.append({'surf': surf, 'rect': rect})
                break
            attempts += 1
    for p in platforms[:]:
        p['rect'].y += scroll_speed
        if p['rect'].bottom < 0: platforms.remove(p)
    for p in platforms:
        if player.collide(p['rect']):
            sound_effect.play()
            win_message = "GAME OVER"
            music.stop()
            return
    now = time.time()
    delta = now - last_update_time
    cumulative_elapsed += delta * 3.5 if player.is_fast() else delta
    last_update_time = now
    current_time = max(0, timer_seconds - int(cumulative_elapsed))
    if current_time <= 0:
        win_message = "YOU WIN!!"
        music.stop()
        wining_sound.play()
        return
    player.update()

# === Mouse Click Handling ===
def on_mouse_down(pos, button):
    global game_status, active_input
    if game_status == 'menu':
        if play_rect.collidepoint(pos): reset_game()
        elif settings_rect.collidepoint(pos): game_status = 'settings'
    elif game_status == 'settings':
        if back_rect.collidepoint(pos): game_status = 'menu'
        else:
            for k,r in settings_key_rects.items():
                if r.collidepoint(pos): active_input = k; return
            active_input = None

# === Keyboard Input Handling for Settings ===
def on_key_down(key, unicode):
    global active_input
    if game_status == 'settings' and active_input:
        if key == keys.BACKSPACE: settings_inputs[active_input] = settings_inputs[active_input][:-1]
        elif key == keys.RETURN: active_input = None
        elif unicode.isdigit(): settings_inputs[active_input] += unicode
