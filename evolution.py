import random
import math

from auxiliary import draw, log_stats_init, log_stats_append
from custom_geometry import compute_intersections, compute_reflections_two_segments, \
    compute_reflection_multiple_segments
from custom_operators import mate, mutate_angle, mutate_length, shift_one_segment, rotate_one_segment
from quality_assesment import glare_reduction, efficiency, illuminance_uniformity, light_pollution

from deap import base
from deap import creator
from deap import tools
from deap.tools import HallOfFame
from python_json_config import ConfigBuilder

from component import Component
from environment import Environment
from quality_precalculations import compute_segments_intensity, compute_proportional_intensity


def evaluate(individual: Component, env: Environment):
    if env.configuration == "two connected":
        compute_reflections_two_segments(individual, env.reflective_factor)
    if env.configuration == "multiple free":
        compute_reflection_multiple_segments(individual)
    if env.quality_criterion == "light pollution":
        return light_pollution(individual.original_rays)
    if env.quality_criterion == "glare reduction":
        return glare_reduction(individual)
    road_intersections = compute_intersections(individual.original_rays, env.road, env.cosine_error)
    if env.quality_criterion == "efficiency":
        return efficiency(road_intersections, individual.original_rays)
    if env.quality_criterion == "illuminance uniformity":
        segments_intensity = compute_segments_intensity(road_intersections, env.road_sections, env.road_start, env.road_length)
        individual.segments_intensity_proportional = compute_proportional_intensity(segments_intensity)
        return illuminance_uniformity(segments_intensity)
    return efficiency(individual)


def evolution(env: Environment, number_of_rays: int, ray_distribution: str,
              angle_lower_bound: int, angle_upper_bound: int, length_lower_bound: int, length_upper_bound: int,
              no_of_reflective_segments: int, distance_limit: int, length_limit: int,
              population_size: int, number_of_generations: int,
              mut_angle_prob: float, mut_length_prob: float, xover_prob: float):

    # Initiating evolutionary algorithm
    creator.create("Fitness", base.Fitness, weights=(1.0,))
    creator.create("Individual", Component, fitness=creator.Fitness)
    toolbox = base.Toolbox()
    toolbox.register("individual", creator.Individual, env=env, number_of_rays=number_of_rays,
                     ray_distribution=ray_distribution, angle_lower_bound=angle_lower_bound,
                     angle_upper_bound=angle_upper_bound, length_lower_bound=length_lower_bound,
                     length_upper_bound=length_upper_bound, no_of_reflective_segments=no_of_reflective_segments,
                     distance_limit=distance_limit, length_limit=length_limit)
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)
    toolbox.register("select", tools.selTournament, tournsize=2)

    # Initiating first population
    pop = toolbox.population(n=population_size)

    draw(pop[0], f"{0}", env)
    # Evaluating fitness
    fitnesses = []
    for item in pop:
        fitnesses.append(evaluate(item, env))
    for ind, fit in zip(pop, fitnesses):
        ind.fitness = fit

    # Rendering individuals in initial population as images
    for i in range(len(pop)):
        draw(pop[i], f"{i}", env)
    print("Drawing initial population finished")

    stats_line = f"0, {max(fitnesses)}, {sum(fitnesses)/population_size}"
    log_stats_init(f"stats", stats_line)

    # Initiating elitism
    hof = HallOfFame(1)

    print("Start of evolution")

    # Begin the evolution
    for g in range(number_of_generations):
        # A new generation
        print(f"-- Generation {g} --")

        # Select the next generation individuals
        offspring = toolbox.select(pop, len(pop))
        # Clone the selected individuals
        offspring = list(map(toolbox.clone, offspring))

        # Apply crossover and mutation on the offspring
        for child1, child2 in zip(offspring[::2], offspring[1::2]):
            # cross two individuals with probability xover_prob
            if random.random() < xover_prob:
                mate(child1, child2)
                # fitness values of the children must be recalculated later
                child1.fitness = 0
                child2.fitness = 0

        for mutant in offspring:
            if random.random() < 0:
                mutant.reflective_segments = shift_one_segment(mutant.reflective_segments, "x", 100)
                mutant.fitness = 0
            if random.random() < 0:
                mutant.reflective_segments = shift_one_segment(mutant.reflective_segments, "y", 100)
                mutant.fitness = 0
            if random.random() < 0:
                mutant.reflective_segments = rotate_one_segment(mutant.reflective_segments, 30)
                mutant.fitness = 0

            # mutate an individual with probability mut_angle_prob and mut_length_prob
            if random.random() < mut_angle_prob:
                mutate_angle(mutant)
                mutant.fitness = 0
            if random.random() < mut_length_prob:
                mutate_length(mutant, length_upper_bound, length_lower_bound)
                mutant.fitness = 0

        # Evaluate the individuals with an invalid fitness
        invalid_ind = [ind for ind in offspring if ind.fitness == 0]
        fitnesses = []
        for item in invalid_ind:
            fitnesses.append(evaluate(item, env))
        for ind, fit in zip(invalid_ind, fitnesses):
            ind.fitness = fit

        print(f"  Evaluated {len(invalid_ind)} individuals")
        # The population is entirely replaced by the offspring
        pop[:] = offspring
        hof.update(pop)

        # best_ind = tools.selBest(pop, 1)[0]
        best_ind = hof[0]

        fitnesses = []
        for item in pop:
            fitnesses.append(evaluate(item, env))
        print(fitnesses)

        stats_line = f"{g+1}, {best_ind.fitness}, {sum(fitnesses) / population_size}"
        log_stats_append(f"stats", stats_line)
        print(f"Best individual has fitness: {best_ind.fitness}")
        draw(best_ind, f"best{g}", env)

    print("-- End of (successful) evolution --")
    print("--")


def main():
    # create config parser
    builder = ConfigBuilder()
    # parse configuration from file parameters.json
    config = builder.parse_config('parameters.json')

    # Load parameters for environment
    base_length = config.lamp.base_length
    base_slope = config.lamp.base_angle
    road_start = config.road.start
    road_end = config.road.end
    road_depth = config.road.depth
    road_sections = config.road.sections
    configuration = config.lamp.configuration

    # Load parameters for evaluation
    criterion = config.evaluation.criterion
    cosine_error = config.evaluation.cosine_error
    reflective_factor = config.evaluation.reflective_factor

    # Init environment
    env = Environment(base_length, base_slope, road_start, road_end, road_depth, road_sections,
                      criterion, cosine_error, reflective_factor, configuration)

    # Load parameters for LED
    number_of_rays = config.lamp.number_of_rays
    ray_distribution = config.lamp.ray_distribution

    # Load limits for two connected reflective surfaces
    angle_lower_bound = config.lamp.two_connected.angle_lower_bound
    angle_upper_bound = config.lamp.two_connected.angle_upper_bound
    length_lower_bound = config.lamp.two_connected.length_lower_bound
    length_upper_bound = config.lamp.two_connected.length_upper_bound

    # Load limits for multiple free reflective surfaces
    no_of_reflective_segments = config.lamp.multiple_free.no_of_reflective_segments
    distance_limit = config.lamp.multiple_free.distance_limit
    length_limit = config.lamp.multiple_free.length_limit


    population_size = config.evolution.population_size
    number_of_generations = config.evolution.number_of_generations

    # Load parameters for evolution
    operators = config.evolution.operators
    angle_mut_prob = operators.mutation.angle_mutation_prob
    length_mut_prob = operators.mutation.length_mutation_prob
    xover_prob = operators.xover_prob


    # Run evolution algorithm
    evolution(env, number_of_rays, ray_distribution, angle_lower_bound, angle_upper_bound,
              length_lower_bound, length_upper_bound, no_of_reflective_segments, distance_limit, length_limit,
              population_size, number_of_generations, angle_mut_prob, length_mut_prob, xover_prob)


if __name__ == "__main__":
    random.seed(2)
    main()
