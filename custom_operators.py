import random
from typing import List

from sympy import Segment, Point

from component import Component
from custom_geometry import rotate_segment, change_size_segment


def shift_one_segment(reflective_segments: List[Segment], axis: str) -> List[Segment]:
    """
    Shift one segment from list of reflective segments of an individual

    :param reflective_segments: List of all reflective segments of one individual
    :param axis: Indicator whether to use X-axis or Y-axis
    :return: List of all reflective segments with one shifted
    """
    chosen_segment_index = random.randint(0, len(reflective_segments)-1)
    chosen_segment = reflective_segments[chosen_segment_index]
    shift_amount = random.randint(-100, 100)
    if axis == "x":
        shifted_segment = Segment(Point(chosen_segment.p1.x + shift_amount, chosen_segment.p1.y),
                                  Point(chosen_segment.p2.x + shift_amount, chosen_segment.p2.y))
    else:
        shifted_segment = Segment(Point(chosen_segment.p1.x, chosen_segment.p1.y + shift_amount),
                                  Point(chosen_segment.p2.x, chosen_segment.p2.y + shift_amount))
    modified_segments = reflective_segments[:chosen_segment_index]
    modified_segments.append(shifted_segment)
    modified_segments = modified_segments + reflective_segments[chosen_segment_index+1:]
    return modified_segments


def rotate_one_segment(reflective_segments: List[Segment]) -> List[Segment]:
    """
    Rotate one segment from list of reflective segments of an individual

    :param reflective_segments: List of all reflective segments of one individual
    :return: List of all reflective segments with one rotated
    """
    chosen_segment_index = random.randint(0, len(reflective_segments)-1)
    chosen_segment = reflective_segments[chosen_segment_index]
    shift_amount = random.randint(-30, 30)
    rotated_segment = rotate_segment(chosen_segment, shift_amount)
    modified_segments = reflective_segments[:chosen_segment_index]
    modified_segments.append(rotated_segment)
    modified_segments = modified_segments + reflective_segments[chosen_segment_index+1:]
    return modified_segments


def resize_one_segment(reflective_segments: List[Segment]) -> List[Segment]:
    """
    Resize one segment from list of reflective segments of an individual

    :param reflective_segments: List of all reflective segments of one individual
    :return: List of all reflective segments with one resized
    """
    chosen_segment_index = random.randint(0, len(reflective_segments)-1)
    chosen_segment = reflective_segments[chosen_segment_index]
    change_size_coefficient = random.random()*2
    if change_size_coefficient < 0.5:
        change_size_coefficient = 0.5
    changed_segment = change_size_segment(chosen_segment, change_size_coefficient)
    modified_segments = reflective_segments[:chosen_segment_index]
    modified_segments.append(changed_segment)
    modified_segments = modified_segments + reflective_segments[chosen_segment_index+1:]
    return modified_segments


def tilt_base(base_angle: int, base_angle_limit_min: int, base_angle_limit_max: int) -> int:
    """
    Modify base angle. In the new value is outside of limit, replace is by given limit.

    :param base_angle: Original base angle
    :param base_angle_limit_min: Lower bound for base angle
    :param base_angle_limit_max: Upper bound for base angle
    :return: Modified base angle
    """
    base_angle += random.randint(-10, 10)
    base_angle = max(base_angle_limit_min, base_angle)
    base_angle = min(base_angle_limit_max, base_angle)
    return base_angle


def x_over_multiple_segments(ind1: Component, ind2: Component) -> (Component, Component):
    """
    Perform crossover of two individuals. Split the lists of reflective segments at randomly selected point
    and concatenate two parts from two individuals.

    :param ind1: First individual
    :param ind2: Second individual
    :return: Tuple of individuals with crossover of reflective segments
    """
    length = len(ind1.reflective_segments)
    x_over_point = random.randint(1, length-1)
    new_list_1 = ind1.reflective_segments[:x_over_point] + ind2.reflective_segments[x_over_point:]
    new_list_2 = ind2.reflective_segments[:x_over_point] + ind1.reflective_segments[x_over_point:]
    ind1.reflective_segments = new_list_1
    ind2.reflective_segments = new_list_2
    return ind1, ind2


def mutate_length(individual: Component, length_upper_bound: int, length_lower_bound: int) -> Component:
    """
    Modify length of both segments of an individual

    :param individual: Individual to be modified
    :param length_upper_bound: Upper bound for segment length
    :param length_lower_bound: Lower bound for segment length
    :return: Individual with modified lengths of two segments
    """
    individual.left_length_coef += random.uniform(-0.1, 0.1)
    individual.right_length_coef += random.uniform(-0.1, 0.1)
    individual.left_length_coef = min(individual.left_length_coef, length_upper_bound)
    individual.right_length_coef = min(individual.right_length_coef, length_upper_bound)
    individual.left_length_coef = max(individual.left_length_coef, length_lower_bound)
    individual.right_length_coef = max(individual.right_length_coef, length_lower_bound)
    return individual


def mutate_angle(individual: Component) -> Component:
    """
    Modify angle of both segments of an individual

    :param individual: Individual to be modified
    :return: Individual with modified angles of two segments
    """
    individual.right_angle += random.randint(-10, 10)
    individual.right_angle = max(individual.angle_limit_min, individual.right_angle)
    individual.right_angle = min(individual.angle_limit_max, individual.right_angle)
    individual.left_angle += random.randint(-10, 10)
    individual.left_angle = max(individual.angle_limit_min - 90, individual.left_angle)
    individual.left_angle = min(individual.angle_limit_max - 90, individual.left_angle)
    return individual


def x_over_two_segments(ind1: Component, ind2: Component) -> (Component, Component):
    """
    Perform crossover of two individuals. Swap one of the two segments.

    :param ind1: First individual
    :param ind2: Second individual
    :return: Tuple of individuals with crossover of reflective segments
    """
    dummy_angle = ind1.right_angle
    ind1.right_angle = ind2.right_angle
    ind2.right_angle = dummy_angle
    dummy_length = ind1.right_length_coef
    ind1.right_length_coef = ind2.right_length_coef
    ind2.right_length_coef = dummy_length
    return ind1, ind2
