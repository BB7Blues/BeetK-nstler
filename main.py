import tkinter as tk
from tkinter import ttk, messagebox

class BeetKünstlerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("BeetKünstler - Gartenplaner")
        
        # Standard-Gartengröße in Metern
        self.garden_width_m = 20  # z.B. 20 Meter
        self.garden_height_m = 15  # z.B. 15 Meter
        self.scale = 50  # Pixel pro Meter (anpassen nach Bedarf)
        
        self.grid_spacing_m = 1  # 1 Meter
        self.show_grid = tk.BooleanVar(value=False)
        
        # Hauptlayout erstellen
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Canvas für das Zeichnen (Größe basierend auf Gartenmaße und Skalierung)
        self.canvas_width = int(self.garden_width_m * self.scale)
        self.canvas_height = int(self.garden_height_m * self.scale)
        self.canvas = tk.Canvas(self.main_frame, bg="white", width=self.canvas_width, height=self.canvas_height)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Seitenleiste für Formen und Einstellungen
        self.sidebar = ttk.Frame(self.main_frame, width=200)
        self.sidebar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Gartengröße einstellen (in Metern)
        ttk.Label(self.sidebar, text="Gartengröße festlegen (m):").pack(pady=10)
        size_frame = ttk.Frame(self.sidebar)
        size_frame.pack(pady=5, padx=10, fill=tk.X)
        
        ttk.Label(size_frame, text="Breite:").grid(row=0, column=0, sticky=tk.W)
        self.garden_width_var = tk.DoubleVar(value=self.garden_width_m)
        self.garden_width_entry = ttk.Entry(size_frame, textvariable=self.garden_width_var)
        self.garden_width_entry.grid(row=0, column=1, padx=5, pady=2)
        
        ttk.Label(size_frame, text="Höhe:").grid(row=1, column=0, sticky=tk.W)
        self.garden_height_var = tk.DoubleVar(value=self.garden_height_m)
        self.garden_height_entry = ttk.Entry(size_frame, textvariable=self.garden_height_var)
        self.garden_height_entry.grid(row=1, column=1, padx=5, pady=2)
        
        self.set_size_button = ttk.Button(self.sidebar, text="Größe setzen", command=self.set_garden_size)
        self.set_size_button.pack(pady=5, padx=10, fill=tk.X)
        
        # Gitternetz-Einstellungen
        ttk.Label(self.sidebar, text="Gitternetz-Einstellungen:").pack(pady=10)
        grid_frame = ttk.Frame(self.sidebar)
        grid_frame.pack(pady=5, padx=10, fill=tk.X)
        
        self.grid_spacing_var = tk.DoubleVar(value=self.grid_spacing_m)
        ttk.Label(grid_frame, text="Abstand (m):").grid(row=0, column=0, sticky=tk.W)
        self.grid_spacing_slider = ttk.Scale(
            grid_frame, from_=0.5, to=10, orient=tk.HORIZONTAL, variable=self.grid_spacing_var, command=self.update_grid
        )
        self.grid_spacing_slider.grid(row=0, column=1, padx=5, pady=2, sticky=tk.EW)
        
        self.grid_checkbox = ttk.Checkbutton(
            self.sidebar, text="Gitternetz anzeigen", variable=self.show_grid, command=self.toggle_grid
        )
        self.grid_checkbox.pack(pady=5, padx=10, anchor=tk.W)
        
        # Formen-Auswahl
        ttk.Label(self.sidebar, text="Form auswählen:").pack(pady=10)
        self.form_var = tk.StringVar(value="Rechteck")
        formen = ["Rechteck", "Kreis", "Dreieck", "Ring"]
        for form in formen:
            ttk.Radiobutton(self.sidebar, text=form, variable=self.form_var, value=form).pack(anchor=tk.W)
        
        # Option für Ring-Durchmesser
        self.inner_diameter_var = tk.DoubleVar(value=0.3)  # Standardwert für Ringbreite (30%)
        ttk.Label(self.sidebar, text="Ring-Durchmesser (%)").pack(pady=10)
        self.inner_diameter_slider = ttk.Scale(
            self.sidebar, from_=0.1, to=0.9, orient=tk.HORIZONTAL, variable=self.inner_diameter_var
        )
        self.inner_diameter_slider.pack(fill=tk.X, padx=10)
        
        # Variablen für das Zeichnen
        self.start_x = None
        self.start_y = None
        self.current_shape = None
        self.inner_shape = None  # Für Ringe
        self.text_items = []  # Für Beschriftungen
        
        # Mouse-Bindings für das Zeichnen
        self.canvas.bind("<ButtonPress-1>", self.on_button_press)
        self.canvas.bind("<B1-Motion>", self.on_move_press)
        self.canvas.bind("<ButtonRelease-1>", self.on_button_release)
        
        # Initiales Gitternetz zeichnen, falls aktiviert
        if self.show_grid.get():
            self.draw_grid()
    
    def set_garden_size(self):
        """Setzt die Größe des Gartens basierend auf den Benutzereingaben."""
        try:
            new_width_m = self.garden_width_var.get()
            new_height_m = self.garden_height_var.get()
            if new_width_m <= 0 or new_height_m <= 0:
                raise ValueError
            self.garden_width_m = new_width_m
            self.garden_height_m = new_height_m
            self.canvas_width = int(self.garden_width_m * self.scale)
            self.canvas_height = int(self.garden_height_m * self.scale)
            self.canvas.config(width=self.canvas_width, height=self.canvas_height)
            self.canvas.delete("all")  # Löscht alle gezeichneten Formen und Texte
            if self.show_grid.get():
                self.draw_grid()
            messagebox.showinfo("Erfolg", f"Gartenfläche auf {self.garden_width_m}m x {self.garden_height_m}m gesetzt.")
        except:
            messagebox.showerror("Fehler", "Bitte geben Sie gültige positive Zahlen für Breite und Höhe ein.")
    
    def draw_grid(self):
        """Zeichnet ein Gitternetz auf die Canvas."""
        self.canvas.delete("grid_line")  # Löscht alte Gitterlinien
        spacing_m = self.grid_spacing_var.get()
        spacing_px = spacing_m * self.scale
        # Vertikale Linien
        for x in range(0, self.canvas_width, int(spacing_px)):
            self.canvas.create_line(x, 0, x, self.canvas_height, fill="lightgray", tags="grid_line")
        # Horizontale Linien
        for y in range(0, self.canvas_height, int(spacing_px)):
            self.canvas.create_line(0, y, self.canvas_width, y, fill="lightgray", tags="grid_line")
    
    def toggle_grid(self):
        """Schaltet das Gitternetz ein oder aus."""
        if self.show_grid.get():
            self.draw_grid()
        else:
            self.canvas.delete("grid_line")
    
    def update_grid(self, event):
        """Aktualisiert das Gitternetz, wenn der Abstand geändert wird."""
        if self.show_grid.get():
            self.draw_grid()
    
    def on_button_press(self, event):
        """Startpunkt beim Klicken speichern."""
        self.start_x = event.x
        self.start_y = event.y
        form = self.form_var.get()
        
        # Form basierend auf Auswahl erstellen
        if form == "Rechteck":
            self.current_shape = self.canvas.create_rectangle(event.x, event.y, event.x, event.y, outline="black")
        elif form == "Kreis":
            self.current_shape = self.canvas.create_oval(event.x, event.y, event.x, event.y, outline="black")
        elif form == "Dreieck":
            # Wir zeichnen ein Dreieck mit drei Punkten
            self.current_shape = self.canvas.create_polygon(event.x, event.y, event.x, event.y, event.x, event.y, outline="black", fill="")
        elif form == "Ring":
            # Zeichne äußeren Kreis
            self.current_shape = self.canvas.create_oval(event.x, event.y, event.x, event.y, outline="black")
            # Zeichne inneren Kreis initial gleich, später wird er angepasst
            self.inner_shape = self.canvas.create_oval(event.x, event.y, event.x, event.y, outline="black")
    
    def on_move_press(self, event):
        """Form beim Bewegen der Maus aktualisieren."""
        cur_x, cur_y = event.x, event.y
        form = self.form_var.get()
        if self.current_shape:
            if form == "Dreieck":
                # Koordinaten für Dreieckspunkte anpassen
                mid_x = (self.start_x + cur_x) / 2
                self.canvas.coords(self.current_shape, self.start_x, cur_y, cur_x, cur_y, mid_x, self.start_y)
                # Berechne Seitenlängen und Fläche
                side1 = self.calculate_distance(self.start_x, self.start_y, self.start_x, cur_y) / self.scale
                side2 = self.calculate_distance(self.start_x, cur_y, cur_x, cur_y) / self.scale
                side3 = self.calculate_distance(cur_x, cur_y, mid_x, self.start_y) / self.scale
                # Fläche mit Heron's Formel
                s = (side1 + side2 + side3) / 2
                area = (s * (s - side1) * (s - side2) * (s - side3)) ** 0.5
                # Entferne alte Texte
                for text in self.text_items:
                    self.canvas.delete(text)
                self.text_items.clear()
                # Füge Texte hinzu
                self.text_items.append(self.canvas.create_text((self.start_x + cur_x) / 2, (self.start_y + cur_y) / 2, text=f"Fläche: {area:.2f} m²"))
                self.text_items.append(self.canvas.create_text((self.start_x + cur_x) / 2, cur_y + 10, text=f"Breite: {side2:.2f} m"))
                self.text_items.append(self.canvas.create_text(self.start_x - 30, (self.start_y + cur_y) / 2, text=f"Höhe: {side1:.2f} m", angle=90))
            elif form == "Ring":
                # Äußerer Kreis aktualisieren
                self.canvas.coords(self.current_shape, self.start_x, self.start_y, cur_x, cur_y)
                # Innerer Kreis basierend auf Slider-Wert aktualisieren
                inner_scale = self.inner_diameter_var.get()
                width = cur_x - self.start_x
                height = cur_y - self.start_y
                # Berechne die neuen Koordinaten für den inneren Kreis
                inner_offset_x = width * inner_scale
                inner_offset_y = height * inner_scale
                self.canvas.coords(
                    self.inner_shape,
                    self.start_x + inner_offset_x,
                    self.start_y + inner_offset_y,
                    cur_x - inner_offset_x,
                    cur_y - inner_offset_y
                )
                # Berechne Fläche (π*(R² - r²))
                radius_outer = ((width)**2 + (height)**2)**0.5 / 2 / self.scale
                radius_inner = radius_outer * inner_scale
                area = 3.1416 * (radius_outer**2 - radius_inner**2)
                # Entferne alte Texte
                for text in self.text_items:
                    self.canvas.delete(text)
                self.text_items.clear()
                # Füge Text hinzu
                self.text_items.append(self.canvas.create_text((self.start_x + cur_x) / 2, (self.start_y + cur_y) / 2, text=f"Fläche: {area:.2f} m²"))
            elif form in ["Rechteck", "Kreis"]:
                # Rechteck oder Kreis aktualisieren
                self.canvas.coords(self.current_shape, self.start_x, self.start_y, cur_x, cur_y)
                # Berechne Maße und Fläche
                if form == "Rechteck":
                    width_px = abs(cur_x - self.start_x)
                    height_px = abs(cur_y - self.start_y)
                    width_m = width_px / self.scale
                    height_m = height_px / self.scale
                    area = width_m * height_m
                    # Entferne alte Texte
                    for text in self.text_items:
                        self.canvas.delete(text)
                    self.text_items.clear()
                    # Füge Texte hinzu
                    self.text_items.append(self.canvas.create_text((self.start_x + cur_x) / 2, (self.start_y + cur_y) / 2, text=f"Fläche: {area:.2f} m²"))
                    self.text_items.append(self.canvas.create_text((self.start_x + cur_x) / 2, self.start_y - 10, text=f"Breite: {width_m:.2f} m"))
                    self.text_items.append(self.canvas.create_text(self.start_x - 30, (self.start_y + cur_y) / 2, text=f"Höhe: {height_m:.2f} m", angle=90))
                elif form == "Kreis":
                    # Berechne Radius und Fläche
                    radius_px = ((cur_x - self.start_x)**2 + (cur_y - self.start_y)**2)**0.5 / 2
                    radius_m = radius_px / self.scale
                    area = 3.1416 * radius_m**2
                    # Entferne alte Texte
                    for text in self.text_items:
                        self.canvas.delete(text)
                    self.text_items.clear()
                    # Füge Texte hinzu
                    self.text_items.append(self.canvas.create_text((self.start_x + cur_x) / 2, (self.start_y + cur_y) / 2, text=f"Fläche: {area:.2f} m²"))
                    self.text_items.append(self.canvas.create_text((self.start_x + cur_x) / 2, self.start_y - 10, text=f"Radius: {radius_m:.2f} m"))
            else:
                # Andere Formen (falls hinzugefügt)
                pass
    
    def calculate_distance(self, x1, y1, x2, y2):
        """Berechnet die Entfernung zwischen zwei Punkten."""
        return ((x2 - x1)**2 + (y2 - y1)**2)**0.5
    
    def on_button_release(self, event):
        """Form fertigstellen, wenn Maustaste losgelassen wird."""
        form = self.form_var.get()
        if form == "Ring":
            # Stelle sicher, dass der innere Kreis finalisiert ist
            # Bereits während des Draggings aktualisiert
            pass
        self.current_shape = None
        self.inner_shape = None  # Reset für den nächsten Ring
        # Entferne alte Texte (falls nötig)
        self.text_items = []

if __name__ == "__main__":
    root = tk.Tk()
    app = BeetKünstlerApp(root)
    root.mainloop()