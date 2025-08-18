# Copyright 2025, Battelle Energy Alliance, LLC All Rights Reserved

import random
import colorsys


def generate_distinct_colors(n):
    """Generate n visually distinct RGB colors."""
    colors = []

    for i in range(n):
        hue = i / n  # Spread the hue values evenly
        saturation = 0.5 + random.random() * 0.5  # Random saturation between 0.5 and 1
        lightness = 0.4 + random.random() * 0.2  # Random lightness between 0.4 and 0.6

        rgb = colorsys.hls_to_rgb(hue, lightness, saturation)
        rgb = tuple(int(255 * x) for x in rgb)  # Convert to 0-255 range
        colors.append(rgb)

    random.shuffle(colors)  # Optional: shuffle the list to randomize the order
    return colors
