import re
import tkinter as tk
from tkinter import filedialog
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.tri as tri

class HeatmapApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Heatmap Application")
        self.geometry("800x600")

        self.open_button = tk.Button(self, text="Open File", command=self.load_file)
        self.open_button.pack(pady=10)

        # Kontener na wykres
        self.canvas_frame = tk.Frame(self)
        self.canvas_frame.pack(fill=tk.BOTH, expand=True)

    def load_file(self):
        # Otwórz okno dialogowe, aby wybrać plik
        file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])

        if file_path:
            try:
                # Wczytaj dane i stwórz heatmapę
                grid, extent = self.process_file(file_path)
                self.display_heatmap(grid, extent)
            except Exception as e:
                tk.messagebox.showerror("Error", f"An error occurred: {e}")

    def process_file(self, file_path):
        with open(file_path, 'rt') as plik:
            l = 1
            azimuth = 0
            angle_start = 0
            angle = 0
            radian = 0
            distance = 0
            value = []

            for i in range(4):
                line = plik.readline()
                elements = re.split(r"[\s]+", line)
                if l == 2:
                    step = int(elements[1])
                    radian = int(elements[2])
                if l == 4:
                    angle_start = int(elements[0])
                    angle = int(elements[1])
                    azimuth = int(elements[2])
                if not line:
                    break
                l += 1

            for line in plik:
                line = line.strip()
                if line:
                    value.append(float(line))  # Konwersja wartości do float

        grid = np.zeros((radian, azimuth))  # Siatka na dane
        current_index = 0

        for r in range(radian):  # Iteracja po promieniu
            for a in range(azimuth):  # Iteracja po kącie
                if current_index < len(value):
                    grid[r, a] = value[current_index]
                    current_index += 1

        if radian * distance == 0:
            radian = max(radian, 1)
            distance = max(distance, 1)

        extent = (angle_start, angle_start + azimuth * angle, 0, radian * distance)
        return grid, extent

    def display_heatmap(self, grid, extent):
        # Usuń poprzedni wykres, jeśli istnieje
        for widget in self.canvas_frame.winfo_children():
            widget.destroy()

        # Tworzenie danych dla siatki polarnej
        radian, azimuth = grid.shape
        theta = np.linspace(np.radians(extent[0]), np.radians(extent[1]), azimuth)
        radii = np.linspace(0, extent[3], radian)

        # Siatka w układzie kartezjańskim
        theta_grid, radii_grid = np.meshgrid(theta, radii)
        x = radii_grid * np.cos(theta_grid)
        y = radii_grid * np.sin(theta_grid)

        # Dane wyflattenowane
        x_flat = x.flatten()
        y_flat = y.flatten()
        values_flat = grid.flatten()

        # Filtrowanie danych (usunięcie NaN)
        valid_mask = ~np.isnan(values_flat)
        x_filtered = x_flat[valid_mask]
        y_filtered = y_flat[valid_mask]
        values_filtered = values_flat[valid_mask]

        # Tworzenie triangulacji
        triang = tri.Triangulation(x_filtered, y_filtered)

        # Usuwanie trójkątów poza zasięgiem danych
        mask = np.any(np.sqrt(triang.x[triang.triangles]**2 + triang.y[triang.triangles]**2) > extent[3], axis=1)
        triang.set_mask(mask)

        # Tworzenie wykresu
        fig, ax = plt.subplots(subplot_kw={'projection': 'polar'})
        custom_cmap = LinearSegmentedColormap.from_list("custom", ["#0000FF", "#00FF00", "#FCFC00", "#FC0000"])

        # Tworzenie kolorowego wypełnienia trójkątów
        tpc = ax.tripcolor(triang, values_filtered, cmap=custom_cmap, shading='gouraud')
        fig.colorbar(tpc, label='Value')
        ax.set_title('Heatmap')

        # Dodanie wykresu do Tkinter
        canvas = FigureCanvasTkAgg(fig, self.canvas_frame)
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.pack(fill=tk.BOTH, expand=True)
        canvas.draw()



# Uruchomienie aplikacji
if __name__ == "__main__":
    app = HeatmapApp()
    app.mainloop()
