import tkinter as tk
from tkinter import ttk  # Needed for separators

import numpy as np


# Global parameters
w = 20
running = False
step_count = 0
speed_ms = 80
bool_array = np.zeros((w, w))




def update_cell(i, j):
    global w
    global bool_array
    
    state = bool_array[i][j]

    left_coord =  (j-1) if j != 0     else (w-1)
    right_coord = (j+1) if j != (w-1) else 0
    up_coord =    (i-1) if i != 0     else (w-1)
    down_coord =  (i+1) if i != (w-1) else 0
        
    # if not in boundary case:
    neighbours = [bool_array[up_coord, left_coord], bool_array[up_coord, j], bool_array[up_coord, right_coord],
                  bool_array[i, left_coord], bool_array[i, right_coord],
                  bool_array[down_coord, left_coord], bool_array[down_coord, j], bool_array[down_coord, right_coord]]

    total = sum(neighbours)

    # game of life rules
    new_state = state
    if state:
        if total < 2 or total > 3:
            new_state = False
    elif total == 3:
        new_state = True
    return new_state

#========================================================================================
# UI
#========================================================================================

root = tk.Tk()
root.title("Game of life")
root.geometry("600x600")



main_frame = tk.Frame(root)
main_frame.pack(fill="both", expand=True)

canvas = tk.Canvas(main_frame, bg = "gray")
canvas.pack(side = "left", fill = "both", expand = True)


control_frame = tk.Frame(main_frame)
control_frame.pack(side = "right", fill = "y", padx = 10, pady = 10)






def update_labels(nb_cells, nb_step):
    label_nb_cells.config(text = f"Current non-zero values:\n{nb_cells} ({round(nb_cells / (w * w) * 100, 2)}%)")
    label_step.config(text = f"Step: {nb_step}")

def on_canvas_click(event):
    global bool_array
    global step_count
    if running:
        return

    canvas_width = canvas.winfo_width()
    canvas_height = canvas.winfo_height()
    grid_size = min(canvas_width, canvas_height)
    cell_size = grid_size / w
    offset_x = (canvas_width - grid_size) / 2
    offset_y = (canvas_height - grid_size) / 2

    x = event.x - offset_x
    y = event.y - offset_y

    if 0 <= x < grid_size and 0 <= y < grid_size:
        col = int(x // cell_size)
        row = int(y // cell_size)

        # Invert the cell
        bool_array[row][col] = not bool_array[row][col]
        draw_grid()
        update_labels(bool_array.astype(int).sum(), step_count)





            


"""
0 -----> j
|
|
V
i
"""



def step():
    global PendingDeprecationWarning
    global bool_array
    global step_count
    
    grid_new = bool_array.copy()

    for i in range(w):
        for j in range(w):
            # for each cell
            grid_new[i][j] = update_cell(i, j)


    bool_array = grid_new.copy()


    step_count += 1

    draw_grid()
    update_labels(bool_array.astype(int).sum(), step_count)
    if running:
        root.after(speed_ms, step)



#========================================================================================
# Commands
#========================================================================================

def reset():
    global w
    global bool_array
    global running
    global step_count
    if running:
        start_stop()
    w = int(entry.get())
    bool_array = np.zeros((w,w))
    step_count = 0
    draw_grid()
    update_labels(bool_array.astype(int).sum(), 0)

def randomize():
    global w
    global bool_array
    global step_count
    bool_array = np.random.choice([True, False], size=(w,w))
    step_count = 0
    draw_grid()
    update_labels(bool_array.astype(int).sum(), 0)

def start_stop():
    global running
    running = not running
    if running:
        canvas.config(bg="darkred")
        step()
    else:
        canvas.config(bg="gray")

def one_step():
    global running
    if running:
        return
    step()


def draw_grid(event = None):
    canvas.delete("all")
    canvas_width = canvas.winfo_width()
    canvas_height = canvas.winfo_height()
    
    grid_size = min(canvas_width, canvas_height)
    cell_size = grid_size / (w)

    offset_x = (canvas_width - grid_size) / 2
    offset_y = (canvas_height - grid_size) / 2

    for i in range(w):
        for j in range(w):
            x1 = offset_x + j * cell_size
            y1 = offset_y + i * cell_size
            color = "black" if bool_array[i][j] else "white"
            canvas.create_rectangle(x1, y1, x1 + cell_size, y1 + cell_size, fill = color, outline="lightgray")

canvas.bind("<Configure>", draw_grid)
canvas.bind("<Button-1>", on_canvas_click)



#========================================================================================
# Load and save grids
#========================================================================================

from tkinter import filedialog, messagebox
def save_bool_array_to_file(filename="grid_save.txt"):
    global bool_array
    # Open save file dialog
    filepath = filedialog.asksaveasfilename(
        defaultextension=".txt",
        filetypes=[("Text files", "*.txt")],
        title="Save grid state as...",
        parent = root
    )

    if not filepath:
        return  # User cancelled

    with open(filepath, "w") as f:
        f.write(f"{w}\n")
        flat = bool_array.astype(int).flatten()
        f.write("".join(map(str, flat)))

def load_bool_array_from_file():
    global bool_array

    filepath = filedialog.askopenfilename(
        filetypes=[("Text files", "*.txt")],
        title="Open saved grid",
        parent = root
    )

    if not filepath:
        return  # User cancelled

    try:
        with open(filepath, "r") as f:
            # Read size from first line
            loaded_w = int(f.readline().strip())

            # Validate size
            if loaded_w != w:
                messagebox.showerror("Size mismatch", f"Loaded size ({loaded_w}) does not match current grid size ({w}).", parent = root)
                return

            # Read flat string of 0s and 1s
            data = f.read().strip()

            if len(data) != w * w:
                messagebox.showerror("Data error", f"Expected {w * w} values, got {len(data)}.", parent = root)
                return

            # Convert to 2D boolean array
            flat = np.array([int(char) for char in data], dtype=bool)
            bool_array = flat.reshape((w, w))

            draw_grid()
            update_labels(bool_array.astype(int).sum(), 0)

    except Exception as e:
        messagebox.showerror("File error", f"Failed to load file:\n{e}")


#========================================================================================
# UI
#========================================================================================

# === File Section ===
file_frame = tk.Frame(control_frame)
file_frame.pack(fill="x", pady=5)

tk.Button(file_frame, text="Load", command=load_bool_array_from_file).pack(fill="x", pady=2)
tk.Button(file_frame, text="Save", command=save_bool_array_to_file).pack(fill="x", pady=2)
tk.Button(file_frame, text="Random", command=randomize).pack(fill="x", pady=2)
tk.Button(file_frame, text="Reset", command=reset).pack(fill="x", pady=2)

entry = tk.Entry(file_frame, width=4, justify="center")
entry.insert(0, str(w))
entry.pack(pady=2)


ttk.Separator(control_frame, orient="horizontal").pack(fill="x", pady=5)
# === Simulation Section ===

sim_frame = tk.Frame(control_frame)
sim_frame.pack(fill="x", pady=5)

label_nb_cells = tk.Label(sim_frame, text="Current non-zero values: \n0", font=("Arial", 10))
label_nb_cells.pack(pady=2)

label_step = tk.Label(sim_frame, text="Steps: 0", font=("Arial", 10))
label_step.pack(pady=2)



tk.Button(sim_frame, text="Start/stop", command=start_stop).pack(fill="x", pady=2)
tk.Button(sim_frame, text="1Step", command=step).pack(fill="x", pady=2)






root.lift()
#root.attributes("-topmost", True)
root.after_idle(root.attributes, "-topmost", True)

root.mainloop()
