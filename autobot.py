import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
from matplotlib.widgets import Button
import tkinter as tk
from tkinter import simpledialog, Canvas, messagebox
from tkinter import messagebox

class QLearning:
    def __init__(self, grid, start, goal, autobots, other_bots=None, learning_rate=0.1, discount_factor=0.95, exploration_rate=1.0, exploration_decay=0.99, min_exploration_rate=0.01):
        self.grid = grid
        self.start = start
        self.goal = goal
        self.autobots = autobots
        self.other_bots = other_bots if other_bots is not None else []
        self.q_table = np.zeros((grid.shape[0], grid.shape[1], 4))
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.exploration_rate = exploration_rate
        self.exploration_decay = exploration_decay
        self.min_exploration_rate = min_exploration_rate
        self.actions = [(0, 1), (0, -1), (1, 0), (-1, 0)]

    def is_collision(self, next_state):
        for bot in self.autobots:
            if bot.position == next_state and bot.position != self.start:
                return True
        return False

    def learn(self, episodes=1000):
        for _ in range(episodes):
            state = self.start
            while state != self.goal:
                if np.random.rand() < self.exploration_rate:
                    action_idx = np.random.randint(4)
                else:
                    action_idx = np.argmax(self.q_table[state[0], state[1]])

                action = self.actions[action_idx]
                next_state = (state[0] + action[0], state[1] + action[1])

                if not (0 <= next_state[0] < self.grid.shape[0] and 0 <= next_state[1] < self.grid.shape[1]) or self.grid[next_state] == 1:
                    reward = -100  
                    next_state = state
                elif self.is_collision(next_state):
                    reward = -50  
                    next_state = state
                elif next_state == self.goal:
                    reward = 100  
                else:
                    reward = -1  

                # Q-learning update
                old_value = self.q_table[state[0], state[1], action_idx]
                next_max = np.max(self.q_table[next_state[0], next_state[1]])
                new_value = (1 - self.learning_rate) * old_value + self.learning_rate * (reward + self.discount_factor * next_max)
                self.q_table[state[0], state[1], action_idx] = new_value

                state = next_state

            self.exploration_rate = max(self.min_exploration_rate, self.exploration_rate * self.exploration_decay)

    def get_path(self):
        path = []
        state = self.start
        while state != self.goal:
            action_idx = np.argmax(self.q_table[state[0], state[1]])
            action = self.actions[action_idx]
            next_state = (state[0] + action[0], state[1] + action[1])
            path.append(next_state)
            state = next_state
            if len(path) > 10000: 
                break
        return path


class Autobot:
    def __init__(self, start, end, name, grid, simulation):
        self.position = start
        self.destination = end
        self.name = name
        self.grid = grid
        self.simulation = simulation
        self.q_learning = QLearning(grid, start, end, self.simulation.autobots)
        self.q_learning.learn(episodes=1000)
        self.path = self.q_learning.get_path()
        self.at_destination = False
        self.time = -1
        self.waiting_time = 0
        self.is_waiting = False  
        self.gave_way = False  
        self.command_count = 0

        self.label_text = self.simulation.ax.text(self.position[1], self.simulation.grid.shape[0] - 1 - self.position[0], self.name,
                                                   ha='center', va='center', color='#333', fontsize=12)

    def is_face_to_face(self, next_step):
        """ Check if two autobots are moving face-to-face."""
        for autobot in self.simulation.autobots:
            if autobot.name != self.name:
                autobot_next_step = autobot.path[0] if autobot.path else None
                if autobot_next_step and autobot_next_step == self.position and next_step == autobot.position:
                    return True
        return False

    def find_safe_move(self):
        """ Find a safe adjacent cell to move to temporarily. """
        for action in self.q_learning.actions:
            temp_pos = (self.position[0] + action[0], self.position[1] + action[1])
            if 0 <= temp_pos[0] < self.grid.shape[0] and 0 <= temp_pos[1] < self.grid.shape[1] and self.grid[temp_pos] != 1:
                if not any(bot.position == temp_pos for bot in self.simulation.autobots):
                    return temp_pos
        return None  

    def move(self):
        if not self.path:
            print(f"{self.name}: Path not found for AI.")
            return

        if not self.at_destination:
            next_step = self.path[0]

            if self.is_face_to_face(next_step):
                print(f"{self.name} is in a face-to-face situation.")
                if not self.gave_way:
                    safe_move = self.find_safe_move()
                    if safe_move:
                        print(f"{self.name} gives way and moves temporarily to {safe_move}.")
                        
                        self.position = safe_move
                        self.label_text.set_position((safe_move[1], self.simulation.grid.shape[0] - 1 - safe_move[0]))
                        self.gave_way = True
                        self.waiting_time += 1
                        self.command_count += 1
                        return  
                    else:
                        print(f"{self.name} cannot find a temporary move.")
                        self.waiting_time += 1
                        self.command_count += 1
                        return
                else:
                    print(f"{self.name} has already given way, resuming movement.")
                    self.gave_way = False  

            for autobot in self.simulation.autobots:
                if autobot.position == next_step and autobot.name != self.name:
                    print(f"{self.name} waiting due to potential collision with {autobot.name}.")
                    self.is_waiting = True
                    self.waiting_time += 1
                    self.command_count += 1
                    return


            print(f"{self.name} moves from {self.position} to {next_step}.")
            self.command_count += 1
            if next_step == self.destination:
                self.at_destination = True
                print(f"{self.name} reached destination {self.destination}.")
            else:
                self.label_text.set_position((next_step[1], self.simulation.grid.shape[0] - 1 - next_step[0]))

            self.position = next_step
            self.path.pop(0)
            self.time += 1
            self.is_waiting = False
            self.waiting_time = 0  
        else:
            print(f"{self.name} has reached its destination or has no valid path.")

        if self.waiting_time > 5:
            messagebox.showinfo("Alert", f"{self.name} cannot reach its destination due to obstacles.")
            self.at_destination = True


    def adjust_text_position(self, next_step):
        """ Adjusts text position to avoid overlap with other autobots. """
        other_autobots = [autobot for autobot in self.simulation.autobots if autobot.name != self.name]
        close_bots = [bot for bot in other_autobots if abs(bot.position[0] - next_step[0]) <= 1 and abs(bot.position[1] - next_step[1]) <= 1]

        if close_bots:
            self.label_text.set_position((next_step[1] + 0.3, self.simulation.grid.shape[0] - 1 - next_step[0] - 0.3))
        else:
            self.label_text.set_position((next_step[1], self.simulation.grid.shape[0] - 1 - next_step[0]))



class AutoBotSimulation:
    def __init__(self, grid, autobot_starts, autobot_goals):
        plt.rcParams['toolbar'] = 'none'
        self.grid = grid
        self.autobots = []
        self.goal_circles = {}
        self.move_count = 0  
        self.any_path_found = False  

        self.fig, self.ax = plt.subplots(figsize=(grid.shape[1] * 0.7, grid.shape[0] * 0.7))
        self.fig.patch.set_facecolor('#222')  
        self.ax.set_facecolor('#333')         
        self.ax.set_xticks(np.arange(-0.5, grid.shape[1], 1))
        self.ax.set_yticks(np.arange(-0.5, grid.shape[0], 1))
        self.ax.grid(True, color='white', linewidth=0.5) 
        self.ax.set_xlim(-0.5, grid.shape[1] - 0.5)
        self.ax.set_ylim(-0.5, grid.shape[0] - 0.5)

        self.ax.set_xticklabels([])  
        self.ax.set_yticklabels([]) 
        self.ax.grid(True, color='white', linewidth=0.5)
        self.fig.canvas.manager.set_window_title("AutoBot Simulation")
        

        for idx, (start, goal) in enumerate(zip(autobot_starts, autobot_goals)):
            autobot = Autobot(start, goal, f"A{idx+1}", grid, self)  
            self.autobots.append(autobot)
            if autobot.path is not None and len(autobot.path) > 0:
                self.any_path_found = True  

        if not self.any_path_found:
            print("Warning: No valid paths for any autobots due to obstacles. The simulation will proceed but movements may be limited.")

        self.create_obstacles()
        self.runtime_label = plt.text(0.5, grid.shape[0] + 0.5, f'Move Count: {self.move_count}', fontsize=12, ha='center')

        for autobot in self.autobots:
            autobot_circle = Circle((autobot.position[1], grid.shape[0] - 1 - autobot.position[0]), 0.3, color='royalblue')
            self.ax.add_patch(autobot_circle)
            self.ax.text(autobot.position[1], grid.shape[0] - 1 - autobot.position[0], autobot.name, ha='center', va='center', color='#333', fontsize=14)
            goal_circle = Circle((autobot.destination[1], grid.shape[0] - 1 - autobot.destination[0]), 0.3, color='gold', alpha=0.7)
            self.ax.add_patch(goal_circle)
            self.goal_circles[autobot.name] = goal_circle
            self.ax.text(autobot.destination[1], grid.shape[0] - 1 - autobot.destination[0], f"B{autobot.name[1]}", ha='center', va='center', color='black', fontsize=12)

        self.next_step_button = Button(plt.axes([0.6, 0.02, 0.40, 0.06]), 'Next Step', color='lightgreen', hovercolor='green')
        self.next_step_button.on_clicked(lambda event: self.next_step())
        self.auto_button = Button(plt.axes([0.0, 0.02, 0.40, 0.06]), 'Run Simulation', color='skyblue', hovercolor='dodgerblue')
        self.auto_button.on_clicked(lambda event: self.auto_run())

        self.update()


    def create_obstacles(self):
        for i in range(self.grid.shape[0]):
            for j in range(self.grid.shape[1]):
                if self.grid[i, j] == 1:
                    self.ax.add_patch(plt.Rectangle((j - 0.5, self.grid.shape[0] - 1 - i - 0.5), 1, 1, color='black'))

    def update(self):
        autobot_patches = [patch for patch in self.ax.patches if isinstance(patch, Circle) and patch not in self.goal_circles.values()]
        for patch in autobot_patches:
            patch.remove()

        for autobot in self.autobots:
            autobot_circle = Circle((autobot.position[1], self.grid.shape[0] - 1 - autobot.position[0]), 0.3, color='blue')
            self.ax.add_patch(autobot_circle)

        self.runtime_label.set_text(f'Move Count: {self.move_count}')
        plt.draw()

    def next_step(self):
        for autobot in self.autobots:
            autobot.move()  
            print(f"{autobot.name} time: {autobot.time}, waiting time: {autobot.waiting_time}, moves:  {autobot.time}")
            print(f"{autobot.name} total commands executed: {autobot.command_count}")
        self.move_count += 1  
        self.update()  

    def auto_run(self):
        while any(not autobot.at_destination for autobot in self.autobots):
            self.next_step()
            plt.pause(0.6)

class GridCreator(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Enhanced Grid Creator")
        self.configure(bg="#333")  # Dark theme background
        self.grid_size = simpledialog.askinteger("Input", "Enter grid size (e.g., 4 for 4x4):", minvalue=2, maxvalue=50)
        self.geometry(f"{self.grid_size * 30 + 50}x{self.grid_size * 30 + 100}")
        self.grid = np.zeros((self.grid_size, self.grid_size), dtype=object)
        self.autobot_starts = []
        self.autobot_goals = []

        self.canvas = Canvas(self, width=self.grid_size * 30, height=self.grid_size * 30, bg="white")
        self.canvas.pack()

        self.draw_grid()

        self.canvas.bind("<Button-1>", self.add_obstacle)
        self.canvas.bind("<Button-3>", self.set_start_and_goal)

        self.start_button = tk.Button(self, text="Start Simulation", command=self.start_simulation, state=tk.DISABLED, bg="#0c9", fg="white", font=("Helvetica", 12, "bold"))
        self.start_button.pack(side=tk.LEFT)

    def draw_grid(self):
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                x0 = j * 30
                y0 = i * 30
                x1 = x0 + 30
                y1 = y0 + 30
                self.canvas.create_rectangle(x0, y0, x1, y1, outline="gray", fill="lightgray")

    def add_obstacle(self, event):
        row = event.y // 30
        col = event.x // 30
        if self.grid[row, col] == 0 and ((len(self.autobot_starts) == 0 or len(self.autobot_starts) == len(self.autobot_goals)) or (len(self.autobot_starts) > len(self.autobot_goals))):  
            self.grid[row, col] = 1
            self.canvas.create_rectangle(col * 30, row * 30, (col + 1) * 30, (row + 1) * 30, fill="black")
        elif self.grid[row, col] == 1:  
            self.grid[row, col] = 0
            self.canvas.create_rectangle(col * 30, row * 30, (col + 1) * 30, (row + 1) * 30, fill="lightgray")

    def set_start_and_goal(self, event):
        row = event.y // 30
        col = event.x // 30
        if (len(self.autobot_starts) == 0 or len(self.autobot_starts) == len(self.autobot_goals)) and self.grid[row, col] == 0:
            self.grid[row, col] = "S"
            self.autobot_starts.append((row, col))
            self.canvas.create_oval(col * 30 + 5, row * 30 + 5, (col + 1) * 30 - 5, (row + 1) * 30 - 5, fill="blue")
        elif (len(self.autobot_starts) > len(self.autobot_goals)) and self.grid[row, col] == 0:
            self.grid[row, col] = "G"
            self.autobot_goals.append((row, col))
            self.canvas.create_oval(col * 30 + 5, row * 30 + 5, (col + 1) * 30 - 5, (row + 1) * 30 - 5, fill="yellow")
        if len(self.autobot_starts) == len(self.autobot_goals) and len(self.autobot_starts) > 0:
            self.start_button.config(state=tk.NORMAL)

    def start_simulation(self):
        self.destroy() 
        AutoBotSimulation(self.grid, self.autobot_starts, self.autobot_goals)
        plt.show()
        

if __name__ == "__main__":
    app = GridCreator()
    app.mainloop()
