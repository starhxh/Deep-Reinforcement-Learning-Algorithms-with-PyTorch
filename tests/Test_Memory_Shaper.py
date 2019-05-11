from Memory_Shaper import Memory_Shaper
import numpy as np

buffer_size = 10
batch_size = 5
seed = 1



def test_calculate_max_action_length():
    """Tests that calculate_max_action_length works correctly"""

    memory_shaper = Memory_Shaper(buffer_size, batch_size, seed, reward_length_increment=0.0)
    action_rules = {(0, 2, 33, 1, 22, 0, 0): 99, (0, 4): 2, (0, 9): 100}
    assert memory_shaper.calculate_max_action_length(action_rules) == 7

    action_rules = {(0, 2, 3): 99, (0, 4, 0, 0): 2, (0, 9): 100}
    assert memory_shaper.calculate_max_action_length(action_rules) == 4

def test_add_adapted_experience_for_an_episode():
    """Tests that add_adapted_experience_for_an_episode works correctly"""

    buffer_size = 3

    for reward_increment in [0.0, 0.5, 1.5]:

        memory_shaper = Memory_Shaper(buffer_size, batch_size, seed, reward_length_increment=reward_increment)
        memory_shaper.reset(buffer_size, 3, seed)
        states = [0, 1]
        next_states = [1, 10]
        rewards = [10, 5]
        actions = [0, 5]
        dones = [False, True]
        memory_shaper.add_episode_experience(states, next_states, rewards, actions, dones)

        action_rules = {(0, 5): 6}

        memory_shaper.add_adapted_experience_for_an_episode(0, action_rules, 2)

        assert len(memory_shaper.replay_buffer) == 3

        s_states, s_actions, s_rewards, s_next_states, s_dones = memory_shaper.replay_buffer.sample(separate_out_data_types=True)

        assert all(s_states.numpy() == np.array([[0.0], [1.0,], [0.0]]))
        assert all(s_actions.numpy() == np.array([[0.0], [5.0, ], [6.0]]))
        assert all(s_rewards.numpy() == np.array([[10.0], [5.0, ], [15.0 + reward_increment * 15.0]]))
        assert all(s_next_states.numpy() == np.array([[1.0], [10.0, ], [10.0]]))
        assert all(s_dones.numpy() == np.array([[0.0], [1.0, ], [1.0]]))

        buffer_size = 5
        memory_shaper = Memory_Shaper(buffer_size, buffer_size, seed, reward_length_increment=reward_increment)
        memory_shaper.reset(buffer_size, buffer_size, seed)
        states = [0, 1, 2]
        next_states = [1, 10, 11]
        rewards = [10, 5, -4]
        actions = [0, 5, 2]
        dones = [False, False, True]
        memory_shaper.add_episode_experience(states, next_states, rewards, actions, dones)

        action_rules = {(0, 5): 6, (0, 5, 2): 7}

        memory_shaper.add_adapted_experience_for_an_episode(0, action_rules, 3)

        assert len(memory_shaper.replay_buffer) == 5

        s_states, s_actions, s_rewards, s_next_states, s_dones = memory_shaper.replay_buffer.sample(
            separate_out_data_types=True)

        assert all(s_states.numpy() == np.array([[0.0], [0.0], [1.0], [0.0], [2.0]]))
        assert all(s_actions.numpy() == np.array([[6.0], [0.0], [5.0], [7.0], [2.0]]))
        assert all(s_rewards.numpy() == np.array([[15.0 * (1.0 + reward_increment)], [10.0], [5.0], [11.0 * (1.0 + reward_increment)], [-4.0]]))
        assert all(s_next_states.numpy() == np.array([[10.0], [1.0], [10.0], [11.0], [11.0]]))
        assert all(s_dones.numpy() == np.array([[0.0], [0.0], [0.0], [1.0], [1.0]]))






