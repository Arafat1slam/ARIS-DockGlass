from typing import List, Tuple

def compute_positions(scaled_widths: List[float], spacing: float, position_mode: str, screen_width: float) -> Tuple[List[float], float]:
    """
    Compute the x-coordinates for each item in the dock based on their scaled widths.
    
    :param scaled_widths: A list of widths for each item after applying magnification.
    :param spacing: Gap between items in pixels.
    :param position_mode: 'BOTTOM_CENTER', 'BOTTOM_LEFT', or 'BOTTOM_RIGHT'.
    :param screen_width: Width of the available screen space.
    :return: A tuple containing:
             - A list of center x-coordinates for each item (relative to screen).
             - The total width of the dock (sum of scaled widths + spacing).
    """
    if not scaled_widths:
        return [], 0.0
        
    total_width = sum(scaled_widths) + (len(scaled_widths) - 1) * spacing
    
    if position_mode == 'BOTTOM_LEFT':
        start_x = 0.0
    elif position_mode == 'BOTTOM_RIGHT':
        start_x = screen_width - total_width
    else:  # BOTTOM_CENTER
        start_x = (screen_width - total_width) / 2.0

    positions = []
    current_x = start_x
    for width in scaled_widths:
        center_x = current_x + width / 2.0
        positions.append(center_x)
        current_x += width + spacing

    return positions, total_width
