import os
from asyncio import coroutines
import torch
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

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        return self.fc3(x)

QNetwork = DQN

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
    def __init__(self, state_size=179, action_size=8, lr=0.001):
        super().__init__()
        #device
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        # networks
        self.policy_net = DQN(state_size, 256, action_size).to(self.device)
        self.target_net = DQN(state_size, 256, action_size).to(self.device)
        self.target_net.load_state_dict(self.policy_net.state_dict())
        self.target_net.eval()
        # replay buffer
        self.memory = ReplayBuffer(capacity=10000)
        # optimiser + loss
        self.optimizer = torch.optim.Adam(self.policy_net.parameters(), lr=lr)
        self.loss_fn = nn.MSELoss()
        # epsilon greedy
        self.epsilon = 1.0        
        self.epsilon_min = 0.05   
        self.epsilon_decay = 5e-5
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
        self.weights_path = "data/bot_weights.pth"
        self.load_weights()


    # save weights
    def save_weights(self):
        os.makedirs("data", exist_ok=True)
        torch.save(self.policy_net.state_dict(), self.weights_path)
        print("weights saved")
    
    # load weights
    def load_weights(self):
        if os.path.exists(self.weights_path):
            self.policy_net.load_state_dict(torch.load(self.weights_path))
            self.target_net.load_state_dict(torch.load(self.weights_path))
            print("weights loaded")
        else:
            print("no weights found, training from scratch")    