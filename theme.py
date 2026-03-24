# theme.py — alias for utils.py (backward compatibility)
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from utils import apply_theme, theme_colors, plotly_layout, LIGHT_CSS, DARK_CSS, PLOTLY_COLORS_LIGHT, PLOTLY_COLORS_DARK
