from typing import List, Tuple

from sympy import Rational, sin
from sympy.geometry import Ray, Point, Segment

from custom_ray import MyRay


def compute_reflection(ray: Ray, surface: Segment) -> Ray:
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
    return reflected_ray


# computes intersections of rays from LED and road below the lamp
def compute_intersections(rays: List[MyRay], road: Segment, cosine_error: str) -> List[Tuple[Rational, float]]:
    inter_array = []
    for ray in rays:
        inter_point = road.intersection(ray.ray_array[-1])
        if inter_point:
            intensity = ray.intensity
            if cosine_error == "Yes":
                reduction = float(sin(ray.ray_array[-1].angle_between(road)))
                intensity = ray.intensity*reduction
                #print(ray.intensity, reduction, ray.intensity*reduction)
            inter_array.append((inter_point[0].x, intensity, ))
            ray.road_intersection = inter_point[0].x
    return inter_array


def compute_reflections_two_segments(ind):
    ind.compute_right_segment()
    ind.compute_left_segment()
    no_of_reflections = 0
    for ray in ind.original_rays:
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
                intersection = intersection_r[0]
                reflected_ray = compute_reflection(last_ray, ind.right_segment)
                no_of_reflections += 1
                new_ray_array = ray.ray_array[:-1]
                new_ray_array.append(Ray(last_ray.p1, intersection_r[0]))
                new_ray_array.append(reflected_ray)
                ray.ray_array = new_ray_array
                continue_left = True
            last_ray = ray.ray_array[-1]
            intersection_l = last_ray.intersection(ind.left_segment)
            if intersection_l and intersection_l[0] != previous_i_l:
                previous_i_l = intersection_l[0]
                intersection = intersection_l[0]
                reflected_ray = compute_reflection(last_ray, ind.left_segment)
                no_of_reflections += 1
                new_ray_array = ray.ray_array[:-1]
                new_ray_array.append(Ray(last_ray.p1, intersection_l[0]))
                new_ray_array.append(reflected_ray)
                ray.ray_array = new_ray_array
                continue_right = True
    ind.no_of_reflections = no_of_reflections


def prepare_intersections(points: List[Tuple[Rational, float]]) -> List[Tuple[float, float]]:
    return sorted([(float(x), y) for x, y in points])
