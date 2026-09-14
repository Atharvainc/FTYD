import pygame as pg
from abc import ABC,abstractmethod
from typing import Any
#abstract class
class inputhandler(ABC):
    @abstractmethod
    def get_action(self,keys)->dict[str,Any]:
        ...

#player1
class  keyinput1(inputhandler):
    def __init__(self):
        self.prev_keys=None 
    def get_action(self,keys):
        if self.prev_keys is None:
            self.prev_keys=keys
        # edge detection — only True on first frame pressed
        def clicked(key):
            return keys[key] and not self.prev_keys[key]
        action = {
            "direction": "right"  if keys[pg.K_d] else
                         "left"   if keys[pg.K_a] else
                         "neutral",
            'jump':clicked(pg.K_w),
            'duck':keys[pg.K_s],
            "attack": "light" if clicked(pg.K_k) else
                      "heavy" if clicked(pg.K_o) else
                      None,
            "parry": clicked(pg.K_l),
            }
        self.prev_keys = keys
        return action

#player2
class  keyinput2(inputhandler):
    def __init__(self):
        self.prev_keys=None 
    def get_action(self,keys):
        if self.prev_keys is None:
            self.prev_keys=keys
        # edge detection — only True on first frame pressed
        def clicked(key):
            return keys[key] and not self.prev_keys[key]
        action = {
            "direction": "right"  if keys[pg.K_RIGHT] else
                         "left"   if keys[pg.K_LEFT] else
                         "neutral",
            'jump':clicked(pg.K_UP),
            'duck':keys[pg.K_DOWN],
            "attack": "light" if clicked(pg.K_KP2) else
                      "heavy" if clicked(pg.K_KP5) else
            None,
            "parry": clicked(pg.K_KP6) 
            }
        self.prev_keys = keys
        return action

#bot
class botinput(inputhandler):
    def get_action(self,keys):
        action={}
        return action