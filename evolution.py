import json
import random
import copy as cp
import math
import sys

import custom_operators as co
import auxiliary as ax

from deap import base
from deap import creator
from deap import tools
from deap.tools import HallOfFame
from python_json_config import ConfigBuilder

from sympy.geometry import Line, Ray, Point, Segment
from sympy import pi, sin, cos


class MyRay:

    def __init__(self, origin, ray_angle, base_angle):
        # Intensity is calculated according to Lambertian distribution
        self.intensity = abs(math.sin(math.radians(abs(ray_angle-base_angle))))
        # End coordinates are calculated from ray angle
        x_coordinate = 10000 * math.cos(math.radians(ray_angle)) + origin.x
        y_coordinate = 10000 * math.sin(math.radians(ray_angle)) + origin.y
        # Ray goes from the origin in direction of end coordinates
        self.ray = Ray(origin, Point(x_coordinate, y_coordinate))
        # Array used for storing segments of reflected ray
        self.ray_array = [Ray(origin, Point(x_coordinate, y_coordinate))]


class Individual:

    def __init__(self):
        self.base_slope = config.lamp.base_angle
        self.base_length = config.lamp.base_length
        self.origin = Point(0, 0)

        # Calculating base coordinates from slope and length parameters
        y_diff = round(self.base_length/2 * sin(math.radians(self.base_slope)))
        x_diff = round(self.base_length/2 * cos(math.radians(self.base_slope)))
        self.base = Segment(Point(-x_diff, -y_diff), Point(x_diff, y_diff))

        # Sampling light rays for given base slope
        self.original_rays = self.sample_rays(config.lamp.number_of_rays, config.lamp.ray_distribution, self.base_slope)

        self.road = Segment(Point(config.road.start, config.road.depth), Point(config.road.end, config.road.depth))
        self.start = config.road.start
        self.end = config.road.end
        self.road_length = (self.end - self.start)

        self.angle_limit_min = config.lamp.angle_lower_bound + self.base_slope
        self.angle_limit_max = config.lamp.angle_upper_bound + self.base_slope

        self.right_angle = random.randint(self.angle_limit_min, self.angle_limit_max)
        self.left_angle = random.randint(self.angle_limit_min, self.angle_limit_max) - 90

        self.length_limit_max = config.lamp.length_lower_bound
        self.length_limit_min = config.lamp.length_upper_bound
        self.length_limit_diff = self.length_limit_max - self.length_limit_min

        self.left_length_coef = random.random() * self.length_limit_diff + self.length_limit_min
        self.right_length_coef = random.random() * self.length_limit_diff + self.length_limit_min



        self.compute_right_segment()
        self.compute_left_segment()

        self.reflections = []
        self.reflected = []
        self.intersections_on = []
        self.intersections_on_intensity = 0
        self.intersections_out = []
        self.no_of_reflections = 0
        self.segments_intensity = []

    # Sampling given number of rays, base angle is used for intensity calculations
    def sample_rays(self, number_of_rays, distribution, base_angle):
        ray_array = []
        if distribution == "uniform":
            step = 180 / number_of_rays
        for ray in range(number_of_rays):
            if distribution == "uniform":
                angle = 180 + ray*step + step/2 + base_angle
            else:
                angle = random.randint(180, 360) + base_angle
            new_ray = MyRay(self.origin, angle, base_angle)
            ray_array.append(new_ray)
        return ray_array

    # Computing coordinates for right segment based on right angle and base info
    def compute_right_segment(self):
        base_right_p = self.base.points[1]
        right_ray = Ray(base_right_p, angle= self.right_angle/180 * pi)
        x_diff = self.base.length * self.right_length_coef * cos(self.right_angle/180 * pi)
        y_diff = self.base.length * self.right_length_coef * sin(self.right_angle/180 * pi)
        if right_ray.xdirection == "oo":
            right_end_x = base_right_p.x + x_diff
        else:
            right_end_x = base_right_p.x - x_diff
        if right_ray.ydirection == "oo":
            right_end_y = base_right_p.y + y_diff
        else:
            right_end_y = base_right_p.y - y_diff

        self.right_segment = Segment(base_right_p, Point(float(right_end_x),float(right_end_y)))

    # Computing coordinates for left segment based on left angle and base info
    def compute_left_segment(self):
        base_left_p = self.base.points[0]
        left_ray = Ray(base_left_p, angle= self.left_angle/180 * pi)
        x_diff = self.base.length * self.left_length_coef * cos(self.left_angle/180 * pi)
        y_diff = self.base.length * self.left_length_coef * sin(self.left_angle/180 * pi)

        if left_ray.xdirection == "oo":
            left_end_x = base_left_p.x + x_diff
        else:
            left_end_x = base_left_p.x - x_diff
        if left_ray.ydirection == "oo":
            left_end_y = base_left_p.y + y_diff
        else:
            left_end_y = base_left_p.y - y_diff

        self.left_segment = Segment(base_left_p, Point(float(left_end_x),float(left_end_y)))


def compute_reflection(ray, surface, intersection):
    #print(ray)
    #print((surface))
    #print("intersection" + str(intersection))
    orig_point = ray.p1
    parallel = surface.parallel_line(orig_point)
    perpendicular = surface.perpendicular_line(intersection)
    meet_point = parallel.intersection(perpendicular)[0]
    x_diff = (meet_point.x - orig_point.x)
    y_diff = (meet_point.y - orig_point.y)
    new_point = Point(meet_point.x + x_diff, meet_point.y + y_diff)
    #print(intersection, new_point)
    reflected_ray = Ray(intersection, new_point)
    return reflected_ray


# computes intersections of rays from LED and road below the lamp
def compute_intersections(ind):
    inter_array = []
    intensity_sum = 0
    for ray in ind.original_rays:
        inter_point = ind.road.intersection(ray.ray_array[-1])
        if inter_point != []:
            intensity_sum += ray.intensity
            inter_array.append(inter_point[0].x)
    # print(len(ind.original_rays))
    # print(inter_array)
    ind.intersections_on = inter_array
    ind.intersections_on_intensity = intensity_sum


def compute_reflections_two_segments(ind):
    ind.compute_right_segment()
    ind.compute_left_segment()
    no_of_reflections = 0
    for ray in ind.original_rays:
        #print("NEW ")
        continue_left = True
        continue_right = True
        previous_i_r = Point(0, 0)
        previous_i_l = Point(0, 0)
        ray.ray_array=[ray.ray]
        while continue_left or continue_right:
            continue_left = False
            continue_right = False
            last_ray = ray.ray_array[-1]
            intersection_r = last_ray.intersection(ind.right_segment)
            #print("right ", len(intersection_r))

            if intersection_r and intersection_r[0] != previous_i_r:
                #ax.print_ray(last_ray)
                #ax.print_point(intersection_r[0])
                previous_i_r = intersection_r[0]
                intersection = intersection_r[0]
                reflected_ray = compute_reflection(last_ray, ind.right_segment, intersection)
                no_of_reflections += 1
                new_ray_array = ray.ray_array[:-1]
                new_ray_array.append(Ray(last_ray.p1, intersection_r[0]))
                new_ray_array.append(reflected_ray)
                ray.ray_array = new_ray_array
                continue_left = True
            last_ray = ray.ray_array[-1]
            intersection_l = last_ray.intersection(ind.left_segment)
            #print("left ", len(intersection_l))
            if intersection_l and intersection_l[0] != previous_i_l:
                #ax.print_ray(last_ray)
                #ax.print_point(intersection_l[0])
                previous_i_l = intersection_l[0]
                intersection = intersection_l[0]
                reflected_ray = compute_reflection(last_ray, ind.left_segment, intersection)
                no_of_reflections += 1
                new_ray_array = ray.ray_array[:-1]
                new_ray_array.append(Ray(last_ray.p1, intersection_l[0]))
                new_ray_array.append(reflected_ray)
                ray.ray_array = new_ray_array
                continue_right = True
    ind.no_of_reflections = no_of_reflections


def prepare_intersections(points):
    x_coordinates = []
    for point in points:
        x_coordinates.append(float(point))
    return sorted(x_coordinates)


def compute_road_segments(ind):
    segments_size = ind.road_length / config.road.sections
    segments_intensity = [0] * config.road.sections
    intersections = prepare_intersections(ind.intersections_on)
    #print(intersections)
    left_border = ind.start
    right_border = ind.start
    counter = 0
    for segment in range(config.road.sections):
        left_border = right_border
        right_border += segments_size
        stay = True
        while stay and counter < len(intersections):
            stay = False
            if left_border <= intersections[counter] < right_border:
                segments_intensity[segment] += 1
                counter += 1
                stay = True
    segments_intensity_proportional = [0] * config.road.sections
    for segment in range(config.road.sections):
        segments_intensity_proportional[segment] = segments_intensity[segment] / len(intersections)
    ind.segments_intensity = segments_intensity_proportional

    #print(segments_intensity)
    #print(segments_intensity_proportional)


def evaluate_simple(individual):
    #print("SIMPLE")
    compute_reflections_two_segments(individual)
    compute_intersections(individual)
    #print(individual.intersections_on_intensity)
    #print(len(individual.intersections_on))
    #print(individual.intersections_on)
    compute_road_segments(individual)
    return len(individual.intersections_on)


def evolution():
    random.seed(10)

    # Initiating evolutionary algorithm
    creator.create("Fitness", base.Fitness, weights=(1.0))
    creator.create("Individual", list, fitness=creator.Fitness)

    toolbox = base.Toolbox()

    toolbox.register("population", tools.initRepeat, list, Individual)
    toolbox.register("select", tools.selTournament, tournsize=2)

    # Initiating first population
    pop = toolbox.population(config.evolution.population_size)

    # Loading genetic operators probabilities
    xover_prob = config.evolution.operators.xover_prob
    mut_angle_prob = config.evolution.operators.mutation.angle_mutation_prob
    mut_length_prob = config.evolution.operators.mutation.length_mutation_prob

    # Initiating elitism
    #hof = HallOfFame(1)

    fitnesses = list(map(evaluate_simple, pop))
    for ind, fit in zip(pop, fitnesses):
        ind.fitness = fit
    print("Start of evolution")

    # Rendering individuals in initial population as images
    for i in range(len(pop)):
        ax.draw(pop[i], i, config)

    print("Drawing finished")



    print("  Evaluated %i individuals" % len(pop))


    # Begin the evolution
    for g in range(config.evolution.number_of_generations):
        # A new generation

        print("-- Generation %i --" % g)

        # Select the next generation individuals
        offspring = toolbox.select(pop, len(pop))
        # Clone the selected individuals
        offspring = list(map(toolbox.clone, offspring))

        # Apply crossover and mutation on the offspring
        for child1, child2 in zip(offspring[::2], offspring[1::2]):

            # cross two individuals with probability xover_prob
            if random.random() < xover_prob:
                co.mate(child1, child2)
                # fitness values of the children must be recalculated later
                child1.fitness = 0
                child2.fitness = 0

        for mutant in offspring:

            # mutate an individual with probability mut_angle_prob and mut_length_prob
            if random.random() < mut_angle_prob:
                co.mutate_angle(mutant)
                mutant.fitness = 0

            if random.random() < mut_length_prob:
                co.mutate_length(mutant)
                mutant.fitness = 0

        # Evaluate the individuals with an invalid fitness
        invalid_ind = [ind for ind in offspring if ind.fitness == 0]
        fitnesses = map(evaluate_simple, invalid_ind)
        for ind, fit in zip(invalid_ind, fitnesses):
            ind.fitness = fit

        print("  Evaluated %i individuals" % len(invalid_ind))
        # The population is entirely replaced by the offspring
        pop[:] = offspring
        # hof.update(pop)

        # hof.update(pop)

        best_ind = tools.selBest(pop, 1)[0]
        # best_ind = hof[0]

        print("Best individual is %s, %s, %s, %s, %s, %s, %s" % (best_ind.left_length_coef, best_ind.left_angle,
                                                         best_ind.intersections_on_intensity, best_ind.fitness, ind.no_of_reflections,
                                                         best_ind.right_angle, best_ind.right_length_coef))
        ax.draw(best_ind,"best"+str(g), config)

    print("-- End of (successful) evolution --")

    best_ind = tools.selBest(pop, 1)[0]
    print("--")


    print("Best individual is %s" % (best_ind.fitness))


# create config parser
builder = ConfigBuilder()

# parse configuration from file parameters.json
config = builder.parse_config('parameters.json')


def main():
    # Run evolution algorithm
    evolution()


if __name__ == "__main__":
    main()
