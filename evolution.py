import json
import random
import copy as cp
import math
import sys

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
        #print("Initiating individual")
        self.base_slope = config.lamp.base_angle
        self.base_length = config.lamp.base_length
        self.origin = Point(0, 0)

        #print("length " + str(self.base_length))
        #print("slope " + str(self.base_slope))

        # Calculating base coordinates from slope and length parameters
        y_diff = round(self.base_length/2 * sin(math.radians(self.base_slope)))
        x_diff = round(self.base_length/2 * cos(math.radians(self.base_slope)))
        self.base = Segment(Point(-x_diff, -y_diff), Point(x_diff, y_diff))
        #print (self.base)

        # Sampling light rays for given base slope
        self.original_rays = self.sample_rays(config.lamp.number_of_rays, config.lamp.ray_distribution, self.base_slope)

        #upper_ray = self.rays[0][0].slope
        self.road = Segment(Point(config.road.start, config.road.depth), Point(config.road.end, config.road.depth))
        self.start = config.road.start
        self.end = config.road.end

        self.right_angle = random.randint(config.lamp.angle_lower_bound, config.lamp.angle_upper_bound)
        self.left_angle = random.randint(config.lamp.angle_lower_bound, config.lamp.angle_upper_bound)

        self.length_limit_max = config.lamp.length_lower_bound
        self.length_limit_min = config.lamp.length_upper_bound
        self.length_limit_diff = self.length_limit_max - self.length_limit_min

        self.left_length_coef = random.random() * self.length_limit_diff + self.length_limit_min
        self.right_length_coef = random.random() * self.length_limit_diff + self.length_limit_min

        self.angle_limit_min = config.lamp.angle_lower_bound
        self.angle_limit_max = config.lamp.angle_upper_bound

        self.compute_right_segment()
        self.compute_left_segment()

        self.reflections = []
        self.reflected = []
        self.intersections_on = []
        self.intersections_on_intensity = 0
        self.intersections_out = []

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

    def draw(self, name):
        svg_name = "img/img-" + str(name).zfill(2) + ".svg".format(name)
        # Generating drawing in SVG format
        with open(svg_name, "w") as f:
            x_offset = 1000
            y_offset = 1000
            f.write('<svg width="8000" height="5500">')
            f.write('<rect width="8000" height="5500" fill="black"/>')
            # f.write('<rect x="950" y="950" width="100" height="4070" fill="gray"/>') #stožár
            # f.write('<rect x="100" y="950" width="900" height="70" fill="gray"/>') # výložník + lampa

            for ray in []:
                r = ray.ray
                alpha = str(round(ray.intensity, 3))
                color = "(250, 216, 22)"
                f.write('<line x1="{0}" y1="{1}" x2="{2}" y2="{3}" style="stroke:rgb{4};stroke-opacity:{5};stroke-width:10"/>\n'
                    .format(float(r.points[0].x) + x_offset, - float(r.points[0].y) + y_offset,
                            float(r.points[1].x) + x_offset, - float(r.points[1].y) + y_offset, color, alpha))

            for ray in self.original_rays:
                array = ray.ray_array
                alpha = str(round(ray.intensity, 3))
                color = "(250, 216, 22)"
                for r in array[:-1]:
                    f.write('<line x1="{0}" y1="{1}" x2="{2}" y2="{3}" style="stroke:rgb{4};stroke-opacity:{5};stroke-width:10"/>\n'
                    .format(float(r.points[0].x) + x_offset, - float(r.points[0].y) + y_offset,
                            float(r.points[1].x) + x_offset, - float(r.points[1].y) + y_offset, color, alpha))
                r = array[-1]
                intersection = self.road.intersection(r)
                if intersection:
                    intersection = intersection[0]
                    f.write(
                        '<line x1="{0}" y1="{1}" x2="{2}" y2="{3}" style="stroke:rgb{4};stroke-opacity:{5};stroke-width:10"/>\n'
                        .format(float(r.points[0].x) + x_offset, - float(r.points[0].y) + y_offset,
                                float(intersection.x) + x_offset, - float(intersection.y) + y_offset,
                                color, alpha))
                else:
                    x_diff = float(r.points[1].x - r.points[0].x) * 100
                    y_diff = float(r.points[1].y - r.points[0].y) * 100
                    f.write(
                        '<line x1="{0}" y1="{1}" x2="{2}" y2="{3}" style="stroke:rgb{4};stroke-opacity:{5};stroke-width:10"/>'
                        '\n'.format(float(r.points[0].x) + x_offset, - float(r.points[0].y) + y_offset,
                                    float(r.points[0].x) + x_offset + x_diff,
                                    -float(r.points[0].y) + y_offset - y_diff,
                                    color, alpha))

            #print(self.reflected)
            for r_sequence in []:
                color = "(250, 216, 22)"
                for r in r_sequence:
                    f.write('<line x1="{0}" y1="{1}" x2="{2}" y2="{3}" style="stroke:rgb{4};stroke-width:10"/>\n'
                        .format(float(r.points[0].x) + x_offset, - float(r.points[0].y) + y_offset,
                                float(r.points[1].x) + x_offset, - float(r.points[1].y) + y_offset, color))
                intersection = self.road.intersection(r)
                if intersection:
                    intersection = intersection[0]
                    f.write('<line x1="{0}" y1="{1}" x2="{2}" y2="{3}" style="stroke:rgb(250, 216, 22);stroke-width:10"/>\n'
                    .format(float(r.points[0].x) + x_offset, - float(r.points[0].y) + y_offset,
                            float(intersection.x) + x_offset, - float(intersection.y) + y_offset))
                else:
                    x_diff = float(r.points[1].x - r.points[0].x) * 10000
                    y_diff = float(r.points[1].y - r.points[0].y) * 10000
                    f.write(
                        '<line x1="{0}" y1="{1}" x2="{2}" y2="{3}" style="stroke:rgb(196, 185, 118);stroke-width:10"/>'
                        '\n'.format(float(r.points[0].x) + x_offset, - float(r.points[0].y) + y_offset,
                                    float(r.points[0].x) + x_offset + x_diff,
                                    -float(r.points[0].y) + y_offset - y_diff))

        #    step = 7000 / len(self.rays)
        #    for i in range(len(self.rays)//2):
        #        f.write('<rect x="{0}" y="5000" width="{1}" height="50" fill="gray"/>'.format(i*step*2,step)) #silnice

            f.write('<rect x="{0}" y="{1}" width="{2}" height="50" fill="gray"/>'
                    .format(self.road.p1.x + x_offset, -self.road.p1.y + y_offset,
                            (self.road.p2.x-self.road.p1.x)))  # road

            # Base
            f.write('<line x1="{0}" y1="{1}" x2="{2}" y2="{3}" style="stroke:gray;stroke-width:40"/>'.format(
                self.base.p1.x + x_offset, -self.base.p1.y + y_offset,
                self.base.p2.x + x_offset, -self.base.p2.y + y_offset))

            #pravá laple
            f.write('<line x1="{0}" y1="{1}" x2="{2}" y2="{3}" style="stroke:gray;stroke-width:40"/>'.format(
                self.base.p2.x + x_offset, -self.base.p2.y + y_offset,
                float(self.right_segment.p2.x) + x_offset, float(-self.right_segment.p2.y) + y_offset))

            # levá laple
            #f.write('<line x1="{0}" y1="{1}" x2="{2}" y2="{3}" style="stroke:gray;stroke-width:40"/>'.format(
            #    self.base.p1.x + x_offset, -self.base.p1.y + y_offset,
            #    float(self.left_segment.p2.x) + x_offset, float(-self.left_segment.p2.y) + y_offset))

            f.write('</svg>')

    # Updated - needs beter parameters
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

    # Outdated
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
    orig_point = ray.p1
    parallel = surface.parallel_line(orig_point)
    perpendicular = surface.perpendicular_line(intersection)
    meet_point = parallel.intersection(perpendicular)[0]
    x_diff = (meet_point.x - orig_point.x)
    y_diff = (meet_point.y - orig_point.y)
    new_point = Point(meet_point.x + x_diff, meet_point.y + y_diff)
    #print((intersection))
    #print((new_point))
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
            inter_array.append(inter_point)
    # print(len(ind.original_rays))
    # print(inter_array)
    ind.intersections_on = inter_array
    ind.intersections_on_intensity = intensity_sum


def compute_reflections_right(ind):
   # compute_intersections(ind)

   # ind.compute_right_segment()
    #print("computing reflected")
    reflected = 0
    reflected_rays = []
    for ray in ind.original_rays:
        previous_i_r = Point(0, 0)
        intersection_r = ray.ray_array[-1].intersection(ind.right_segment)
        if intersection_r and intersection_r[0] != previous_i_r:
            reflected += 1
            #print(type(ray.ray_array[-1]))
            #print(type(ind.right_segment))
            #print(type(intersection_r[0]))
            reflected_ray = compute_reflection(ray.ray_array[-1], ind.right_segment, intersection_r[0])
            new_ray = [Ray(ray.ray_array[0].p1,intersection_r[0]), reflected_ray]
            #print(ray.ray_array[-1].p2)
            #ray.ray_array[-1].p2 = intersection_r[0]
            #ray.ray_array.append(reflected_ray)
            ray.ray_array = new_ray
            reflected_rays.append(new_ray)
        #else:
            #reflected_rays.append(ray.ray_array)
    ind.reflected = reflected_rays
    return reflected


def compute_reflections(ind):
    compute_intersections(ind)

    ind.compute_right_segment()
    ind.compute_left_segment()
    print("computing reflected")
    reflected = 0
    reflected_rays = []
    for ray in ind.original_rays:
        new_ray = cp.deepcopy(ray)
        continue_left = True
        continue_right = True
        previous_i_r = Point(0, 0)
        previous_i_l = Point(0, 0)
        while continue_left or continue_right:
            continue_left = False
            continue_right = False
            intersection_r = new_ray.ray.intersection(ind.right_segment)
            if intersection_r and intersection_r[0] != previous_i_r:
                previous_i_r = intersection_r[0]
                intersection = intersection_r[0]
                reflected += 1
                reflected_ray = compute_reflection(new_ray.ray, ind.right_segment, intersection)
                new_ray.ray = Ray(new_ray.ray.p1, intersection)
                new_ray.append(reflected_ray)
                continue_right = True
            intersection_l = new_ray.ray.intersection(ind.left_segment)
            if intersection_l and intersection_l[0] != previous_i_l:
                previous_i_l = intersection_l[0]
                intersection = intersection_l[0]
                reflected += 1
                reflected_ray = compute_reflection(new_ray.ray, ind.left_segment, intersection)
                new_ray.ray = Ray(new_ray[-1].p1, intersection)
                new_ray.append(reflected_ray)
                continue_left = True
        reflected_rays.append(new_ray)
    ind.reflected = reflected_rays
    intersections = []

    for r in ind.reflected:
        intersection = ind.road.intersection(r.ray)  # průsečík se silnicí
        if intersection:
            intersections.append(intersection[0])

    ind.intersections_on = intersections

    return intersections, reflected


def mutate_base(individual):
    individual.base_slope += random.randint(-5,5)
    individual.base_slope = max(individual.base_slope, 90)
    individual.base_slope = min(individual.base_slope, 0)
    return individual

def mutate_angle(individual):
    individual.right_angle += random.randint(-5, 5)
    individual.right_angle = max(individual.angle_limit_min, individual.right_angle)
    individual.right_angle = min(individual.angle_limit_max, individual.right_angle)
 #   individual.left_angle += random.randint(-5,5)
 #   individual.left_angle = max(individual.angle_l_1, individual.left_angle)
 #   individual.left_angle = min(individual.angle_l_2, individual.left_angle)
    return individual


def mutate_length(individual):
    individual.left_length_coef += random.random() / 2
    individual.right_length_coef += random.random() / 2
    individual.left_length_coef = min(individual.left_length_coef, individual.length_limit_max)
    individual.right_length_coef = min(individual.right_length_coef, individual.length_limit_max)
    individual.left_length_coef = max(individual.left_length_coef, individual.length_limit_min)
    individual.right_length_coef = max(individual.right_length_coef, individual.length_limit_min)

    return individual


def mate(ind1, ind2):
    dummy_angle = ind1.right_angle
    ind1.right_angle = ind2.right_angle
    ind2.right_angle = dummy_angle
    dummy_length = ind1.right_length_coef
    ind1.right_length_coef = ind2.right_length_coef
    ind2.right_length_coef = dummy_length
    return ind1, ind2


def evaluate_simple(individual):
    reflected = compute_reflections_right(individual)
    compute_intersections(individual)
    print(individual.intersections_on_intensity)
    print(len(individual.intersections_on))
    return individual.intersections_on_intensity


def evaluate(individual):
    individual.fitness = individual.right_angle
    all_intersections, un = compute_reflections(individual)
    start = individual.start
    end = individual.end
    intersections_x = []
    for i in all_intersections:
        intersections_x.append(float(i.x))
    #intersections_x.append(end)
    intersections = sorted(intersections_x)

    section_length = (end-start)/(len(intersections)+1)
    no_sections = len(intersections)+1
    parts = len(individual.rays)
    part_length = (end-start) / parts
    fitness = 0
    for p in range(parts):
        counter = 0
        for i in intersections:
            if i > start + p*part_length and i <= start + (p+1)*part_length:
                counter += 1
        fitness += abs(counter - 1)

    #fitness = len(all_intersections)
    #fitness = un
    individual.fitness = (-fitness, un)
    fitness_together = (-fitness + len(all_intersections))
    return fitness_together


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
    mut_base_prob = config.evolution.operators.mutation.base_mutation_prob

    # Initiating elitism
    hof = HallOfFame(1)

    fitnesses = list(map(evaluate_simple, pop))
    for ind, fit in zip(pop, fitnesses):
        ind.fitness = fit
    print("Start of evolution")

    # Rendering individuals in initial population as images
    for i in range(len(pop)):
        pop[i].draw(i)
        #print(pop[i].right_angle)

    print("Drawing finished")



    print("  Evaluated %i individuals" % len(pop))


    # Extracting all the fitnesses of
    fits = [ind.fitness for ind in pop]

    # Variable keeping track of the number of generations
    g = 0
    line = str(mut_angle_prob) + " " + str(mut_length_prob)

    # Begin the evolution
    while g < 10:
        # A new generation
        g = g + 1
        print("-- Generation %i --" % g)

        # Select the next generation individuals
        offspring = toolbox.select(pop, len(pop))
        # Clone the selected individuals
        offspring = list(map(toolbox.clone, offspring))

        # Apply crossover and mutation on the offspring
        for child1, child2 in zip(offspring[::2], offspring[1::2]):

            # cross two individuals with probability xover_prob
            if random.random() < 0:
                mate(child1, child2)

                # fitness values of the children
                # must be recalculated later
                child1.fitness = 0
                child2.fitness = 0

        for mutant in offspring:

            # mutate an individual with probability mut_angle_prob
            if random.random() < 0:
                mutate_angle(mutant)
                mutant.fitness = 0

            if random.random() < 0:
                mutate_length(mutant)
                mutant.fitness = 0

            if random.random() < 0:
                mutate_base(mutant)
                mutant.fitness = 0

        # Evaluate the individuals with an invalid fitness
        invalid_ind = [ind for ind in offspring if ind.fitness == 0]
        fitnesses = map(evaluate_simple, invalid_ind)
        for ind, fit in zip(invalid_ind, fitnesses):
            ind.fitness = fit

        print("  Evaluated %i individuals" % len(invalid_ind))
        # The population is entirely replaced by the offspring
        pop[:] = offspring
        hof.update(pop)

        #hof.update(pop)
        # Gather all the fitnesses in one list and print the stats
        fits = [ind.fitness for ind in pop]
        print(fits)
        rang = [ind.right_angle for ind in pop]
        print(rang)

        best_ind = tools.selBest(pop, 1)[0]
        best_ind = hof[0]

        print("Best individual is %s, %s, %s, %s, %s" % (best_ind.left_length_coef, best_ind.left_angle,
                                                         best_ind.fitness, best_ind.right_angle,
                                                         best_ind.right_length_coef))
        line = line + ", " + str(best_ind.fitness)
        #best_ind.draw(g)

    print("-- End of (successful) evolution --")
    line = line + "\n"
    stat_name = "stats/prob"
    with open(stat_name, "a") as f:
        f.write(line)

    best_ind = tools.selBest(pop, 1)[0]
    print("--")
    #print(best_ind.reflected)

    print("Best individual is %s" % (best_ind.fitness))

 #   for j in range(len(hof)):
 #       hof[j].draw(j)



# create config parser
builder = ConfigBuilder()

# parse config
config = builder.parse_config('parameters.json')



def main():
    # Example - angle mutation probability
    #print(config.evolution.operators.mutation.angle_mutation_prob)
    # Run evolution algorithm with given configuration
    evolution()


if __name__ == "__main__":
    main()
