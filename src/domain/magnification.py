import math

def calculate_scale(distance: float, max_scale: float = 1.5, sigma: float = 100.0, radius: float = 100.0) -> float:
    """
    Calculate the scale factor for a dock item based on its distance from the cursor.
    Uses a Gaussian function: scale(d) = 1 + (max_scale - 1) * exp(-(d^2) / (2 * sigma^2))
    """
    effective_sigma = sigma if sigma != 100.0 or radius == 100.0 else radius
    if max_scale <= 1.0 or effective_sigma <= 0.0:
        return 1.0
    val = 1.0 + (max_scale - 1.0) * math.exp(-(float(distance) ** 2) / (2.0 * float(effective_sigma) ** 2))
    return val

def exponential_easing(current: float, target: float, factor: float = 0.25) -> float:
    """
    Calculate exponential easing towards a target value.
    current += (target - current) * factor
    """
    return current + (target - current) * factor

compute_scale = calculate_scale
ease_toward = exponential_easing

