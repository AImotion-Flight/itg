import math
import numpy as np
import matplotlib.pyplot as plt

class EnsembleQLearning():
    def __init__(self, n, init_state, final_state, agent, env, ep, alpha, gamma, eps, plot=False):
        self.n = n
        self.init_state = init_state
        self.final_state = final_state
        self.agent = agent
        self.env = env
        self.ep = ep
        self.alpha = alpha
        self.gamma = gamma
        self.eps = eps
        self.plot = plot

        Qs = []
        for i in range(self.n):
            Qs.append(np.zeros((self.agent.get_state_count(), self.agent.get_action_count())))
        self.Qs = np.array(Qs)

        if plot:
            self.fig = plt.figure(self.__class__.__name__, figsize=(2, 2))
            self.ax = self.fig.add_subplot(111)

    def clear(self):
        Qs = []
        for i in range(self.n):
            Qs.append(np.zeros((self.agent.get_state_count(), self.agent.get_action_count())))
        self.Qs = np.array(Qs)

    def plot_learning(self, path):
        self.ax.clear()
        self.ax.imshow(np.flip(self.env.grid, 0), cmap='gray', origin='lower')
        self.ax.plot(self.init_state[0], self.init_state[1], 'go')
        self.ax.plot(self.final_state[0], self.final_state[1], 'r*')
        self.ax.plot(path[:, 0], path[:, 1], 'b--')
        self.ax.plot(path[-1, 0], path[-1, 1], 'rx')
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()

    def save(self, filename):
        np.save(filename, self.Qs)

    def load(self, filename):
        self.Qs = np.load(filename)

    def is_final(self, state):
        return state == self.final_state

    def is_terminal(self, state, next_state):
        if not self.env.is_valid(next_state[0:2]):
            return True
        if self.env.is_obstacle(next_state[0:2]):
            return True
        if self.is_final(next_state):
            return True
        if not self.env.is_free(state[0:2], next_state[0:2]):
            return True
        return False

    def reset_agent(self):
        self.agent.set_state(self.init_state)
    
    def epsilon_greedy_policy(self, state):
        if np.random.uniform() < self.eps:
            return self.agent.get_random_action()
        else:
            row = self.agent.find_state_index(state)
            argmaxQ = np.argmax(np.sum(self.Qs, axis=0)[row])
            return self.agent.get_action_by_index(argmaxQ)

    def convergence(self):
        return np.sum(np.max(self.Qs, axis=2), axis=0) / self.n

    def compute_reward(self, state, next_state):
        if not self.env.is_valid(next_state):
            return -10
        elif self.env.is_obstacle(next_state):
            return -10
        elif not self.env.is_free(state[0:2], next_state[0:2]):
            return -10
        elif self.is_final(next_state):
            return 10
        elif state == next_state:
            return -2
        else:
            return 0
        
    def update_Q(self, state, next_state, action, r):
        row = self.agent.find_state_index(state)
        col = self.agent.find_action_index(action)
            
        pQ = np.random.randint(0, self.n)
        pmaxQ = np.random.randint(0, self.n)

        maxQ = 0
        if not self.is_terminal(state, next_state):
            row_next = self.agent.find_state_index(next_state)
            maxQ = self.Qs[pQ][row_next, np.argmax(self.Qs[pmaxQ][row_next])]

        self.Qs[pQ][row, col] = self.Qs[pQ][row, col] + self.alpha * (r + self.gamma * maxQ - self.Qs[pQ][row, col])

    def run_episode(self):
        self.reset_agent()
        path = []
        aseq = []
        er = 0

        last_state = self.agent.get_state()
        state = self.agent.get_state()
            
        while not self.is_terminal(last_state, state):
            action = self.epsilon_greedy_policy(state)
            next_state, c = self.agent.transition_state(action)
            
            path.append(state)
            aseq.append(action)
            
            r = self.compute_reward(state, next_state) - c/10
            self.update_Q(state, next_state, action, r)

            last_state = state
            state = next_state

            er = er + r

        return path, state, aseq, er
        
    def learn(self, logger):
        if self.plot:
             self.fig.show()

        convg = []
        rew = []
        best = -10e99
        try:
            for i in range(1, self.ep + 1):
                path, terminal_state, _, er = self.run_episode()

                convg.append(self.convergence()[self.agent.find_state_index(self.init_state)])
                rew.append(er)

                best = er if  er > best else best

                if self.is_final(terminal_state):
                    path.append(terminal_state)
                    logger.log("Goal reached! Reward: " + str(er - 10) + " Best Reward: " + str(best - 10))

                if self.plot:
                    self.plot_learning(np.array(path))
                    
                if i % 1000 == 0:
                    logger.log('Completed Episode ' + str(i))
        except KeyboardInterrupt:
            logger.log('stop learning ...')
            
        return np.array(convg), np.array(rew)

    def get_policy(self):
        self.reset_agent()
        path = []
        aseq = []

        state = self.agent.get_state() 
        
        while not self.is_final(state):
            row = self.agent.find_state_index(state)
            col = np.argmax(np.sum(self.Qs, axis=0)[row])
            action = self.agent.get_action_by_index(col)

            path.append(state)
            aseq.append(action)
            
            state, _ = self.agent.transition_state(action)

        path.append(state)
        aseq.append((0, 0))
        
        return np.array(path), np.array(aseq)

class QLearning(EnsembleQLearning):
    def __init__(self, init_state, final_state, agent, env, ep, alpha, gamma, eps, plot=False):
            super().__init__(1, init_state, final_state, agent, env, ep, alpha, gamma, eps, plot)
    