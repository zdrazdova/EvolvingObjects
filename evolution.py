
import random

from deap import base
from deap import creator
from deap import tools

class Individual:
    rays = [1/2, 1/8, -1/8, -1/3, -1/2, -2/3, -6/7, -1, -7/6, -3/2, -2, -3, -8, 8, 2]
    road = -4000
    start = -1000
    end = 6000
    right_angle = random.randint(0,90)
    left_angle = random.randint(0,90)
    fitness = right_angle

creator.create("FitnessMax", base.Fitness, weights=(1.0,))
creator.create("Individual", list, fitness=creator.FitnessMax)

toolbox = base.Toolbox()


toolbox.register("population", tools.initRepeat, list, Individual)

def mutate(individual):
    individual.right_angle += random.gauss(0,20)
    individual.left_angle += random.gauss(0,20)
    individual.right_angle = max(0, individual.right_angle)
    individual.left_angle = max(0, individual.left_angle)
    individual.right_angle = min(90, individual.right_angle)
    individual.left_angle = min(90, individual.left_angle)
    return individual

def mate(ind1, ind2):
    right = ind1.right_angle 
    ind1.right_angle = ind2.right_angle
    ind2.right_angle = right
    return ind1, ind2
    

def evaluate(individual):
    individual.fitness = individual.right_angle
    return individual.right_angle
    intersections = sorted(compute_intersections(left, right, line))
    start = line.start
    end = line.end
    section = (end-start)/len(intercestions)
    no_sections = len(intersections)
    i_cnt = 0
    fitness = 0
    for s in no_sections:
        if intercestions[i_cnt] > s*section:
            upper = (s+1)*section
            if intercestions[i_cnt] <= upper:
                fitness += 1
                i_cnt +=1
                while intercestions[i_cnt] <= upper:
                    fitness -= 1
                    i_cnt += 1
            else:
                fitness -= 1

    return fitness

toolbox.register("select", tools.selTournament, tournsize=3)

#----------

def main():
    random.seed(64)

    pop = toolbox.population(n=30)

    CXPB, MUTPB = 0.5, 0.2
    
    print("Start of evolution")
    
    # Evaluate the entire population
    fitnesses = list(map(evaluate, pop))
    for ind, fit in zip(pop, fitnesses):
        ind.fitness = fit
    
    print("  Evaluated %i individuals" % len(pop))

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
        
        length = len(pop)
        mean = sum(fits) / length
        sum2 = sum(x*x for x in fits)
        std = abs(sum2 / length - mean**2)**0.5
        
        print("  Min %s" % min(fits))
        print("  Max %s" % max(fits))
        print("  Avg %s" % mean)
        print("  Std %s" % std)
    
    print("-- End of (successful) evolution --")
    
    best_ind = tools.selBest(pop, 1)[0]
    print("Best individual is %s, %s, %s" % (best_ind.right_angle, best_ind.left_angle, best_ind.fitness))

if __name__ == "__main__":
    main()
