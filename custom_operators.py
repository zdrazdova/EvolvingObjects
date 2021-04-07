import random
from typing import List

from sympy import Segment, Point

from component import Component
from custom_geometry import rotate_segment


def shift_one_segment(reflective_segments: List[Segment], axis: str, shift_limit: int) -> List[Segment]:
    chosen_segment_index = random.randint(0, len(reflective_segments)-1)
    chosen_segment = reflective_segments[chosen_segment_index]
    shift_amount = random.randint(-shift_limit, shift_limit)
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


def rotate_one_segment(reflective_segments: List[Segment], angle_limit: int) -> List[Segment]:
    chosen_segment_index = random.randint(0, len(reflective_segments)-1)
    chosen_segment = reflective_segments[chosen_segment_index]
    shift_amount = random.randint(-angle_limit, angle_limit)
    rotated_segment = rotate_segment(chosen_segment, shift_amount)
    modified_segments = reflective_segments[:chosen_segment_index]
    modified_segments.append(rotated_segment)
    modified_segments = modified_segments + reflective_segments[chosen_segment_index+1:]
    return modified_segments


def mutate_length(individual: Component, length_upper_bound: int, length_lower_bound: int) -> Component:
    individual.left_length_coef += random.uniform(-0.1, 0.1)
    individual.right_length_coef += random.uniform(-0.1, 0.1)
    individual.left_length_coef = min(individual.left_length_coef, length_upper_bound)
    individual.right_length_coef = min(individual.right_length_coef, length_upper_bound)
    individual.left_length_coef = max(individual.left_length_coef, length_lower_bound)
    individual.right_length_coef = max(individual.right_length_coef, length_lower_bound)
    return individual


def mutate_angle(individual: Component) -> Component:
    individual.right_angle += random.randint(-5, 5)
    individual.right_angle = max(individual.angle_limit_min, individual.right_angle)
    individual.right_angle = min(individual.angle_limit_max, individual.right_angle)
    individual.left_angle += random.randint(-5, 5)
    individual.left_angle = max(individual.angle_limit_min - 90, individual.left_angle)
    individual.left_angle = min(individual.angle_limit_max - 90, individual.left_angle)
    return individual


def mate(ind1: Component, ind2: Component) -> (Component, Component):
    dummy_angle = ind1.right_angle
    ind1.right_angle = ind2.right_angle
    ind2.right_angle = dummy_angle
    dummy_length = ind1.right_length_coef
    ind1.right_length_coef = ind2.right_length_coef
    ind2.right_length_coef = dummy_length
    return ind1, ind2
