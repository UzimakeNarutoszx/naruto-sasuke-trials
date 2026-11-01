import arcade as aa
import time
import pandas as pd
import numpy as np
import random
import shutil
import sys
from pathlib import Path

map_scale = 2
screen_width = int(30 * 18 * map_scale)
screen_height = int(20 * 18 * map_scale)

RESOURCE_ROOT = Path(getattr(sys, '_MEIPASS', Path(__file__).resolve().parent))

def resource_path(*parts):
    return str(RESOURCE_ROOT.joinpath(*parts))

gravity = 1
start_level = 3
max_level = 9
jump_file = resource_path('sounds', 'jump.wav')
slk_file = resource_path('sounds', 'slk.mp3')
qdl_file = resource_path('sounds', 'qdl.mp3')
eye_file = resource_path('sounds', 'eye.mp3')
naruto_attack_file = resource_path('sounds', 'naruto_attack.wav')
shadow_clone_file = resource_path('sounds', 'shadow_clone.wav')
rasengan_file = resource_path('sounds', 'rasengan.wav')
sasuke_attack_file = resource_path('sounds', 'sasuke_attack.wav')
fireball_file = resource_path('sounds', 'fireball.wav')

CHAKRA_MAX = 100
CHAKRA_REGEN_PER_SECOND = 12
CHAKRA_COSTS = {'I': 25, 'O': 60, 'SASUKE_I': 40}
NARUTO_SKILL_ASSET_DIR = ('技能素材', '鸣人')
SASUKE_SKILL_ASSET_DIR = ('技能素材', '佐助')

save = False
header = ['name', 'level', 'money', 'a_money', 'heart', 'slk', 'cdd', 'x', 'y', 'x1', 'y1']
BUNDLED_SAVE_FILE = RESOURCE_ROOT / 'files' / 'zhanghao.csv'

if getattr(sys, 'frozen', False):
    if sys.platform == 'darwin':
        SAVE_DIRECTORY = Path.home() / 'Library' / 'Application Support' / '鸣佐的试炼'
    elif sys.platform == 'win32':
        SAVE_DIRECTORY = Path(os.environ.get('APPDATA', Path.home())) / '鸣佐的试炼'
    else:
        SAVE_DIRECTORY = Path(os.environ.get('XDG_DATA_HOME', Path.home() / '.local' / 'share')) / '鸣佐的试炼'
    SAVE_DIRECTORY.mkdir(parents=True, exist_ok=True)
    SAVE_FILE = SAVE_DIRECTORY / 'zhanghao.csv'
    if not SAVE_FILE.exists():
        shutil.copy2(BUNDLED_SAVE_FILE, SAVE_FILE)
else:
    SAVE_FILE = BUNDLED_SAVE_FILE

form_read = pd.read_csv(SAVE_FILE, header=0, names=['name', 'level', 'money', 'a_money', 'heart', 'slk', 'cdd', 'x', 'y', 'x1', 'y1'])
form_list = form_read.values.tolist()

class BGmodel(aa.View):
    def __init__(self):
        super().__init__()
        self.bg = aa.Sprite()
        self.bg.position = screen_width // 2, screen_height // 2
        self.bg.alpha = 50
        self.bg.ac = True
        
        self.bg_list = []
        self.bg.num = 0
        for i in range(5):
            t = aa.load_texture(resource_path('button&bg', f'start_bg{i + 1}.jpg'))
            self.bg_list.append(t)
        self.bg.texture = self.bg_list[self.bg.num]

        self.rectangle = aa.SpriteList()
        self.time = 0

    def texture_change(self):
        self.bg.texture = self.bg_list[self.bg.num]
        self.bg.scale = self.scale_change(resource_path('button&bg', f'start_bg{self.bg.num + 1}.jpg'))
        if self.bg.ac:
            self.bg.alpha += 1
            if self.bg.alpha >= 100:
                self.bg.ac = False
        else:
            self.bg.alpha -= 1
            if self.bg.alpha <= 0:
                self.bg.ac = True
                self.bg.num += 1
                if self.bg.num > 4:
                    self.bg.num = 0
    
    def scale_change(self, image):
        texture = aa.load_texture(image)
        width, height = texture.width, texture.height
        scale1, scale2 = screen_height / height, screen_width / width
        return max(scale1, scale2)

class Game3(aa.View):
    def qdl_move(self):
        self.qdl.center_y = self.player_1.center_y + 25
        if self.player_1.pre_key == 0:
            self.qdl.center_x = self.player_1.center_x + 10
        else:
            self.qdl.center_x = self.player_1.center_x - 10
            
        self.qdl.cd = 15 - time.time() + self.qdl.last_use_time
        if not self.qdl.using:
            self.qdl.alpha = 0
            self.player_last_speed = self.player_move_speed
            
        else:
            self.qdl.alpha = 255
            self.qdl.using_time = time.time() - self.qdl.last_use_time
            self.player_move_speed = self.player_last_speed + 3
            if self.qdl.using_time >= 6:
                self.qdl.using = False
                self.player_move_speed -= 3
                self.qdl.using_time = 0

        if self.qdl.cd < 0:
            self.qdl.cd = 0
