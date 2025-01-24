import re
import tkinter as tk
from tkinter import filedialog
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.colors import Normalize
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import subprocess
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
        file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.mat")])
        p = subprocess.Popen(["t1.exe", file_path])
        p.wait()
        if file_path:
            try:
                # Wczytaj dane i stwórz heatmapę
                grid, extent, deadzone_dis = self.process_file("dane.txt")
                self.display_heatmap(grid, extent, deadzone_dis)
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
            deadzone_dis = 0
            value = []

            for i in range(6):
                line = plik.readline()
                print(line)
                elements = re.split(r"[\s]+", line)
                if l == 6:
                    step = int(elements[1])
                    radian = int(elements[2])
                if l == 2:
                    angle_start = int(elements[0])
                    angle = int(elements[1])
                    azimuth = int(elements[2])
                if l == 4:
                    deadzone_dis = int(elements[0])
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

        extent = (angle_start, angle_start + azimuth * angle, deadzone_dis, radian * distance)
        return grid, extent, deadzone_dis

    def display_heatmap(self, grid, extent, deadzone_dis):
        # Usuń poprzedni wykres, jeśli istnieje
        for widget in self.canvas_frame.winfo_children():
            widget.destroy()

        # Tworzenie danych dla siatki polarnej
        radian, azimuth = grid.shape
        theta = np.linspace(np.radians(extent[0]), np.radians(extent[1]), azimuth + 1)
        radii = np.linspace(extent[2], extent[3], radian + 1)
        theta_grid, radii_grid = np.meshgrid(theta, radii)
        # Tworzenie wykresu
        fig, ax = plt.subplots(subplot_kw={'projection': 'polar'})
        custom_cmap = LinearSegmentedColormap.from_list("custom", ["#0000FF", "#00FF00", "#FFFF00", "#FF0000"])
        norm = Normalize(vmin=0, vmax=3)
        c = ax.pcolormesh(theta_grid, radii_grid, grid, cmap=custom_cmap, shading='auto', norm = norm)
        fig.colorbar(c, label='Value')
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
