import random


def mutate_length(individual):
    individual.left_length_coef += random.random() / 2
    individual.right_length_coef += random.random() / 2
    individual.left_length_coef = min(individual.left_length_coef, individual.length_limit_max)
    individual.right_length_coef = min(individual.right_length_coef, individual.length_limit_max)
    individual.left_length_coef = max(individual.left_length_coef, individual.length_limit_min)
    individual.right_length_coef = max(individual.right_length_coef, individual.length_limit_min)
    return individual


def mutate_angle(individual):
    individual.right_angle += random.randint(-5, 5)
    individual.right_angle = max(individual.angle_limit_min, individual.right_angle)
    individual.right_angle = min(individual.angle_limit_max, individual.right_angle)
 #   individual.left_angle += random.randint(-5,5)
 #   individual.left_angle = max(individual.angle_l_1, individual.left_angle)
 #   individual.left_angle = min(individual.angle_l_2, individual.left_angle)
    return individual


def mate(ind1, ind2):
    dummy_angle = ind1.right_angle
    ind1.right_angle = ind2.right_angle
    ind2.right_angle = dummy_angle
    dummy_length = ind1.right_length_coef
    ind1.right_length_coef = ind2.right_length_coef
    ind2.right_length_coef = dummy_length
    return ind1, ind2