import pygame as pg
import os
from fighter import fighter,ATTACK_DATA
from inputhandler import keyinput1,keyinput2
pg.init()

#---buttons---
class button:
    def __init__(self,x,y,w,h,text):
        self.rect=pg.Rect(x,y,w,h)
        self.text=text
        self.selected=False
    def is_clicked(self,event):
        if event.type==pg.MOUSEBUTTONDOWN:
            return self.rect.collidepoint(event.pos)
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
        #global vars
        self.width=1280
        self.height=720
        pg.display.set_caption('FTYD')
        icon = pg.image.load('assets/icon.png')
        pg.display.set_icon(icon)
        self.red = (255,0,0)
        self.blue = (0,0,255)
        self.green = (0,255,0)
        self.black = (0,0,0)
        self.white = (255,255,255)
        self.clock = pg.time.Clock()
        self.FPS=60
        self.win=pg.display.set_mode((self.width,self.height))
        self.font = pg.font.SysFont("arial", 36)
        #states
        self.state='menu'
        self.gamemode=None # local, bot
        self.fight_type=None #3round,endless 
        self.endlessmode=None # local,bot
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
        localb= button(self.width//2 - 100, self.height//2 - 60, 200, 80, "Local Multiplayer")
        botb= button(self.width//2 - 100, self.height//2 + 60, 200, 80, "Bot Mode")
        selected = 0

        while self.state == "menu":
            self.clock.tick(self.FPS)
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit(); return
                if event.type == pg.KEYDOWN:
                    if event.key in (pg.K_UP, pg.K_DOWN):
                        selected = 1 - selected
                    if event.key == pg.K_RETURN:
                        self.game_mode = "local" if selected == 0 else "bot"
                        self.state = "fight_type_select"
                if event.type == pg.MOUSEBUTTONDOWN:
                    if localb.is_clicked(event):
                        self.game_mode = "local"
                        self.state = "fight_type_select"
                    if botb.is_clicked(event):
                        self.game_mode = "bot"
                        self.state = "fight_type_select"
            
            localb.selected = (selected == 0)
            botb.selected = (selected == 1)
            self.win.fill(self.black)
            localb.draw(self.win, self.font)
            botb.draw(self.win, self.font)
            pg.display.update()

    def run_fight_type_select(self):
        duelb=button(x=self.width//2-100,y=self.height//2-110,w=200,h=100,text='duel')
        endlessb=button(x=self.width//2-100,y=self.height//2+110,w=200,h=100,text='endless(FTYD)') 
        selected=0 
        while self.state == "fight_type_select":
            self.clock.tick(self.FPS)
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit(); return
                if event.type == pg.KEYDOWN:
                    if event.key in (pg.K_UP, pg.K_DOWN):
                        selected = 1 - selected
                    if event.key == pg.K_RETURN:
                        self.fight_type = "duel" if selected == 0 else "ftyd"
                        self.endless_mode = 'bot' if self.game_mode == 'bot' else 'local' 
                        self.state = "char_select"
                if event.type == pg.MOUSEBUTTONDOWN:
                    if duelb.is_clicked(event):
                        self.fight_type = "duel"
                        self.state = "char_select"
                    if endlessb.is_clicked(event):
                        self.fight_type = "ftyd"
                        self.endlessmode='bot' if self.game_mode=='bot' else 'local'
                        self.state = "char_select"
            
            duelb.selected=(selected==0)
            endlessb.selected=(selected==1)
            self.win.fill((self.black)) 
            duelb.draw(self.win,self.font)
            endlessb.draw(self.win,self.font)
            pg.display.update()

    def run_char_select(self):
        localb=button(x=self.width//2-100,y=self.height//2-110,w=200,h=100,text='local multiplayer')
        botb=button(x=self.width//2-100,y=self.height//2+110,w=200,h=100,text='bot_mode') 
        while self.state == "char_select":
            self.clock.tick(self.FPS)
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    return
                
            self.win.fill((self.black))

            pg.display.update()


                    
    def run_fight(self):
        while self.state == "fight":
            self.clock.tick(self.FPS)
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    return
    def run_round_over(self):
        while self.state == "round_over":
            self.clock.tick(self.FPS)
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    return
    def run_endless_over(self):
        while self.state == "endless_over":
            self.clock.tick(self.FPS)
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    return
            
        #---functions---
    def check_hit(self,attacker:fighter,defender:fighter):
        hitbox=attacker.get_hitbox()
        if hitbox is None:
            return
        defender_rect=pg.Rect(defender.x,defender.y,defender.char_w,defender.char_h)
        if hitbox.colliderect(defender_rect) and not attacker.hit_landed:
            dmg=ATTACK_DATA[attacker.attack_type]['damage']#type:ignore
            defender.hp-=dmg
            defender.hp=max(0,defender.hp)
            attacker.hit_landed=True

    def check_round_over(self,p1,p2):
        if p1.hp<=0:
            return p2
        if p2.hp<=0:
            return p1
        return None
    
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

if __name__=='__main__':
    g=game()
    g.run()
    pg.quit()