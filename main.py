import pygame as pg
import sys
import math
import os
from fighter import fighter,ATTACK_DATA
from inputhandler import keyinput1,keyinput2,botinput
pg.init()

#--global vars---
CHARACTER_DATA={0:{'name':'Ragnarock','color':(0,0,255),'hp':100},
                1:{'name':'Rosa','color':(255,0,0),'hp':100}}


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
        if self.selected:
            color = (150, 150, 255)    # keyboard selected — bright
        elif self.is_hovered(pg.mouse.get_pos()):
            color = (100, 100, 255)    # mouse hover — medium
        else:
            color = (50, 50, 150)      # default — dark
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
        self.game_mode=None # local, bot
        self.fight_type=None #3round,endless 
        self.endless_mode=None # local,bot
        # character selections
        self.p1_char = None
        self.p2_char = None
        #fighters
        self.p1=None
        self.p2=None
        self.p1_input=None
        self.p2_input=None
        self.round_time=60*self.FPS
        #score
        self.p1_rounds=0
        self.p2_rounds=0
        self.hi_score=self.load_hs()
        self.score=0
        self.last_round_winner=None

    def run(self):
        states={
            "menu":self.run_menu,
            "char_select":self.run_char_select,
            "fight_type_select":self.run_fight_type_select,
            "fight":self.run_fight,
            "round_over":self.run_round_over,
            'duel_over':self.run_duel_over,
            "endless_over":self.run_endless_over,
            "pause":self.run_pause,
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
                    self.quit_game()
                if event.type == pg.KEYDOWN:
                    if event.key in (pg.K_UP, pg.K_DOWN):
                        selected = 1 - selected
                    if event.key == pg.K_RETURN:
                        self.game_mode = "local" if selected == 0 else "bot"
                        self.p1_rounds = 0      
                        self.p2_rounds = 0
                        self.state = "fight_type_select"
                if event.type == pg.MOUSEBUTTONDOWN:
                    if localb.is_clicked(event):
                        self.game_mode = "local"
                        self.p1_rounds = 0      
                        self.p2_rounds = 0
                        self.state = "fight_type_select"
                    if botb.is_clicked(event):
                        self.game_mode = "bot"
                        self.p1_rounds = 0      
                        self.p2_rounds = 0
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
                    self.quit_game()
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
                        self.endless_mode='bot' if self.game_mode=='bot' else 'local'
                        self.state = "char_select"
            
            duelb.selected=(selected==0)
            endlessb.selected=(selected==1)
            self.win.fill((self.black)) 
            duelb.draw(self.win,self.font)
            endlessb.draw(self.win,self.font)
            pg.display.update()

    def run_char_select(self):
        p1_choice=self.select_character(title='P1 - Choose Your FIGHTER')
        if p1_choice is None: return
        self.p1_char=p1_choice
        if self.game_mode=='local':
            p2_choice=self.select_character('P2 - Choose Your FIGHTER')
            if p2_choice is None: return 
            self.p2_char=p2_choice
        else:
            self.p2_char=1-self.p1_char
        self.state='fight'

                    
    def run_fight(self):
        if self.p1 is None:
            p1_data=CHARACTER_DATA[self.p1_char]#type:ignore
            p2_data=CHARACTER_DATA[self.p2_char]#type:ignore
            self.p1=fighter(200,500,p1_data['color'],(255,50,50),self.width,self.height,hp=p1_data['hp'])
            self.p2=fighter(900,500,p2_data['color'],(50,50,255),self.width,self.height,hp=p2_data['hp'])
            self.p1_input=keyinput1()
            self.p2_input=keyinput2() if self.game_mode=='local' else botinput()
            self.round_time=60*self.FPS
            
        while self.state == "fight":
            self.clock.tick(self.FPS)
            self.round_time -= 1
            if self.round_time <= 0:
                if self.p1.hp > self.p2.hp:
                    self.last_round_winner = "p1"
                elif self.p2.hp > self.p1.hp:
                    self.last_round_winner = "p2"
                else:
                    self.last_round_winner = "p1" 
                self.state = "round_over"
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.quit_game()
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_ESCAPE:
                        self.state = "pause"
            keys=pg.key.get_pressed()
            p1_action=self.p1_input.get_action(keys)
            p2_action=self.p2_input.get_action(keys)

            self.p1.move(p1_action)
            self.p2.move(p2_action)
            self.p1.attack(p1_action)
            self.p2.attack(p2_action)
            self.check_hit(self.p1,self.p2)
            self.check_hit(self.p2,self.p1)
            self.p1.update_facing(self.p2)
            self.p2.update_facing(self.p1)
            winner=self.check_round_over()
            if winner:
                self.last_round_winner=winner
                self.state="round_over"
            self.win.fill(self.black)
            pg.draw.line(self.win, (100, 100, 100), (0, self.p1.ground_y), (self.width, self.p1.ground_y), 2)
            self.p1.draw(self.win)
            self.p2.draw(self.win)
            p1_name = CHARACTER_DATA[self.p1_char]["name"]  # type:ignore
            p2_name = CHARACTER_DATA[self.p2_char]["name"]  # type:ignore
            p1_surf = self.font.render(p1_name, True, self.white)
            p2_surf = self.font.render(p2_name, True, self.white)
            self.win.blit(p1_surf, (50, 110))
            self.win.blit(p2_surf, (self.width - 50 - p2_surf.get_width(), 110))
            if self.fight_type == "duel":
                for i in range(2):
                    color = self.white if i < self.p1_rounds else self.black
                    pg.draw.circle(self.win, color, (50 + i*35, 40), 12)
                    pg.draw.circle(self.win, self.white, (50 + i*35, 40), 12, 2)
                    color = self.white if i < self.p2_rounds else self.black
                    pg.draw.circle(self.win, color, (self.width - 50 - i*35, 40), 12)
                    pg.draw.circle(self.win, self.white, (self.width - 50 - i*35, 40), 12, 2)

            elif self.fight_type == "ftyd":
                score_surf = self.font.render(f"Round: {self.p1_rounds + self.p2_rounds + 1}", True, self.white)
                self.win.blit(score_surf, (self.width//2 - score_surf.get_width()//2, 55))
            self.win.blit(self.p1.get_health_bar(),(50,50))
            self.win.blit(pg.transform.flip(self.p2.get_health_bar(), True, False), (self.width - 450, 50))
            pr = self.p1.get_parry_rect()
            if pr:
                pg.draw.rect(self.win, (0, 255, 255), pr, 2)
            pr = self.p2.get_parry_rect()
            if pr:
                pg.draw.rect(self.win, (0, 255, 255), pr, 2)
            seconds_left = self.round_time // self.FPS
            timer_surf = self.font.render(str(seconds_left), True, self.white)
            self.win.blit(timer_surf, (self.width//2 - timer_surf.get_width()//2, 20))
            pg.display.update()

                    
    def run_round_over(self):
        # update scores
        if self.last_round_winner == "p1":
            self.p1_rounds += 1
        else:
            self.p2_rounds += 1

        # determine next state
        if self.fight_type == "duel":
            if self.p1_rounds >= 2 or self.p2_rounds >= 2:
                next_state = "duel_over"
            else:
                self.p1 = None  
                self.p2 = None
                next_state = "fight"

        elif self.fight_type == "ftyd" and self.game_mode == "local":
            self.p1 = None  
            self.p2 = None
            next_state = "fight"

        elif self.fight_type == "ftyd" and self.game_mode == "bot":
            if self.last_round_winner == "p2":  # p1 died
                next_state = "endless_over"
            else:
                # p1 won round — regen 20%
                regen_amt = int(self.p1.max_hp * 0.2)  # type:ignore
                self.p1.hp = min(self.p1.max_hp, self.p1.hp + regen_amt)  # type:ignore
                # update highscore
                if self.p1_rounds > self.hi_score:
                    self.hi_score = self.p1_rounds
                    self.save_hs()
                next_state = "fight"
        else:
            self.p1 = None  
            self.p2 = None
            next_state = "fight"

        winner_name = CHARACTER_DATA[self.p1_char if self.last_round_winner == "p1" else self.p2_char]["name"]  # type:ignore
        msg = f"{winner_name} wins the round!"
        delay = int(self.FPS * 2.5)
        frame = 0

        while self.state == "round_over":
            self.clock.tick(self.FPS)
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.quit_game()
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_ESCAPE:
                        self.quit_game()

            frame += 1
            if frame >= delay:
                if next_state in ("menu", "endless_over", "duel_over"):
                    self.p1_rounds = 0
                    self.p2_rounds = 0
                self.state = next_state

            self.win.fill(self.black)
            msg_surf = self.font.render(msg, True, self.white)
            self.win.blit(msg_surf, (
                self.width//2 - msg_surf.get_width()//2,
                self.height//3
            ))
            score_txt = f"P1: {self.p1_rounds}  —  P2: {self.p2_rounds}"
            score_surf = self.font.render(score_txt, True, self.white)
            self.win.blit(score_surf, (
                self.width//2 - score_surf.get_width()//2,
                self.height//3 + 60
            ))
            pg.display.update()

    def run_duel_over(self):
        # who won the match
        match_winner = "p1" if self.p1_rounds >= 2 else "p2"
        winner_name = CHARACTER_DATA[
            self.p1_char if match_winner == "p1" else self.p2_char
        ]["name"]  # type:ignore

        msg1 = f"{winner_name} wins the match!"
        msg2 = "VICTORY"
        delay = int(self.FPS * 4)   # 4 seconds
        frame = 0

        # pulse effect for VICTORY text
        pulse = 0

        while self.state == "duel_over":
            self.clock.tick(self.FPS)
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.quit_game()

            frame += 1
            pulse = (pulse + 3) % 360

            if frame >= delay:
                self.state = "menu"

            # pulsing colour for VICTORY
            import math
            pulse_val = int((math.sin(math.radians(pulse)) + 1) * 127)
            victory_color = (255, pulse_val, 0)   # gold pulse

            # scale VICTORY text
            big_font = pg.font.SysFont("arial", 80, bold=True)
            small_font = pg.font.SysFont("arial", 36)

            self.win.fill(self.black)

            # VICTORY
            v_surf = big_font.render(msg2, True, victory_color)
            self.win.blit(v_surf, (
                self.width//2 - v_surf.get_width()//2,
                self.height//3 - 60
            ))

            # winner name
            msg_surf = small_font.render(msg1, True, self.white)
            self.win.blit(msg_surf, (
                self.width//2 - msg_surf.get_width()//2,
                self.height//3 + 60
            ))

            # progress bar — time remaining
            bar_w = int((1 - frame/delay) * 400)
            pg.draw.rect(self.win, (100, 100, 100), (self.width//2 - 200, self.height - 80, 400, 10))
            pg.draw.rect(self.win, victory_color, (self.width//2 - 200, self.height - 80, bar_w, 10))

            pg.display.update()

    def run_endless_over(self):
        msg1 = f"You survived {self.hi_score} rounds!"
        msg2 = "GAME OVER"
        delay = int(self.FPS * 4)
        frame = 0

        while self.state == "endless_over":
            self.clock.tick(self.FPS)
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.quit_game()

            frame += 1
            if frame >= delay:
                self.state = "menu"

            big_font = pg.font.SysFont("arial", 80, bold=True)
            small_font = pg.font.SysFont("arial", 36)

            self.win.fill(self.black)

            go_surf = big_font.render(msg2, True, self.red)
            self.win.blit(go_surf, (
                self.width//2 - go_surf.get_width()//2,
                self.height//3 - 60
            ))

            score_surf = small_font.render(msg1, True, self.white)
            self.win.blit(score_surf, (
                self.width//2 - score_surf.get_width()//2,
                self.height//3 + 60
            ))

            hs_surf = small_font.render(f"High Score: {self.hi_score}", True, (255, 215, 0))
            self.win.blit(hs_surf, (
                self.width//2 - hs_surf.get_width()//2,
                self.height//3 + 120
            ))

            pg.display.update()

    def run_pause(self):
        overlay = pg.Surface((self.width, self.height), pg.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        
        resume_btn = button(self.width//2 - 100, self.height//2 - 100, 200, 70, "Resume")
        menu_btn   = button(self.width//2 - 100, self.height//2, 200, 70, "Main Menu")
        quit_btn   = button(self.width//2 - 100, self.height//2 + 100, 200, 70, "Quit")
        selected = 0

        while self.state == "pause":
            self.clock.tick(self.FPS)
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.quit_game()
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_ESCAPE:
                        self.state = "fight"   # ESC again resumes
                    if event.key in (pg.K_UP, pg.K_DOWN):
                        selected = (selected + 1) % 3   # cycle through 3 buttons
                    if event.key == pg.K_RETURN:
                        if selected == 0: self.state='fight'
                        if selected == 1: 
                            self.p1 = None
                            self.p2 = None
                            self.p1_rounds = 0
                            self.p2_rounds = 0
                            self.state = "menu"
                            return
                        if selected == 2: self.quit_game()
                if event.type == pg.MOUSEBUTTONDOWN:
                    if resume_btn.is_clicked(event):
                        self.state = "fight"
                    if menu_btn.is_clicked(event):
                        self.p1 = None
                        self.p2 = None
                        self.p1_rounds = 0
                        self.p2_rounds = 0
                        self.state = "menu"
                        return 
                    if quit_btn.is_clicked(event):
                        self.quit_game()
            
            resume_btn.selected = (selected == 0)
            menu_btn.selected   = (selected == 1)
            quit_btn.selected   = (selected == 2)
            
            # draw frozen game state underneath
            self.p1.draw(self.win) #type:ignore
            self.p2.draw(self.win) #type:ignore
            
            # overlay on top
            self.win.blit(overlay, (0, 0))
            
            # draw buttons
            resume_btn.draw(self.win, self.font)
            menu_btn.draw(self.win, self.font)
            quit_btn.draw(self.win, self.font)
            
            pg.display.update()

        #---helper functions---
    def check_hit(self, attacker, defender):
        hitbox = attacker.get_hitbox()
        if hitbox is None:
            return
        
        defender_rect = pg.Rect(defender.x, defender.y, defender.char_w, defender.char_h)
        
        if hitbox.colliderect(defender_rect) and not attacker.hit_landed:
            data = ATTACK_DATA[attacker.attack_type]  # type:ignore
            
            # check parry first
            parry_rect = defender.get_parry_rect()
            if parry_rect and hitbox.colliderect(parry_rect):
                # check parry type vs attack type
                if data.get("parry_type") == "high" and defender.char_h == defender.standing_h:
                    # successful high parry
                    attacker.hit_stun = 20
                    attacker.hit_landed = True
                    defender.is_parrying = False
                    defender.parry_frame=0
                    defender.parry_recovery=10
                    return
                elif data.get("parry_type") == "low" and defender.char_h == defender.ducking_h:
                    # successful low parry
                    attacker.hit_stun = 20
                    attacker.hit_landed = True
                    defender.is_parrying = False
                    defender.parry_frame=0
                    defender.parry_recovery=10
                    return
            
            # normal hit
            defender.hp -= data["damage"]
            defender.hp = max(0, defender.hp)
            defender.hit_stun = data["stun"]
            defender.got_hit = True
            attacker.hit_landed = True
            defender.apply_knockback(attacker.facing, data["damage"], data.get("knockup", False))

#for run_char_select
    def select_character(self, title, characters=CHARACTER_DATA):
        names = [characters[i]["name"] for i in characters]
        btn1 = button(self.width//2 - 220, self.height//2, 200, 80, names[0])
        btn2 = button(self.width//2 + 20,  self.height//2, 200, 80, names[1])
        selected = 0
        
        while True:
            self.clock.tick(self.FPS)
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.quit_game()
                    return None
                if event.type == pg.KEYDOWN:
                    if event.key in (pg.K_LEFT, pg.K_RIGHT):
                        selected = 1 - selected
                    if event.key == pg.K_RETURN:
                        return selected    # ← returns chosen index
                if event.type == pg.MOUSEBUTTONDOWN:
                    if btn1.is_clicked(event): return 0
                    if btn2.is_clicked(event): return 1
            
            btn1.selected = (selected == 0)
            btn2.selected = (selected == 1)
            
            self.win.fill(self.black)
            # draw title
            title_surf = self.font.render(title, True, self.white)
            self.win.blit(title_surf, (self.width//2 - title_surf.get_width()//2, self.height//3))
            btn1.draw(self.win, self.font)
            btn2.draw(self.win, self.font)
            pg.display.update()

    def check_round_over(self):
        if self.p1.hp<=0: #type:ignore
            return 'p2'
        if self.p2.hp<=0: #type:ignore
            return 'p1'
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
            f.write(str(self.hi_score))

    #closing the game
    def quit_game(self):
        pg.quit()
        sys.exit(0)

if __name__=='__main__':
    g=game()
    g.run()