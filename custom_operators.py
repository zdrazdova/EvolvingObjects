import random
from custom_classes import Component


def mutate_length(individual: Component, length_upper_bound: int, length_lower_bound:int) -> Component:
    individual.left_length_coef += random.uniform(-0.1, 0.1)
    individual.right_length_coef += random.uniform(-0.1, 0.1)
    individual.left_length_coef = min(individual.left_length_coef, length_upper_bound)
    individual.right_length_coef = min(individual.right_length_coef, length_upper_bound)
    individual.left_length_coef = max(individual.left_length_coef, length_lower_bound)
    individual.right_length_coef = max(individual.right_length_coef, length_lower_bound)
    return individual


def mutate_angle(individual:Component) -> Component:
    individual.right_angle += random.randint(-5, 5)
    individual.right_angle = max(individual.angle_limit_min, individual.right_angle)
    individual.right_angle = min(individual.angle_limit_max, individual.right_angle)
    individual.left_angle += random.randint(-5,5)
    individual.left_angle = max(individual.angle_limit_min - 90, individual.left_angle)
    individual.left_angle = min(individual.angle_limit_max - 90, individual.left_angle)
    return individual


def mate(ind1:Component, ind2:Component) -> (Component, Component):
    dummy_angle = ind1.right_angle
    ind1.right_angle = ind2.right_angle
    ind2.right_angle = dummy_angle
    dummy_length = ind1.right_length_coef
    ind1.right_length_coef = ind2.right_length_coef
    ind2.right_length_coef = dummy_length
    return ind1, ind2