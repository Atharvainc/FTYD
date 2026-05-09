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
    def get_action(self,keys):
        action = {
            "direction": "right"  if keys[pg.K_d] else
                "left"   if keys[pg.K_a] else
                "neutral",
            'jump':True if keys[pg.K_w] else False,
            'duck':True if keys[pg.K_s] else False,
            "attack": "light" if keys[pg.K_k] else
            "heavy" if keys[pg.K_o] else
            None,
            "parry": True if keys[pg.K_l] else False
            }
        return action

#player2
class  keyinput2(inputhandler):
    def get_action(self,keys):
        action = {
            "direction": "right"  if keys[pg.K_RIGHT] else
                "left"   if keys[pg.K_LEFT] else
                "neutral",
            'jump':True if keys[pg.K_UP] else False,
            'duck':True if keys[pg.K_DOWN] else False,
            "attack": "light" if keys[pg.K_KP2] else
            "heavy" if keys[pg.K_KP5] else
            None,
            "parry": True if keys[pg.K_KP6] else False
            }
        return action

#bot
class botinput(inputhandler):
    def get_action(self,keys):
        action={}
        return action