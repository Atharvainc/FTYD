import pygame as pg

ATTACK_DATA = {
    "jab":          {"startup": 3,  "active": 6,  "recovery": 3,  "damage": 4},
    "hook":         {"startup": 6,  "active": 6,  "recovery": 6,  "damage": 8},
    "low_punch":    {"startup": 6,  "active": 6,  "recovery": 6,  "damage": 4},
    "forward_punch":{"startup": 6,  "active": 6,  "recovery": 6,  "damage": 6},
    "back_punch":   {"startup": 6,  "active": 6,  "recovery": 6,  "damage": 6},
    "uppercut":     {"startup": 9,  "active": 9,  "recovery": 12, "damage": 12},
    "swing_kick":   {"startup": 6,  "active": 9,  "recovery": 12, "damage": 8},
    "double_punch": {"startup": 6,  "active": 12, "recovery": 9,  "damage": 10},
    "back_kick":    {"startup": 6,  "active": 6,  "recovery": 9,  "damage": 10},
    "cross":        {"startup": 6,  "active": 6,  "recovery": 9,  "damage": 8},
}

class fighter:
    def __init__(self, x, y, color, width=1280, height=720, hp=100, char_w=70, char_h=100):
        # position
        self.x = x
        self.y = y

        # appearance
        self.color = color
        self.char_w = char_w
        self.char_h = char_h

        # screen bounds
        self.width = width
        self.height = height

        # health
        self.hp = hp
        self.max_hp = hp

        # physics
        self.ground_y = height - 20
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

    # --- facing ---
    def update_facing(self, opponent):
        self.facing = "R" if self.x < opponent.x else "L"

    # --- movement ---
    def move(self, action):
        vel = self.jump_duck_vel if (action["duck"] or self.is_jump) else self.normal_vel

        if action["direction"] == "left" and self.x > 0:
            self.x -= vel
        if action["direction"] == "right" and self.x < self.width - self.char_w:
            self.x += vel

        # gravity — every frame
        self.vel_y += self.gravity
        self.y += self.vel_y

        # ground check
        if self.y >= self.ground_y - self.char_h:
            self.y = self.ground_y - self.char_h
            self.vel_y = 0
            self.is_jump = False

        # duck and jump — only on ground
        if not self.is_jump:
            self.char_h = 70 if action["duck"] else 100
            self.y = self.ground_y - self.char_h

            if action["jump"]:
                self.is_jump = True
                self.vel_y = self.jump_vel
                self.char_h = 100
                self.y = self.ground_y - self.char_h

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

        hw, hh = 80, 60

        # vertical position — lower for ducking attacks
        hy = self.y + 30 if self.attack_type in ("low_punch", "swing_kick") else self.y

        # horizontal position — depends on facing
        if self.facing == "R":
            hx = self.x + self.char_w
        else:
            hx = self.x - hw

        return pg.Rect(hx, hy, hw, hh)

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
        pg.draw.rect(win, self.color, (self.x, self.y, self.char_w, self.char_h))

        # debug — draw hitbox in yellow
        hb = self.get_hitbox()
        if hb:
            pg.draw.rect(win, (255, 255, 0), hb, 2)