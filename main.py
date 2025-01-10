# Main driver 
# train or test our models 
import datetime
import pygame
from snake_game import SnakeGame
from agent import Agent
import os
import signal
import sys
import matplotlib.pyplot as plt

def signal_handler(sig, frame, scores, rewards):
    print('Interrupted! Saving plots and exiting...')
    save_plots(scores, rewards)
    sys.exit(0)

def save_plots(scores, rewards):
    plt.figure(figsize=(12, 5))
    plt.subplot(1, 2, 1)
    plt.plot(scores, label='Score per Episode')
    plt.xlabel('Episode')
    plt.ylabel('Score')
    plt.title('Scores Over Episodes')
    plt.legend()

    plt.subplot(1, 2, 2)
    plt.plot(rewards, label='Total Reward per Episode')
    plt.xlabel('Episode')
    plt.ylabel('Total Reward')
    plt.title('Rewards Over Episodes')
    plt.legend()

    plt.tight_layout()
    plt.savefig('training_performance.png')
    plt.close()

# Function for training
def train_agent(episodes, model_path=None, render=False, save_interval=100):
    game = SnakeGame()
    agent = Agent(state_size=11, action_size=4, batch_size=32)
    scores = []
    rewards = []

    if model_path:
        agent.load(model_path)
        print("Model loaded successfully, continuing training.")
    
    signal.signal(signal.SIGINT, lambda sig, frame: signal_handler(sig, frame, scores, rewards))

    for episode in range(episodes):
        game.reset()
        state = game.get_state()
        total_reward = 0

        while True:
            action = agent.act(state)
            next_state, reward, done = game.step(action)
            agent.remember(state, action, reward, next_state, done)
            total_reward += reward

            if done:
                scores.append(game.score)
                rewards.append(total_reward)
                print(f"Episode: {episode}, Score: {game.score}, Total Reward: {total_reward}")
                break

            state = next_state
            agent.replay()

            if render:
                game.render_game()

        if episode % save_interval == 0:
            if not os.path.exists("Models"):
                os.makedirs("Models")
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            agent.save(f"./Models/snake_model_{episode}_{timestamp}.pth")

    print("Training completed.")
    save_plots(scores, rewards)

# Function for testing
def run_pretrained_model(model_path, render=True, fps=10):
    game = SnakeGame()
    agent = Agent(state_size=11, action_size=4, batch_size=32)
    agent.load(model_path)

    clock = pygame.time.Clock()

    game.reset()
    while True:
        state = game.get_state()
        action = agent.act(state, testing=True)
        _, _, done = game.step(action)

        if render:
            game.render_game()
            pygame.display.update()

        if done:
            print(f"Final Score: {game.score}")
            break

        clock.tick(fps)


# Main
if __name__ == "__main__":
    pretrained_model_path = "snake_model_1900_20240708_192525.pth"
    
    # TRAIN MODEL (render to show the training)
    train_agent(2000, render=True)
    
    # TRAIN MODEL FROM PREVIOUS MODEL
    # train_agent(2000,model_path = pretrained_model_path, render=True)
    
    # RUN PRETRAINED MODEL
    #run_pretrained_model(pretrained_model_path, render=True, fps=45)

