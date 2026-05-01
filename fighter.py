import pygame as pg

ATTACK_DATA = {
    "jab":          {"startup": 3,  "active": 6,  "recovery": 3,  "damage": 4},
    "hook":         {"startup": 6,  "active": 6,  "recovery": 6,  "damage": 8},
    "lowpunch":     {"startup": 6,  "active": 6,  "recovery": 6,  "damage": 4},
    "forwardpunch": {"startup": 6,  "active": 6,  "recovery": 6,  "damage": 6},
    "backpunch":    {"startup": 6,  "active": 6,  "recovery": 6,  "damage": 6},
    "uppercut":     {"startup": 9,  "active": 9,  "recovery": 12, "damage": 12},
    "swingkick":    {"startup": 6,  "active": 9,  "recovery": 12, "damage": 8},
    "doublepunch":  {"startup": 6,  "active": 12,  "recovery": 9, "damage": 10},
    "backkick":     {"startup": 6,  "active": 6,  "recovery": 9,  "damage": 10},
    "cross":        {"startup": 6,  "active": 6,  "recovery": 9, "damage": 8},
}

class fighter:
    def __init__(self, x, y,color,width=1280,height=720, hp=100, charw=70, charh=100):
        self.x = x
        self.y = y
        self.color=color
        self.hp = hp
        self.charw = charw
        self.charh = charh
        self.width=width
        self.height=height
        # always the same — hardcoded
        
        # attack 
        self.isattacking=False
        self.attacktype=None
        self.attackframe=None
        self.gothit=False
        #
        self.max_hp=hp
        self.groundy = height-20
        self.isjump = False
        self.vel_y = 0 
        self.gravity = 1.5
        self.jump_vel = -30
        self.normal_vel = 10
        self.jump_duck_vel = 5
        self.facing='R'
    def update_facing(self,oppo):
        self.facing='R' if self.x<oppo.x else 'L'
    #-movement fn-
    def move(self,action):
        vel = self.jump_duck_vel if (action["duck"] == True or self.isjump == True) else self.normal_vel
        if action["direction"] == "left" and self.x > 0:
            self.x -= vel
        if action["direction"] == "right" and self.x < self.width - self.charw:
            self.x += vel    
        # gravity applies every frame, always
        self.vel_y += self.gravity
        self.y += self.vel_y
        #ground check
        if self.y >= self.groundy - self.charh:
            self.y = self.groundy - self.charh   # snap to ground
            self.vel_y = 0                        # stop falling
            self.isjump = False                   # on ground now

        # ducking — only when on ground
        if not self.isjump:
            self.charh = 70 if action["duck"] == True else 100
            self.y = self.groundy - self.charh

            # jump trigger
            if action["jump"] == True:
                self.isjump = True
                self.vel_y = self.jump_vel        # launch upward
                self.charh = 100
                self.y = self.groundy - self.charh

    #-draw_health_bar-
    def get_health_bar(self):
        hpercent=self.hp/self.max_hp
        barw,barh=400,50 
        surface = pg.Surface((barw, barh), pg.SRCALPHA)
        pg.draw.rect(surface, (255,0,0,128), (0, 0, barw+20, barh+20))
        pg.draw.rect(surface, (0,255,0,255), (0, 0, int(barw * hpercent), barh))
        return surface

    #-attack_function-
    def resolve_attack(self, action):
        button = action["attack"]
        is_jumping = self.isjump
        is_ducking = action['duck']
        
        # resolve forward/backward relative to facing
        if self.facing == "R":
            is_forward = action["direction"] == "right"
            is_backward = action["direction"] == "left"
        else:
            is_forward = action["direction"] == "left"
            is_backward = action["direction"] == "right"
        
        if button == "light":
            if is_jumping:
                return 'hook'
            elif is_ducking:
                return 'lowpunch'
            elif is_forward:
                return 'forwardpunch'
            elif is_backward:
                return 'backpunch'
            else:
                return "jab"    # neutral
        
        elif button == "heavy":
            if is_jumping:
                return 'uppercut'
            elif is_ducking:
                return 'swingkkick'
            elif is_forward:
                return 'doublepunch'
            elif is_backward:
                return 'backkick'
            else:
                return 'cross'
            
    #-attack fn-
    def attack(self, action):
        if action["attack"] is not None and not self.attacking:
            self.attacking = True
            self.attack_type = self.resolve_attack(action)
            self.attack_frame = 0
        
        if self.attacking:
            self.attack_frame += 1
            data = ATTACK_DATA[self.attack_type]
            total = data["startup"] + data["active"] + data["recovery"]
            if self.attack_frame >= total:
                self.attacking = False
                self.attack_type = None
                self.attack_frame = 0
                self.hit_landed = False

    #-draw window fn-
    def draw(self,win):
        pg.draw.rect(win,self.color,(self.x,self.y,self.charw,self.charh))
      