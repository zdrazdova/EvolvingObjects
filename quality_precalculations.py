from typing import List, Tuple

from sympy import Rational, Segment

from custom_geometry import prepare_intersections
from custom_ray import MyRay


def intensity_of_intersections(road_intersections: List[Tuple[Rational, float, float]]) -> float:
    """
    Compute sum of intensities of road intersections

    :param road_intersections: List of tuples (x-coord of road intersection, intensity of incident ray)
    :return: Sum of intensities of rays intersection the road
    """
    return sum([y for x, y, z in road_intersections])


def intensity_of_intersections_cos_error(road_intersections: List[Tuple[Rational, float, float]]) -> float:
    """
    Compute sum of intensities of road intersections

    :param road_intersections: List of tuples (x-coord of road intersection, intensity of incident ray)
    :return: Sum of intensities of rays intersection the road
    """
    return sum([z for x, y, z in road_intersections])


def sum_original_intensity(rays: List[MyRay]) -> float:
    """
    Compute sum of intensity of all rays form LED

    :param rays: All rays from LED
    :return: Sum of intensity of all rays form the LED
    """
    return sum([ray.original_intensity for ray in rays])


def sum_intensity(rays: List[MyRay]) -> float:
    """
    Compute sum of intensity of all rays form LED

    :param rays: All rays from LED
    :return: Sum of intensity of all rays form the LED
    """
    return sum([ray.intensity for ray in rays if not ray.terminated])


def compute_segments_intensity(road_intersections: List[Tuple[Rational, float, float]], road_sections: int,
                               road_start: int, road_length: int, cosine_error: str) -> List[float]:
    """
    Compute sum of intensity of incidents rays for each segment

    :param road_intersections: List of tuples (x-coord of road intersection, intensity of incident ray,
    intensity with cosine error)
    :param road_sections: Number of road sections
    :param road_start: X coordinate of start of the road
    :param road_length: Length of the road
    :cosine_error: yes/no indicator whether to work with cosine error
    :return: List of intensity of incident rays of each road segment
    """
    segments_size = road_length / road_sections
    segments_intensity = [0] * road_sections
    intersections = prepare_intersections(road_intersections)
    right_border = road_start
    counter = 0
    for segment in range(road_sections):
        left_border = right_border
        right_border += segments_size
        stay = True
        while stay and counter < len(intersections):
            stay = False
            if left_border <= intersections[counter][0] < right_border:
                if cosine_error == "no":
                    segments_intensity[segment] += intersections[counter][1]
                else:
                    segments_intensity[segment] += intersections[counter][2]
                counter += 1
                stay = True
    return segments_intensity


def compute_proportional_intensity(segments_intensity: List[float]) -> List[float]:
    """
    Compute list of intensities for all segments proportional to maximum segment intensity

    :param segments_intensity: List of intensity of rays intersecting the road segments
    :return: List of
    """
    road_sections = len(segments_intensity)
    segments_intensity_proportional = [0] * road_sections
    max_intensity = max(segments_intensity)
    if max_intensity == 0:
        return segments_intensity_proportional
    for segment in range(road_sections):
        segments_intensity_proportional[segment] = segments_intensity[segment] / max_intensity
    return segments_intensity_proportional


def rays_upwards(rays: List[List[Segment]]):
    upwards_rays_counter = 0
    for ray in rays:
        last_segment = ray[-1]
        start_y = last_segment.p1.y
        end_y = last_segment.p2.y
        if end_y > start_y:
            upwards_rays_counter += 1
    return upwards_rays_counter
