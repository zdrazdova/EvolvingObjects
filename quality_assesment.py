from custom_classes import Component


def efficiency(individual: Component) -> float:
    return individual.intersections_on_intensity


def illuminance_uniformity(individual: Component) -> float:
    min_illuminance = min(individual.segments_intensity)
    avg_illuminance = sum(individual.segments_intensity)/len(individual.segments_intensity)
    return min_illuminance/avg_illuminance


def glare_reduction(individual: Component) -> int:
    return individual.no_of_reflections


def light_pollution(individual: Component):
    rays_total = len(individual.original_rays)
    rays_on_road = len(individual.intersections_on)
    return (rays_total - rays_on_road)
