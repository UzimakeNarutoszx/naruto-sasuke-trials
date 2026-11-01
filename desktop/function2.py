from function3 import *

class Game2(Game3):
    def is_on_brick(self, player):
        result = ''
        player.center_y -= 1
        for i in self.scene.name_mapping['砖块']:
            if player.collides_with_sprite(i):
                result = player.collides_with_sprite(i)
                i.kill()
        player.center_y += 1
        return result

    def is_on_block(self, player):
        player.center_y -= 1
        try:
            result = any(
                player.collides_with_list(self.scene.name_mapping[name])
                for name in ("墙", "砖块", "按钮碰撞体", "移动的砖块")
                if self.scene.name_mapping.get(name)
            )
        finally:
            player.center_y += 1
        return result

    def collect_money(self):
        if self.scene.name_mapping.get('金币'):
            for jb in self.money_list:
                if aa.check_for_collision_with_list(jb, self.scene.name_mapping['玩家']):
                    jb.kill()
                    self.money += 1
                    self.all_collected_money += 1
                    self.get_money += 1
                    break
            
            if self.get_money < 0:
                self.get_money = 0
            if self.money < 0:
                self.money = 0

    def slk_move(self):
        if self.slk.status == 'move':
            if self.player_1.now_key == 1:
                self.slk.center_x += self.slk.change_x
                self.slk.angle += self.slk.change_angle
            elif self.player_1.now_key == 0:
                self.slk.center_x -= self.slk.change_x
                self.slk.angle -= self.slk.change_angle
            if (self.slk.left >= screen_width and self.slk.left >= screen_width // 2 + self.player_1.center_x) or self.slk.right <= self.player_1.center_x - screen_width // 2 or aa.check_for_collision_with_list(self.slk, self.static[0]):
                self.slk.status = 'stop'
                self.slk.alpha = 0
                self.slk.center_x = 0
                self.slk.angle = 0
                self.slk.change_x = 0
            if self.scene.name_mapping.get('障碍物'):
                for i in self.scene.name_mapping['障碍物']:
                    if aa.check_for_collision(i, self.slk):
                        self.slk.status = 'stop'
                        self.slk.alpha = 0
                        self.slk.center_x = 0
                        self.slk.angle = 0
                        self.slk.change_x = 0
                        i.kill()

    def _naruto_active(self):
        """Naruto skills are available only in single-player Naruto stages."""
        return self.player_num == 1 and self.level in self.naruto_level

    def _sasuke_active(self):
        """Sasuke skills are available only in single-player Sasuke stages."""
        return self.player_num == 1 and self.level in self.sasuke_level

    def _chakra_active(self):
        return self._naruto_active() or self._sasuke_active()

    def attack_ready(self):
        return (time.time() >= self.attack_until and
                not (self._sasuke_active() and self.qdl.using))

    def start_attack(self, duration):
        self.attack_until = time.time() + duration

    def has_chakra(self, key):
        return self.chakra >= CHAKRA_COSTS[key]

    def spend_chakra(self, key):
        self.chakra -= CHAKRA_COSTS[key]

    def _skill_targets(self):
        for name in ("砖块", "障碍物"):
            targets = self.scene.name_mapping.get(name)
            if targets:
                yield from targets

    def _clear_area(self, area):
        for target in list(self._skill_targets()):
            if aa.check_for_collision(area, target):
                target.kill()

    def _spawn_skill_effect(self, asset_name, position, scale=1.0, lifetime=0.25,
                            frame_count=1, loop_animation=False):
        effect = aa.Sprite(resource_path(*NARUTO_SKILL_ASSET_DIR, asset_name), scale=scale)
        effect.position = position
        effect.expires_at = time.time() + lifetime
        effect.animation_frames = [
            aa.load_texture(resource_path(*NARUTO_SKILL_ASSET_DIR, f'{asset_name[:-4]}_{i:02d}.png'))
            for i in range(1, frame_count + 1)
        ]
        effect.animation_frame_index = 0
        effect.animation_next_time = time.time() + lifetime / max(frame_count, 1)
        effect.loop_animation = loop_animation
        self.skill_effects.append(effect)

    def _start_player_action(self, action, frame_count, duration, direction=None):
        self.skill_action = action
        self.skill_action_frame = 0
        self.skill_action_frame_count = frame_count
        self.skill_action_until = time.time() + duration
        self.skill_action_next_frame = time.time()
        self.skill_action_direction = direction
        self.skill_action_start_x = self.player_1.center_x
        if action not in ('ultimate_cast', 'clone_lock'):
            if self.skill_action != 'clone_lock':
                self.player_1.change_x = 0
                self.player_1.change_y = 0

    def _finish_naruto_ultimate(self):
        """Stop Naruto, then apply Rasengan's single impact at the cast's end."""
        direction = self.skill_action_direction
        impact = (
            self.player_1.center_x + direction * 54,
            self.player_1.center_y,
        )
        blast_area = aa.SpriteCircle(96, (60, 180, 255, 1))
        blast_area.position = impact
        self._clear_area(blast_area)
        # Hold the enlarged ripple long enough for the delayed impact to read
        # clearly, then surround it with small outward-moving chakra wisps.
        self._spawn_skill_effect(
            '螺旋丸.png', impact, scale=1.45, lifetime=0.85,
            frame_count=8, loop_animation=True,
        )
        particle_texture = aa.load_texture(
            resource_path(*NARUTO_SKILL_ASSET_DIR, '螺旋丸_06.png')
        )
        particle_lifetime = 0.62
        for index in range(10):
            angle = index * (2 * np.pi / 10) + np.pi / 10
            particle = aa.Sprite(scale=0.28 if index % 2 == 0 else 0.19)
            particle.texture = particle_texture
            particle.position = impact
            particle.is_rasengan_particle = True
            particle.particle_velocity_x = np.cos(angle) * (2.0 + (index % 3) * 0.55)
            particle.particle_velocity_y = np.sin(angle) * (2.0 + (index % 3) * 0.55)
            particle.particle_lifetime = particle_lifetime
            particle.expires_at = time.time() + particle_lifetime
            self.skill_effects.append(particle)

    def update_player_skill_action(self):
        if not self.skill_action:
            return
        now = time.time()
        if now >= self.skill_action_until:
            self.player_1.change_x = 0
            self.player_1.change_y = 0
            if self.skill_action == 'ultimate_cast':
                self._finish_naruto_ultimate()
            self.skill_action = None
            self.player_1.texture = (
                self.naruto_common_texture if self._naruto_active()
                else self.sasuke_common_texture
            )
            return
        if now >= self.skill_action_next_frame:
            self.skill_action_frame = min(self.skill_action_frame + 1, self.skill_action_frame_count - 1)
            if self.skill_action == 'attack':
                direction_name = '普攻右' if self.skill_action_direction > 0 else '普攻左'
                self.player_1.texture = aa.load_texture(
                    resource_path(*NARUTO_SKILL_ASSET_DIR, f'{direction_name}_{self.skill_action_frame + 1:02d}.png')
                )
            elif self.skill_action == 'sasuke_attack':
                direction_name = '草薙剑右' if self.skill_action_direction > 0 else '草薙剑左'
                self.player_1.texture = aa.load_texture(
                    resource_path(*SASUKE_SKILL_ASSET_DIR, f'{direction_name}_{self.skill_action_frame + 1:02d}.png')
                )
            elif self.skill_action == 'ultimate_cast':
                index = self.skill_action_frame % 8 + (1 if self.skill_action_direction > 0 else 9)
                self.player_1.texture = aa.load_texture(resource_path('角色', f'{index}.png'))
            self.skill_action_next_frame = now + (self.skill_action_until - now) / max(self.skill_action_frame_count, 1)
        if self.skill_action == 'ultimate_cast':
            self.player_1.change_x = self.skill_action_direction * (self.player_move_speed + 1)

    def _facing(self):
        return 1 if self.player_1.pre_key else -1

    def use_basic_attack(self):
        if self._naruto_active():
            return self.use_naruto_basic_attack()
        if self._sasuke_active():
            return self.use_sasuke_basic_attack()
        return False

    def use_naruto_basic_attack(self):
        if not self.attack_ready():
            return False
        direction = self._facing()
        area = aa.SpriteSolidColor(72, 52, color=(255, 180, 60, 1))
        area.position = self.player_1.center_x + direction * 42, self.player_1.center_y
        self._clear_area(area)
        self._start_player_action('attack', 10, 0.2, direction)
        self.start_attack(0.2)
        self.naruto_attack_file.play()
        return True

    def use_sasuke_basic_attack(self):
        if not self.attack_ready():
            return False
        direction = self._facing()
        area = aa.SpriteSolidColor(76, 58, color=(220, 220, 255, 1))
        area.position = self.player_1.center_x + direction * 44, self.player_1.center_y
        self._clear_area(area)
        self._start_player_action('sasuke_attack', 6, 0.24, direction)
        self.start_attack(0.24)
        self.sasuke_attack_file.play()
        return True

    def use_naruto_skill(self):
        if not self.attack_ready() or not self._naruto_active() or not self.has_chakra('I'):
            return False
        direction = self._facing()
        clone_frames = [
            aa.load_texture(resource_path('角色', f'{i}.png')) for i in range(1, 9)
        ] if direction == 1 else [
            aa.load_texture(resource_path('角色', f'{i}.png')) for i in range(9, 17)
        ]
        # Begin with a running frame, rather than the taller standing texture.
        # This keeps the clone's collision body and visible animation in sync.
        clone = aa.Sprite(scale=self.player_1.scale)
        clone.texture = clone_frames[0]
        # Spawn at the player's feet, just beyond the leading edge.  The clone
        # texture is a different height from Naruto's, so centre-to-centre
        # placement makes it appear to emerge above the player.
        clone.center_x = self.player_1.center_x + direction * (
            self.player_1.width / 2 + clone.width / 2 + 12
        )
        clone.bottom = self.player_1.bottom
        clone.skill_direction = direction
        clone.skill_speed = self.player_move_speed + 2
        clone.is_shadow_clone = True
        clone.skill_end_x = self.player_1.center_x + direction * (screen_width // 2)
        clone.expires_at = time.time() + abs(clone.skill_end_x - clone.center_x) / clone.skill_speed / 60
        clone.animation_frames = clone_frames
        clone.animation_frame_index = 0
        clone.animation_next_time = time.time()
        clone.change_x = direction * clone.skill_speed
        clone.physics_engine = aa.PhysicsEnginePlatformer(
            clone, platforms=self.platforms, walls=self.static, gravity_constant=gravity
        )
        clone.last_center_x = clone.center_x
        clone.blocked_frames = 0
        self.skill_effects.append(clone)
        self.spend_chakra('I')
        self.start_attack(clone.expires_at - time.time())
        self.shadow_clone_file.play()
        return True

    def use_naruto_ultimate(self):
        if not self.attack_ready() or not self._naruto_active() or not self.has_chakra('O'):
            return False
        direction = self._facing()
        center = self.player_1.center_x + direction * 34, self.player_1.center_y
        self.naruto_invincible_until = time.time() + 1.5
        self._start_player_action('ultimate_cast', 8, 1.2, direction)
        self._spawn_skill_effect(
            '螺旋丸.png', center, scale=0.9, lifetime=1.2,
            frame_count=8, loop_animation=True,
        )
        ultimate = self.skill_effects[-1]
        ultimate.texture = ultimate.animation_frames[0]
        ultimate.alpha = 255
        ultimate.follow_player = True
        ultimate.skill_direction = direction
        ultimate.skill_offset_x = 34
        self.spend_chakra('O')
        self.start_attack(1.2)
        self.rasengan_file.play()
        return True

    def use_sasuke_skill(self):
        if (not self.attack_ready() or not self._sasuke_active() or
                not self.has_chakra('SASUKE_I')):
            return False
        direction = self._facing()
        fireball = aa.Sprite(
            resource_path(
                *SASUKE_SKILL_ASSET_DIR,
                '豪火球.png' if direction > 0 else '豪火球左.png',
            ),
            scale=0.85,
        )
        fireball.center_x = self.player_1.center_x + direction * (
            self.player_1.width / 2 + fireball.width / 2 + 4
        )
        fireball.center_y = self.player_1.center_y + 5
        fireball.is_fireball = True
        fireball.skill_direction = direction
        fireball.skill_speed = 10
        fireball.skill_end_x = self.player_1.center_x + direction * (screen_width // 2)
        fireball.skill_hits = 0
        self.skill_effects.append(fireball)
        self.spend_chakra('SASUKE_I')
        self.start_attack(0.25)
        self.fireball_file.play()
        return True

    def update_skill_effects(self):
        now = time.time()
        for effect in list(self.skill_effects):
            if getattr(effect, 'is_fireball', False):
                effect.center_x += effect.skill_direction * effect.skill_speed
                for target in list(self._skill_targets()):
                    if aa.check_for_collision(effect, target):
                        target.kill()
                        effect.skill_hits += 1
                        if effect.skill_hits >= 2:
                            effect.kill()
                            break
                hit_wall = any(
                    aa.check_for_collision_with_list(effect, walls)
                    for walls in [self.scene.name_mapping.get('墙')]
                    if walls
                )
                reached_end = ((effect.skill_direction > 0 and effect.center_x >= effect.skill_end_x) or
                               (effect.skill_direction < 0 and effect.center_x <= effect.skill_end_x))
                if hit_wall or reached_end:
                    effect.kill()
                continue
            if getattr(effect, 'is_rasengan_particle', False):
                effect.center_x += effect.particle_velocity_x
                effect.center_y += effect.particle_velocity_y
                remaining = max(0, effect.expires_at - now)
                effect.alpha = int(255 * remaining / effect.particle_lifetime)
            if getattr(effect, 'is_shadow_clone', False):
                previous_x = effect.center_x
                effect.change_x = effect.skill_direction * effect.skill_speed
                effect.physics_engine.update()
                if abs(effect.center_x - previous_x) < 0.1:
                    effect.blocked_frames += 1
                else:
                    effect.blocked_frames = 0
                if effect.blocked_frames >= 2 or effect.top < 0:
                    effect.kill()
                    continue
            if now >= getattr(effect, 'expires_at', 0):
                effect.kill()
            elif now >= getattr(effect, 'animation_next_time', now + 1):
                frames = getattr(effect, 'animation_frames', ())
                if frames:
                    if getattr(effect, 'loop_animation', False):
                        effect.animation_frame_index = (effect.animation_frame_index + 1) % len(frames)
                    else:
                        effect.animation_frame_index = min(effect.animation_frame_index + 1, len(frames) - 1)
                    # Arcade preserves a sprite's centre when changing texture.
                    # Naruto's run frames are different heights, so retain the
                    # clone's feet position to stop it floating upward.
                    current_bottom = effect.bottom if getattr(effect, 'is_shadow_clone', False) else None
                    effect.texture = frames[effect.animation_frame_index]
                    if current_bottom is not None:
                        effect.bottom = current_bottom
                    effect.animation_next_time = now + max(0.03, (effect.expires_at - now) / max(len(frames), 1))
            if hasattr(effect, 'skill_direction') and not getattr(effect, 'is_shadow_clone', False):
                if getattr(effect, 'follow_player', False):
                    effect.position = (
                        self.player_1.center_x + effect.skill_direction * effect.skill_offset_x,
                        self.player_1.center_y,
                    )
                else:
                    effect.center_x += effect.skill_direction * effect.skill_speed
                area = aa.SpriteSolidColor(80, 62, color=(255, 180, 60, 1))
                area.position = effect.position
                self._clear_area(area)
                if (not getattr(effect, 'follow_player', False) and
                        ((effect.skill_direction > 0 and effect.center_x >= effect.skill_end_x) or
                        (effect.skill_direction < 0 and effect.center_x <= effect.skill_end_x))):
                    effect.kill()
                        
    def power_up(self):
        if self.player_level < 6:
            self.player_level = self.all_collected_money // 50
            self.player_jump_speed = 15 + self.player_level
            self.player_move_speed = 5 + self.player_level * 0.5
        else:
            self.player_level = 6
            self.player_jump_speed = 20
            self.player_move_speed = 8
    
    def button(self):
        if self.scene.name_mapping.get('按钮'):
            if aa.check_for_collision_with_list(self.scene.name_mapping['按钮'][1], self.scene.name_mapping['玩家']) or aa.check_for_collision_with_list(self.scene.name_mapping['按钮'][2], self.scene.name_mapping['玩家']) or aa.check_for_collision_with_list(self.scene.name_mapping['按钮'][3], self.scene.name_mapping['玩家']) or aa.check_for_collision_with_list(self.scene.name_mapping['按钮'][4], self.scene.name_mapping['玩家']) or aa.check_for_collision_with_list(self.scene.name_mapping['按钮'][5], self.scene.name_mapping['玩家']) or aa.check_for_collision_with_list(self.scene.name_mapping['按钮'][7], self.scene.name_mapping['玩家']):
                self.physics_engine_1 = aa.PhysicsEnginePlatformer(self.player_1, walls=self.static_1, gravity_constant=gravity)
                self.physics_engine_2 = aa.PhysicsEnginePlatformer(self.player_2, walls=self.static_1, gravity_constant=gravity)
            elif aa.check_for_collision_with_list(self.scene.name_mapping['按钮'][0], self.scene.name_mapping['玩家']) or aa.check_for_collision_with_list(self.scene.name_mapping['按钮'][6], self.scene.name_mapping['玩家']) or aa.check_for_collision_with_list(self.scene.name_mapping['按钮'][8], self.scene.name_mapping['玩家']) or aa.check_for_collision_with_list(self.scene.name_mapping['按钮'][9], self.scene.name_mapping['玩家']):
                self.physics_engine_1 = aa.PhysicsEnginePlatformer(self.player_1, walls=self.static_2, gravity_constant=gravity)
                self.physics_engine_2 = aa.PhysicsEnginePlatformer(self.player_2, walls=self.static_2, gravity_constant=gravity)
            else:
                self.physics_engine_1 = aa.PhysicsEnginePlatformer(self.player_1, platforms=self.platforms, walls=self.static, gravity_constant=gravity)
                self.physics_engine_2 = aa.PhysicsEnginePlatformer(self.player_2, platforms=self.platforms, walls=self.static, gravity_constant=gravity)

    def eyes_level9(self):
        if self.scene.name_mapping.get("眼睛触发"):
            if self.eyes_hs_status == 1:
                self.player_1.change_x = 0
                self.player_1.change_y = 0
                self.eye.alpha += 5
                self.eye.angle += 1
                if self.eye.alpha == 255:
                    self.eyes_hs_status = 2

            if self.eyes_hs_status == 2:
                self.player_1.change_x = 0
                self.player_1.change_y = 0
                self.eye.alpha -= 5
                self.eye.angle += 1
                if self.eye.alpha == 0:
                    self.eyes_hs_status = 0
                    self.eye.angle = 0
                    
            for i in self.scene.name_mapping['眼睛触发']:
                if aa.check_for_collision(self.player_1, i):
                    i.kill()
                    self.eye_file.play()
                    num = random.random()
                    self.eyes_hs_status = 1
                    if num < 0.3:
                        self.player_1.position = 90, 288

    
    def is_collide_barrier(self, player):
        result = False
        if self.scene.name_mapping.get("障碍物"):
            for i in self.scene.name_mapping['障碍物']:
                if aa.check_for_collision(player, i):
                    if self.qdl.using:
                        i.kill()
                    else:
                        result = True
            return result

    def move_player_camera(self):
        camera_x = max(screen_width // 2, self.player_1.center_x)
        camera_y = max(screen_height // 2, self.player_1.center_y)
        camera_pos = camera_x, camera_y
        self.player_camera.position = camera_pos

    def stick_to_lift(self, player):
        for lift in self.scene.name_mapping.get('移动的砖块', []):
            gap = player.bottom - lift.top
            if lift.change_y and 0 <= gap <= 2 and player.right > lift.left and player.left < lift.right:
                player.bottom = lift.top
                return

    def texture_change_use(self):
        if self.skill_action:
            return
        n, z = False, False
        player = self.player_1
        if self.level in self.naruto_level:
            n = True
        elif self.level in self.sasuke_level:
            z = True
        elif self.player_num == 2:
            n = True
            z = True
            player = self.player_2
        self.texture_change(player, n, z)

    def texture_change(self, player, n, z):
        if n:
            on_block = self.is_on_block(self.player_1)
            if not on_block:
                if self.player_1.pre_key == 1:
                    self.player_1.texture = self.naruto_jump_texture
                else:
                    self.player_1.texture = self.naruto_jump_left_texture
            elif self.player_1.change_x > 0:
                if time.time() - self.last_switch_time > 0.1:
                    self.naruto_right_index = (self.naruto_right_index + 1) % (len(self.naruto_texture_list) // 2)
                    self.player_1.texture = self.naruto_texture_list[self.naruto_right_index]
                    self.last_switch_time = time.time()
            elif self.player_1.change_x < 0:
                if time.time() - self.last_switch_time > 0.1:
                    self.naruto_left_index = (self.naruto_left_index + 1) % (len(self.naruto_texture_list) // 2)
                    self.player_1.texture = self.naruto_texture_list[self.naruto_left_index + 8]
                    self.last_switch_time = time.time()
            else:
                self.player_1.texture = self.naruto_common_texture
                
        if z:
            on_block = self.is_on_block(player)
            if not on_block:
                if player.pre_key == 1:
                    player.texture = self.sasuke_jump_texture
                else:
                    player.texture = self.sasuke_jump_left_texture
            elif player.change_x > 0 or (self.qdl.using and player.pre_key == 1):
                if time.time() - self.last_switch_time > 0.1:
                    self.susuke_right_index = (self.susuke_right_index + 1) % (len(self.naruto_texture_list) // 2)
                    player.texture = self.sasuke_texture_list[self.susuke_right_index]
                    self.last_switch_time = time.time()
            elif player.change_x < 0 or (self.qdl.using and player.pre_key == 0):
                if time.time() - self.last_switch_time > 0.1:
                    self.susuke_left_index = (self.susuke_left_index + 1) % (len(self.naruto_texture_list) // 2)
                    player.texture = self.sasuke_texture_list[self.susuke_left_index + 8]
                    self.last_switch_time = time.time()
            else:
                player.texture = self.sasuke_common_texture

    def load_level6_position(self):
        if self.level == 6:
            if len(self.scene.name_mapping['砖块']) == 2:
                self.level6_save_position = 1
            elif len(self.scene.name_mapping['砖块']) == 1:
                self.level6_save_position = 2

    def load_game(self):
        if self.save_data_index != 10:
            self.save_data_list = form_list[self.save_data_index]
            self.level = int(self.save_data_list[1])
            self.money = int(self.save_data_list[2])
            self.all_collected_money = int(self.save_data_list[3])
            self.heart = int(self.save_data_list[4])
            self.slk_num = int(self.save_data_list[5])
            self.level6_save_position = int(self.save_data_list[6])

    def scale_change(self, image):
        texture = aa.load_texture(image)
        width, height = texture.width, texture.height
        scale1, scale2 = screen_height / height, screen_width / width
        return max(scale1, scale2)
        
