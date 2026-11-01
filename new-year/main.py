from pyglet.media import Player, load, StaticSource
import arcade as aa
import random
import os
import sys

# resource
base_dir = os.path.dirname(os.path.realpath(sys.argv[0]))
os.chdir(base_dir)

class Using(aa.View):
    def __init__(self):
        super().__init__()
        self.mb = aa.Sprite()
        self.start_mb = True
        self.over_mb = False

    def in_out(self, xian, yin, c_view):
        if xian:
            if self.start_mb:
                self.mb.alpha -= 3
                if self.mb.alpha == 0:
                    self.start_mb = False

        if yin:
            if self.over_mb:
                self.mb.alpha += 3
                if self.mb.alpha == 255:
                    self.over_mb = False
                    self.window.show_view(c_view)

    def scale_change(self, image):
        texture = aa.load_texture(image)
        width, height = texture.width, texture.height
        scale1, scale2 = 1280 / width, 720 / height
        
        return max(scale1, scale2)

class Start(Using):
    def __init__(self):
        super().__init__()
        self.bg = aa.Sprite('images/bg1.jpg', scale=self.scale_change('images/bg1.jpg'))
        self.bg.position = 640, 360
        self.mb = aa.Sprite('images/mb.jpg', scale=3)
        self.mb.position = 640, 360
        self.mb.alpha = 0
        
        self.start_mb = False
        self.over_mb = False

    def on_draw(self):
        self.clear()
        self.bg.draw()
        self.mb.draw()

    def on_update(self, time):
        self.in_out(False, True, mysound)

    def on_mouse_release(self, x, y, button, modifiers):
        self.over_mb = True

class Mysound(Using):
    def __init__(self):
        super().__init__()
        self.bg = aa.Sprite('images/海阔天空.jpg', scale=self.scale_change('images/海阔天空.jpg'))
        self.bg.position = 640, 360
        self.mb = aa.Sprite('images/mb.jpg', scale=3)
        self.mb.position = 640, 360
        self.start_mb = True
        self.over_mb = False

    def on_draw(self):
        self.clear()
        self.bg.draw()
        self.mb.draw()

    def on_update(self, time):
        self.in_out(True, True, game1)

    def on_mouse_release(self, x, y, button, modifiers):
        self.over_mb = True

class Game1(Using):
    def __init__(self):
        super().__init__()
        self.bg = aa.Sprite('images/bg2.jpg', scale=self.scale_change('images/bg2.jpg'))
        self.bg.position = 640, 360
        self.mb = aa.Sprite('images/mb.jpg', scale=3)
        self.mb.position = 640, 360
        self.button = aa.Sprite('images/抽.png')
        self.button.position = 900, 460
        self.jt = aa.Sprite('images/箭头.png')
        self.jt.position = 900, 200
        self.start_mb = True
        self.over_mb = False

        self.class4 = ['Participant_024', 'Participant_060', 'Participant_010', 'Participant_044', 'Participant_008', 'Participant_055', 'Participant_009', 'Participant_050', 'Participant_036', 
             'Participant_081', 'Participant_049', 'Participant_018', 'Participant_026', 'Participant_069', 'Participant_063', 'Participant_051', 'Participant_075', 'Participant_082', 
             'Participant_021', 'Participant_053', 'Participant_080', 'Demo', 'Participant_043', 'Participant_022', 'Participant_013', 'Participant_011', 'Participant_070', 
             'Participant_039', 'Participant_059', 'Participant_065', 'Participant_079', 'Participant_023', 'Participant_025', 'Participant_071', 'Participant_052', 'Participant_017', 'Participant_019', 
             'Participant_020', 'Participant_045', 'Participant_040']
        self.class3 = ['Participant_032', 'Participant_037', 'Participant_054', 'Participant_047', 'Participant_076', 'Participant_068', 'Participant_062', 'Participant_072', 'Participant_030', 'Participant_028', 
                  'Participant_077', 'Participant_041', 'Participant_074', 'Participant_057', 'Participant_015', 'Participant_035', 'Participant_064', 'Participant_056', 'Participant_048', 'Participant_078',
                  'Participant_073', 'Participant_027', 'Participant_083', 'Participant_067', 'Participant_061', 'Participant_046', 'Participant_038', 'Participant_058', 'Participant_014', 'Participant_031', 
                  'Participant_042', 'Participant_033', 'Participant_034', 'Participant_016', 'Participant_012', 'Participant_066', 'Participant_029']
        
        self.times = 0
        self.name = ''
        self.c = self.class4.copy()
        for i in range(37):
            self.c.append(self.class3[i])

    def on_draw(self):
        self.clear()
        self.bg.draw()
        self.button.draw()
        self.jt.draw()
        aa.draw_text(self.name, 900, 300, aa.color.BLACK, font_size=40, anchor_x='center', anchor_y='center', font_name='simhei')
        self.mb.draw()

    def on_update(self, time):
        self.in_out(True, True, game2)

    def on_mouse_release(self, x, y, button, modifiers):
        if self.jt.collides_with_point((x, y)):
            self.over_mb = True

        if self.button.collides_with_point((x, y)):
            self.cq()

    def cq(self):
        if self.times >= 2 and 'Participant_014' in self.c:
            self.name = 'Participant_014'
            self.c.remove('Participant_014')
            self.times += 1
        else:
            self.name = random.choice(self.c)
            self.c.remove(self.name)
            self.times += 1

class Game2(Using):
    def __init__(self):
        super().__init__()
        self.bg = aa.Sprite('images/bg3.jpg', scale=self.scale_change('images/bg3.jpg'))
        self.bg.position = 640, 360
        self.button = aa.Sprite('images/抽.png')
        self.button.position = 640, 360
        self.mb = aa.Sprite('images/mb.jpg', scale=3)
        self.mb.position = 640, 360
        self.jt = aa.Sprite('images/箭头.png')
        self.jt.position = 1000, 200
        self.start_mb = True
        self.over_mb = False
        self.l1 = 'qwertypasdfghjklzxcbnm'
        self.l2 = self.l1
        self.l = ''

    def on_draw(self):
        self.clear()
        self.bg.draw()
        self.jt.draw()
        self.button.draw()
        aa.draw_text(self.l, 640, 200, aa.color.BLACK, font_size=70, anchor_x='center', anchor_y='center', font_name='simhei')
        self.mb.draw()
    
    def on_update(self, time):
        self.in_out(True, True, hechang)

    def on_mouse_release(self, x, y, button, modifiers):
        if self.jt.collides_with_point((x, y)):
            self.over_mb = True

        if self.button.collides_with_point((x, y)):
            self.l = random.choice(self.l1) + random.choice(self.l2)
            if self.l in ['sb', 'bs', 'cm', 'cn', 'nm']:
                self.l = random.choice(self.l1) + random.choice(self.l2)

class Hechang(Using):
    def __init__(self):
        super().__init__()
        self.bg = aa.Sprite('images/合唱.jpg', scale=self.scale_change('images/合唱.jpg'))
        self.bg.position = 640, 360
        self.mb = aa.Sprite('images/mb.jpg', scale=3)
        self.mb.position = 640, 360
        self.start_mb = True
        self.over_mb = False

    def on_draw(self):
        self.clear()
        self.bg.draw()
        self.mb.draw()

    def on_update(self, time):
        self.in_out(True, True, start)
        start.mb.alpha = 0

    def on_mouse_release(self, x, y, button, modifiers):
        self.over_mb = True
        
w = aa.Window(1280, 720, '鸣佐的试炼_辞旧迎新')
start = Start()
mysound = Mysound()
game1 = Game1()
game2 = Game2()
hechang = Hechang()
w.show_view(start)
w.run()
