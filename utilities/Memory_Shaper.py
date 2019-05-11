# NOT FINISHED
from Replay_Buffer import Replay_Buffer
import numpy as np
import random

class Memory_Shaper(object):
    """Takes in the experience of full episodes and reshapes it according to macro-actions you define. Then it provides
    a replay buffer with this reshaped data to learn from"""

    def __init__(self, buffer_size, batch_size, seed, proportion_of_one_step_actions_to_include=1.0, reward_length_increment=0.0):
        self.reset(buffer_size, batch_size, seed)
        self.proportion_of_one_step_actions_to_include = proportion_of_one_step_actions_to_include
        self.reward_length_increment = reward_length_increment

    def order_action_rules_according_to_length_of_rule(self, action_rules):
        sorted(action_rules, key=lambda k: len(action_rules), reverse=True)

    def add_adapted_experiences_to_replay_buffer(self, action_rules):
        """Adds experiences to the replay buffer after re-imagining that the actions taken were macro-actions according to
         action_rules as well as primitive actions.

         NOTE that we want to put both primitive actions and macro-actions into replay buffer so that it can learn that
         its better to do a macro-action rather than the same primitive actions (which we will enforce with reward penalty)
         """
        for key in action_rules.keys():
            assert isinstance(key, tuple)
            assert isinstance(action_rules[key], int)

        episodes = len(self.states)
        for data_type in [self.states, self.next_states, self.rewards, self.actions, self.dones]:
            assert len(data_type) == episodes

        max_action_length = self.calculate_max_action_length(action_rules)

        for episode_ix in range(episodes):
            self.add_adapted_experience_for_an_episode(episode_ix, action_rules, max_action_length)

    def calculate_max_action_length(self, action_rules):
        """Calculates the max length of the provided macro-actions"""
        max_length = 0
        for key in action_rules.keys():
            action_length = len(key)
            if action_length > max_length:
                max_length = action_length
        return max_length

    def increment_reward_according_to_action_length(self, cumulative_reward):
        if cumulative_reward != 0.0:
            increment = self.reward_length_increment * abs(cumulative_reward)
            reward = cumulative_reward + increment
        else:
            reward = cumulative_reward + 1.0 * self.reward_length_increment
        return reward

    def add_adapted_experience_for_an_episode(self, episode_ix, action_rules, max_action_length):
        """Adds all the experiences we have been given to a replay buffer after adapting experiences that involved doing a
          macro action"""
        states = self.states[episode_ix]
        next_states = self.next_states[episode_ix]
        rewards = self.rewards[episode_ix]
        actions = self.actions[episode_ix]
        dones = self.dones[episode_ix]
        assert len(states) == len(next_states) == len(rewards) == len(dones) == len(actions)
        steps = len(states)
        for step in range(steps):
            if random.random() <= self.proportion_of_one_step_actions_to_include:
                self.replay_buffer.add_experience(states[step], actions[step], rewards[step], next_states[step], dones[step])
            for action_length in range(2, max_action_length + 1):
                if step < action_length - 1: continue
                action_sequence =  tuple(actions[step - action_length + 1 : step + 1])
                if action_sequence in action_rules.keys():
                    new_action = action_rules[action_sequence]
                    new_state = states[step - action_length + 1]
                    new_reward = np.sum(rewards[step - action_length + 1:step + 1])
                    new_reward = self.increment_reward_according_to_action_length(new_reward)
                    new_next_state = next_states[step]
                    new_dones = dones[step]
                    self.replay_buffer.add_experience(new_state, new_action, new_reward, new_next_state, new_dones)

    def add_episode_experience(self, states, next_states, rewards, actions, dones):
        """Adds in an episode of experience"""
        self.states.append(states)
        self.next_states.append(next_states)
        self.rewards.append(rewards)
        self.actions.append(actions)
        self.dones.append(dones)

    def reset(self, buffer_size, batch_size, seed):
        self.states = []
        self.next_states = []
        self.rewards = []
        self.actions = []
        self.dones = []
        self.replay_buffer = Replay_Buffer(buffer_size, batch_size, seed)




