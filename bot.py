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
from collections import deque
import random

class DQN(nn.Module):
    def __init__(self, input_size: int = 183, hidden_size: int = 256, output_size: int = 4):
        super().__init__()
        self.fc1 = nn.Linear(input_size, hidden_size)
        self.fc2 = nn.Linear(hidden_size, hidden_size)
        self.fc3 = nn.Linear(hidden_size, output_size)

    def forward(self, x: tc.Tensor) -> tc.Tensor:
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        return self.fc3(x)

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

# layer 1: reaction buffer
class ReactionBuffer:
    def __init__(self, delay_frames=15):
        self.delay = delay_frames
        self.buffer = deque(maxlen=delay_frames + 1)
    
    def push(self, game_state):
        self.buffer.append(game_state)
    
    def get_delayed_state(self):
        # return oldest state in buffer
        # if buffer not full yet, return what we have
        if len(self.buffer) == 0:
            return None
        return self.buffer[0]
# layer 2: behavior tree
BEHAVIOR_MOVES = {
    "zone": {
        "moves": [0, 1, 2, 5],   # neutral, left, right, light attack
        "weights": [0.3, 0.3, 0.2, 0.2]
    },
    "pressure": {
        "moves": [2, 5, 6],      # right, light, heavy
        "weights": [0.3, 0.4, 0.3]
    },
    "defensive": {
        "moves": [1, 4, 7],      # left, duck, parry
        "weights": [0.4, 0.3, 0.3]
    },
    "punish": {
        "moves": [5, 6],         # light, heavy
        "weights": [0.4, 0.6]
    }
}

# layer 3: behavior dqn
class BehaviorDQN(nn.Module):
    def __init__(self, input_size=179, hidden_size=256, output_size=8):
        super().__init__()
        self.fc1 = nn.Linear(input_size, hidden_size)
        self.fc2 = nn.Linear(hidden_size, hidden_size)
        self.fc3 = nn.Linear(hidden_size, output_size)
    
    def forward(self, x):
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        return self.fc3(x)
        