import math

def calculate_scale(distance: float, max_scale: float, sigma: float) -> float:
    """
    Calculate the scale factor for a dock item based on its distance from the cursor.
    Uses a Gaussian function: scale(d) = 1 + (max_scale - 1) * exp(-(d^2) / (2 * sigma^2))
    
    :param distance: Distance from cursor in pixels (or normalized units).
    :param max_scale: The maximum scale factor at distance 0 (must be >= 1.0).
    :param sigma: The standard deviation (falloff rate, must be > 0.0).
    :return: The computed scale factor.
    """
    if max_scale <= 1.0 or sigma <= 0.0:
        return 1.0
    return 1.0 + (max_scale - 1.0) * math.exp(-(distance ** 2) / (2.0 * sigma ** 2))

def exponential_easing(current: float, target: float, factor: float = 0.25) -> float:
    """
    Calculate exponential easing towards a target value.
    current += (target - current) * factor
    
    :param current: Current value.
    :param target: Target value.
    :param factor: The smoothing factor (0.0 to 1.0).
    :return: The new eased value.
    """
    return current + (target - current) * factor
