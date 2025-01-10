# Agent class
# handles how we interpret data
import torch
import torch.nn.functional as F
import random
from collections import deque
from dqn import DQN
from replay_buffer import ReplayBuffer 

class Agent:
    # Initialize all defaults and utility of the agent
    def __init__(self, state_size, action_size, batch_size):
        self.state_size = state_size
        self.action_size = action_size
        self.batch_size = batch_size
        self.memory = ReplayBuffer(10000)
        self.epsilon = 1.0
        self.epsilon_decay = 0.995
        self.epsilon_min = 0.01
        self.gamma = 0.99
        self.model = DQN(state_size, action_size)
        self.optimizer = torch.optim.Adam(self.model.parameters(), lr=0.001)

    # Add a transition to memory
    def remember(self, state, action, reward, next_state, done):
        self.memory.push(state, action, reward, next_state, done)

    # Handles making decision
    def act(self, state, testing=False):
        # Epsilon handles exploration
        if testing or self.epsilon < 0.01:
            state = torch.tensor(state, dtype=torch.float32).unsqueeze(0)
            q_values = self.model(state)
            return torch.argmax(q_values).item()
        else:
            if random.random() <= self.epsilon:
                return random.randrange(self.action_size)
            else:
                state = torch.tensor(state, dtype=torch.float32).unsqueeze(0)
                q_values = self.model(state)
                return torch.argmax(q_values).item()
    # Replay function for decision making
    def replay(self):
        if len(self.memory) < self.batch_size:
            return

        transitions = self.memory.sample(self.batch_size)
        batch = list(zip(*transitions))

        state_batch = torch.tensor(batch[0], dtype=torch.float32)
        action_batch = torch.tensor(batch[1], dtype=torch.long)
        reward_batch = torch.tensor(batch[2], dtype=torch.float32)
        next_state_batch = torch.tensor(batch[3], dtype=torch.float32)
        done_batch = torch.tensor(batch[4], dtype=torch.float32)

        current_q_values = self.model(state_batch).gather(1, action_batch.unsqueeze(-1)).squeeze(-1)
        next_q_values = self.model(next_state_batch).max(1)[0]
        expected_q_values = reward_batch + (self.gamma * next_q_values * (1 - done_batch))

        loss = F.mse_loss(current_q_values, expected_q_values)
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()

        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay

    # Save model
    def save(self, filepath):
        torch.save({
            'model_state_dict': self.model.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict()
        }, filepath)

    # Load model
    def load(self, filepath):
        checkpoint = torch.load(filepath)
        self.model.load_state_dict(checkpoint['model_state_dict'])
        self.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
        self.model.eval()

