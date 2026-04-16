import pygame as pg
from fighter import fighter
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

#-player action getter-

#---objects---
p1=fighter(50,600,blue,width,height)
p2=fighter(1160,600,red,width,height)
p1input=keyinput1()
p2input=keyinput2()

while run:
    clock.tick(FPS)
    for event in pg.event.get():
        if event.type==pg.QUIT:
            run=False
    keys=pg.key.get_pressed()   
    p1.move(p1input.get_action(keys))
    p2.move(p2input.get_action(keys))
    p1.update_facing(p2)
    p2.update_facing(p1)
    win.fill((black)) 
    p1.draw(win)
    p2.draw(win)
    win.blit(p1.get_health_bar(), (50, 100))
    win.blit(pg.transform.flip(p2.get_health_bar(), True, False), (width - 450, 100))
    pg.display.update()  

pg.quit()
