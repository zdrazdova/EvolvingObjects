import math

from sympy import Point, Segment, Polygon, Plane


class Environment:
    def __init__(self, base_length: int, base_slope: int,
                 road_start: int, road_end: int, road_depth: int, road_sections: int,
                 criterion: str, cosine_error: str, reflective_factor: float, configuration: str):
        dimensions = 2
        self.origin = Point(0, 0)
        self.base_slope = base_slope

        if dimensions == 2:
            # Calculating base coordinates from slope and length parameters
            y_diff = round(base_length / 2 * math.sin(math.radians(base_slope)))
            x_diff = round(base_length / 2 * math.cos(math.radians(base_slope)))
            self.base = Segment(Point(-x_diff, -y_diff), Point(x_diff, y_diff))
            self.road = Segment(Point(road_start, road_depth), Point(road_end, road_depth))

        if dimensions == 3:

            self.base = Plane(Point(base_width / 2, 0, base_length / 2),
                              Point(base_width / 2, 0, -base_length / 2),
                              Point(-base_width / 2, 0, -base_length / 2)
                              )
            self.road = Polygon(Point(road_start, road_width/2),
                                Point(road_end, road_width / 2),
                                Point(road_end, -road_width / 2),
                                Point(road_start, -road_width / 2)
                                )

        self.road_start = road_start
        self.road_end = road_end
        self.road_length = (self.road_end - self.road_start)
        #self.road_width = road_width
        self.road_depth = road_depth
        self.road_sections = road_sections

        self.reflective_factor = reflective_factor
        self.cosine_error = cosine_error
        self.quality_criterion = criterion
        self.configuration = configuration
