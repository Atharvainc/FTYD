import pygame as pg

ATTACK_DATA = {
    #          startup  active  recovery  damage  stun
    "jab":          {'hw':70,"hh":50,"parry_type": "high","startup": 3,  "active": 6,  "recovery": 3,  "damage": 4,  "stun": 8},
    "hook":         {'hw':80,"hh":60,"parry_type": "high","startup": 6,  "active": 6,  "recovery": 6,  "damage": 8,  "stun": 12},
    "low_punch":    {'hw':70,"hh":40,"parry_type": "low","startup": 6,  "active": 6,  "recovery": 6,  "damage": 4,  "stun": 8},
    "forward_punch":{'hw':100,"hh":55,"parry_type": "high","startup": 6,  "active": 6,  "recovery": 6,  "damage": 6,  "stun": 10},
    "back_punch":   {'hw':60,"hh":100,"parry_type": "low","startup": 6,  "active": 6,  "recovery": 6,  "damage": 6,  "stun": 10},
    "uppercut":     {'hw':60,"hh":90,"parry_type": "high","startup": 9,  "active": 9,  "recovery": 12, "damage": 12, "stun": 20,'knockup':True},
    "swing_kick":   {'hw':110,"hh":50,"parry_type": "low","startup": 6,  "active": 9,  "recovery": 12, "damage": 8,  "stun": 15},
    "double_punch": {'hw':90,"hh":55,"parry_type": "high","startup": 6,  "active": 12, "recovery": 9,  "damage": 10, "stun": 18},
    "back_kick":    {'hw':100,"hh":100,"parry_type": "low","startup": 6,  "active": 6,  "recovery": 9,  "damage": 10, "stun": 15},
    "cross":        {'hw':95,"hh":55,"parry_type": "high","startup": 6,  "active": 6,  "recovery": 9,  "damage": 8,  "stun": 12},
}

class fighter:
    def __init__(self, x, y, color,outline_color, width=1280, height=720, hp=100, char_w=120, char_h=180):
        # position
        self.x = x
        self.y = y

        # appearance
        self.color = color
        self.outline_color=outline_color
        self.char_w = char_w
        self.char_h = char_h
        self.standing_h=char_h
        self.ducking_h=int(char_h/1.5)

        # screen bounds
        self.width = width
        self.height = height

        # health
        self.hp = hp
        self.max_hp = hp

        # physics
        self.ground_y = height - 150
        self.is_jump = False
        self.vel_y = 0
        self.gravity = 1.5
        self.jump_vel = -30
        self.normal_vel = 10
        self.jump_duck_vel = 5

        # facing
        self.facing = "R"

        # attack state
        self.is_attacking = False
        self.attack_type = ''
        self.attack_frame = 0
        self.hit_landed = False
        self.got_hit = False
        self.hit_stun=0
        #parry
        self.is_parrying=False
        self.parry_frame = 0
        self.parry_duration = 12
        self.parry_recovery = 0
        self.parry_recovery_dur = 20 

    # --- facing ---
    def update_facing(self, opponent):
        self.facing = "R" if self.x < opponent.x else "L"

    # --- movement ---
    def move(self, action):
        # dont move if stunned
        if self.hit_stun:
            self.hit_stun-=1
            self.vel_y+=self.gravity
            self.y+=self.vel_y
            if self.y>=self.ground_y-self.char_h:
                self.y=self.ground_y-self.char_h
                self.vel_y=0
                self.is_jump=False
            return

        vel = self.jump_duck_vel if (action["duck"] or self.is_jump) else self.normal_vel
        if not self.is_parrying:
            if action["direction"] == "left" and self.x > 0:
                self.x -= vel
            if action["direction"] == "right" and self.x < self.width - self.char_w:
                self.x += vel
        # vertical movement & gravity
        if self.is_jump:
            # Only apply gravity if we are in the air
            self.vel_y += self.gravity
            self.y += self.vel_y

            # ground check (landing)
            if self.y >= self.ground_y - self.char_h:
                self.y = self.ground_y - self.char_h
                self.vel_y = 0
                self.is_jump = False
        else:
            self.char_h = self.ducking_h if action["duck"] else self.standing_h
            self.y = self.ground_y - self.char_h
            
            self.update_parry(action)   # always call — handles all parry state
            
            if action["parry"] and self.is_parrying:
                return   # stop movement only if actually parrying
            
            if action["jump"]:
                self.char_h = self.standing_h
                self.y = self.ground_y - self.char_h
                self.is_jump = True
                self.vel_y = self.jump_vel
                

    # --- attack resolver ---
    def resolve_attack(self, action):
        button = action["attack"]
        is_jumping = self.is_jump
        is_ducking = action["duck"]

        if self.facing == "R":
            is_forward = action["direction"] == "right"
            is_backward = action["direction"] == "left"
        else:
            is_forward = action["direction"] == "left"
            is_backward = action["direction"] == "right"

        if button == "light":
            if is_jumping:   return "hook"
            if is_ducking:   return "low_punch"
            if is_forward:   return "forward_punch"
            if is_backward:  return "back_punch"
            return "jab"

        if button == "heavy":
            if is_jumping:   return "uppercut"
            if is_ducking:   return "swing_kick"
            if is_forward:   return "double_punch"
            if is_backward:  return "back_kick"
            return "cross"

    # --- attack ---
    def attack(self, action):
        # no attack when stun
        if self.hit_stun>0 or self.is_parrying:
            return
        # trigger new attack only if not already attacking
        if action["attack"] is not None and not self.is_attacking:
            self.is_attacking = True
            self.attack_type = self.resolve_attack(action)
            self.attack_frame = 0
            self.hit_landed = False

        # progress current attack
        if self.is_attacking:
            self.attack_frame += 1
            if self.attack_type and self.attack_type in ATTACK_DATA:
                data = ATTACK_DATA[self.attack_type]
                total = data["startup"] + data["active"] + data["recovery"]
                if self.attack_frame >= total:
                    self.is_attacking = False
                    self.attack_type = ""
                    self.attack_frame = 0
                    self.hit_landed = False

    # --- knockback ---
    def apply_knockback(self,attacker_facing,dmg,knockup=False):
        kb=dmg*2
        if attacker_facing=='R':
            self.x+=kb
        else:
            self.x-=kb
        self.x=max(0,min(self.x,self.width-self.char_w))
        if knockup:
            self.is_jump=True
            self.vel_y-=20



    # --- hitbox ---
    def get_hitbox(self):
        if not self.is_attacking or not self.attack_type:
            return None
            
        if self.attack_type not in ATTACK_DATA:
            return None
    
        data = ATTACK_DATA[self.attack_type]
        in_active = data["startup"] <= self.attack_frame < data["startup"] + data["active"]

        if not in_active:
            return None

        hw = data["hw"]
        hh = data["hh"]

        if data.get("parry_type") == "high":
            hy = self.y    # upper body — ducking dodges this
        else:
            hy = self.y + self.char_h - data["hh"]  # low — hits duckers
        # horizontal position — depends on facing
        if self.facing == "R":
            hx = self.x + self.char_w
        else:
            hx = self.x - hw

        return pg.Rect(hx, hy, hw, hh)

    # --- parry ---
    def update_parry(self, action):
        # no parry during jump or stun
        if self.is_jump or self.hit_stun > 0 or self.is_attacking:
            self.is_parrying = False
            self.parry_frame = 0
            return
        
        # count down recovery
        if self.parry_recovery > 0:
            self.parry_recovery -= 1
            self.is_parrying = False
            return
        
        # trigger parry
        if action["parry"] and not self.is_parrying and self.parry_frame == 0:
            self.is_parrying = True
            self.parry_frame = 1
        
        # progress parry
        if self.is_parrying:
            self.parry_frame += 1
            if self.parry_frame > self.parry_duration:
                self.is_parrying = False
                self.parry_frame = 0
                self.parry_recovery = self.parry_recovery_dur  # ← start recovery

    def get_parry_rect(self):
        if not self.is_parrying:
            return None
        
        pw, ph = 40, 100
        py = self.y    # upper body
        
        # if ducking — lower body parry
        if self.char_h == self.ducking_h:
            ph = 60
            py = self.y + self.char_h - ph
        
        if self.facing == "R":
            px = self.x + self.char_w
        else:
            px = self.x - pw
        
        return pg.Rect(px, py, pw, ph)
    
    # --- health bar ---
    def get_health_bar(self):
        hp_percent = self.hp / self.max_hp
        bar_w, bar_h = 400, 50
        surface = pg.Surface((bar_w, bar_h), pg.SRCALPHA)
        pg.draw.rect(surface, (255, 0, 0, 128), (0, 0, bar_w, bar_h))
        pg.draw.rect(surface, (0, 255, 0, 255), (0, 0, int(bar_w * hp_percent), bar_h))
        return surface

    # --- draw ---
    def draw(self, win):
        pg.draw.rect(win, self.outline_color, (self.x-3, self.y-3, self.char_w+6, self.char_h+6), border_radius=4)
        pg.draw.rect(win, self.color, (self.x, self.y, self.char_w, self.char_h))

        # debug — draw hitbox in yellow
        hb = self.get_hitbox()
        if hb:
            pg.draw.rect(win, (255, 255, 0), hb, 2)