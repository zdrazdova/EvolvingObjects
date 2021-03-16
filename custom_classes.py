import math
import random

from sympy.geometry import Line, Ray, Point, Segment
from sympy import pi, sin, cos

import custom_geometry as cg


class Environment:
    def __init__(self, base_length: int, base_slope: int, road_start: int, road_end: int, road_depth: int, road_sections: int):

        self.origin = Point(0, 0)
        self.base_slope = base_slope

        # Calculating base coordinates from slope and length parameters
        y_diff = round(base_length/2 * sin(math.radians(base_slope)))
        x_diff = round(base_length/2 * cos(math.radians(base_slope)))
        self.base = Segment(Point(-x_diff, -y_diff), Point(x_diff, y_diff))

        self.road = Segment(Point(road_start, road_depth), Point(road_end, road_depth))
        self.road_start = road_start
        self.road_end = road_end
        self.road_length = (self.road_end - self.road_start)
        self.road_depth = road_depth
        self.road_sections = road_sections


class Component:

    def __init__(self, env: Environment, number_of_rays: int, ray_distribution: str, angle_lower_bound: int, angle_upper_bound: int,
                 length_lower_bound: int, length_upper_bound: int):

        self.origin = Point(0, 0)

        # Sampling light rays for given base slope
        self.original_rays = self.sample_rays(number_of_rays, ray_distribution, env.base_slope)


        self.angle_limit_min = angle_lower_bound + env.base_slope
        self.angle_limit_max = angle_upper_bound + env.base_slope
        self.right_angle = random.randint(self.angle_limit_min, self.angle_limit_max)
        self.left_angle = random.randint(self.angle_limit_min, self.angle_limit_max) - 90

        self.length_limit_diff = length_upper_bound - length_lower_bound
        self.left_length_coef = random.random() * self.length_limit_diff + length_lower_bound
        self.right_length_coef = random.random() * self.length_limit_diff + length_lower_bound

        self.base = env.base

        self.compute_right_segment()
        self.compute_left_segment()

        self.intersections_on = []
        self.intersections_on_intensity = 0
        self.no_of_reflections = 0
        self.segments_intensity = []

    # Sampling given number of rays, base angle is used for intensity calculations
    def sample_rays(self, number_of_rays: int, distribution: str, base_angle: int) :
        ray_array = []
        if distribution == "uniform":
            step = 180 / number_of_rays
        for ray in range(number_of_rays):
            if distribution == "uniform":
                angle = 180 + ray*step + step/2 + base_angle
            else:
                angle = random.randint(180, 360) + base_angle
            new_ray = cg.MyRay(self.origin, angle, base_angle)
            ray_array.append(new_ray)
        return ray_array

    # Computing coordinates for right segment based on right angle and base info
    def compute_right_segment(self):
        base_right_p = self.base.points[1]
        right_ray = Ray(base_right_p, angle= self.right_angle/180 * pi)
        x_diff = self.base.length * self.right_length_coef * cos(self.right_angle/180 * pi)
        y_diff = self.base.length * self.right_length_coef * sin(self.right_angle/180 * pi)
        if right_ray.xdirection == "oo":
            right_end_x = base_right_p.x + x_diff
        else:
            right_end_x = base_right_p.x - x_diff
        if right_ray.ydirection == "oo":
            right_end_y = base_right_p.y + y_diff
        else:
            right_end_y = base_right_p.y - y_diff

        self.right_segment = Segment(base_right_p, Point(float(right_end_x),float(right_end_y)))

    # Computing coordinates for left segment based on left angle and base info
    def compute_left_segment(self):
        base_left_p = self.base.points[0]
        left_ray = Ray(base_left_p, angle= self.left_angle/180 * pi)
        x_diff = self.base.length * self.left_length_coef * cos(self.left_angle/180 * pi)
        y_diff = self.base.length * self.left_length_coef * sin(self.left_angle/180 * pi)

        if left_ray.xdirection == "oo":
            left_end_x = base_left_p.x + x_diff
        else:
            left_end_x = base_left_p.x - x_diff
        if left_ray.ydirection == "oo":
            left_end_y = base_left_p.y + y_diff
        else:
            left_end_y = base_left_p.y - y_diff

        self.left_segment = Segment(base_left_p, Point(float(left_end_x),float(left_end_y)))

