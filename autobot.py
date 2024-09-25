import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
from matplotlib.widgets import Button
import tkinter as tk
from tkinter import simpledialog
from tkinter import Canvas
import heapq
from tkinter import messagebox
import sys

def heuristic(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def astar(grid, start, goal):
    rows, cols = grid.shape
    open_list = []
    heapq.heappush(open_list, (0, start))
    came_from = {start: None}
    g_score = {start: 0}
    
    while open_list:
        current = heapq.heappop(open_list)[1]
        
        if current == goal:
            path = []
            while current:
                path.append(current)
                current = came_from[current]
            return path[::-1]
        
        neighbors = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        for direction in neighbors:
            neighbor = (current[0] + direction[0], current[1] + direction[1])
            
            if 0 <= neighbor[0] < rows and 0 <= neighbor[1] < cols and grid[neighbor] != 1:
                tentative_g_score = g_score[current] + 1
                if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f_score = tentative_g_score + heuristic(neighbor, goal)
                    heapq.heappush(open_list, (f_score, neighbor))
    
    return None

class Autobot:
    def __init__(self, start, end, name, grid, simulation):
        self.position = start
        self.destination = end
        self.name = name
        self.grid = grid
        self.path = astar(grid, start, end)
        self.time = -1
        self.waiting_time = 0
        self.simulation = simulation

        if self.path is None:  
            messagebox.showinfo("Alert", f"Path for {self.name} is not found due to obstacles.")
        else:
            print(f"{self.name} starts at {self.position}")  

    def move(self):
        if self.path:
            step = self.path.pop(0)
            direction = "initial point"
            if step[0] > self.position[0]:  
                direction = "down"
            elif step[0] < self.position[0]:  
                direction = "up"
            elif step[1] > self.position[1]:  
                direction = "right"
            elif step[1] < self.position[1]: 
                direction = "left"

            if self.name == "A1" and self.simulation.autobot2.position == step:
                print(f"{self.name} waits for A2 to move away from {step}")
                self.path.insert(0, step) 
                self.waiting_time += 1
                return
            elif self.name == "A2" and self.simulation.autobot1.position == step:
                print(f"{self.name} waits for A1 to move away from {step}")
                self.path.insert(0, step)  
                self.waiting_time += 1
                return

            print(f"{self.name} moves from {self.position} to {step} ({direction})")
            self.grid[self.position] = 0  
            self.position = step
            self.grid[self.position] = self.name  
            text_x = self.position[1]  
            text_y = self.simulation.grid.shape[0] - 1 - self.position[0]  
            self.simulation.ax.text(text_x, text_y, self.name, ha='center', va='center', color='white', fontsize=12)
            self.simulation.update() 
            self.time += 1
            if not self.path:
                if self.name=="A1":
                    self.simulation.goal_a1_circle.set_visible(False) 
                    red_circle = Circle((self.position[1], self.simulation.grid.shape[0] - 1 - self.position[0]), 0.3, color='red')
                    self.simulation.ax.add_patch(red_circle)
                    if self.simulation.text_b1:
                        self.simulation.text_b1.remove();
                elif self.name == "A2":
                    self.simulation.goal_a2_circle.set_visible(False) 
                    red_circle = Circle((self.position[1], self.simulation.grid.shape[0] - 1 - self.position[0]), 0.3, color='red')
                    self.simulation.ax.add_patch(red_circle)
                    if self.simulation.text_b2:
                        self.simulation.text_b2.remove();
            
        else:
            print(f"{self.name} has reached its destination.")
            if self.name == "A1":
                self.simulation.goal_a1_circle.set_visible(False) 
                red_circle = Circle((self.position[1], self.simulation.grid.shape[0] - 1 - self.position[0]), 0.3, color='red')
                self.simulation.ax.add_patch(red_circle)
                
            elif self.name == "A2":
                self.simulation.goal_a2_circle.set_visible(False) 
                red_circle = Circle((self.position[1], self.simulation.grid.shape[0] - 1 - self.position[0]), 0.3, color='red')
                self.simulation.ax.add_patch(red_circle)
     
            self.simulation.update()  

class AutoBotSimulation:
    def __init__(self, grid, start_a1 , start_a2, goal_a1, goal_a2):
        self.grid = grid
        self.autobot1 = Autobot(start_a1, goal_a1, "A1", grid, self)
        self.autobot2 = Autobot(start_a2, goal_a2, "A2", grid, self)  

        self.fig, self.ax = plt.subplots()
        self.ax.set_xticks(np.arange(-0.5, grid.shape[1], 1))
        self.ax.set_yticks(np.arange(-0.5, grid.shape[0], 1))
        self.ax.grid(True)
        self.ax.set_xlim(-0.5, grid.shape[1] - 0.5)
        self.ax.set_ylim(-0.5, grid.shape[0] - 0.5)

        self.create_obstacles()
        self.a1_circle = Circle((start_a1[1], grid.shape[0] - 1 - start_a1[0]), 0.3, color='blue')
        self.a2_circle = Circle((start_a2[1], grid.shape[0] - 1 - start_a2[0]), 0.3, color='blue')
        self.ax.text(start_a1[1], grid.shape[0]-1-start_a1[0], 'A1', ha='center', va='center', color='white', fontsize=12)
        self.ax.text(start_a2[1], grid.shape[0]-1-start_a2[0], 'A2', ha='center', va='center', color='white', fontsize=12)
        self.ax.add_patch(self.a1_circle)
        self.ax.add_patch(self.a2_circle)
        self.goal_a1_circle = Circle((goal_a1[1], grid.shape[0] - 1 - goal_a1[0]), 0.3, color='yellow')
        self.goal_a2_circle = Circle((goal_a2[1], grid.shape[0] - 1 - goal_a2[0]), 0.3, color='yellow')
        self.text_b1 =self.ax.text(goal_a1[1], grid.shape[0]-1-goal_a1[0], 'B1', ha='center', va='center', color='black', fontsize=12)
        self.text_b2 =self.ax.text(goal_a2[1], grid.shape[0]-1-goal_a2[0], 'B2', ha='center', va='center', color='black', fontsize=12)
        self.ax.add_patch(self.goal_a1_circle)
        self.ax.add_patch(self.goal_a2_circle)
        
        
        self.next_step_button = Button(plt.axes([0.8, 0.01, 0.1, 0.05]), 'Next Step')
        self.next_step_button.on_clicked(lambda event: self.next_step())

        if self.autobot1.path is None and self.autobot2.path is None:
            messagebox.showinfo("Error", "Paths for both autobots are blocked by obstacles.")
            self.next_step_button.ax.set_visible(False) 
            sys.exit()
        elif self.autobot1.path is None:
            messagebox.showinfo("Warning", "Path for A1 is blocked. Only A2 will move.")
        elif self.autobot2.path is None:
            messagebox.showinfo("Warning", "Path for A2 is blocked. Only A1 will move.")
        
        self.update()

    def create_obstacles(self):
        for i in range(self.grid.shape[0]):
            for j in range(self.grid.shape[1]):
                if self.grid[i, j] == 1:
                    self.ax.add_patch(plt.Rectangle((j - 0.5, self.grid.shape[0] - 1 - i - 0.5), 1, 1, color='black'))

    def update(self):
        if self.autobot1.path is not None :
            self.a1_circle.center = (self.autobot1.position[1], self.grid.shape[0] - 1 - self.autobot1.position[0])
            self.ax.text(self.autobot1.position[1], self.grid.shape[0]-1-self.autobot1.position[0], 'A1', ha='center', va='center', color='white', fontsize=12)
        if self.autobot2.path is not None:
            self.a2_circle.center = (self.autobot2.position[1], self.grid.shape[0] - 1 - self.autobot2.position[0])
            self.ax.text(self.autobot2.position[1], self.grid.shape[0]-1-self.autobot2.position[0], 'A2', ha='center', va='center', color='white', fontsize=12)
        plt.draw()

    def start_simulation(self):
        plt.show()

    def next_step(self):
        if self.autobot1.path is not None:
            self.autobot1.move()
        if self.autobot2.path is not None:
            self.autobot2.move()
        print(f"A1 time: {self.autobot1.time}, waiting time: {self.autobot1.waiting_time}, moves:  {self.autobot1.time}")
        print(f"A2 time: {self.autobot2.time}, waiting time: {self.autobot2.waiting_time}, moves: {self.autobot2.time}")
        self.update()

class GridCreator(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Grid Creator")
        self.geometry("400x400")

        self.grid_size = simpledialog.askinteger("Input", "Enter grid size (e.g., 4 for 4x4):", minvalue=2)
        self.grid = np.zeros((self.grid_size, self.grid_size), dtype=object)
        self.start_a1 = None
        self.start_a2 = None
        self.goal_a1 = None
        self.goal_a2 = None

        self.canvas = Canvas(self, width=300, height=300)
        self.canvas.pack()

        self.draw_grid()

        self.canvas.bind("<Button-1>", self.add_obstacle)
        self.canvas.bind("<Button-3>", self.set_start_and_goal)

        self.start_button = tk.Button(self, text="Start Simulation", command=self.start_simulation, state=tk.DISABLED)
        self.start_button.pack(side=tk.LEFT)

    def draw_grid(self):
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                x0 = j * 30
                y0 = i * 30
                x1 = x0 + 30
                y1 = y0 + 30
                self.canvas.create_rectangle(x0, y0, x1, y1, outline="gray")

    def add_obstacle(self, event):
        row = event.y // 30
        col = event.x // 30
        if self.grid[row, col] == 0:
            self.grid[row, col] = 1
            self.canvas.create_rectangle(col * 30, row * 30, (col + 1) * 30, (row + 1) * 30, fill="black")

    def set_start_and_goal(self, event):
        row = event.y // 30
        col = event.x // 30

        if self.start_a1 is None:
            self.start_a1 = (row, col)
            self.canvas.create_oval(col * 30, row * 30, (col + 1) * 30, (row + 1) * 30, fill="blue")
        elif self.start_a2 is None:
            self.start_a2 = (row, col)
            self.canvas.create_oval(col * 30, row * 30, (col + 1) * 30, (row + 1) * 30, fill="blue")
        elif self.goal_a1 is None:
            self.goal_a1 = (row, col)
            self.canvas.create_oval(col * 30, row * 30, (col + 1) * 30, (row + 1) * 30, fill="yellow")
        elif self.goal_a2 is None:
            self.goal_a2 = (row, col)
            self.canvas.create_oval(col * 30, row * 30, (col + 1) * 30, (row + 1) * 30, fill="yellow")

        if self.start_a1 and self.start_a2 and self.goal_a1 and self.goal_a2:
            self.start_button.config(state=tk.NORMAL)

    def start_simulation(self):
        self.destroy()
        simulation = AutoBotSimulation(self.grid, self.start_a1, self.start_a2, self.goal_a1, self.goal_a2)
        simulation.start_simulation()

if __name__ == "__main__":
    app = GridCreator()
    app .mainloop()