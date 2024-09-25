import tkinter as tk
from tkinter import ttk

class GartenPlaner:
    def __init__(self, root):
        self.root = root
        self.root.title("Gartenplaner")
        
        # Hauptframe
        self.main_frame = ttk.Frame(root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Canvas zum Zeichnen
        self.canvas = tk.Canvas(self.main_frame, bg="white")
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Rechte Seitenleiste
        self.sidebar = ttk.Frame(self.main_frame, width=200)
        self.sidebar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Formen auswählen
        ttk.Label(self.sidebar, text="Form auswählen:").pack(pady=10)
        self.form_var = tk.StringVar(value="Rechteck")
        for form in ["Rechteck", "Quadrat", "Kreis"]:
            ttk.Radiobutton(self.sidebar, text=form, variable=self.form_var, value=form).pack(anchor=tk.W)
        
        # Bindings für das Zeichnen
        self.canvas.bind("<ButtonPress-1>", self.on_button_press)
        self.canvas.bind("<B1-Motion>", self.on_move_press)
        self.canvas.bind("<ButtonRelease-1>", self.on_button_release)
        
        self.start_x = None
        self.start_y = None
        self.current_shape = None

    def on_button_press(self, event):
        self.start_x = event.x
        self.start_y = event.y
        form = self.form_var.get()
        if form == "Rechteck":
            self.current_shape = self.canvas.create_rectangle(event.x, event.y, event.x, event.y, outline="black")
        elif form == "Quadrat":
            self.current_shape = self.canvas.create_rectangle(event.x, event.y, event.x, event.y, outline="black")
        elif form == "Kreis":
            self.current_shape = self.canvas.create_oval(event.x, event.y, event.x, event.y, outline="black")

    def on_move_press(self, event):
        cur_x, cur_y = event.x, event.y
        if self.current_shape:
            if self.form_var.get() == "Quadrat":
                side = max(abs(cur_x - self.start_x), abs(cur_y - self.start_y))
                cur_x = self.start_x + side if cur_x >= self.start_x else self.start_x - side
                cur_y = self.start_y + side if cur_y >= self.start_y else self.start_y - side
            self.canvas.coords(self.current_shape, self.start_x, self.start_y, cur_x, cur_y)

    def on_button_release(self, event):
        self.current_shape = None

if __name__ == "__main__":
    root = tk.Tk()
    app = GartenPlaner(root)
    root.mainloop()
