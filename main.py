import pygame as pg
import os
from fighter import fighter,ATTACK_DATA
from inputhandler import keyinput1,keyinput2
pg.init()

#---important variables ---
width=1280
height=720
FPS=60

#-window-
win=pg.display.set_mode((width,height))
pg.display.set_caption('FTYD')
icon=pg.image.load('assets/icon.png')
pg.display.set_icon(icon)

#-colours-
red=(255,0,0)
blue=(0,0,255)
green=(0,255,0)
black=(0,0,0)
white=(255,255,255)

#-clock-
clock=pg.time.Clock()
run=True

#---functions---
def check_hit(attacker:fighter,defender:fighter):
    hitbox=attacker.get_hitbox()
    if hitbox is None:
        return
    defender_rect=pg.Rect(defender.x,defender.y,defender.char_w,defender.char_h)
    if hitbox.colliderect(defender_rect) and not attacker.hit_landed:
        dmg=ATTACK_DATA[attacker.attack_type]['damage']#type:ignore
        defender.hp-=dmg
        defender.hp=max(0,defender.hp)
        attacker.hit_landed=True

def check_round_over(p1,p2):
    if p1.hp<=0:
        return p2
    if p2.hp<=0:
        return p1
    return None
#---objects---
p1=fighter(200,500,blue,width,height)
p2=fighter(1080,500,red,width,height)
p1input=keyinput1()
p2input=keyinput2()

#---mainloop---
while run:
    clock.tick(FPS)
    for event in pg.event.get():
        if event.type==pg.QUIT:
            run=False
    keys=pg.key.get_pressed()   
    
    p1_ac=p1input.get_action(keys)
    p2_ac=p2input.get_action(keys)
    p1.move(p1_ac)
    p2.move(p2_ac)
    p1.attack(p1_ac)
    p2.attack(p2_ac)
    check_hit(p1,p2)
    check_hit(p2,p1)
    weiner=check_round_over(p1,p2)
    if weiner:
        print(f'{weiner} wins!')
    p1.update_facing(p2)
    p2.update_facing(p1)
    win.fill((black)) 
    p1.draw(win)
    p2.draw(win)
    win.blit(p1.get_health_bar(), (50, 100))
    win.blit(pg.transform.flip(p2.get_health_bar(), True, False), (width - 450, 100))
    pg.display.update()  

pg.quit()

#---buttons---
class button:
    def __init__(self,x,y,w,h,text):
        self.rect=pg.Rect(x,y,w,h)
        self.text=text
        self.selected=False
    def is_clicked(self,event):
        if event.type==pg.MOUSEBUTTONDOWN:
            return self.rect.colliderect(event.pos)
        return None
    def is_hovered(self,mouse_pos):
        return self.rect.collidepoint(mouse_pos)
    def draw(self,win,font):
        color=(100,100,255) if (self.selected or self.is_hovered(pg.mouse.get_pos())) else (50,50,150)
        pg.draw.rect(win,color,self.rect,border_radius=10)
        text_surf=font.render(self.text,True,(255,255,255))
        text_rect=text_surf.get_rect(center=self.rect.center)
        win.blit(text_surf,text_rect)
                                                                          
#---main class---
class game:
    def __init__(self):
        self.win=pg.display.set_mode((width,height))
        self.clock=pg.time.Clock()

        #states
        self.state='menu'
        self.gamemode=None # local, bot
        self.fight_type=None #3round,endless 
        #fighters
        self.p1=None
        self.p2=None
        self.p1input=None
        self.p2input=None
        #score
        self.p1rounds=0
        self.p2rounds=0
        self.hiscore=self.load_hs()
        self.score=0
    
    def load_hs(self):
        try:
            with open('data/hs.txt','r') as f:
                return int(f.read())
        except:
            return 0
    
    def save_hs(self):
        os.makedirs('data',exist_ok=True)
        with open('data/hs.txt','w') as f:
            f.write(str(self.hiscore))

    def run(self):
        states={
            "menu":self.run_menu,
            "char_select":self.run_char_select,
            "fight_type_select":self.run_fight_type_select,
            "fight":self.run_fight,
            "round_over":self.run_round_over,
            "endless_over":self.run_endless_over,
        }
        while True:
            states[self.state]()

    def run_menu(self):                
        while self.state == "menu":
            self.clock.tick(FPS)
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    return
            key=pg.key.get_pressed()
            button=B
                    
    def run_char_select(self):
        while self.state == "char_select":
            self.clock.tick(FPS)
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    return

    def run_fight_type_select(self):
        while self.state == "fight_type_select":
            self.clock.tick(FPS)
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    return
                    
    def run_fight(self):
        while self.state == "fight":
            self.clock.tick(FPS)
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    return
    def run_round_over(self):
        while self.state == "round_over":
            self.clock.tick(FPS)
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    return
    def run_endless_over(self):
        while self.state == "endless_over":
            self.clock.tick(FPS)
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    return