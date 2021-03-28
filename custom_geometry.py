from typing import List, Tuple

from sympy import Rational, sin
from sympy.geometry import Ray, Point, Segment

from component import Component
from custom_ray import MyRay


def compute_intersections(rays: List[MyRay], road: Segment, cosine_error: str) -> List[Tuple[Rational, float]]:
    """
    Compute intersections of rays from LED and road below the lamp. Zip x coordinates of each intersection
    with intensity of the ray. If cosine_error has value "Yes" multiply intensity by redustion caused by the angle
    of incident ray and the road.

    :param rays: List of rays directed from LED
    :param road: Segment representing road that rays should fall on
    :param cosine_error: Yes/No indicator whether to work with cosine error or not
    :return: List of tuples (x-coord of road intersection, intensity of incident ray)
    """
    inter_array = []
    for ray in rays:
        inter_point = road.intersection(ray.ray_array[-1])
        if inter_point:
            intensity = ray.intensity
            if cosine_error == "Yes":
                reduction = float(sin(ray.ray_array[-1].angle_between(road)))
                intensity = ray.intensity*reduction
            inter_array.append((inter_point[0].x, intensity))
            ray.road_intersection = inter_point[0].x
    return inter_array


def compute_reflection(ray: Ray, surface: Segment, intensity: float, reflective_factor: float) -> (Ray, float):
    """
    Compute reflection of ray from given surface. Intensity of ray is multiplied by reflective factor of the surface.

    :param ray: Ray that should be reflected
    :param surface: Reflective surface segment
    :param intensity:
    :param reflective_factor:
    :return: Reflected ray
    """
    all_intersections = ray.intersection(surface)
    if len(all_intersections) != 1:
        return None
    intersection = all_intersections[0]
    orig_point = ray.p1
    parallel = surface.parallel_line(orig_point)
    perpendicular = surface.perpendicular_line(intersection)
    meet_point = parallel.intersection(perpendicular)[0]
    x_diff = (meet_point.x - orig_point.x)
    y_diff = (meet_point.y - orig_point.y)
    new_point = Point(meet_point.x + x_diff, meet_point.y + y_diff)
    reflected_ray = Ray(intersection, new_point)
    ray_intensity = intensity * reflective_factor
    return reflected_ray, ray_intensity


def compute_reflections_two_segments(ind: Component, r_factor: float):
    ind.compute_right_segment()
    ind.compute_left_segment()
    no_of_reflections = 0
    for ray in ind.original_rays:
        ray_intensity = ray.intensity
        continue_left = True
        continue_right = True
        previous_i_r = Point(0, 0)
        previous_i_l = Point(0, 0)
        ray.ray_array = [ray.ray]
        while continue_left or continue_right:
            continue_left = False
            continue_right = False
            last_ray = ray.ray_array[-1]
            intersection_r = last_ray.intersection(ind.right_segment)
            if intersection_r and intersection_r[0] != previous_i_r:
                previous_i_r = intersection_r[0]
                reflected_ray, ray_intensity = compute_reflection(last_ray, ind.right_segment, ray_intensity, r_factor)
                no_of_reflections += 1
                new_ray_array = ray.ray_array[:-1]
                new_ray_array.append(Ray(last_ray.p1, intersection_r[0]))
                new_ray_array.append(reflected_ray)
                ray.ray_array = new_ray_array
                ray.intensity = ray_intensity
                continue_left = True
            last_ray = ray.ray_array[-1]
            intersection_l = last_ray.intersection(ind.left_segment)
            if intersection_l and intersection_l[0] != previous_i_l:
                previous_i_l = intersection_l[0]
                reflected_ray, ray_intensity = compute_reflection(last_ray, ind.left_segment, ray_intensity, r_factor)
                no_of_reflections += 1
                new_ray_array = ray.ray_array[:-1]
                new_ray_array.append(Ray(last_ray.p1, intersection_l[0]))
                new_ray_array.append(reflected_ray)
                ray.ray_array = new_ray_array
                ray.intensity = ray_intensity
                continue_right = True
    ind.no_of_reflections = no_of_reflections


def prepare_intersections(points: List[Tuple[Rational, float]]) -> List[Tuple[float, float]]:
    """
    Prepare a list of tuples sorted according to first items which are also converted to float

    :param points: List of tuples (x-coord of road intersection, intensity of incident ray)
    :return: List of tuples (x-coord to float, intensity of incident ray) sorted according to first item
    """
    return sorted([(float(x), y) for x, y in points])
