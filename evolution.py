
import random
import copy as cp

from deap import base
from deap import creator
from deap import tools
from sympy.geometry import Line, Ray, Point, Segment
from sympy import pi, sin, cos

random.seed(5)


def compute_reflection(ray, surface, intersection):
    orig_point = ray.p1
    #print(float(ray.p1.x), float (ray.p1.y))
    parallel = surface.parallel_line(orig_point)
    perpendicular = surface.perpendicular_line(intersection)
    meet_point = parallel.intersection(perpendicular)[0]
    x_diff = (meet_point.x - orig_point.x)
    y_diff = (meet_point.y - orig_point.y)
    #print(float(x_diff), float(y_diff))
    new_point = Point(meet_point.x + x_diff, meet_point.y + y_diff)
    #print(float(intersection.x), float (intersection.y))
    #print(float(new_point.x), float (new_point.y))
    reflected_ray = Ray(intersection, new_point)
    return reflected_ray


class Individual:

    def __init__(self):
        self.rays = [
        [Ray(Point(0, 0), Point(1, 1/2))],
        [Ray(Point(0, 0), Point(1, 1/8))],
        [Ray(Point(0, 0), Point(1, 1/12))],
        [Ray(Point(0, 0), Point(1, 1/20))],
        [Ray(Point(0, 0), Point(1, -1/20))],
        [Ray(Point(0, 0), Point(1, -1/12))],
        [Ray(Point(0, 0), Point(1, -1/10))],
        [Ray(Point(0, 0), Point(1, -1/8))],
        [Ray(Point(0, 0), Point(1, -1/6))],
        [Ray(Point(0, 0), Point(1, -1/4))],
        [Ray(Point(0, 0), Point(1, -1/3))],
        [Ray(Point(0, 0), Point(1, -3/5))],
        [Ray(Point(0, 0), Point(1, -1/2))],
        [Ray(Point(0, 0), Point(1, -2/3))],
        [Ray(Point(0, 0), Point(1, -3/4))],
        [Ray(Point(0, 0), Point(1, -4/5))],
        [Ray(Point(0, 0), Point(1, -5/6))],
        [Ray(Point(0, 0), Point(1, -8/9))],
        [Ray(Point(0, 0), Point(1, -14/15))],
        [Ray(Point(0, 0), Point(1, -19/20))],
        [Ray(Point(0, 0), Point(1, -20/19))],
        [Ray(Point(0, 0), Point(1, -15/14))],
        [Ray(Point(0, 0), Point(1, -9/8))],
        [Ray(Point(0, 0), Point(1, -6/5))],
        [Ray(Point(0, 0), Point(1, -5/4))],
        [Ray(Point(0, 0), Point(1, -4/3))],
        [Ray(Point(0, 0), Point(1, -3/2))],
        [Ray(Point(0, 0), Point(1, -2))],
        [Ray(Point(0, 0), Point(1, -5/3))],
        [Ray(Point(0, 0), Point(1, -3))],
        [Ray(Point(0, 0), Point(1, -4))],
        [Ray(Point(0, 0), Point(1, -6))],
        [Ray(Point(0, 0), Point(1, -8))],
        [Ray(Point(0, 0), Point(1, -10))],
        [Ray(Point(0, 0), Point(1, -12))],
        [Ray(Point(0, 0), Point(1, -20))],
        [Ray(Point(0, 0), Point(-1, -20))],
        [Ray(Point(0, 0), Point(-1, -12))],
        [Ray(Point(0, 0), Point(-1, -8))],
        [Ray(Point(0, 0), Point(-1, -2))]
        ]

        self.original_rays = self.rays

        self.base = Segment(Point(-141, -141), Point(141, 141))

        upper_ray = self.rays[0][0].slope
        self.road = Segment(Point(-1000, -4000), Point(6000, -4000))
        self.start = -1000
        self.end = 6000
        self.angle_r_1 = 90
        self.angle_r_2 = 180
        self.angle_l_1 = 30
        self.angle_l_2 = 120
        self.right_angle = random.randint(self.angle_r_1,self.angle_r_2)
        self.left_angle = random.randint(self.angle_l_1,self.angle_l_2)

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
            f.write('<rect x="100" y="950" width="900" height="70" fill="gray"/>') # výložník + lampa

            for r_sequence in self.reflected:
                #print("len")
                color = "(250, 216, 22)"
                for r in r_sequence:
                    f.write('<line x1="{0}" y1="{1}" x2="{2}" y2="{3}" style="stroke:rgb{4};stroke-width:20"/>\n'
                        .format(float(r.points[0].x) + x_offset, - float(r.points[0].y) + y_offset,
                                float(r.points[1].x) + x_offset, - float(r.points[1].y) + y_offset, color))
                intersection = self.road.intersection(r)
                if intersection:
                    intersection = intersection[0]
                    f.write('<line x1="{0}" y1="{1}" x2="{2}" y2="{3}" style="stroke:rgb(250, 216, 22);stroke-width:20"/>\n'
                    .format(float(r.points[0].x) + x_offset, - float(r.points[0].y) + y_offset,
                            float(intersection.x) + x_offset, - float(intersection.y) + y_offset))
                else:
                    x_diff = float(r.points[1].x - r.points[0].x) * 10000
                    y_diff = float(r.points[1].y - r.points[0].y) * 10000
                    f.write(
                        '<line x1="{0}" y1="{1}" x2="{2}" y2="{3}" style="stroke:rgb(196, 185, 118);stroke-width:20"/>'
                        '\n'.format(float(r.points[0].x) + x_offset, - float(r.points[0].y) + y_offset,
                                    float(r.points[0].x) + x_offset + x_diff,
                                    -float(r.points[0].y) + y_offset - y_diff))

            """
            for r in self.rays: #všechny paprsky
                x = float(10000*r.points[1].x)
                y = float(10000*r.points[1].y)
                f.write('<line x1="{0}" y1="{1}" x2="{2}" y2="{3}" style="stroke:rgb(196, 185, 118);stroke-width:20;stroke-dasharray:50,50" />'
                        '\n'.format(x_offset, y_offset, x+x_offset, -y+y_offset))


            for r in self.reflections:
                intersection = self.road.intersection(r) #průsečík se silnicí
                if intersection:
                    intersection = intersection[0]
                    f.write('<line x1="{0}" y1="{1}" x2="{2}" y2="{3}" style="stroke:rgb(250, 216, 22);stroke-width:20" />'
                        .format(float(r.points[0].x) + x_offset, - float(r.points[0].y) + y_offset,
                                float(intersection.x) + x_offset, -float(intersection.y) + y_offset))
                    if r.p1 != Point(0,0):
                        f.write('<line x1="{0}" y1="{1}" x2="{2}" y2="{3}" style="stroke:rgb(250, 216, 22);stroke-width:20" />'
                        .format(float(r.points[0].x) + x_offset, - float(r.points[0].y) + y_offset,
                                0 + x_offset, 0 + y_offset))
                else:
                    if r.p1 != Point(0,0):
                        x_diff = float(r.points[1].x - r.points[0].x) * 10
                        y_diff = float(r.points[1].y - r.points[0].y) * 10
                        

                        f.write('<line x1="{0}" y1="{1}" x2="{2}" y2="{3}" style="stroke:rgb(196, 185, 118);stroke-width:20" />'
                            '\n'.format(float(r.points[0].x) + x_offset, - float(r.points[0].y) + y_offset, float(r.points[0].x)+x_offset + x_diff, -float(r.points[0].y)+y_offset - y_diff))
            """
            step = 7000 / 40
            for i in range(20):
                f.write('<rect x="{0}" y="5000" width="{1}" height="50" fill="gray"/>'.format(i*step*2,step)) #silnice




            #základna
            f.write('<line x1="{0}" y1="{1}" x2="{2}" y2="{3}" style="stroke:gray;stroke-width:40"/>'.format(
                self.base.p1.x + x_offset, -self.base.p1.y + y_offset,
                self.base.p2.x + x_offset, -self.base.p2.y + y_offset))

            #pravá laple
            f.write('<line x1="{0}" y1="{1}" x2="{2}" y2="{3}" style="stroke:gray;stroke-width:40"/>'.format(
                self.base.p2.x + x_offset, -self.base.p2.y + y_offset,
                float(self.right_segment.p2.x) + x_offset, float(-self.right_segment.p2.y) + y_offset))

            # levá laple
            f.write('<line x1="{0}" y1="{1}" x2="{2}" y2="{3}" style="stroke:gray;stroke-width:40"/>'.format(
                self.base.p1.x + x_offset, -self.base.p1.y + y_offset,
                float(self.left_segment.p2.x) + x_offset, float(-self.left_segment.p2.y) + y_offset))

            f.write('</svg>')

    def compute_right_segment(self):
        base_right_p = self.base.points[1]
        right_ray = Ray(base_right_p, angle= self.right_angle/180 * pi)
        x_diff = self.base.length * cos(self.right_angle/180 * pi)
        y_diff = self.base.length * sin(self.right_angle/180 * pi)
        if right_ray.xdirection == "oo":
            right_end_x = base_right_p.x + x_diff
        else:
            right_end_x = base_right_p.x - x_diff
        if right_ray.ydirection == "oo":
            right_end_y = base_right_p.y + y_diff
        else:
            right_end_y = base_right_p.y - y_diff

        self.right_segment = Segment(base_right_p, Point(float(right_end_x),float(right_end_y)))

    def compute_left_segment(self):
        base_left_p = self.base.points[0]
        left_ray = Ray(base_left_p, angle= self.left_angle/180 * pi)
        x_diff = self.base.length * cos(self.left_angle/180 * pi)
        y_diff = self.base.length * sin(self.left_angle/180 * pi)

        if left_ray.xdirection == "oo":
            left_end_x = base_left_p.x + x_diff
        else:
            left_end_x = base_left_p.x - x_diff
        if left_ray.ydirection == "oo":
            left_end_y = base_left_p.y + y_diff
        else:
            left_end_y = base_left_p.y - y_diff

        self.left_segment = Segment(base_left_p, Point(float(left_end_x),float(left_end_y)))



creator.create("FitnessMax", base.Fitness, weights=(1.0,))
creator.create("Individual", list, fitness=creator.FitnessMax)

toolbox = base.Toolbox()

toolbox.register("population", tools.initRepeat, list, Individual)


def compute_intersections(ind):
    inter_array = []
    for ray in ind.rays:
        inter_point = ind.road.intersection(ray[-1])
        if inter_point != []:
            inter_array.append(inter_point)
    ind.intersections_on = inter_array


def compute_reflections(ind):
    compute_intersections(ind)

    ind.compute_right_segment()
    ind.compute_left_segment()

    reflected = 0
    #print("new_ind")
    #print(ind)
    reflected_rays = []
    for ray in ind.original_rays:
        new_ray = cp.deepcopy(ray)
        #print("new_ray")
        #print(ray)
        continue_left = True
        continue_right = True
        previous_i_r = Point(0,0)
        previous_i_l = Point(0,0)
        while continue_left or continue_right:
            #print(reflected)
            #print(float(previous_i_r.x), float(previous_i_r.y))
            continue_left = False
            continue_right = False
            intersection_r = new_ray[-1].intersection(ind.right_segment)
            if intersection_r and intersection_r[0] != previous_i_r:
                #print("R")
                previous_i_r = intersection_r[0]
                intersection = intersection_r[0]
                reflected += 1
                reflected_ray = compute_reflection(new_ray[-1], ind.right_segment, intersection)
                new_ray[-1] = Ray(new_ray[-1].p1,intersection)
                new_ray.append(reflected_ray)
                continue_right = True
            intersection_l = new_ray[-1].intersection(ind.left_segment)
            if intersection_l and intersection_l[0] != previous_i_l:
                #print("L")
                previous_i_l = intersection_l[0]
                intersection = intersection_l[0]
                reflected += 1
                reflected_ray = compute_reflection(new_ray[-1], ind.left_segment, intersection)
                new_ray[-1] = Ray(new_ray[-1].p1,intersection)
                new_ray.append(reflected_ray)
                continue_left = True
        reflected_rays.append(new_ray)
    ind.reflected = reflected_rays
    intersections = []

    for r in ind.reflected:
        intersection = ind.road.intersection(r[-1])  # průsečík se silnicí
        if intersection:
            intersections.append(intersection[0])

    ind.intersections_on = intersections

    return intersections, reflected


def mutate(individual):
    #print("b " + str( individual.right_angle))
    individual.right_angle += random.randint(-5,5)
    individual.right_angle = max(individual.angle_r_1, individual.right_angle)
    individual.right_angle = min(individual.angle_r_2, individual.right_angle)
    #print(individual.right_angle)
    individual.left_angle += random.randint(-5,5)
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
    start = individual.start
    end = individual.end
    intersections_x = []
    for i in all_intersections:
        intersections_x.append(float(i.x))
    #intersections_x.append(end)
    intersections = sorted(intersections_x)

    section_length = (end-start)/(len(intersections)+1)
    no_sections = len(intersections)+1
    parts = 40
    part_length = (end-start) / 40
    fitness = 0
    for p in range(parts):
        counter = 0
        for i in intersections:
            if i > start + p*part_length and i <= start + (p+1)*part_length:
                counter += 1
        fitness += abs(counter - 1)
    """
    for i in range(len(intersections_x)-1):
        gap = intersections_x[i+1] - intersections_x[i]
        difference = abs(gap-section_length)
        fitness -= difference

   
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
    #fitness = len(all_intersections)
    #fitness = un
    return -fitness


toolbox.register("select", tools.selTournament, tournsize=3)


def main():

    pop = toolbox.population(n=30)

    CXPB, MUTPB = 0.5, 0.4

    print("Start of evolution")

    # Evaluate the entire population
    fitnesses = list(map(evaluate, pop))
    for ind, fit in zip(pop, fitnesses):
        ind.fitness = fit

    print("  Evaluated %i individuals" % len(pop))

    #for i in range(len(pop)):
        #pop[i].draw(i)

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
            if random.random() < 0:
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
        print(fits)
        rang = [ind.right_angle for ind in pop]
        print(rang)

        best_ind = tools.selBest(pop, 1)[0]
        print("Best individual is %s, %s, %s" % (best_ind.left_angle, best_ind.fitness, best_ind.right_angle))
        best_ind.draw(g)

    print("-- End of (successful) evolution --")

    best_ind = tools.selBest(pop, 1)[0]
    print("--")
    print(best_ind.reflected)

    print("Best individual is %s, %s, %s" % (best_ind.left_angle, best_ind.fitness, best_ind.right_angle))


if __name__ == "__main__":
    main()
