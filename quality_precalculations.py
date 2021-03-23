from typing import List, Tuple

from sympy import Rational

from component import Component
from custom_geometry import prepare_intersections
from custom_ray import MyRay
from environment import Environment


def intensity_of_intersections(road_intersections: List[Tuple[Rational, float]]) -> float:
    return sum([y for x, y in road_intersections])


def sum_intensity(rays: List[MyRay]) -> float:
    return sum([ray.intensity for ray in rays])


def compute_road_segments(ind: Component, env: Environment):
    segments_size = env.road_length / env.road_sections
    segments_intensity = [0] * env.road_sections
    intersections = prepare_intersections(ind.intersections_on)
    right_border = env.road_start
    counter = 0
    for segment in range(env.road_sections):
        left_border = right_border
        right_border += segments_size
        stay = True
        while stay and counter < len(intersections):
            stay = False
            if left_border <= intersections[counter][0] < right_border:
                segments_intensity[segment] += intersections[counter][1]
                counter += 1
                stay = True
    ind.segments_intensity = segments_intensity
    segments_intensity_proportional = [0] * env.road_sections
    max_intensity = max(segments_intensity)
    for segment in range(env.road_sections):
        segments_intensity_proportional[segment] = segments_intensity[segment] / max_intensity
    ind.segments_intensity_proportional = segments_intensity_proportional
