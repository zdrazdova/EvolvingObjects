import math
import random
from typing import List

from sympy.geometry import Ray, Point, Segment
from sympy import pi, sin, cos

from custom_ray import MyRay
from environment import Environment


class Component:

    def __init__(self, env: Environment, number_of_rays: int, ray_distribution: str,
                 angle_lower_bound: int, angle_upper_bound: int,
                 length_lower_bound: int, length_upper_bound: int,
                 no_of_reflective_segments: int, distance_limit: int, length_limit: int,
                 base_length: int, base_slope: int):

        self.origin = Point(0, 0)
        self.base_slope = base_slope
        self.base_length = base_length

        self.calculate_base()

        # Sampling light rays for given base slope
        self.original_rays = self.sample_rays(number_of_rays, ray_distribution)

        self.angle_limit_min = angle_lower_bound + base_slope
        self.angle_limit_max = angle_upper_bound + base_slope
        self.right_angle = random.randint(self.angle_limit_min, self.angle_limit_max)
        self.left_angle = random.randint(self.angle_limit_min, self.angle_limit_max) - 90

        self.length_limit_diff = length_upper_bound - length_lower_bound
        self.left_length_coef = random.random() * self.length_limit_diff + length_lower_bound
        self.right_length_coef = random.random() * self.length_limit_diff + length_lower_bound

        if env.configuration == "two connected":
            self.right_segment = None
            self.left_segment = None
            self.compute_right_segment()
            self.compute_left_segment()

        if env.configuration == "multiple free":
            self.reflective_segments = generate_reflective_segments(no_of_reflective_segments,
                                                                    distance_limit, length_limit)

        self.intersections_on = []
        self.intersections_on_intensity = 0
        self.no_of_reflections = 0
        self.segments_intensity = []
        self.fitness_array = []

    def calculate_base(self):
        y_diff = round(self.base_length / 2 * math.sin(math.radians(self.base_slope)))
        x_diff = round(self.base_length / 2 * math.cos(math.radians(self.base_slope)))
        self.base = Segment(Point(-x_diff, -y_diff), Point(x_diff, y_diff))

    def sample_rays(self, number_of_rays: int, distribution: str) -> List[MyRay]:
        """
        Sample given number of rays from LED according to base angle and distribution parameter.

        :param number_of_rays: Number of rays going from LED
        :param distribution: random vs uniform distribution - random is default
        :param base_angle: Angle of base for LED
        :return: List of rays from LED
        """
        base_angle = self.base_slope
        ray_array = []
        if distribution == "uniform":
            step = 180 / number_of_rays
        for ray in range(number_of_rays):
            if distribution == "uniform":
                angle = 180 + ray*step + step/2 + base_angle
            else:
                angle = random.randint(180, 360) + base_angle
            new_ray = MyRay(self.origin, angle, base_angle)
            ray_array.append(new_ray)
        return ray_array

    def compute_right_segment(self):
        """
        Computing coordinates for right segment based on right angle and base info
        :return:
        """
        base_right_p = self.base.points[1]
        right_ray = Ray(base_right_p, angle=self.right_angle/180 * pi)
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

        self.right_segment = Segment(base_right_p, Point(float(right_end_x), float(right_end_y)))

    def compute_left_segment(self):
        """
        Computing coordinates for left segment based on left angle and base info
        """
        base_left_p = self.base.points[0]
        left_ray = Ray(base_left_p, angle=self.left_angle/180 * pi)
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

        self.left_segment = Segment(base_left_p, Point(float(left_end_x), float(left_end_y)))


def generate_reflective_segments(number_of_segments: int, distance_limit: int, length_limit: int):
    reflective_segments = []
    for index in range(number_of_segments):
        origin = Point(random.randint(-distance_limit, distance_limit), random.randint(-distance_limit, distance_limit))
        end = Point(origin.x+random.randint(-length_limit, length_limit),
                    origin.y+random.randint(-length_limit, length_limit))
        segment = Segment(origin, end)

        reflective_segments.append(segment)
    return reflective_segments



