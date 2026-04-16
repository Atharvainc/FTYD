import pygame as pg

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


    #-draw window fn-
    def draw(self,win):
        pg.draw.rect(win,self.color,(self.x,self.y,self.charw,self.charh))
      