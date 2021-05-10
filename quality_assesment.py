from typing import List, Tuple

from sympy import Rational, Segment

from custom_ray import MyRay
from quality_precalculations import intensity_of_intersections, sum_intensity, rays_upwards, sum_original_intensity


def efficiency(all_rays: List[MyRay]) -> float:
    """
    Compute efficiency of component from the amount of rays intersecting the road and their intensity.

    :param all_rays: List of all rays from LED
    :return: fraction of intensity of rays on the road to the total intensity of all ray from LED
    """
    total_intensity = sum_original_intensity(all_rays)
    intensity_from_device = sum_intensity(all_rays)
    return intensity_from_device/total_intensity


def illuminance_uniformity(segments_intensity: List[float]) -> float:
    """
    Compute illuminance uniformity from intensity of incident rays on road segments

    :param segments_intensity: List of intensity of incident rays on segments of the road
    :return: ratio of minimal segment illuminance to average segment illuminance ~ illuminance uniformity
    """
    min_illuminance = min(segments_intensity)
    max_illuminance = max(segments_intensity)
    if max_illuminance == 0:
        return 0
    return min_illuminance/max_illuminance


def obtrusive_light_elimination(all_rays: List[MyRay], road_intersections: List[Tuple[Rational, float, float]],
                                number_of_led: int) -> float:
    intensity_on_road = intensity_of_intersections(road_intersections) / (sum_intensity(all_rays) * number_of_led)
    return intensity_on_road


def light_pollution(individual_rays: List[List[Segment]]) -> int:
    """
    Compute light pollution that is a result of using Component

    :param individual_rays:
    :return: The amount of rays that are misdirected
    """
    return rays_upwards([ray.ray_array for ray in individual_rays])
