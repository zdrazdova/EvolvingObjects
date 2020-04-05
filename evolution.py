
import random

from deap import base
from deap import creator
from deap import tools
from sympy.geometry import Line, Ray, Point, Segment
from sympy import pi, sin, cos

random.seed(5)


class Individual:

    rays = [
        Ray(Point(0, 0), Point(1, 1/2)),
        Ray(Point(0, 0), Point(1, 1/8)),
        Ray(Point(0, 0), Point(1, -1/8)),
        Ray(Point(0, 0), Point(1, -1/3)),
        Ray(Point(0, 0), Point(1, -1/2)),
        Ray(Point(0, 0), Point(1, -2/3)),
        Ray(Point(0, 0), Point(1, -6/7)),
        Ray(Point(0, 0), Point(1, -1)),
        Ray(Point(0, 0), Point(1, -7/6)),
        Ray(Point(0, 0), Point(1, -3/2)),
        Ray(Point(0, 0), Point(1, -2)),
        Ray(Point(0, 0), Point(1, -3)),
        Ray(Point(0, 0), Point(1, -8)),
        Ray(Point(0, 0), Point(-1, -8)),
        Ray(Point(0, 0), Point(-1, -2))
    ]

    base = Segment(Point(-141, -141), Point(141, 141))

    upper_ray = rays[0].slope
    road = Segment(Point(-1000, -4000), Point(6000, -4000))
    start = -1000
    end = 6000
    angle_r_1 = 90
    angle_r_2 = 180
    angle_l_1 = 30
    angle_l_2 = 120
    right_angle = random.randint(angle_r_1,angle_r_2)
    left_angle = random.randint(angle_l_1,angle_l_2)

    reflections = []
    reflected = []
    intersections_on = []
    intersections_out = []

    def draw(self, name):
        svg_name = "img/img-" + str(name).zfill(2) + ".svg".format(name)
        with open(svg_name, "w") as f:
            x_offset = 1000
            y_offset = 1000
            f.write('<svg width="8000" height="5500">')
            f.write('<rect width="8000" height="5500" fill="black"/>')
            f.write('<rect x="100" y="950" width="100" height="4070" fill="gray"/>') #stožár
            f.write('<rect x="100" y="950" width="1000" height="70" fill="gray"/>') # výložník + lampa

            for r in self.rays: #všechny paprsky
                x = float(10000*r.points[1].x)
                y = float(10000*r.points[1].y)
                f.write('<line x1="{0}" y1="{1}" x2="{2}" y2="{3}" style="stroke:rgb(196, 185, 118);stroke-width:20" />'
                        '\n'.format(x_offset, y_offset, x+x_offset, -y+y_offset))


            for r in self.reflections:
                intersection = self.road.intersection(r) #průsečík se silnicí
                if intersection != []:
                    intersection = intersection[0]
                    f.write('<line x1="{0}" y1="{1}" x2="{2}" y2="{3}" style="stroke:rgb(250, 216, 22);stroke-width:20" />'
                        .format(float(r.points[0].x) + x_offset, - float(r.points[0].y) + y_offset,
                                float(intersection.x) + x_offset, -float(intersection.y) + y_offset))

            f.write('<rect x="100" y="5000" width="7000" height="50" fill="gray"/>') #silnice

            #základna
            f.write('<line x1="{0}" y1="{1}" x2="{2}" y2="{3}" style="stroke:gray;stroke-width:40"/>'.format(
                self.base.p1.x + x_offset, -self.base.p1.y + y_offset,
                self.base.p2.x + x_offset, -self.base.p2.y + y_offset))

            #pravá laple
            f.write('<line x1="{0}" y1="{1}" x2="{2}" y2="{3}" style="stroke:gray;stroke-width:40"/>'.format(
                self.base.p2.x + x_offset, -self.base.p2.y + y_offset,
                float(self.right_segment.p2.x) + x_offset, float(-self.right_segment.p2.y) + y_offset))

            # levá laple
            f.write('<line x1="{0}" y1="{1}" x2="{2}" y2="{3}" style="stroke:pink;stroke-width:40"/>'.format(
                self.base.p1.x + x_offset, -self.base.p1.y + y_offset,
                float(self.left_segment.p2.x) + x_offset, float(-self.left_segment.p2.y) + y_offset))

            f.write('</svg>')



creator.create("FitnessMax", base.Fitness, weights=(1.0,))
creator.create("Individual", list, fitness=creator.FitnessMax)

toolbox = base.Toolbox()

toolbox.register("population", tools.initRepeat, list, Individual)


def compute_intersections(ind):
    inter_array = []
    for ray in ind.rays:
        inter_point = ind.road.intersection(ray)
        if inter_point != []:
            inter_array.append(inter_point)
    ind.intersections_on = inter_array


def compute_reflections(ind):
    compute_intersections(ind)

    base_right_p = ind.base.points[1]
    right_ray = Ray(base_right_p, angle= ind.right_angle/180 * pi)
    x_diff = ind.base.length * cos(ind.right_angle/180 * pi)
    y_diff = ind.base.length * sin(ind.right_angle/180 * pi)

    if right_ray.xdirection == "oo":
        right_end_x = base_right_p.x + x_diff
    else:
        right_end_x = base_right_p.x - x_diff
    if right_ray.ydirection == "oo":
        right_end_y = base_right_p.y + y_diff
    else:
        right_end_y = base_right_p.y - y_diff

    ind.right_segment = Segment(base_right_p, Point(float(right_end_x),float(right_end_y)))

    base_left_p = ind.base.points[0]
    left_ray = Ray(base_right_p, angle= ind.left_angle/180 * pi)
    x_diff = ind.base.length * cos(ind.left_angle/180 * pi)
    y_diff = ind.base.length * sin(ind.left_angle/180 * pi)

    if left_ray.xdirection == "oo":
        left_end_x = base_left_p.x + x_diff
    else:
        left_end_x = base_left_p.x - x_diff
    if left_ray.ydirection == "oo":
        left_end_y = base_left_p.y + y_diff
    else:
        left_end_y = base_left_p.y - y_diff

    ind.left_segment = Segment(base_left_p, Point(float(left_end_x),float(left_end_y)))

    updated_rays = []
    reflected = 0
    for ray in ind.rays:
        intersection = ray.intersection(ind.right_segment)
        if intersection:
            intersection = intersection[0]
            reflected += 1
            orig_point = ray.p1
            parallel = ind.right_segment.parallel_line(orig_point)
            perpendicular = ind.right_segment.perpendicular_line(intersection)
            meet_point = parallel.intersection(perpendicular)[0]
            x_diff = (meet_point.x-orig_point.x)
            y_diff = (meet_point.y-orig_point.y)
            new_point = Point(meet_point.x + x_diff, meet_point.y + y_diff)

            reflected_ray = Ray(intersection,new_point)
            updated_rays.append(reflected_ray)
        else:
            intersection = ray.intersection(ind.left_segment)
            if intersection:
                intersection = intersection[0]
                reflected += 1
                orig_point = ray.p1
                parallel = ind.left_segment.parallel_line(orig_point)
                perpendicular = ind.left_segment.perpendicular_line(intersection)
                meet_point = parallel.intersection(perpendicular)[0]
                x_diff = (meet_point.x-orig_point.x)
                y_diff = (meet_point.y-orig_point.y)
                new_point = Point(meet_point.x + x_diff, meet_point.y + y_diff)

                reflected_ray = Ray(intersection,new_point)
                updated_rays.append(reflected_ray)
            else:
                updated_rays.append(ray)

    ind.reflections = updated_rays
    intersections = []
    for r in updated_rays:
        intersection = ind.road.intersection(r)  # průsečík se silnicí
        if intersection:
            intersections.append(intersection[0])

    ind.intersections_on = intersections

    return intersections, reflected


def mutate(individual):
    individual.right_angle += random.randint(-10,10)
    individual.right_angle = max(individual.angle_r_1, individual.right_angle)
    individual.right_angle = min(individual.angle_r_2, individual.right_angle)
    individual.left_angle += random.randint(-10,10)
    individual.left_angle = max(individual.angle_l_1, individual.left_angle)
    individual.left_angle = min(individual.angle_l_2, individual.left_angle)
    return individual


def mate(ind1, ind2):
    right = ind1.right_angle
    ind1.right_angle = ind2.right_angle
    ind2.right_angle = right
    return ind1, ind2


def evaluate(individual):
    individual.fitness = individual.right_angle
    all_intersections, un = compute_reflections(individual)
    intersections_x = []
    for i in all_intersections:
        intersections_x.append(float(i.x))

    intersections = sorted(intersections_x)
    start = individual.start
    end = individual.end
    section = (end-start)/len(intersections)
    no_sections = len(intersections)+1


    """
    i_cnt = 0
    fitness = 0
    for s in range(no_sections):
        if intersections[i_cnt] > s*section:
            upper = (s+1)*section
            if intersections[i_cnt] <= upper:
                fitness += 1
                i_cnt +=1
                while intersections[i_cnt] <= upper:
                    fitness -= 1
                    i_cnt += 1
            else:
                fitness -= 1
    """
    fitness = len(individual.intersections_on)
    #fitness = un
    return fitness


toolbox.register("select", tools.selTournament, tournsize=3)


def main():

    pop = toolbox.population(n=30)

    CXPB, MUTPB = 0.5, 0.2

    print("Start of evolution")

    # Evaluate the entire population
    fitnesses = list(map(evaluate, pop))
    for ind, fit in zip(pop, fitnesses):
        ind.fitness = fit

    print("  Evaluated %i individuals" % len(pop))

    compute_intersections(pop[0])
    pop[0].draw("orig")
    print(pop[0].right_angle)

    # Extracting all the fitnesses of
    fits = [ind.fitness for ind in pop]

    # Variable keeping track of the number of generations
    g = 0

    # Begin the evolution
    while g < 20:
        # A new generation
        g = g + 1
        print("-- Generation %i --" % g)

        # Select the next generation individuals
        offspring = toolbox.select(pop, len(pop))
        # Clone the selected individuals
        offspring = list(map(toolbox.clone, offspring))

        # Apply crossover and mutation on the offspring
        for child1, child2 in zip(offspring[::2], offspring[1::2]):

            # cross two individuals with probability CXPB
            if random.random() < CXPB:
                mate(child1, child2)

                # fitness values of the children
                # must be recalculated later
                child1.fitness = 0
                child2.fitness = 0

        for mutant in offspring:

            # mutate an individual with probability MUTPB
            if random.random() < MUTPB:
                mutate(mutant)
                mutant.fitness = 0

        # Evaluate the individuals with an invalid fitness
        invalid_ind = [ind for ind in offspring if ind.fitness == 0]
        fitnesses = map(evaluate, invalid_ind)
        for ind, fit in zip(invalid_ind, fitnesses):
            ind.fitness = fit

        print("  Evaluated %i individuals" % len(invalid_ind))

        # The population is entirely replaced by the offspring
        pop[:] = offspring

        # Gather all the fitnesses in one list and print the stats
        fits = [ind.fitness for ind in pop]

        best_ind = tools.selBest(pop, 1)[0]
        print("Best individual is %s, %s, %s" % (best_ind.right_angle, best_ind.fitness, best_ind.left_angle))
        best_ind.draw(g)
        print(best_ind.right_segment)

    print("-- End of (successful) evolution --")

    best_ind = tools.selBest(pop, 1)[0]
    print(best_ind.reflections)
    print("--")
    print(best_ind.reflected)

    print(best_ind.reflections)
    print("Best individual is %s, %s, %s" % (best_ind.right_angle, best_ind.fitness, best_ind.left_angle))


if __name__ == "__main__":
    main()
