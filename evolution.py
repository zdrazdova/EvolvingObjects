import random
from math import factorial
from typing import List

from deap.base import Fitness

from auxiliary import draw, log_stats_init, log_stats_append, check_parameters_environment, check_parameters_evolution, \
    choose_unique
from custom_geometry import compute_intersections, compute_reflections_two_segments, \
    compute_reflection_multiple_segments, recalculate_intersections
from custom_operators import mutate_angle, mutate_length, shift_one_segment, rotate_one_segment, \
    resize_one_segment, x_over_multiple_segments, x_over_two_segments, tilt_base
from quality_assessment import efficiency, illuminance_uniformity, light_pollution, obtrusive_light_elimination

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
        compute_reflection_multiple_segments(individual, env.reflective_factor, env.reflections_timeout)
    if env.quality_criterion == "efficiency":
        return efficiency(individual.original_rays)
    road_intersections = compute_intersections(individual.original_rays, env.road, env.cosine_error)
    if env.number_of_led > 1:
        road_intersections = recalculate_intersections(road_intersections, env.number_of_led, env.separating_distance,
                                                       env.modification, env.road_start, env.road_end)
    if env.quality_criterion == "obtrusive light":
        return obtrusive_light_elimination(individual.original_rays, road_intersections, env.number_of_led)
    individual.segments_intensity = compute_segments_intensity(road_intersections, env.road_sections, env.road_start,
                                                    env.road_length, env.cosine_error)
    individual.segments_intensity_proportional = compute_proportional_intensity(individual.segments_intensity)
    if env.quality_criterion == "illuminance uniformity":
        return illuminance_uniformity(individual.segments_intensity)
    if env.quality_criterion == "weighted sum":
        individual.fitness_array = [efficiency(individual.original_rays), illuminance_uniformity(individual.segments_intensity),
                                    obtrusive_light_elimination(individual.original_rays, road_intersections, env.number_of_led),
                                    -env.number_of_led*light_pollution(individual.original_rays)]
        weights = env.weights
        product = [x * y for x, y in zip(individual.fitness_array, weights)]
        return sum(product)
    if env.quality_criterion == "nsgaii":
        return Fitness((efficiency(individual.original_rays), illuminance_uniformity(individual.segments_intensity),
                        obtrusive_light_elimination(individual.original_rays, road_intersections, env.number_of_led),
                        env.number_of_led * light_pollution(individual.original_rays)))
    return efficiency(individual)


def evolution(env: Environment, number_of_rays: int, ray_distribution: str,
              angle_lower_bound: int, angle_upper_bound: int, length_lower_bound: int, length_upper_bound: int,
              no_of_reflective_segments: int, distance_limit: int, length_limit: int,
              population_size: int, number_of_generations: int,
              xover_prob: float, mut_angle_prob: float, mut_length_prob: float,
              shift_segment_prob: float, rotate_segment_prob: float, resize_segment_prob: float, tilt_base_prob: float,
              base_length: int, base_slope: int, base_angle_limit_min: int, base_angle_limit_max: int):

    # Initiating evolutionary algorithm
    creator.create("Fitness", base.Fitness, weights=(1.0,))
    base.Fitness.weights = (1.0, 10.0, 5.0, -1.0)
    creator.create("Individual", Component, fitness=creator.Fitness)
    toolbox = base.Toolbox()
    toolbox.register("individual", creator.Individual, env=env, number_of_rays=number_of_rays,
                     ray_distribution=ray_distribution, angle_lower_bound=angle_lower_bound,
                     angle_upper_bound=angle_upper_bound, length_lower_bound=length_lower_bound,
                     length_upper_bound=length_upper_bound, no_of_reflective_segments=no_of_reflective_segments,
                     distance_limit=distance_limit, length_limit=length_limit, base_length=base_length,
                     base_slope=base_slope)
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)
    toolbox.register("evaluate", evaluate)
    if env.quality_criterion == "nsgaii":
        toolbox.register("select", tools.selNSGA2)
    else:
        toolbox.register("select", tools.selTournament, tournsize=2)


    # Initiating first population
    pop = toolbox.population(n=population_size)

    # Evaluating fitness
    fitnesses = []
    for item in pop:
        fitnesses.append(evaluate(item, env))
    for ind, fit in zip(pop, fitnesses):
        ind.fitness = fit

    # Rendering individuals in initial population as images
    #for i in range(len(pop)):
    #    draw(pop[i], f"{i}", env)
    #print("Drawing initial population finished")

    if env.quality_criterion != "nsgaii":
        if env.configuration == "two connected":
            stats_line = f"generation, best fitness, average fitness, fitness array, left segment angle, " \
                     f"left segment length, right segment angle, right segment length  \n"
        else:
            stats_line = f"generation, best fitness, average fitness, fitness array, reflective segments  \n"
        log_stats_init(f"stats", stats_line)

    # Initiating elitism

    if env.quality_criterion == "nsgaii":
        pop = toolbox.select(pop, len(pop))
        hof = tools.ParetoFront()
        hof.update(pop)
    else:
        hof = HallOfFame(1)
        hof.update(pop)

    print("Start of evolution")

    # Begin the evolution
    for g in range(number_of_generations):
        # A new generation
        print(f"-- Generation {g} --")

        # Select the next generation individuals
        if env.quality_criterion == "nsgaii":
            offspring = tools.selTournamentDCD(pop, len(pop))
            offspring = [toolbox.clone(ind) for ind in offspring]
        else:
            offspring = toolbox.select(pop, len(pop))
            offspring = list(map(toolbox.clone, offspring))

        # Apply crossover and mutation on the offspring

        for child1, child2 in zip(offspring[::2], offspring[1::2]):
            # cross two individuals with probability xover_prob
            if env.configuration == "multiple free":
                if random.random() < xover_prob:
                    x_over_multiple_segments(child1, child2)
                    # fitness values of the children must be recalculated later
                    child1.fitness = None
                    child2.fitness = None
            if env.configuration == "two connected":
                if random.random() < xover_prob:
                    x_over_two_segments(child1, child2)
                    # fitness values of the children must be recalculated later
                    child1.fitness = None
                    child2.fitness = None

        for mutant in offspring:
            if env.configuration == "multiple free":
                if random.random() < shift_segment_prob:
                    mutant.reflective_segments = shift_one_segment(mutant.reflective_segments, "x")
                    mutant.fitness = None
                if random.random() < shift_segment_prob:
                    mutant.reflective_segments = shift_one_segment(mutant.reflective_segments, "y")
                    mutant.fitness = None
                if random.random() < rotate_segment_prob:
                    mutant.reflective_segments = rotate_one_segment(mutant.reflective_segments)
                    mutant.fitness = None
                if random.random() < resize_segment_prob:
                    mutant.reflective_segments = resize_one_segment(mutant.reflective_segments)
                    mutant.fitness = None
                if random.random() < tilt_base_prob:
                    mutant.base_slope = tilt_base(mutant.base_slope, base_angle_limit_min, base_angle_limit_max)
                    mutant.calculate_base()
                    mutant.original_rays = mutant.sample_rays(number_of_rays, ray_distribution)
                    mutant.fitness = None

            if env.configuration == "two connected":
                if random.random() < mut_angle_prob:
                    mutate_angle(mutant)
                    mutant.fitness = None
                if random.random() < mut_length_prob:
                    mutate_length(mutant, length_upper_bound, length_lower_bound)
                    mutant.fitness = None

        # Evaluate the individuals with an invalid fitness
        invalid_ind = [ind for ind in offspring if ind.fitness is None]
        fitnesses = []
        for item in invalid_ind:
            fitnesses.append(evaluate(item, env))
        for ind, fit in zip(invalid_ind, fitnesses):
            ind.fitness = fit

        if env.quality_criterion == "nsgaii":
            pop = toolbox.select(offspring + pop, population_size)
        else:
            pop[:] = offspring

        hof.update(pop)
        best_ind = hof[0]

        fitnesses = []
        for item in pop:
            fitnesses.append(item.fitness)
        print(fitnesses)

        if env.configuration == "two connected" and env.quality_criterion != "nsgaii":
            stats_line = f"{g+1}, {best_ind.fitness}, {sum(fitnesses) / population_size}, {best_ind.fitness_array}, " \
                     f"left angle: {180-best_ind.left_angle+best_ind.base_slope}, " \
                     f"left length: {best_ind.left_length_coef*best_ind.base_length}, " \
                     f"right angle: {best_ind.right_angle-best_ind.base_slope}, " \
                     f"right length: {best_ind.right_length_coef*best_ind.base_length} "
            log_stats_append(f"stats", stats_line)

        if env.configuration == "multiple free" and env.quality_criterion != "nsgaii":
            stats_line = f"{g + 1}, {best_ind.fitness}, {sum(fitnesses) / population_size}, {best_ind.fitness_array}, "
            for reflective_segment in best_ind.reflective_segments:
                dimensions = f" start: {reflective_segment.p1}, end: {reflective_segment.p2}"
                stats_line = stats_line + dimensions
            log_stats_append(f"stats", stats_line)
        print(f"Best individual has fitness: {best_ind.fitness}")
        draw(best_ind, f"best{g}", env)

    if env.quality_criterion == "nsgaii":
        unique = choose_unique(hof, env.configuration)
        stats_line = f"index, fitness array"
        log_stats_init(f"stats", stats_line)
        for index in range(len(unique)):
            draw(unique[index], f"unique{index}", env)
            if env.configuration == "two connected":
                stats_line = f"{index}, {unique[index].fitness}," \
                         f"left angle: {180-unique[index].left_angle+unique[index].base_slope}, " \
                         f"left length: {unique[index].left_length_coef*unique[index].base_length}, " \
                         f"right angle: {unique[index].right_angle-unique[index].base_slope}, " \
                         f"right length: {unique[index].right_length_coef*unique[index].base_length} "
            else:
                stats_line = f"{index}, {unique[index].fitness}, {unique[index].base_slope}"
                for reflective_segment in unique[index].reflective_segments:
                    dimensions = f" start: {reflective_segment.p1}, end: {reflective_segment.p2}"
                    stats_line = stats_line + dimensions
            log_stats_append(f"stats", stats_line)
    print("-- End of (successful) evolution --")
    print("--")


def main():
    # create config parser
    builder = ConfigBuilder()
    # parse configuration from file parameters.json
    config = builder.parse_config('parameters.json')

    # Load parameters for environment
    base_length = config.lamp.base_length
    base_slope = config.lamp.base_slope
    road_start = config.road.start
    road_end = config.road.end
    road_depth = config.road.depth
    road_sections = config.road.sections
    configuration = config.lamp.configuration

    # Load parameters for evaluation
    criterion = config.evaluation.criterion
    cosine_error = config.evaluation.cosine_error
    reflective_factor = config.evaluation.reflective_factor
    reflections_timeout = config.evaluation.reflections_timeout
    weights = config.evaluation.weights

    number_of_LEDs = config.lamp.number_of_LEDs
    separating_distance = config.lamp.separating_distance
    modification = config.lamp.modification

    invalid_parameters = check_parameters_environment(road_start, road_end, road_depth,
                                                      road_sections, criterion, cosine_error, reflective_factor,
                                                      configuration, number_of_LEDs, separating_distance, modification,
                                                      weights, reflections_timeout)
    if invalid_parameters:
        print(f"Invalid value for parameters {invalid_parameters}")
        return
    else:
        print(f" Environment parameters: ok")
    # Init environment
    env = Environment(road_start, road_end, road_depth, road_sections,
                      criterion, cosine_error, reflective_factor, configuration,
                      number_of_LEDs, separating_distance, modification, weights, reflections_timeout)

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
    base_angle_limit_min = config.lamp.multiple_free.base_angle_limit_min
    base_angle_limit_max = config.lamp.multiple_free.base_angle_limit_max


    population_size = config.evolution.population_size
    number_of_generations = config.evolution.number_of_generations

    # Load parameters for evolution
    operators = config.evolution.operators
    xover_prob = operators.xover_prob
    angle_mut_prob = operators.mutation.angle_mutation_prob
    length_mut_prob = operators.mutation.length_mutation_prob
    shift_segment_prob = operators.mutation.segment_shift_prob
    rotate_segment_prob = operators.mutation.segment_rotation_prob
    resize_segment_prob = operators.mutation.segment_resizing_prob
    tilt_base_prob = operators.mutation.tilt_base_prob

    invalid_parameters = check_parameters_evolution(number_of_rays, ray_distribution, angle_lower_bound,
                                                    angle_upper_bound, length_lower_bound, length_upper_bound,
                                                    no_of_reflective_segments, distance_limit, length_limit,
                                                    population_size, number_of_generations, xover_prob, angle_mut_prob,
                                                    length_mut_prob, shift_segment_prob, rotate_segment_prob,
                                                    resize_segment_prob, tilt_base_prob, base_length, base_slope,
                                                    base_angle_limit_min, base_angle_limit_max)
    if invalid_parameters:
        print(f"Invalid value for parameters {invalid_parameters}")
        return
    else:
        print(f" Evolution parameters: ok")

    # Run evolution algorithm
    evolution(env, number_of_rays, ray_distribution, angle_lower_bound, angle_upper_bound,
              length_lower_bound, length_upper_bound, no_of_reflective_segments, distance_limit, length_limit,
              population_size, number_of_generations, xover_prob, angle_mut_prob, length_mut_prob,
              shift_segment_prob, rotate_segment_prob, resize_segment_prob, tilt_base_prob, base_length, base_slope,
              base_angle_limit_min, base_angle_limit_max)


if __name__ == "__main__":
    main()
