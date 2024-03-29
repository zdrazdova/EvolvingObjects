from math import pi
from typing import List, Tuple

from sympy import Rational, sin, cos, Plane
from sympy.geometry import Ray, Point, Segment

from auxiliary import print_ray, print_point_3d
from component import Component
from custom_ray import MyRay
from custom_ray_3d import MyRay3D, print_ray_3d


def compute_intersections_3d(rays: List[MyRay3D], road: Plane) -> List[Tuple[Rational, float]]:
    """
    Compute intersections of rays from LED and road below the lamp. Zip x coordinates of each intersection
    with intensity of the ray. If cosine_error has value "Yes" multiply intensity by reduction caused by the angle
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
            #print_point_3d(inter_point[0])
            intensity = ray.intensity
            inter_array.append((inter_point[0].x, inter_point[0].y, intensity))
            ray.road_intersection = (inter_point[0].x, inter_point[0].y, inter_point[0].z)
    return inter_array


def compute_reflections_multiple_planes(ind: Component):
    no_of_reflections = 0
    plane = ind.reflective_segments[0]
    for ray in ind.original_rays:
        intersection = plane.intersection(ray.ray)
        if intersection:
            print_point_3d(intersection[0])
            reflection = compute_reflection_plane(plane, ray.ray)
            print_ray_3d(reflection)
            ray.ray_array = [Ray(ray.ray.p1, intersection[0]), reflection]


def compute_reflection_plane(plane: Plane, ray: Ray) -> Ray:
    all_intersections = ray.intersection(plane)
    if len(all_intersections) != 1:
        return None
    intersection = all_intersections[0]
    orig_point = ray.p1
    parallel = plane.parallel_plane(orig_point)
    perpendicular = plane.perpendicular_line(intersection)
    meet_point = parallel.intersection(perpendicular)[0]
    x_diff = (meet_point.x - orig_point.x)
    y_diff = (meet_point.y - orig_point.y)
    new_point = Point(meet_point.x + x_diff, meet_point.y + y_diff)
    new_point = Point(orig_point.x, intersection.y + (intersection.y -orig_point.y), intersection.z + (intersection.z - orig_point.z))
    reflected_ray = Ray(intersection, new_point)
    return reflected_ray


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


def compute_reflection_segment(ray_array, segment, previous_intersection, ray_intensity, r_factor):
    """
    Compute reflection of last part of the ray from given segment. If there is an intersection of ray and segment,
    compute reflected ray, update ray intensity, update ray array. If there is not, return False and original values.

    :param ray_array: array representing parts of ray
    :param segment: segment that the ray should reflect from
    :param previous_intersection: previous intersection of given ray on this segment
    :param ray_intensity: intensity of ray before reflection
    :param r_factor: reflective factor
    :return: True/False whether the ray was reflected, possibly updated ray array, previous intersection and intensity
    """
    last_ray = ray_array[-1]
    intersection = last_ray.intersection(segment)
    if intersection and intersection[0] != previous_intersection:
        reflected_ray, ray_intensity = compute_reflection(last_ray, segment, ray_intensity, r_factor)
        new_ray_array = ray_array[:-1]
        new_ray_array.append(Ray(last_ray.p1, intersection[0]))
        new_ray_array.append(reflected_ray)
        ray_array = new_ray_array
        return True, ray_array, intersection[0], ray_intensity
    return False, ray_array, previous_intersection, ray_intensity


def compute_reflection_segment_simple(ray_array, segment):
    """
    Compute reflection of last part of the ray from given segment. If there is an intersection of ray and segment,
    compute reflected ray, update ray intensity, update ray array. If there is not, return False and original values.

    :param ray_array: array representing parts of ray
    :param segment: segment that the ray should reflect from
    :param previous_intersection: previous intersection of given ray on this segment
    :param ray_intensity: intensity of ray before reflection
    :param r_factor: reflective factor
    :return: True/False whether the ray was reflected, possibly updated ray array, previous intersection and intensity
    """
    last_ray = ray_array[-1]
    intersection = segment.intersection(last_ray)
    if intersection:
        reflected_ray, ray_intensity = compute_reflection(last_ray, segment, 1, 1)
        new_ray_array = ray_array[:-1]
        new_ray_array.append(Ray(last_ray.p1, intersection[0]))
        new_ray_array.append(reflected_ray)
        ray_array = new_ray_array
    return ray_array


def compute_reflection_multiple_segments(ind: Component):
    no_of_reflection = 0
    for ray in ind.original_rays:
        ray.ray_array = [ray.ray]
        last_reflection = ind.base
        reflection_exists = True
        while reflection_exists:
            segment = closest_segment(ind.reflective_segments+[ind.base], ray.ray_array[-1], last_reflection)
            if len(segment) == 1:
                ray.ray_array = compute_reflection_segment_simple(ray.ray_array, segment[0])
                last_reflection = segment[0]
                no_of_reflection += 1
            else:
                reflection_exists = False
    ind.no_of_reflections = no_of_reflection



def compute_reflections_two_segments(ind: Component, r_factor: float):
    """

    :param ind:
    :param r_factor:
    :return:
    """
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
            continue_left, ray.ray_array, previous_i_r, ray_intensity = \
                compute_reflection_segment(ray.ray_array, ind.right_segment, previous_i_r, ray_intensity, r_factor)
            if continue_left:
                no_of_reflections += 1
            continue_right, ray.ray_array, previous_i_l, ray_intensity = \
                compute_reflection_segment(ray.ray_array, ind.left_segment, previous_i_l, ray_intensity, r_factor)
            if continue_right:
                no_of_reflections += 1
    ind.no_of_reflections = no_of_reflections


def compute_reflections_two_segments_unused(ind: Component, r_factor: float):
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


def closest_segment(segments: List[Segment], ray: Ray, last_reflection: Segment):
    intersection_dict = {}
    for segment in segments:
        intersection = ray.intersection(segment)
        #print(segment, last_reflection)
        if intersection and segment != last_reflection:
            ray_segment = Segment(ray.p1, intersection[0])
            length = ray_segment.length
            intersection_dict.setdefault(segment, length)
    if intersection_dict == {}:
        return []
    min_value = min(intersection_dict.values())
    segment = [key for key in intersection_dict if intersection_dict[key] == min_value]
    return segment


def rotate_segment(segment: Segment, angle: int) -> Segment:
    a = [segment.p1.x, segment.p1.y]
    b = [segment.p2.x, segment.p2.y]

    angle = angle * pi / 180

    midpoint = [(a[0] + b[0])/2, (a[1] + b[1])/2]
    a_mid = [a[0] - midpoint[0], a[1] - midpoint[1]]
    b_mid = [b[0] - midpoint[0], b[1] - midpoint[1]]

    a_rotated = [
        cos(angle) * a_mid[0] - sin(angle) * a_mid[1],
        sin(angle) * a_mid[0] + cos(angle) * a_mid[1]
    ]
    b_rotated = [
        cos(angle) * b_mid[0] - sin(angle) * b_mid[1],
        sin(angle) * b_mid[0] + cos(angle) * b_mid[1]
    ]

    a_rotated[0] = (a_rotated[0] + midpoint[0])
    a_rotated[1] = (a_rotated[1] + midpoint[1])
    b_rotated[0] = (b_rotated[0] + midpoint[0])
    b_rotated[1] = (b_rotated[1] + midpoint[1])

    rotated_segment = Segment(Point(int(a_rotated[0]), int(a_rotated[1])), Point(int(b_rotated[0]), int(b_rotated[1])))

    return rotated_segment


def change_size_segment(segment: Segment, coefficient: float) -> Segment:
    a = [segment.p1.x, segment.p1.y]
    b = [segment.p2.x, segment.p2.y]

    midpoint = [(a[0] + b[0])/2, (a[1] + b[1])/2]
    x_diff_half = (b[0] - a[0]) / 2
    y_diff_half = (b[1] - a[1]) / 2

    a_changed = [midpoint[0] - coefficient * x_diff_half, midpoint[1] - coefficient * y_diff_half]
    b_changed = [midpoint[0] + coefficient * x_diff_half, midpoint[1] + coefficient * y_diff_half]

    changed_segment = Segment(Point(int(a_changed[0]), int(a_changed[1])), Point(int(b_changed[0]), int(b_changed[1])))

    return changed_segment
