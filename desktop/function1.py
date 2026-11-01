import arcade as aa
from function2 import *

class Game1(Game2):
    def setup(self):
        if self.load_game_statue < 1:
            self.load_game()
        # 加载地图
        map_name = resource_path('files', f'map{self.level}.tmx')
        self.tile_map = aa.load_tilemap(map_name, scaling=map_scale)
        self.scene = aa.Scene.from_tilemap(self.tile_map)
        # Arcade 3 keeps the layer mapping private; retain the original lookup
        # interface used throughout the game.
        self.scene.name_mapping = {
            name: self.scene.get_sprite_list(name)
            for name in self.scene._name_mapping
        }
        if self.level == 6:
            pipe = aa.Sprite(resource_path('images', 'tile_0132.png'), scale=2)
            pipe.position = 8370, 1818
            self.scene.add_sprite_list_before('管道', '砖块', sprite_list=aa.SpriteList())
            self.scene.name_mapping['管道'] = self.scene.get_sprite_list('管道')
            self.scene.name_mapping['管道'].append(pipe)
        bg_path = resource_path('button&bg', f'bg{self.level % 4 + 1}.jpg')
        self.bg = aa.Sprite(bg_path, scale=self.scale_change(bg_path))
        self.bg.position = screen_width // 2, screen_height // 2
        bg_alpha_path = resource_path('button&bg', 'bg_alpha.png')
        self.bg_alpha = aa.Sprite(bg_alpha_path, scale=self.scale_change(bg_alpha_path))
        self.bg_alpha.position = screen_width // 2, screen_height // 2
        self.bg_alpha.alpha = 50
        # 玩家
        self.key_list = [[aa.key.UP, aa.key.W, aa.key.LEFT, aa.key.A, aa.key.RIGHT, aa.key.D],
                         [aa.key.RETURN, aa.key.SPACE, aa.key.DOWN, aa.key.S, aa.key.UP, aa.key.W]]
        self.player_num = len(self.scene.name_mapping['玩家'])
        self.player_1 = self.scene.name_mapping["玩家"][0]
        self.player_1.pre_key = 1
        self.player_1.now_key = 1
        if self.save_data_index != 10 and self.load_game_statue < 1:
            self.save_data_list = form_list[self.save_data_index]
            self.player_1.position = self.save_data_list[7], self.save_data_list[8]
        
        if self.player_num == 2:
            self.player_2 = self.scene.name_mapping['玩家'][1]
            self.player_1.texture = self.naruto_common_texture
            self.player_2.texture = self.sasuke_common_texture
            self.player_2.pre_key = 1
            self.player_2.now_key = 1
            if self.save_data_index != 10 and self.load_game_statue < 1:
                self.save_data_list = form_list[self.save_data_index]
                self.player_2.position = self.save_data_list[9], self.save_data_list[10]
        else:
            self.player_2 = aa.Sprite()
            if self.level in self.naruto_level:
                self.player_1.texture = self.naruto_common_texture
            elif self.level in self.sasuke_level:
                self.player_1.texture = self.sasuke_common_texture
        if self.player_num != 1 or (self.level not in self.naruto_level and self.level not in self.sasuke_level):
            self.skill_action = None
            self.attack_until = 0.0
        self.load_game_statue += 1
            
        self.platforms = []
        if self.scene.name_mapping.get('移动的砖块'):
            self.platforms.append(self.scene.name_mapping["移动的砖块"])
        if self.level == 6:
            if self.level6_save_position == 1:
                self.player_1.position = 8442, 1800
                self.scene.name_mapping['砖块'][0].kill()
            elif self.level6_save_position == 2:
                self.player_1.position = 108, 1260
                self.scene.name_mapping['砖块'][0].kill()
                self.scene.name_mapping['砖块'][0].kill()
        # 转换属性
        self.static = [self.scene.name_mapping["墙"], self.scene.name_mapping["砖块"]]
        if self.player_num == 2 and self.level >= 8:
            self.static_1 = [self.scene.name_mapping["墙"], self.scene.name_mapping["砖块"], self.scene.name_mapping['按钮碰撞体'], self.scene.name_mapping['墙3']]
            self.static_2 = [self.scene.name_mapping["墙"], self.scene.name_mapping["砖块"], self.scene.name_mapping['按钮碰撞体'], self.scene.name_mapping['墙2']]
            self.static = [self.scene.name_mapping["墙"], self.scene.name_mapping["砖块"], self.scene.name_mapping['按钮碰撞体'], self.scene.name_mapping['墙2'], self.scene.name_mapping['墙3']]
        for brick in self.scene.name_mapping["砖块"]:
            brick.properties["num"] = 1
        self.physics_engine_1 = aa.PhysicsEnginePlatformer(self.player_1, platforms=self.platforms, walls=self.static, gravity_constant=gravity)
        if self.player_num == 2:
            self.physics_engine_2 = aa.PhysicsEnginePlatformer(self.player_2, platforms=self.platforms, walls=self.static, gravity_constant=gravity)
        # 数字为0砖块
        self.zero_brick_list = aa.SpriteList()
        # 游戏状态
        self.game_status = aa.Sprite()
        self.game_status.position = screen_width // 2, screen_height // 2
        self.game_status.scale = 0.5
        self.game_status.text = "游戏中"

        self.money_list = aa.SpriteList()
        if self.scene.name_mapping.get('金币'):
            for jb in self.scene.name_mapping["金币"]:
                self.money_list.append(jb)
        self.get_money = 0

        self.player_camera = aa.camera.Camera2D(window=self.window)
        self.game_status_camera = aa.camera.Camera2D(window=self.window)

        if self.scene.name_mapping.get('手里剑'):
            self.slk = self.scene.name_mapping['手里剑'][0]
        else:
            self.slk = aa.Sprite()
        self.slk.alpha = 0
        self.slk.status = 'stop'

        self.skill_effects = aa.SpriteList()
        self.naruto_invincible_until = 0.0
        self.skill_action = None
        self.skill_action_until = 0.0
        self.skill_action_frame = 0
        self.attack_until = 0.0
        self.chakra = CHAKRA_MAX

        if self.scene.name_mapping.get('千鸟'):
            self.qdl = self.scene.name_mapping['千鸟'][0]
        else:
            self.qdl = aa.Sprite()
        self.qdl.alpha = 0
        self.qdl.last_use_time = time.time() - 15
        self.qdl.using = False
        self.qdl.using_time = 0
        self.qdl.load_level6_position = 15 - time.time() + self.qdl.last_use_time

        self.menu_button = aa.Sprite(resource_path('button&bg', 'menu_button.png'), scale=0.75)
        self.menu_button.position = screen_width // 2, screen_height - 100
        self.menu = aa.Sprite(resource_path('button&bg', 'menu.png'), scale=0.9)
        self.menu_draw = False
        self.menu.position = screen_width // 2, screen_height // 2
        self.close = aa.Sprite(resource_path('button&bg', 'close.png'))
        self.close.position = screen_width // 2 + 270, screen_height - 170
        
        self.next_bgm_button = aa.Sprite(resource_path('button&bg', 'next.png'))
        self.next_bgm_button.position = screen_width // 2 + 40, screen_height - 180
        self.stop_bgm_button = aa.Sprite(resource_path('button&bg', 'stop.png'), scale=0.7)
        self.stop_bgm_button.position = screen_width // 2, screen_height - 180
        self.continue_bgm_button = aa.Sprite(resource_path('button&bg', 'continue.png'), scale=0.7)
        self.continue_bgm_button.position = screen_width // 2 - 40, screen_height - 180

        self.save_time = time.time()
        self.save_flag = False
        self.save_alpha = 255

        self.heart_pic = aa.Sprite(resource_path('button&bg', '心脏.png'), scale=0.3)
        self.heart_pic.position = 60, screen_height - 40
        self.slk_pic = aa.Sprite(resource_path('button&bg', 'slk.png'), scale=0.15)
        self.slk_pic.position = 60, screen_height - 100
        self.money_pic = aa.Sprite(resource_path('button&bg', '金币.png'), scale=0.1)
        self.money_pic.position = screen_width - 130, screen_height - 40
        self.chakra_pic = aa.Sprite(resource_path(*NARUTO_SKILL_ASSET_DIR, '查克拉.png'), scale=0.68)
        self.chakra_pic.position = screen_width - 130, screen_height - 100

        self.eye = aa.Sprite(resource_path('button&bg', '鼬万花筒.png'))
        self.eye.alpha = 0
        self.eye.position = screen_width // 2, screen_height // 2
        self.eyes_hs_status = 0

    def on_draw(self):
        self.clear()
        aa.draw_sprite(self.bg)
        aa.draw_sprite(self.bg_alpha)
        if self.tile_map.width * self.tile_map.tile_width * 2 > screen_width or self.tile_map.height * self.tile_map.tile_height * 2 > screen_height:
            self.player_camera.use()
        self.scene.draw()
        self.skill_effects.draw()
        self.game_status_camera.use()
        aa.draw_sprite(self.menu_button)
        aa.draw_sprite(self.heart_pic)
        aa.draw_sprite(self.slk_pic)
        aa.draw_sprite(self.money_pic)
        if self._chakra_active():
            aa.draw_sprite(self.chakra_pic)
        aa.draw_sprite(self.eye)

        aa.draw_text(f"第{self.level}关", screen_width // 2, screen_height-40, aa.color.BLACK,
                        font_size=20, font_name='simhei', anchor_x="center", anchor_y="center")
        aa.draw_text(f"x{self.money}", screen_width-90, screen_height-40, aa.color.YELLOW, 
                     font_size=20, font_name='simhei', anchor_x='center', anchor_y='center')
        if self._chakra_active():
            aa.draw_text(f"x{int(self.chakra)}", screen_width-90, screen_height-100, aa.color.DARK_BLUE,
                         font_size=20, font_name='simhei', anchor_x='center', anchor_y='center')
        aa.draw_text(f"x{self.heart}", 110, screen_height-40, aa.color.RED, 
                     font_size=20, font_name='simhei', anchor_x='center', anchor_y='center')
        aa.draw_text(f"x{self.slk_num}", 110, screen_height-100, aa.color.BLACK_OLIVE, 
                     font_size=20, font_name='simhei', anchor_x='center', anchor_y='center')
        if self.save_flag:
            aa.draw_text("已完成存档", screen_width // 2, screen_height - 150, (255, 255, 255, self.save_alpha), 
                         font_size=20, font_name='simhei', anchor_x='center', anchor_y='center')
            self.save_alpha -= 1
            if self.save_alpha <= 0:
                self.save_alpha = 255
                self.save_flag = False
            
        if self.menu_draw:
            aa.draw_sprite(self.menu)
            aa.draw_sprite(self.next_bgm_button)
            aa.draw_sprite(self.stop_bgm_button)
            aa.draw_sprite(self.continue_bgm_button)
            aa.draw_sprite(self.close)
            aa.draw_text(f"总金币:{self.all_collected_money}", screen_width // 2 + 100, screen_height-230, aa.color.YELLOW, 
                     font_size=20, font_name='simhei', anchor_x='center', anchor_y='center')
            aa.draw_text(f"等级:{self.player_level}", screen_width // 2 - 100, screen_height-230, aa.color.BLUE, 
                     font_size=20, font_name='simhei', anchor_x='center', anchor_y='center')
            if self.key_num == 1:
                aa.draw_text("空格、W、S和回车、up、down：控制角色移动", screen_width // 2, screen_height-300, aa.color.BLACK, 
                         font_size=20, font_name='simhei', anchor_x='center', anchor_y='center')
            elif self.key_num == 0:
                aa.draw_text("W、A、D和up、left、right：控制角色移动", screen_width // 2, screen_height-300, aa.color.BLACK, 
                         font_size=20, font_name='simhei', anchor_x='center', anchor_y='center')
            aa.draw_text('L：用10金币兑换1生命', screen_width // 2 + 150, screen_height-360, aa.color.BLACK,
                     font_size=20, font_name='simhei', anchor_x='center', anchor_y='center')
            aa.draw_text('K：用10金币兑换10手里剑', screen_width // 2 - 150, screen_height-360, aa.color.BLACK,
                     font_size=20, font_name='simhei', anchor_x='center', anchor_y='center')
            skill_help = (
                'J：苦无    I：影分身    O：螺旋丸' if self._naruto_active()
                else 'J：草薙剑    I：豪火球    O：千鸟' if self._sasuke_active()
                else 'J：普攻    I：技能    O：奥义'
            )
            aa.draw_text(skill_help, screen_width // 2, screen_height-420, aa.color.BLACK,
                     font_size=20, font_name='simhei', anchor_x='center', anchor_y='center')
            aa.draw_text('U：发射1发手里剑', screen_width // 2, screen_height-480, aa.color.BLACK,
                     font_size=20, font_name='simhei', anchor_x='center', anchor_y='center')
            # aa.draw_text('影分身消耗25查克拉，螺旋丸消耗60查克拉', screen_width // 2, screen_height-540, aa.color.AQUAMARINE,
            #          font_size=18, font_name='simhei', anchor_x='center', anchor_y='center')
            aa.draw_text('Q：存档', screen_width // 2, screen_height-540, aa.color.BLACK,
                     font_size=20, font_name='simhei', anchor_x='center', anchor_y='center')
        
    def on_update(self, time):
        self.physics_engine_1.update()
        self.stick_to_lift(self.player_1)
        # Keep the landing frame stable before the goal flag is removed.
        self.texture_change_use()
        self.is_on_brick(self.player_1)
        if self.game_status.text == "游戏中":
            self.deal_game_status()
        self.move_player_camera()
        self.collect_money()
        self.slk_move()
        self.update_player_skill_action()
        self.update_skill_effects()
        if self._chakra_active():
            self.chakra = min(CHAKRA_MAX, self.chakra + CHAKRA_REGEN_PER_SECOND * time)
        self.load_level6_position()
        self.power_up()
        self.eyes_level9()
        if self.player_num == 2:
            self.button()
            self.physics_engine_2.update()
            self.stick_to_lift(self.player_2)
            self.is_on_brick(self.player_2)
        if self.level in self.sasuke_level:
            self.qdl_move()

    def on_key_press(self, key, modifiers):
        if self.skill_action:
            return
        if key == self.key_list[self.key_num][1] and self.physics_engine_1.can_jump():
            self.player_1.change_y = self.player_jump_speed
            self.jump_file.play()
        elif key == self.key_list[self.key_num][3]:
            self.player_1.change_x = -self.player_move_speed
            self.player_1.pre_key = 0
        elif key == self.key_list[self.key_num][5]:
            self.player_1.change_x = self.player_move_speed
            self.player_1.pre_key = 1
        elif self.player_num == 2:
            if key == self.key_list[self.key_num][0] and self.physics_engine_2.can_jump():
                self.player_2.change_y = self.player_jump_speed
                self.jump_file.play()
            elif key == self.key_list[self.key_num][2]:
                self.player_2.change_x = -self.player_move_speed
                self.player_2.pre_key = 0
            elif key == self.key_list[self.key_num][4]:
                self.player_2.change_x = self.player_move_speed
                self.player_2.pre_key = 1
                
    def on_key_release(self, key, modifiers):
        if not self.skill_action and key == self.key_list[self.key_num][1]:
            self.player_1.change_y = 0
        elif not self.skill_action and key in [self.key_list[self.key_num][3], self.key_list[self.key_num][5]]:
            self.player_1.change_x = 0
        if self.player_num == 2:
            if key == self.key_list[self.key_num][0]:
                self.player_2.change_y = 0
            elif key in [self.key_list[self.key_num][2], self.key_list[self.key_num][4]]:
                self.player_2.change_x = 0
        
        if key == aa.key.L:
            if (self.money - self.get_money) >= 0 and self.money >= 10:
                self.money -= 10
                self.get_money -= 10
                self.heart += 1

        if key == aa.key.K:
            if (self.money - self.get_money) >= 0 and self.money >= 10:
                self.money -= 10
                self.get_money -= 10
                self.slk_num += 10

        if key == aa.key.J:
            self.use_basic_attack()

        if key == aa.key.U and self.attack_ready() and self.slk.status == 'stop' and self.slk_num > 0:
            self.slk.position = self.player_1.position
            self.slk.change_x = 10
            self.slk.change_angle = 10
            self.slk.status = 'move'
            self.player_1.now_key = self.player_1.pre_key
            self.slk.alpha = 255
            self.slk_file.play()
            self.slk_num -= 1
            self.start_attack(0.25)

        if key == aa.key.I:
            if self._naruto_active():
                self.use_naruto_skill()
            else:
                self.use_sasuke_skill()

        if key == aa.key.O:
            if self._naruto_active():
                self.use_naruto_ultimate()
            elif (self.attack_ready() and not self.qdl.using and self.qdl.load_level6_position <= 0
                  and self.player_1.change_x != 0 and self.level in self.sasuke_level):
                self.qdl.using = True
                self.qdl_file.play()
                self.qdl.last_use_time = time.time()
                self.start_attack(6)

        if key == aa.key.Q and self.save_data_index != 10:
            form_list[self.save_data_index] = [self.save_data_index + 1, self.level, self.money, self.all_collected_money, self.heart, self.slk_num, self.level6_save_position, self.player_1.center_x, self.player_1.center_y, self.player_2.center_x, self.player_2.center_y]
            score = {'level' : [], 'money' : [], 'a_money' : [], 'heart' : [], 'slk' : [], 'load_level6_positiond' : [], 'x' : [], 'y' : [], 'x1' : [], 'y1' : []}
            for i in range(len(form_list)):
                for j in range(len(form_list[i]) - 1):
                    score[header[j + 1]].append(form_list[i][j + 1])
            form = pd.DataFrame(data=score)
            form.to_csv(SAVE_FILE, index_label='name', header=['level', 'money', 'a_money', 'heart', 'slk', 'load_level6_positiond', 'x', 'y', 'x1', 'y1'])
            self.save_flag = True
            self.save_time = time.time()
            
    def on_mouse_release(self, x, y, button, modifiers):
        if self.next_bgm_button.collides_with_point((x, y)):
            self.bgm_player_list[self.bgm_num].pause()
            self.bgm_player_list[self.bgm_num].seek(0)
            if self.bgm_num == 2:
                self.bgm_num = 0
            else:
                self.bgm_num += 1
            self.bgm_player_list[self.bgm_num].play()
    
        if self.stop_bgm_button.collides_with_point((x, y)):
            self.bgm_player_list[self.bgm_num].pause()
    
        if self.continue_bgm_button.collides_with_point((x, y)):
            self.bgm_player_list[self.bgm_num].play()

        if self.menu_button.collides_with_point((x, y)):
            self.menu_draw = True
            
        if self.close.collides_with_point((x, y)):
            self.menu_draw = False
