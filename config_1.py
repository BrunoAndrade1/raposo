# config.py
import matplotlib.pyplot as plt

# --- Configurações do Mapa ---
MAP_ZOOM = 12

# Configurações para o HeatMap de motocicletas
MOTOCYCLIST_HEATMAP_CONFIG = {
    "radius": 15,
    "blur": 20,
    "min_opacity": 0.5,
    "max_zoom": 15
}

# Configurações para o HeatMap geral
GENERAL_HEATMAP_CONFIG = {
    "radius": 10,
    "blur": 15,
}

# --- Configurações dos Gráficos ---
FIGURE_SIZE_BAR_CHART = (12, 5)
BAR_COLOR = "royalblue"
