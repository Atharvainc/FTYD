from fighter import ATTACK_DATA
from fighter import fighter
import os
import numpy as np
from typing import Any
from asyncio import coroutines
import torch as tc
import torch.nn as nn
import torch.nn.functional as F
from inputhandler import botinput

# LAYER 1 :DQN
class DQN(nn.Module):
    def __init__(self, input_size: int = 179, hidden_size: int = 256, output_size: int = 8):
        super().__init__()
        self.fc1 = nn.Linear(input_size, hidden_size)
        self.fc2 = nn.Linear(hidden_size, hidden_size)
        self.fc3 = nn.Linear(hidden_size, output_size)

    def forward(self, x: tc.Tensor) -> tc.Tensor:
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        return self.fc3(x)

# LAYER 2 :REPLAY BUFFER
from collections import deque
import random

class ReplayBuffer:
    def __init__(self, capacity: int = 10000):
        self.buffer = deque(maxlen=capacity)
    
    def push(self, state, action, reward, next_state, done):
        self.buffer.append((state,action,reward,next_state,done))
    
    def sample(self, batch_size: int):
        if len(self.buffer) < batch_size:
            return None
        batch = random.sample(self.buffer, batch_size)
        states, actions, rewards, next_states, dones = zip(*batch)
        return states, actions, rewards, next_states, dones
    
    def __len__(self):
        return len(self.buffer)

# LAYER 3 : DQN BOT
class DQNBot(botinput):
    def __init__(self, state_size=183, action_size=8, lr=0.001):
        super().__init__()
        #device
        self.device = 'cuda' if tc.cuda.is_available() else 'cpu'
        # networks
        self.policy_net = DQN(state_size, 256, action_size).to(self.device)
        self.target_net = DQN(state_size, 256, action_size).to(self.device)
        self.target_net.load_state_dict(self.policy_net.state_dict())
        self.target_net.eval()
        # replay buffer
        self.memory = ReplayBuffer(capacity=10000)
        # optimiser + loss
        self.optimizer = tc.optim.Adam(self.policy_net.parameters(), lr=lr)
        self.loss_fn = nn.MSELoss()
        # epsilon greedy
        self.epsilon = 1.0        
        self.epsilon_min = 0.05   
        self.epsilon_decay = 0.001 # 5e -5 (original)
        # hyperparams
        self.gamma = 0.95         
        self.batch_size = 64
        self.target_update_freq = 100  
        self.steps = 0
        # state tracking
        self.action_history = deque([0]*10, maxlen=10)
        self.bot_last_action = 0
        self.damage_dealt = deque([0]*60, maxlen=60)
        self.damage_taken = deque([0]*60, maxlen=60)
        # action mapping
        self.ACTION_MAP = {
            0: {"direction": "neutral", "jump": False, "duck": False, "attack": None,    "parry": False},
            1: {"direction": "left",    "jump": False, "duck": False, "attack": None,    "parry": False},
            2: {"direction": "right",   "jump": False, "duck": False, "attack": None,    "parry": False},
            3: {"direction": "neutral", "jump": True,  "duck": False, "attack": None,    "parry": False},
            4: {"direction": "neutral", "jump": False, "duck": True,  "attack": None,    "parry": False},
            5: {"direction": "neutral", "jump": False, "duck": False, "attack": "light", "parry": False},
            6: {"direction": "neutral", "jump": False, "duck": False, "attack": "heavy", "parry": False},
            7: {"direction": "neutral", "jump": False, "duck": False, "attack": None,    "parry": True},
        }
        #spam detection
        self.last_3_actions=deque([0]*3,maxlen=3)
        self.spam=False
        #loading wts
        self.weights_path = "data/bot_weights.pth"
        self.load_weights()

    def get_state(self,p1:fighter,p2:fighter,round_time)->list:
        state=[]
        #fight context
        dist=(p2.x-p1.x)/1280
        state.append(dist)
        state.append(p1.hp/p1.max_hp)
        state.append(p2.hp/p2.max_hp)
        state.append(round_time/(60**2))
        #player's current state
        state.append(float(p1.is_jump))
        state.append(float(p1.char_h==p1.ducking_h))
        state.append(float(p1.is_attacking))
        state.append(float(p1.is_parrying))
        #attack phase
        if p1.is_attacking and p1.attack_type in ATTACK_DATA:
            data=ATTACK_DATA[p1.attack_type]
            if p1.attack_frame<data['startup']:
                phase=1
            elif p1.attack_frame<data['startup']+data['active']:
                phase=2
            else:
                phase=3
        else:
            phase=0
        state.append(phase/3.0)
        #action history OHE past 10 frames, 16 actions, 160 values
        for act_idx in self.action_history:
            ohe=[0.0]*16
            ohe[act_idx]=1.0
            state.extend(ohe)
        #bot OHE
        bot_ohe=[0.0]*8
        bot_ohe[self.bot_last_action]=1.0
        state.extend(bot_ohe)
        #dmg exchange
        state.append(sum(self.damage_dealt)/100.0)
        state.append(sum(self.damage_taken)/100.0)
        state.append(float(p2.is_jump))
        state.append(float(p2.char_h == p2.ducking_h))
        state.append(float(p2.is_attacking))
        state.append(float(p2.hit_stun > 0))
        return state

    def update(self,p1:fighter,p2:fighter,round_time:int):
        self.current_state=self.get_state(p1,p2,round_time)#cache and build current state

    #inherited fromn botinput
    def get_action(self,keys)->dict[str,Any]:
        if not hasattr(self,'current_state') or self.current_state is None:
            return self.ACTION_MAP[0]
        if random.random()<self.epsilon:
            weights = [0.20, 0.20, 0.20, 0.02, 0.15, 0.10, 0.08, 0.05]# neutral left right jump duck latt hatt parry
            action_idx = random.choices(range(8), weights=weights)[0]
        else:
            state_tensor=tc.as_tensor(self.current_state,dtype=tc.float32).unsqueeze(0).to(self.device)
            with tc.no_grad():
                q_values=self.policy_net(state_tensor)
            action_idx=q_values.argmax().item()
        self.bot_last_action=action_idx
        self.last_3_actions.append(action_idx)
        self.spam=len(set(self.last_3_actions))==1 and action_idx in (3,5,6)
        self.action_history.append(action_idx)
        self.steps+=1
        self.epsilon=max(self.epsilon_min,self.epsilon-self.epsilon_decay)
        return self.ACTION_MAP[action_idx]

    def save_weights(self):
        os.makedirs(os.path.dirname(self.weights_path),exist_ok=True)
        tc.save(self.policy_net.state_dict(),self.weights_path)

    def load_weights(self):
        if os.path.exists(self.weights_path):
            state_dict=tc.load(self.weights_path,map_location=self.device)
            self.policy_net.load_state_dict(state_dict)
            self.target_net.load_state_dict(state_dict)

    def train_step(self):
        if len(self.memory) < self.batch_size:
            return 0 # not enuf experience 
        result = self.memory.sample(self.batch_size)
        if result is None:
            return 0
        states, actions, rewards, next_states, dones = result
        self.steps+=1
        # convert states to tensors
        states_t=tc.as_tensor(np.array(states),dtype=tc.float32).to(self.device)
        actions_t=tc.as_tensor(np.array(actions),dtype=tc.int64).to(self.device)
        rewards_t=tc.as_tensor(np.array(rewards),dtype=tc.float32).to(self.device)
        next_states_t=tc.as_tensor(np.array(next_states),dtype=tc.float32).to(self.device)
        dones_t=tc.as_tensor(np.array(dones),dtype=tc.float32).to(self.device)
        #bellman eq.
        #curr Q
        current_q = self.policy_net(states_t).gather(1, actions_t.unsqueeze(1)).squeeze(1)
        # target Q val
        with tc.no_grad():
            next_q = self.target_net(next_states_t).max(1)[0]
            target_q = rewards_t + self.gamma * next_q * (1 - dones_t)
        
        # loss and update
        loss = self.loss_fn(current_q, target_q)
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()
        
        # update target network periodically
        if self.steps % self.target_update_freq == 0:
            self.target_net.load_state_dict(self.policy_net.state_dict())
        
        return loss.item()

    #reward fn
    def calculate_reward(self,events:dict)->float:
        reward=0.0
        reward+=events.get('damage_dealt',0)*0.5
        reward-=events.get('damage_taken',0)*0.5
        reward+=events.get('parry_success',False)*15
        reward-=events.get('parry_failed',False)*5
        reward-=events.get('attack_missed',False)*3
        reward+=events.get('round_win',False)*50
        reward-=events.get('round_loss',False)*50
        reward-=events.get('is_jumping',False)*0.1
        reward-=events.get('attack_spam',False)*2
        return reward

# why we ditched this?
# a DQN that learns purely from reward signals, firing decisions every frame.
# This is academically correct RL but produces exactly the behaviour you described
# inhuman reaction time, spam, no human-like feel.
# The core problem isn't the reward function alone 
# it's that the bot has no concept of time between actions.
# A human naturally pauses between attacks because of reaction time and planning. 
# The bot fires actions every single frame.
# fun fact: this is the same kind of bot which was used in the old arcade games 
# like mk1,mk2 to trick players into dropping more coins into the arcade machine.(cheap trick)

# what we implemented instead: modern more refined and experience focused bot
# [Game State Evaluation] ➔ [Simulated Human Reaction Delay] ➔ [Behavior Tree Selection] ➔ [Action Executed]
# 3 layers
# Behavior Tree —
#   controls what the bot does based on game state.
#   Distance, health, opponent's animation state. 
#   Produces human-like decision making with natural spacing and combo strings.
# Reaction Delay —
#   10-20 frame buffer before the bot can respond to player input.
#   Stops instant counter-attacks. Makes it beatable.
# DQN —
#   adjusts the weights in the behavior tree over time.
#   Doesn't control actions directly. Instead it learns 
#   "against this player, aggressive spacing works better than defensive"
#   and shifts probabilities accordingly.

# arrivederci
