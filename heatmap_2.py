import re
import tkinter as tk
from tkinter import filedialog, simpledialog
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

        button_frame = tk.Frame(self)
        button_frame.pack(pady=10)

        self.open_button = tk.Button(button_frame, text="Open File", command=self.load_file)
        self.open_button.grid(row=0, column=0, padx=5)

        self.change_elevation_button = tk.Button(button_frame, text="Change Elevation", command=self.change_elevation)
        self.change_elevation_button.grid(row=0, column=1, padx=5)

        self.log_scale_var = tk.BooleanVar()
        self.log_scale_checkbox = tk.Checkbutton(button_frame, text="Logarithmic Scale", variable=self.log_scale_var, command=self.toggle_log_scale)
        self.log_scale_checkbox.grid(row=0, column=6, padx=5)

        self.heatmap_button = tk.Button(button_frame, text="Heatmap", command=self.update_heatmap)
        self.heatmap_button.grid(row=0, column=3, padx=5, pady=5)

        self.spectrogram_button = tk.Button(button_frame, text="Spectrogram", command=self.display_spectrogram)
        self.spectrogram_button.grid(row=0, column=4, padx=5, pady=5)

        self.empty_button1 = tk.Button(button_frame, text="Button 1")
        self.empty_button1.grid(row=0, column=5, padx=5, pady=5)

        self.empty_button2 = tk.Button(button_frame, text="Button 2")
        self.empty_button2.grid(row=0, column=7, padx=5, pady=5)

        self.empty_button3 = tk.Button(button_frame, text="Button 3")
        self.empty_button3.grid(row=0, column=8, padx=5, pady=5)

        self.empty_button4 = tk.Button(button_frame, text="Button 4")
        self.empty_button4.grid(row=0, column=9, padx=5, pady=5)

        # Kontener na wykres
        self.canvas_frame = tk.Frame(self)
        self.canvas_frame.pack(fill=tk.BOTH, expand=True)

    def load_file(self):
        self.file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.mat")])
        if self.file_path:
            try:
                self.elevations = self.read_elevations(self.file_path)
                self.selected_elevation = self.select_elevation(self.elevations)
                if self.selected_elevation is not None:
                    self.update_heatmap()
            except Exception as e:
                tk.messagebox.showerror("Error", f"An error occurred: {e}")

    def change_elevation(self):
        if hasattr(self, 'elevations'):
            self.selected_elevation = self.select_elevation(self.elevations)
            if self.selected_elevation is not None:
                self.update_heatmap()

    def update_heatmap(self):
        p = subprocess.Popen(["C:\\Users\\pauli\\OneDrive\\Pulpit\\Studia\\Semestr 5\\PROJEKT GRUPOWY\\Projekt-grupowy\\t1.exe", self.file_path, str(self.selected_elevation)])
        p.wait()
        grid, extent, deadzone_dis = self.process_file("dane.txt")
        self.display_heatmap(grid, extent, deadzone_dis)

    def read_elevations(self, file_path):
        elevations = []
        with open(file_path, 'rt') as plik:
            for line in plik:
                if "# name: elevationRaster" in line:
                    # Skip the next three lines starting with #
                    for _ in range(3):
                        plik.readline()
                    # Read the numbers
                    line = plik.readline().strip()
                    elevations.extend(map(int, line.split()))
        return elevations


    def select_elevation(self, elevations):
        if not elevations:
            tk.messagebox.showerror("Error", "No elevations found in the file.")
            return None

        elevation_var = tk.StringVar(self)
        elevation_var.set(elevations[0])  # Set the default value to the first elevation

        elevation_window = tk.Toplevel(self)
        elevation_window.title("Select Elevation")

        tk.Label(elevation_window, text="Select the desired elevation:").pack(pady=10)
        elevation_menu = tk.OptionMenu(elevation_window, elevation_var, *elevations)
        elevation_menu.pack(pady=10)

        def on_select():
            elevation_window.destroy()

        select_button = tk.Button(elevation_window, text="Select", command=on_select)
        select_button.pack(pady=10)

        self.wait_window(elevation_window)

        try:
            selected_elevation = int(elevation_var.get())
            return selected_elevation
        except ValueError:
            tk.messagebox.showerror("Error", "Invalid elevation selected.")
            return None

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

    def display_heatmap(self, grid=None, extent=None, deadzone_dis=None):
        if grid is None or extent is None or deadzone_dis is None:
            return

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
        c = ax.pcolormesh(theta_grid, radii_grid, grid, cmap=custom_cmap, shading='auto', norm=norm)
        fig.colorbar(c, label='Value')
        ax.set_title('Heatmap')

        # Dodanie wykresu do Tkinter
        canvas = FigureCanvasTkAgg(fig, self.canvas_frame)
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.pack(fill=tk.BOTH, expand=True)
        canvas.draw()

    def display_spectrogram(self):
        # Placeholder function for displaying spectrogram
        pass

    def toggle_log_scale(self):
        # Placeholder function for toggling logarithmic scale
        pass

# Uruchomienie aplikacji
if __name__ == "__main__":
    app = HeatmapApp()
    app.mainloop()