from math import pi
from typing import List, Tuple

from sympy import Rational, sin, cos
from sympy.geometry import Ray, Point, Segment

from component import Component
from custom_ray import MyRay


def compute_intersections(rays: List[MyRay], road: Segment) -> List[Tuple[Rational, float, float]]:
    """
    Compute intersections of rays from LED and road below the lamp. Zip x coordinates of each intersection
    with intensity of the ray and intensity with taking cosine error into account.

    :param rays: List of rays directed from LED
    :param road: Segment representing road that rays should fall on
    :return: List of tuples (x-coord of road intersection, intensity of incident ray, intensity with cosine error)
    """
    inter_array = []
    for ray in rays:
        ray.road_intersection = []
        inter_point = road.intersection(ray.ray_array[-1])
        if inter_point and not ray.terminated:
            intensity = ray.intensity
            reduction = float(sin(ray.ray_array[-1].angle_between(road)))
            cos_error_intensity = ray.intensity*reduction
            inter_array.append((inter_point[0].x, intensity, cos_error_intensity))
            ray.road_intersection = inter_point[0].x
    return inter_array


def recalculate_intersections(intersections: List[Tuple[Rational, float, float]], number_of_led: int,
                              separating_distance: int, modification: str, road_start: int, road_end: int) \
                            -> List[Tuple[Rational, float, float]]:
    """
    Recalculate intersections for situations with more than one LED. The function works either with mirror or
     shift modification.

    :param intersections: List of tuples (x-coord of road intersection, intensity, intensity with cosine error)
    :param number_of_led: Number of LED in the device
    :param separating_distance: Distance separating LEDs
    :param modification: Indicator whether the LEDs are mirrored or shifted only
    :param road_start: Coordinates for start of the road
    :param road_end: Coordinates for end of the road
    :return: List of tuples (x-coord of road intersection, intensity, intensity with cosine error) for all LEDs
    """
    recalculated = []
    if modification == "mirror":
        for i in intersections:
            recalculated.append(i)
            new_x = i[0] * -1 - separating_distance
            if road_start <= new_x <= road_end:
                new_intersection = (new_x, i[1], i[2])
                recalculated.append(new_intersection)
    else:
        for i in intersections:
            for led in range(number_of_led):
                new_x = i[0] + separating_distance * led
                if road_start <= new_x <= road_end:
                    new_intersection = (new_x, i[1], i[2])
                    recalculated.append(new_intersection)
    return recalculated


def compute_reflection(ray: Ray, surface: Segment, intensity: float, reflective_factor: float) -> (Ray, float):
    """
    Compute reflection of ray from given surface. Intensity of ray is multiplied by reflective factor of the surface.

    :param ray: Ray that should be reflected
    :param surface: Reflective surface segment
    :param intensity: Intensity of given ray
    :param reflective_factor: Reflective factor of the material
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


def compute_reflection_segment_simple(ray_array, segment, ray_intensity, r_factor):
    """
    Compute reflection of last part of the ray from given segment. This function is used in scenario with
     multiple reflective segments.

    :param ray_array: Array representing parts of ray
    :param segment: Segment that the ray should reflect from
    :param ray_intensity: Intensity of ray before reflection
    :param r_factor: Reflective factor of the material
    :return: Updated ray array and intensity
    """
    last_ray = ray_array[-1]
    intersection = segment.intersection(last_ray)
    if intersection:
        reflected_ray, ray_intensity = compute_reflection(last_ray, segment, ray_intensity, r_factor)
        new_ray_array = ray_array[:-1]
        new_ray_array.append(Ray(last_ray.p1, intersection[0]))
        new_ray_array.append(reflected_ray)
        ray_array = new_ray_array
    return ray_array, ray_intensity


def compute_reflection_multiple_segments(ind: Component, r_factor: float, r_timeout):
    """
    For each ray compute reflections from all segments. First find closest segment, then calculate reflection from
    the segment a then continue to find new closest segment. If there is no intersection with any of the segments, stop.

    :param ind: Individual
    :param r_factor: Reflective factor of the material
    :param r_timeout: Reflections timeout from parameters
    """
    for ray in ind.original_rays:
        ray_intensity = ray.original_intensity
        ray.ray_array = [ray.ray]
        last_reflection = ind.base
        reflection_exists = True
        no_of_reflections = 0
        while reflection_exists and no_of_reflections < r_timeout:
            segment = closest_segment(ind.reflective_segments+[ind.base], ray.ray_array[-1], last_reflection)
            if len(segment) == 1:
                ray.ray_array, ray_intensity = compute_reflection_segment_simple(ray.ray_array, segment[0], ray_intensity, r_factor)
                last_reflection = segment[0]
                no_of_reflections += 1
                if no_of_reflections == r_timeout:
                    ray.terminated = True
            else:
                reflection_exists = False
        ray.intensity = ray_intensity


def compute_reflections_two_segments(ind: Component, r_factor: float):
    """
    Compute reflections for all rays in scenario with two segments.
    For each ray compute reflections from right and left segment. Continue while there exist any.
    Reflections are recorder in ray_array from each ray

    :param ind: Individual
    :param r_factor: Reflective factor from parameters
    """
    ind.compute_right_segment()
    ind.compute_left_segment()
    no_of_reflections = 0
    for ray in ind.original_rays:
        ray_intensity = ray.original_intensity
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
        ray.intensity = ray_intensity
    ind.no_of_reflections = no_of_reflections


def prepare_intersections(points: List[Tuple[Rational, float, float]]) -> List[Tuple[float, float, float]]:
    """
    Prepare a list of tuples sorted according to first items which are also converted to float

    :param points: List of tuples (x-coord of road intersection, intensity of incident ray, intensity with cosine error)
    :return: List of tuples (x-coord to float, intensity, intensity with cosine error) sorted according to first item
    """
    return sorted([(float(x), y, z) for x, y, z in points])


def closest_segment(segments: List[Segment], ray: Ray, last_reflection: Segment) -> Segment:
    """
    Find closest segment for given ray

    :param segments: List of segments
    :param ray: Ray
    :param last_reflection: Segment of last reflection
    :return: Closest segment
    """
    intersection_dict = {}
    for segment in segments:
        intersection = ray.intersection(segment)
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
    """
    Rotate segment clockwise or counterclockwise according to given angle

    :param segment: Reflective segment
    :param angle: Angle for rotation (in degrees)
    :return: Rotated segment
    """
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
    """
    Change size of a segment according to give coefficient

    :param segment: Reflective segment
    :param coefficient: Coefficient for resizing
    :return: Resized segment
    """
    a = [segment.p1.x, segment.p1.y]
    b = [segment.p2.x, segment.p2.y]

    midpoint = [(a[0] + b[0])/2, (a[1] + b[1])/2]
    x_diff_half = (b[0] - a[0]) / 2
    y_diff_half = (b[1] - a[1]) / 2

    a_changed = [midpoint[0] - coefficient * x_diff_half, midpoint[1] - coefficient * y_diff_half]
    b_changed = [midpoint[0] + coefficient * x_diff_half, midpoint[1] + coefficient * y_diff_half]

    changed_segment = Segment(Point(int(a_changed[0]), int(a_changed[1])), Point(int(b_changed[0]), int(b_changed[1])))

    return changed_segment
