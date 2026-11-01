import arcade as aa
import random
from pyglet.media import Player, load, StaticSource
import os
import sys
import re

# resource
base_dir = os.path.dirname(os.path.realpath(sys.argv[0]))
os.chdir(base_dir)

screen_width = 1080
screen_height = 720

def scale_change(image):
    texture = aa.load_texture(image)
    width, height = texture.width, texture.height
    scale1, scale2 = screen_height / height, screen_width / width
    return max(scale1, scale2)

def natural_sort_key(s):
    return [int(text) if text.isdigit() else text.lower() 
            for text in re.split(r'(\d+)', s)]

class BGmodel(aa.View):
    def __init__(self):
        super().__init__()
        self.bg = aa.Sprite()
        self.bg.position = screen_width // 2, screen_height // 2
        self.bg.alpha = 50
        self.bg.ac = True
        
        self.bg_list = []
        self.bg.num = 0
        for i in range(6):
            t = aa.load_texture(f'images/bg{i + 1}.jpg')
            self.bg_list.append(t)
        self.bg.texture = self.bg_list[self.bg.num]

        self.rectangle = aa.SpriteList()
        self.time = 0

    def texture_change(self):
        self.bg.texture = self.bg_list[self.bg.num]
        self.bg.scale = scale_change(f'images/bg{self.bg.num + 1}.jpg')
        if self.bg.ac:
            self.bg.alpha += 1
            if self.bg.alpha >= 100:
                self.bg.ac = False
        else:
            self.bg.alpha -= 1
            if self.bg.alpha <= 0:
                self.bg.ac = True
                self.bg.num += 1
                if self.bg.num > 5:
                    self.bg.num = 0

    def rectangle_change(self):
        for i in range(50):
            if random.random() <= 0.05:
                height = random.randint(150, 200)
            else:
                height = random.randint(10, 100)
            r = aa.SpriteSolidColor(20, height, aa.color.WHITE)
            r.left = i * 22
            r.bottom = 0
            self.rectangle.append(r)

    def on_update(self, time):
        self.texture_change()
        self.time += time
        if self.time > 0.125:
            self.rectangle.clear()
            self.rectangle_change()
            self.time = 0

class Start(BGmodel):
    def __init__(self):
        super().__init__()
        self.title1 = aa.Sprite('images/title1.png')
        self.title1.position = screen_width // 2, 550
        self.title2 = aa.Sprite('images/title2.png')
        self.title2.position = screen_width // 2, 400
        self.start_button = aa.Sprite('images/start_button.png', scale=1.5)
        self.start_button.position = screen_width // 2, 250

    def on_draw(self):
        self.clear()
        self.bg.draw()
        self.title1.draw()
        self.title2.draw()
        self.start_button.draw()
        self.rectangle.draw()

    def on_update(self, time):
        super().on_update(time)

    def on_mouse_release(self, x, y, button, modifiers):
        if self.start_button.collides_with_point((x, y)):
            w.show_view(menu)

class Menu(BGmodel):
    def __init__(self):
        super().__init__()
        self.pics = aa.SpriteList()
        self.sounds = []

        if os.path.exists('sounds') and os.path.isdir('sounds'):
            for file_name in os.listdir('sounds'):
                if file_name.lower().endswith('.mp3'):
                    file_path = os.path.join('sounds', file_name)
                    self.sounds.append(file_path)

            self.sounds.sort(key=lambda x: natural_sort_key(os.path.basename(x)))

        for i in range(len(self.sounds)):
            pic = aa.Sprite(f'images/{i + 1}.png', scale=0.4)
            pic.position = screen_width // 2, screen_height // 2 + 80
            self.pics.append(pic)
        
        self.current_index = 0
        self.is_playing = False
        self.is_paused = False
        self.loop_all = False # True是列表循环，False是单曲循环
        self.player = Player()
        self.player.volume = 1
        self.load_current_song()
        self.pic_ac = False

        self.next = aa.Sprite('images/next.png', scale=(15 / 7))
        self.next.position = screen_width // 2 + 150, screen_height // 2 - 180
        self.last = aa.Sprite('images/last.png', scale=(15 / 7))
        self.last.position = screen_width // 2 - 150, screen_height // 2 - 180
        self.stop = aa.load_texture('images/stop.png')
        self.con = aa.load_texture('images/continue.png')
        self.sc = aa.Sprite(scale=1.5)
        self.sc.position = screen_width // 2 + 50, screen_height // 2 - 180
        self.sc.texture = self.con
        self.again = aa.Sprite('images/again.png', scale=1.2)
        self.again.position = screen_width // 2 - 50, screen_height // 2 - 180

    def load_current_song(self):
        source = load(self.sounds[self.current_index])
        self.player.delete()
        self.player = Player()
        self.player.queue(source)
        self.player.volume = 0.7
        self.player.on_eos = self.on_song_end

    def on_song_end(self):
        if self.loop_all:
            self.next_song()
            self.play()
        else:
            self.player.seek(0)
            if self.is_playing:
                self.player.play()

    def play(self):
        """播放音乐"""
        if not self.is_playing:
            self.player.play()
            self.is_playing = True
            self.is_paused = False
            self.pic_ac = True
            
    def pause(self):
        """暂停音乐"""
        if self.is_playing and not self.is_paused:
            self.player.pause()
            self.is_playing = False
            self.is_paused = True
            self.pic_ac = False
            
    def resume(self):
        """恢复播放"""
        if self.is_paused:
            self.player.play()
            self.is_playing = True
            self.is_paused = False
            self.pic_ac = True
            
    def stop_last(self):
        """停止播放"""
        self.player.pause()
        self.player.seek(0)
        self.is_playing = False
        self.is_paused = False
        self.pic_ac = False
        
    def next_song(self):
        """下一首"""
        self.stop_last()
        self.current_index = (self.current_index + 1) % len(self.sounds)
        self.pics[self.current_index].angle = 0
        self.load_current_song()
        
    def previous_song(self):
        """上一首"""
        self.stop_last()
        self.current_index = (self.current_index - 1) % len(self.sounds)
        self.current_index = (self.current_index - 1) % len(self.pics)
        self.pics[self.current_index].angle = 0
        self.load_current_song()

    def on_draw(self):
        self.clear()
        self.bg.draw()
        self.rectangle.draw()
        self.pics[self.current_index].draw()
        self.last.draw()
        self.next.draw()
        self.sc.draw()
        self.again.draw()
        sound_name =  os.path.basename(self.sounds[self.current_index]).replace('.mp3', '', 1)
        aa.draw_text(f"当前播放: {sound_name}", screen_width // 2, 650, aa.color.WHITE, 
                    font_size=30, font_name='simhei', anchor_x='center', anchor_y='center')
        if not self.loop_all:
            aa.draw_text('1', screen_width // 2 - 50, screen_height // 2 - 180, aa.color.WHITE, 
                         anchor_x='center', anchor_y='center')

    def on_update(self, time):
        super().on_update(time)
        if self.pic_ac:
            self.pics[self.current_index].angle += 1

    def on_mouse_release(self, x, y, button, modifiers):
        if self.sc.collides_with_point((x, y)):
            if not self.is_playing:
                if self.is_paused:
                    self.resume()
                else:
                    self.play()
                self.sc.texture = self.stop
            else:
                self.pause()
                self.sc.texture = self.con
                
        elif self.next.collides_with_point((x, y)):
            self.next_song()
            self.sc.texture = self.stop if self.is_playing else self.con
            
        # 上一首按钮
        elif self.last.collides_with_point((x, y)):
            self.previous_song()
            self.sc.texture = self.stop if self.is_playing else self.con
            
        # 循环模式切换按钮
        elif self.again.collides_with_point((x, y)):
            self.loop_all = not self.loop_all
            
        # 点击图片重新开始播放当前歌曲
        elif self.pics[self.current_index].collides_with_point((x, y)):
            if self.is_playing:
                self.stop_last()
                self.player.seek(0)
                self.play()
            else:
                self.stop_last()
                self.player.seek(0)
                self.play()
                self.sc.texture = self.stop
            
w = aa.Window(screen_width, screen_height, '鸣佐的试炼_前传')
start = Start()
menu = Menu()
w.show_view(start)
w.run()
