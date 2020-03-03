
import random

from deap import base
from deap import creator
from deap import tools

random.seed(5)


class Individual:
    rays = [1/2, 1/8, -1/8, -1/3, -1/2, -2/3, -6/7, -1, -7/6, -3/2, -2, -3, -8, 8, 2]
    upper_ray = rays[0]
    road = -4000
    start = -1000
    end = 6000
    right_angle = random.randint(-90, 90)
    left_angle = random.randint(-90, 90)

    fitness = right_angle
    reflections = []
    reflected = []
    intersections_on = []
    intersections_out = []

    def draw(self, name):
        svg_name = name + ".svg"
        with open(svg_name, "w") as f:
            x_offset = 1100
            y_offset = 800
            f.write('<svg width="8000" height="5000">')
            f.write('<rect width="8000" height="5000" fill="black"/>')
            f.write('<rect x="100" y="770" width="100" height="4070" fill="gray"/>')
            f.write('<rect x="100" y="770" width="1000" height="70" fill="gray"/>')
            f.write('<rect x="900" y="785" width="400" height="40" fill= "gray" transform = "rotate(-45 1100 800)"/>')
            f.write('<rect x="1210" y="652" width="400" height="40" fill= "gray" transform = "rotate({0} 1230 672)"/>'.format(45-self.right_angle))
            f.write('<rect x="950" y="918" width="400" height="40" fill= "gray" transform = "rotate({0} 970 938)"/>'.format(45+self.right_angle))

            f.write('<rect x="100" y="4800" width="7000" height="50" fill="gray"/>')
            """
            for c in range(len(self.reflections)):
                print(c)
                r = self.reflections[c]
                i = self.reflected[c]
                f.write('<line x1="{0}" y1="{1}" x2="{2}" y2="{3}" style="stroke:red;stroke-width:0,2" />'.format(x_offset, y_offset, r[0]+x_offset, r[1]+y_offset))
                f.write('<line x1="{0}" y1="{1}" x2="{2}" y2="{3}" style="stroke:blue;stroke-width:0,2" />'.format(r[0] + x_offset, r[1] + y_offset, i + x_offset))
            
            for i in self.intersections_on:
                f.write('<line x1="{0}" y1="{1}" x2="{2}" y2="{3}" style="stroke:rgb(250, 216, 22);stroke-width:20" />'.format(x_offset, y_offset, i+x_offset, -self.road+y_offset))
            for i in self.intersections_out:
                f.write(
                    '<line x1="{0}" y1="{1}" x2="{2}" y2="{3}" style="stroke:rgb(250, 117, 22);stroke-width:20" />'.format(
                        x_offset, y_offset, i + x_offset, -self.road+y_offset))
            """
            for r in self.rays:
                if r <= self.upper_ray:
                    x = 10000
                else:
                    x = -10000
                f.write('<line x1="{0}" y1="{1}" x2="{2}" y2="{3}" style="stroke:rgb(250, 117, 22);stroke-width:20" />'.format(x_offset, y_offset, x+x_offset, -r*x+y_offset))
            for i in self.intersections_on:
                f.write('<line x1="{0}" y1="{1}" x2="{2}" y2="{3}" style="stroke:rgb(250, 216, 22);stroke-width:20" />'.format(x_offset, y_offset, i + x_offset, -self.road + y_offset))
            f.write('</svg>')



creator.create("FitnessMax", base.Fitness, weights=(1.0,))
creator.create("Individual", list, fitness=creator.FitnessMax)

toolbox = base.Toolbox()

toolbox.register("population", tools.initRepeat, list, Individual)


def compute_intersections(ind):
    inter_array = []
    inter_array_off = []
    for item in ind.rays:
        x_point = ind.road / (item)
        if x_point > ind.start and x_point < ind.end:
            inter_array.append(x_point)
        else:
            inter_array_off.append(x_point)
        ind.intersections_on = inter_array
        ind.intersections_out = inter_array_off



def compute_reflections(ind):
    inter_array = []
    refl_array = []
    x_low = 1/2
    x_up = 3/2
    x_dir = ind.right_angle/90
    const = (90 - ind.right_angle)/180
    undirect = 0
    updated_rays = []
    for ray in ind.rays:
        if (x_dir-ray) != 0:
            inter_x = -const / (x_dir-ray)
            if inter_x > x_low and inter_x < x_up:
                undirect += 1
                a = ray
                b = -1
                c = 0
                d = x_dir
                e = -1
                f = - const
                new_slope = (a*e*e - a*d*d - 2*b*d*e)/(b*e*e - b*d*d - 2*a*d*e)
                inter_y = (c*d - a*f)/(b*d - a*e)
                refl_array.append((inter_x,inter_y))
                const = inter_y - new_slope*inter_x
                updated_rays.append((new_slope,const))
    ind.reflections = refl_array

    for item in updated_rays:
        x_point = (ind.road + item[1]) / (item[0])
        #if x_point > ind.start and x_point < ind.end:
        inter_array.append(x_point)
        ind.reflected = inter_array
    return inter_array, undirect


def mutate(individual):
    individual.right_angle += random.randint(-10,10)
    individual.right_angle = max(-90, individual.right_angle)
    individual.right_angle = min(90, individual.right_angle)
    return individual


def mate(ind1, ind2):
    right = ind1.right_angle 
    ind1.right_angle = ind2.right_angle
    ind2.right_angle = right
    return ind1, ind2
    

def evaluate(individual):
    individual.fitness = individual.right_angle
    #return individual.right_angle
    all_intersections, un = compute_reflections(individual)
    """
    intersections = sorted(all_intersections)
    start = individual.start
    end = individual.end
    section = (end-start)/len(intersections)
    no_sections = len(intersections)
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
    fitness = un
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
        print("Best individual is %s, %s" % (best_ind.right_angle, best_ind.fitness))
    
    print("-- End of (successful) evolution --")
    
    best_ind = tools.selBest(pop, 1)[0]
    print(best_ind.reflections)
    print("--")
    print(best_ind.reflected)

    print(best_ind.reflections)
    print("Best individual is %s, %s" % (best_ind.right_angle, best_ind.fitness))


if __name__ == "__main__":
    main()
