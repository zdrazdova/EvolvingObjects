from typing import List, Tuple

from sympy import Rational

from component import Component
from custom_ray import MyRay
from quality_precalculations import intensity_of_intersections, sum_intensity


def efficiency(road_intersections: List[Tuple[Rational, float]], all_rays: List[MyRay]) -> float:
    intensity_on_road = intensity_of_intersections(road_intersections)
    total_intensity = sum_intensity(all_rays)
    return intensity_on_road


def illuminance_uniformity(individual: Component) -> float:
    min_illuminance = min(individual.segments_intensity)
    avg_illuminance = sum(individual.segments_intensity)/len(individual.segments_intensity)
    return min_illuminance/avg_illuminance


def glare_reduction(individual: Component) -> int:
    return individual.no_of_reflections


def light_pollution(individual: Component) -> int:
    rays_total = len(individual.original_rays)
    rays_on_road = len(individual.intersections_on)
    return rays_total - rays_on_road
