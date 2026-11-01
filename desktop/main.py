import arcade as aa
import _locale
from pyglet.media import Player, load, StaticSource
import os
import sys

# Resolve resources before importing modules which read the save file.  PyInstaller
# exposes bundled data through _MEIPASS, while normal Python runs use this file's
# directory rather than the shell's current working directory.
base_dir = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
os.chdir(base_dir)

from function1 import *

_locale._getdefaultlocale = (lambda *args: ['en_US', 'utf8'])

success_list = ['佐助，你到底在哪里？',
                '你不能就此落入深渊！',
                '哼，宇智波鼬......',
                '现在，我的实力还远远不足',
                '现在感觉好多了！',
                '是佐助！你，怎么在这里？    ————你还是那么固执',
                '真怀念啊，之前小队生活的日子    ————不如一个人完成，别妨碍我',
                '已经快晕了......    ————这算什么，没有什么是这双眼睛不能看透的',
                '宇智波鼬......今天就将会是你的祭日！']

class MyGame(Game1):
    def __init__(self):
        super().__init__()
        self.load_game_statue = 0
        self.level = start_level
        self.save_data_index = 10
        self.save_data_list = []
        self.key_num = 0
        self.bgm_num = 0
        
        self.jump_file = aa.load_sound(jump_file)
        self.slk_file = aa.load_sound(slk_file)
        self.qdl_file = aa.load_sound(qdl_file)
        self.eye_file = aa.load_sound(eye_file)
        self.naruto_attack_file = aa.load_sound(naruto_attack_file)
        self.shadow_clone_file = aa.load_sound(shadow_clone_file)
        self.rasengan_file = aa.load_sound(rasengan_file)
        self.sasuke_attack_file = aa.load_sound(sasuke_attack_file)
        self.fireball_file = aa.load_sound(fireball_file)
        self.bgm_player_1 = Player()
        self.bgm_player_1.queue(load(resource_path('sounds', '青鸟.flac')))
        self.bgm_player_1.loop = True
        self.bgm_player_2 = Player()
        self.bgm_player_2.queue(load(resource_path('sounds', 'Bones.mp3')))
        self.bgm_player_2.loop = True
        self.bgm_player_3 = Player()
        self.bgm_player_3.queue(load(resource_path('sounds', '骨架.mp3')))
        self.bgm_player_3.loop = True
        self.bgm_player_list = [self.bgm_player_1, self.bgm_player_2, self.bgm_player_3]
        self.bgm_player_list[self.bgm_num].play()

        self.naruto_common_texture = aa.load_texture(resource_path('角色', '鸣人站立.png'))
        self.sasuke_common_texture = aa.load_texture(resource_path('角色', '佐助站立.png'))
        self.naruto_jump_texture = aa.load_texture(resource_path('角色', '鸣人跳跃.png'))
        self.naruto_jump_left_texture = aa.load_texture(resource_path('角色', '鸣人跳跃左.png'))
        self.sasuke_jump_texture = aa.load_texture(resource_path('角色', '佐助跳跃.png'))
        self.sasuke_jump_left_texture = aa.load_texture(resource_path('角色', '佐助跳跃左.png'))
        self.naruto_right_index, self.naruto_left_index, self.susuke_right_index, self.susuke_left_index = 0, 0, 0, 0
        self.naruto_texture_list = []
        self.sasuke_texture_list = []
        for i in range(1, 17):
            tn1, tn2 = resource_path('角色', f'{i}.png'), resource_path('角色', f'{i + 16}.png')
            t1, t2 = aa.load_texture(tn1), aa.load_texture(tn2)
            self.naruto_texture_list.append(t1)
            self.sasuke_texture_list.append(t2)
        
        self.money = 0
        self.all_collected_money = 0
        self.heart = 10
        self.slk_num = 10
        self.player_move_speed = 5
        self.player_jump_speed = 15
        self.player_last_speed = 5
        self.player_level = 1
        
        self.naruto_level = [1, 2, 5, 6]
        self.sasuke_level = [3, 4, 9]
        self.last_switch_time = time.time()
        self.level6_save_position = 0
    
    def deal_game_status(self):
        # 过关
        if len(self.scene.name_mapping["砖块"]) == 0:
            self.game_status.text = "过关"
            # 通关
            if self.level < max_level:
                self.level += 1
                self.qdl.using = False
                self.window.show_view(game_success)
            else:
                self.game_status.text = "通关"
                self.window.show_view(game_win)

        player_1_hit = time.time() >= self.naruto_invincible_until and self.is_collide_barrier(self.player_1)
        if (self.player_num == 2 and (self.player_2.top < 0 or self.is_collide_barrier(self.player_2))) or player_1_hit or self.player_1.top < 0 or (self.level == 6 and (self.player_1.bottom < 1440 and self.level6_save_position == 0) or (self.player_1.bottom < 720 and self.level6_save_position == 1)):
            self.game_status.text = "失败"
            self.window.show_view(game_lose)
            self.qdl.using = False
            self.money -= self.get_money
            self.heart -= 1
            if self.heart < 1:
                self.game_status.text = '结束'
                self.window.show_view(game_over)
                    
class GameStart(BGmodel):
    def __init__(self):
        super().__init__()
        self.start_button = aa.SpriteList()

        self.title = aa.Sprite(resource_path('button&bg', 'title.png'))
        self.title.position = screen_width // 2, 500
        
        sb = aa.Sprite(resource_path('button&bg', 'start_button.png'))
        sb.position = screen_width // 2, screen_height // 2
        self.start_button.append(sb)

        self.key_select_1 = aa.Sprite(resource_path('button&bg', 'brick.png'), scale=0.2)
        self.key_select_1.position = screen_width // 2 + 25, screen_height // 2 - 200
        self.key_select_2 = aa.Sprite(resource_path('button&bg', 'brick.png'), scale=0.2)
        self.key_select_2.position = screen_width // 2 + 25, screen_height // 2 - 250
        self.finger = aa.Sprite(resource_path('button&bg', '箭头.png'), scale=0.25)
        self.finger.position = screen_width // 2 - 75, screen_height // 2 - 200

        self.alpha1, self.alpha2 = 255, 255
        
    def on_draw(self):
        aa.draw_sprite(self.bg)
        aa.draw_sprite(self.title)
        if game.save_data_index == 10:
            self.alpha2 = 255
            self.alpha1 = 255
            aa.draw_text('选择不使用存档', screen_width // 2 + 2, 248, (0, 0, 0, self.alpha1), font_size=25, font_name='simhei', anchor_x='center', anchor_y='center')
            aa.draw_text('选择不使用存档', screen_width // 2, 250, (255, 255, 255, self.alpha1), font_size=25, font_name='simhei', anchor_x='center', anchor_y='center')
        else:
            self.alpha1 = 255
            self.alpha2 = 255
            aa.draw_text(f'已选择第{game.save_data_index}个存档', screen_width // 2 + 2, 248, (0, 0, 0, self.alpha2), font_size=25, font_name='simhei', anchor_x='center', anchor_y='center')
            aa.draw_text(f'已选择第{game.save_data_index}个存档', screen_width // 2, 250, (255, 255, 255, self.alpha2), font_size=25, font_name='simhei', anchor_x='center', anchor_y='center')
        self.start_button.draw()
        aa.draw_sprite(self.key_select_1)
        aa.draw_sprite(self.key_select_2)
        aa.draw_sprite(self.finger)
        aa.draw_text('默认键位', screen_width // 2 + 23, screen_height // 2 - 202, aa.color.BLACK,font_size=20, font_name='simhei', anchor_x="center", anchor_y='center')
        aa.draw_text('默认键位', screen_width // 2 + 25, screen_height // 2 - 200, aa.color.WHITE,font_size=20, font_name='simhei', anchor_x="center", anchor_y='center')
        aa.draw_text('新键位', screen_width // 2 + 23, screen_height // 2 - 252, aa.color.BLACK,font_size=20, font_name='simhei', anchor_x="center", anchor_y='center')
        aa.draw_text('新键位', screen_width // 2 + 25, screen_height // 2 - 250, aa.color.WHITE,font_size=20, font_name='simhei', anchor_x="center", anchor_y='center')

    def on_update(self, time):
        self.texture_change()
    
    def on_mouse_release(self, x, y, button, modifiers):
        if aa.get_sprites_at_point((x, y), self.start_button):
            game.setup()
            self.window.show_view(game)

        if self.key_select_1.collides_with_point((x, y)):
            game.key_num = 0
            self.finger.position = screen_width // 2 - 75, screen_height // 2 - 200

        if self.key_select_2.collides_with_point((x, y)):
            game.key_num = 1
            self.finger.position = screen_width // 2 - 75, screen_height // 2 - 250

    def on_key_release(self, key, modifiers):
        if key == aa.key.KEY_1:
            self.alpha2 = 255
            game.save_data_index = 1
        elif key == aa.key.KEY_2:
            self.alpha2 = 255
            game.save_data_index= 2
        elif key == aa.key.KEY_3:
            self.alpha2 = 255
            game.save_data_index = 3
        elif key == aa.key.KEY_4:
            self.alpha2 = 255
            game.save_data_index = 4
        elif key == aa.key.KEY_5:
            self.alpha2 = 255
            game.save_data_index = 5
        elif key == aa.key.KEY_6:
            self.alpha2 = 255
            game.save_data_index = 6
        elif key == aa.key.KEY_7:
            self.alpha2 = 255
            game.save_data_index = 7
        elif key == aa.key.KEY_8:
            self.alpha2 = 255
            game.save_data_index = 8
        elif key == aa.key.KEY_9:
            self.alpha2 = 255
            game.save_data_index = 9
        elif key == aa.key.KEY_0:
            self.alpha1 = 255
            game.save_data_index = 10
        elif key == aa.key.F:
            self.alpha2 = 255
            game.save_data_index = 0

class Gamelose(BGmodel):
    def __init__(self):
        super().__init__()
        self.start_button = aa.SpriteList()
        
    def on_draw(self):
        aa.draw_sprite(self.bg)
        aa.draw_text("你失败了", screen_width // 2 + 5, 495, aa.color.BLACK,font_size=100, font_name='simhei', anchor_x='center')
        aa.draw_text("你失败了", screen_width // 2, 500, aa.color.WHITE,font_size=100, font_name='simhei', anchor_x='center')
        aa.draw_text("按回车重来", screen_width // 2 + 3, 247, aa.color.BLACK,font_size=50, font_name='simhei', anchor_x='center')
        aa.draw_text("按回车重来", screen_width // 2, 250, aa.color.WHITE,font_size=50, font_name='simhei', anchor_x='center')

    def on_update(self, time):
        self.texture_change()
    
    def on_key_release(self, key, modifiers):
        if key == aa.key.RETURN:
            self.window.show_view(game)
            game.setup()

class Gamesuccess(BGmodel):
    def __init__(self):
        super().__init__()
        self.start_button = aa.SpriteList()
        sb = aa.Sprite(resource_path('button&bg', 'start_button.png'))
        sb.position = screen_width // 2, screen_height // 2
        self.start_button.append(sb)

    def on_draw(self):
        aa.draw_sprite(self.bg)
        aa.draw_text("恭喜过关", screen_width // 2 + 5, 495, aa.color.BLACK,font_size=100, font_name='simhei', anchor_x='center')
        aa.draw_text("恭喜过关", screen_width // 2, 500, aa.color.WHITE,font_size=100, font_name='simhei', anchor_x='center')
        aa.draw_text(success_list[game.level - 2], screen_width // 2+2, 348, aa.color.BLACK,font_size=20, 
                     font_name='simhei', anchor_x='center')
        aa.draw_text(success_list[game.level - 2], screen_width // 2, 350, aa.color.WHITE,font_size=20, 
                     font_name='simhei', anchor_x='center')
        aa.draw_text("按回车继续", screen_width // 2 + 3, 197, aa.color.BLACK,font_size=30, font_name='simhei', anchor_x='center')
        aa.draw_text("按回车继续", screen_width // 2, 200, aa.color.WHITE,font_size=30, font_name='simhei', anchor_x='center')

    def on_update(self, time):
        self.texture_change()

    def on_key_release(self, key, modifiers):
        if key == aa.key.RETURN:
            self.window.show_view(game)
            game.setup()

class Gameswin(BGmodel):
    def __init__(self):
        super().__init__()

    def on_draw(self):
        aa.draw_sprite(self.bg)
        aa.draw_text("恭喜通关", screen_width // 2 + 5, 545, aa.color.BLACK,font_size=100, font_name='simhei', anchor_x='center')
        aa.draw_text("恭喜通关", screen_width // 2, 550, aa.color.WHITE,font_size=100, font_name='simhei', anchor_x='center')
        aa.draw_text("有话直说。说到做到。这就是我的忍道！", screen_width // 2 + 3, 297, aa.color.BLACK,font_size=30, font_name='simhei', anchor_x='center')
        aa.draw_text("有话直说，说到做到。这就是我的忍道！", screen_width // 2, 300, aa.color.WHITE,font_size=30, font_name='simhei', anchor_x='center')

    def on_update(self, time):
        self.texture_change()

class Gameover(BGmodel):
    def __init__(self):
        super().__init__()

    def on_draw(self):
        aa.draw_sprite(self.bg)
        aa.draw_text("很遗憾，你失败了", screen_width // 2 + 5, 595, aa.color.BLACK,
                     font_size=50, font_name='simhei', anchor_x='center', anchor_y='center')
        aa.draw_text("很遗憾，你失败了", screen_width // 2, 600, aa.color.WHITE,
                     font_size=50, font_name='simhei', anchor_x='center', anchor_y='center')
        aa.draw_text("终于......还是失败了吗", screen_width // 2 + 3, 297, aa.color.BLACK,font_size=30, font_name='simhei', anchor_x='center')
        aa.draw_text("终于......还是失败了吗", screen_width // 2, 300, aa.color.WHITE,font_size=30, font_name='simhei', anchor_x='center')

    def on_update(self ,time):
        self.texture_change()

if __name__ == '__main__':
    w = aa.Window(screen_width, screen_height, '鸣佐的试炼')
    game = MyGame()
    game_start = GameStart()
    game_lose = Gamelose()
    game_success = Gamesuccess()
    game_win = Gameswin()
    game_over = Gameover()
    w.show_view(game_start)
    w.run()
