import math
from typing import List

from component import Component
from environment import Environment
from quality_assesment import illuminance_uniformity, light_pollution


def log_stats_init(name: str, line: str):
    stats_name = "stats/log-" + str(name) + ".csv"
    with open(stats_name, "w") as f:
        f.write(line)


def log_stats_append(name: str, line: str):
    stats_name = "stats/log-" + str(name) + ".csv"
    with open(stats_name, "a") as f:
        f.write('\n')
        f.write(line)


def choose_unique(hof: List[Component]) -> List[Component]:
    print(len(hof))
    unique = [hof[0]]
    for ind in hof:
        exists = False
        for uni in unique:
            if ind.left_angle == uni.left_angle and ind.right_angle == uni.right_angle and \
                    ind.left_length_coef == uni.left_length_coef and ind.right_length_coef == uni.right_length_coef:
                exists = True
        if not exists:
            unique.append(ind)
    selected = []
    for uni in unique:
        uniformity = illuminance_uniformity(uni.segments_intensity)
        rays_upwards = light_pollution(uni.original_rays)
        if uniformity > 0.2 and rays_upwards < 4:
            selected.append(uni)
    print(len(unique))
    print(len(selected))
    return unique


def draw(ind: Component, name: str, env: Environment):
    svg_name = "img/img-" + str(name).zfill(2) + ".svg".format(name)
    # Generating drawing in SVG format
    with open(svg_name, "w") as f:
        separating_distance = env.separating_distance
        x_offset = 1000
        if env.road_start < 0:
            x_offset += abs(env.road_start)
        y_offset = 1000
        width = env.road_end + x_offset + 1000
        height = abs(env.road_depth) + 2000
        diag = math.sqrt(width*width + height*height)
        f.write(
            '<svg width="{0}" height="{1}">'.format(env.road_end + x_offset + 1000, abs(env.road_depth) + 2000))
        f.write('<rect width="{0}" height="{1}" fill="black"/>'.format(env.road_end + x_offset + 1000,
                                                                       abs(env.road_depth) + 2000))

        for ray in ind.original_rays:
            array = ray.ray_array
            alpha = str(round(ray.intensity, 3))
            color = "(250, 216, 22)"
            for r in array[:-1]:
                f.write(
                    '<line x1="{0}" y1="{1}" x2="{2}" y2="{3}" style="stroke:rgb{4};stroke-opacity:{5};stroke-width:10"/>\n'
                        .format(float(r.points[0].x) + x_offset, - float(r.points[0].y) + y_offset,
                                float(r.points[1].x) + x_offset, - float(r.points[1].y) + y_offset, color, alpha))
                if env.modification == "mirror":
                    f.write(
                    '<line x1="{0}" y1="{1}" x2="{2}" y2="{3}" style="stroke:rgb{4};stroke-opacity:{5};stroke-width:10"/>\n'
                        .format(-float(r.points[0].x) + x_offset - separating_distance, - float(r.points[0].y) + y_offset,
                                -float(r.points[1].x) + x_offset- separating_distance, - float(r.points[1].y) + y_offset, color, alpha))
                if env.modification == "shift":
                    for l in range(1, env.number_of_led):
                        f.write('<line x1="{0}" y1="{1}" x2="{2}" y2="{3}" style="stroke:rgb{4};stroke-opacity:{5};stroke-width:10"/>\n'
                            .format(float(r.points[0].x) + x_offset + l * env.separating_distance, - float(r.points[0].y) + y_offset,
                                    float(r.points[1].x) + x_offset + l * env.separating_distance, - float(r.points[1].y) + y_offset, color, alpha))
            r = array[-1]
            intersection = env.road.intersection(r)
            if intersection and not ray.terminated:
                intersection = intersection[0]
                f.write(
                    '<line x1="{0}" y1="{1}" x2="{2}" y2="{3}" style="stroke:rgb{4};stroke-opacity:{5};stroke-width:10"/>\n'
                        .format(float(r.points[0].x) + x_offset, - float(r.points[0].y) + y_offset,
                                float(intersection.x) + x_offset, - float(intersection.y) + y_offset, color, alpha))
                if env.modification == "mirror":
                    f.write(
                    '<line x1="{0}" y1="{1}" x2="{2}" y2="{3}" style="stroke:rgb{4};stroke-opacity:{5};stroke-width:10"/>\n'
                        .format(-float(r.points[0].x) + x_offset - separating_distance, - float(r.points[0].y) + y_offset,
                                -float(intersection.x) + x_offset - separating_distance, - float(intersection.y) + y_offset, color, alpha))
                if env.modification == "shift":
                    for l in range(1, env.number_of_led):
                        f.write('<line x1="{0}" y1="{1}" x2="{2}" y2="{3}" style="stroke:rgb{4};stroke-opacity:{5};stroke-width:10"/>\n'
                        .format(float(r.points[0].x) + x_offset + l * env.separating_distance, - float(r.points[0].y) + y_offset,
                                float(intersection.x) + x_offset + l * env.separating_distance, - float(intersection.y) + y_offset, color, alpha))

            else:
                if not ray.terminated:
                    x_diff = float(r.points[1].x - r.points[0].x)
                    y_diff = float(r.points[1].y - r.points[0].y)
                    length = math.sqrt(x_diff * x_diff + y_diff * y_diff)
                    ratio = diag /length
                    x_diff = float(r.points[1].x - r.points[0].x) * ratio
                    y_diff = float(r.points[1].y - r.points[0].y) * ratio
                    f.write(
                        '<line x1="{0}" y1="{1}" x2="{2}" y2="{3}" style="stroke:rgb{4};stroke-opacity:{5};stroke-width:10"/>'
                        '\n'.format(float(r.points[0].x) + x_offset, - float(r.points[0].y) + y_offset,
                                    float(r.points[0].x) + x_offset + x_diff,
                                    -float(r.points[0].y) + y_offset - y_diff,
                                    color, alpha))
                    if env.modification == "mirror":
                        f.write(
                        '<line x1="{0}" y1="{1}" x2="{2}" y2="{3}" style="stroke:rgb{4};stroke-opacity:{5};stroke-width:10"/>'
                        '\n'.format(-float(r.points[0].x) + x_offset - separating_distance, - float(r.points[0].y) + y_offset,
                                    -float(r.points[0].x) + x_offset - x_diff - separating_distance,
                                    -float(r.points[0].y) + y_offset - y_diff,
                                    color, alpha))
                    if env.modification == "shift":
                        for l in range(1, env.number_of_led):
                            f.write(
                                '<line x1="{0}" y1="{1}" x2="{2}" y2="{3}" style="stroke:rgb{4};stroke-opacity:{5};stroke-width:10"/>'
                                '\n'.format(float(r.points[0].x) + x_offset + l * env.separating_distance, - float(r.points[0].y) + y_offset,
                                            float(r.points[0].x) + x_offset + x_diff + l * env.separating_distance,
                                            -float(r.points[0].y) + y_offset - y_diff,
                                            color, alpha))


        f.write('<rect x="{0}" y="{1}" width="{2}" height="50" fill="gray"/>'
                .format(env.road.p1.x + x_offset, -env.road.p1.y + y_offset,
                        (env.road.p2.x - env.road.p1.x)))  # road

        if env.quality_criterion in ["illuminance uniformity", "all", "nsgaii", "nsgaiii"]:
            left_border = env.road_start
            segments_size = env.road_length / env.road_sections

            for segment in range(env.road_sections):
                alpha = str(round(ind.segments_intensity_proportional[segment], 3))
                color = "(250, 6, 22)"
                f.write('<rect x="{0}" y="{1}" width="{2}" height="50" style="fill:rgb{3};fill-opacity:{4};"/>'
                        .format(left_border + x_offset, -env.road.p1.y + y_offset,
                                segments_size, color, alpha))
                left_border += segments_size

        # Base
        f.write('<line x1="{0}" y1="{1}" x2="{2}" y2="{3}" style="stroke:gray;stroke-width:20"/>'.format(
            ind.base.p1.x + x_offset, -ind.base.p1.y + y_offset,
            ind.base.p2.x + x_offset, -ind.base.p2.y + y_offset))
        if env.modification == "mirror":
            f.write('<line x1="{0}" y1="{1}" x2="{2}" y2="{3}" style="stroke:gray;stroke-width:20"/>'.format(
            -ind.base.p1.x + x_offset - separating_distance, -ind.base.p1.y + y_offset,
            -ind.base.p2.x + x_offset - separating_distance, -ind.base.p2.y + y_offset))
        if env.modification == "shift":
            for l in range(1, env.number_of_led):
                f.write('<line x1="{0}" y1="{1}" x2="{2}" y2="{3}" style="stroke:gray;stroke-width:20"/>'.format(
                ind.base.p1.x + x_offset + l * env.separating_distance, -ind.base.p1.y + y_offset,
                ind.base.p2.x + x_offset + l * env.separating_distance, -ind.base.p2.y + y_offset))


        if env.configuration == "two connected":
            # right segment
            f.write('<line x1="{0}" y1="{1}" x2="{2}" y2="{3}" style="stroke:gray;stroke-width:20"/>'.format(
                ind.base.p2.x + x_offset, -ind.base.p2.y + y_offset,
                float(ind.right_segment.p2.x) + x_offset, float(-ind.right_segment.p2.y) + y_offset))
            if env.modification == "mirror":
                f.write('<line x1="{0}" y1="{1}" x2="{2}" y2="{3}" style="stroke:gray;stroke-width:20"/>'.format(
                -ind.base.p2.x + x_offset - separating_distance, -ind.base.p2.y + y_offset,
                -float(ind.right_segment.p2.x) + x_offset - separating_distance, float(-ind.right_segment.p2.y) + y_offset))
            if env.modification == "shift":
                for l in range(1, env.number_of_led):
                    f.write('<line x1="{0}" y1="{1}" x2="{2}" y2="{3}" style="stroke:gray;stroke-width:20"/>'.format(
                        ind.base.p2.x + x_offset + l * env.separating_distance, -ind.base.p2.y + y_offset,
                        float(ind.right_segment.p2.x) + x_offset + l * env.separating_distance, float(-ind.right_segment.p2.y) + y_offset))
            # left segment
            f.write('<line x1="{0}" y1="{1}" x2="{2}" y2="{3}" style="stroke:gray;stroke-width:20"/>'.format(
                ind.base.p1.x + x_offset, -ind.base.p1.y + y_offset,
                float(ind.left_segment.p2.x) + x_offset, float(-ind.left_segment.p2.y) + y_offset))
            if env.modification == "mirror":
                f.write('<line x1="{0}" y1="{1}" x2="{2}" y2="{3}" style="stroke:gray;stroke-width:20"/>'.format(
                -ind.base.p1.x + x_offset - separating_distance, -ind.base.p1.y + y_offset,
                -float(ind.left_segment.p2.x) + x_offset - separating_distance, float(-ind.left_segment.p2.y) + y_offset))
            if env.modification == "shift":
                for l in range(1, env.number_of_led):
                    f.write('<line x1="{0}" y1="{1}" x2="{2}" y2="{3}" style="stroke:gray;stroke-width:20"/>'.format(
                    ind.base.p1.x + x_offset + l * env.separating_distance, -ind.base.p1.y + y_offset,
                    float(ind.left_segment.p2.x) + x_offset + l * env.separating_distance, float(-ind.left_segment.p2.y) + y_offset))

        if env.configuration == "multiple free":
            # reflective segments
            for segment in ind.reflective_segments:
                f.write('<line x1="{0}" y1="{1}" x2="{2}" y2="{3}" style="stroke:gray;stroke-width:20"/>'.format(
                    segment.p1.x + x_offset, -segment.p1.y + y_offset,
                    float(segment.p2.x) + x_offset, float(-segment.p2.y) + y_offset))


        f.write('</svg>')


def check_parameters_environment(road_start: int, road_end: int, road_depth: int,
                                 road_sections: int, criterion: str, cosine_error: str, reflective_factor: float,
                                 configuration: str, number_of_led: int, separating_distance: int,
                                 modification: str, weights: List[int], reflections_timeout: int) -> List[str]:

    invalid = []
    if configuration not in ["multiple free", "two connected"]:
        invalid.append("configuration")
    if modification not in ["mirror", "shift"]:
        invalid.append("modification")
    if criterion not in ["all", "efficiency", "illuminance uniformity", "obtrusive light", "weighted_sum", "nsgaii"]:
        invalid.append("criterion")
    if cosine_error not in ["yes", "no"]:
        invalid.append("cosine error")
    if type(weights) != list or len(weights) != 4:
        invalid.append("weights")

    if type(road_start) != int:
        invalid.append("road start")
    if type(road_end) != int or road_end <= road_start:
        invalid.append("road end")
    if type(road_depth) != int or road_depth >= 0:
        invalid.append("road depth")
    if type(road_sections) != int or road_sections <= 0:
        invalid.append("road sections")

    if type(reflective_factor) != float or reflective_factor <= 0 or reflective_factor > 1:
        invalid.append("reflective factor")
    if type(reflections_timeout) != int or reflections_timeout <= 2:
        invalid.append("reflections timeout")
    if type(number_of_led) != int or number_of_led <= 0:
        invalid.append("number of LEDs")
    if type(separating_distance) != int or reflective_factor <= 0:
        invalid.append("separating distance")

    if modification == "mirror" and number_of_led > 2:
        invalid.append("mirror + number_of_LEDs")

    return invalid


def check_parameters_evolution(number_of_rays: int, ray_distribution: str, angle_lower_bound: int,
                               angle_upper_bound: int, length_lower_bound: int, length_upper_bound: int,
                               no_of_reflective_segments: int, distance_limit: int, length_limit: int,
                               population_size: int, number_of_generations: int, xover_prob: float,
                               angle_mut_prob: float, length_mut_prob: float, shift_segment_prob: float,
                               rotate_segment_prob: float, resize_segment_prob: float,
                               tilt_base_prob, base_length: int, base_slope: int, base_angle_limit_min: int,
                               base_angle_limit_max: int) -> List[str]:
    invalid = []

    if type(number_of_rays) != int or number_of_rays <= 0:
        invalid.append("number of rays")
    if ray_distribution not in ["uniform", "random"]:
        invalid.append("ray distribution")

    if type(base_length) != int or base_length <= 0:
        invalid.append("base length")
    if type(base_slope) != int or 0 > base_slope or base_slope > 180:
        invalid.append("base slope")


    if type(angle_lower_bound) != int or 90 > angle_lower_bound or angle_lower_bound > 180:
        invalid.append("angle lower bound")
    if type(angle_upper_bound) != int or angle_upper_bound > 180 or angle_upper_bound <= angle_lower_bound:
        invalid.append("angle upper bound")
    if type(length_lower_bound) != int or length_lower_bound <= 0:
        invalid.append("length lower bound")
    if type(length_upper_bound) != int or length_upper_bound <= length_lower_bound:
        invalid.append("length upper bound")
    if type(base_angle_limit_min) != int or base_angle_limit_min < 0:
        invalid.append("base angle limit min")
    if type(base_angle_limit_max) != int or base_angle_limit_max <= base_angle_limit_min:
        invalid.append("base angle limit max")

    if type(no_of_reflective_segments) != int or number_of_rays <= 0:
        invalid.append("no of reflective segments")
    if type(distance_limit) != int or distance_limit <= 0:
        invalid.append("distance limit")
    if type(length_limit) != int or length_limit <= 0:
        invalid.append("length limit")

    if type(population_size) != int or population_size <= 0:
        invalid.append("population size")
    if type(number_of_generations) != int or number_of_generations <= 0:
        invalid.append("number of generations")

    if type(xover_prob) != float or xover_prob < 0 or xover_prob > 1:
        invalid.append("xover prob")
    if type(angle_mut_prob) != float or angle_mut_prob < 0 or angle_mut_prob > 1:
        invalid.append("angle mut prob")
    if type(length_mut_prob) != float or length_mut_prob < 0 or length_mut_prob > 1:
        invalid.append("length mut prob")

    if type(shift_segment_prob) != float or shift_segment_prob < 0 or shift_segment_prob > 1:
        invalid.append("shift segment prob")
    if type(rotate_segment_prob) != float or rotate_segment_prob < 0 or rotate_segment_prob > 1:
        invalid.append("rotate segment prob")
    if type(resize_segment_prob) != float or resize_segment_prob < 0 or resize_segment_prob > 1:
        invalid.append("resize segment prob")
    if type(tilt_base_prob) != float or tilt_base_prob < 0 or tilt_base_prob > 1:
        invalid.append("tilt base prob")

    return invalid