from typing import List, Tuple

from sympy import Rational, Segment

from component import Component
from custom_ray import MyRay
from quality_precalculations import intensity_of_intersections, sum_intensity, rays_upwards, sum_original_intensity, \
    intensity_of_obtrusive_light


def efficiency(all_rays: List[MyRay]) -> float:
    """
    Compute efficiency of component from the amount of rays intersecting the road and their intensity.

    :param road_intersections: List of tuples (x-coord of road intersection, intensity of incident ray)
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
    avg_illuminance = sum(segments_intensity)/len(segments_intensity)
    if avg_illuminance == 0:
        return 0
    return min_illuminance/avg_illuminance


def glare_reduction(individual: Component) -> int:
    """
    Compute glare reduction that is a result of using Component

    :param individual: Component that is being evaluated
    :return: Number of ray reflections on the component
    """
    return individual.no_of_reflections


def light_pollution(individual_rays: List[List[Segment]]) -> int:
    """
    Compute light pollution that is a result of using Component

    :param individual_rays:
    :return: The amount of rays that are misdirected
    """
    #return rays_upwards([ray.ray_array for ray in individual_rays])

def obtrusive_light(all_rays: List[MyRay]) -> float:
    return -intensity_of_obtrusive_light(all_rays)/sum_intensity(all_rays)
