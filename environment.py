from typing import List

from sympy import Point, Segment


class Environment:
    def __init__(self, road_start: int, road_end: int, road_depth: int,
                 road_sections: int, criterion: str, cosine_error: str, reflective_factor: float, configuration: str,
                 number_of_led: int, separating_distance: float, modification: str, weights: List[int],
                 reflections_timeout: int):

        self.road = Segment(Point(road_start, road_depth), Point(road_end, road_depth))
        self.road_start = road_start
        self.road_end = road_end
        self.road_length = (self.road_end - self.road_start)
        self.road_depth = road_depth
        self.road_sections = road_sections

        self.reflective_factor = reflective_factor
        self.reflections_timeout = reflections_timeout
        self.cosine_error = cosine_error
        self.quality_criterion = criterion
        self.configuration = configuration
        self.weights = weights

        self.number_of_led = number_of_led
        self.separating_distance = separating_distance
        self.modification = modification
        if self.modification == "mirror" and self.number_of_led != 2:
            self.modification = ""
