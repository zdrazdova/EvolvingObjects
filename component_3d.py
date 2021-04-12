import random
from typing import List

from sympy.geometry import Ray, Point, Segment
from sympy import pi, sin, cos

from custom_ray import MyRay
from custom_ray_3d import MyRay3D
from environment import Environment


class Component3D:

    def __init__(self, number_of_rays: int, ray_distribution: str):

        self.origin = Point(0, 0, 0)

        # Sampling light rays for given base slope
        self.original_rays = self.sample_rays_3d(number_of_rays, "random")

        self.intersections_on = []
        self.intersections_on_intensity = 0
        self.no_of_reflections = 0
        self.segments_intensity = []

    def sample_rays_3d(self, number_of_rays: int, distribution: str) -> List[MyRay]:
        """
        Sample given number of rays from LED according to base angle and distribution parameter.

        :param number_of_rays: Number of rays going from LED
        :param distribution: random vs uniform distribution - random is default
        :param base_angle: Angle of base for LED
        :return: List of rays from LED
        """
        ray_array = []
        if distribution == "uniform":
            step = 180 / number_of_rays
        for ray in range(number_of_rays):
            if distribution == "uniform":
                angle = 180 + ray*step + step/2
            else:
                first_angle = random.randint(180, 360)
                second_angle = random.randint(180, 360)
            new_ray = MyRay3D(self.origin, first_angle, second_angle)
            ray_array.append(new_ray)
        return ray_array


def generate_reflective_segments(number_of_segments: int, distance_limit: int, length_limit: int):
    reflective_segments = []
    for index in range(number_of_segments):
        origin = Point(random.randint(-distance_limit, distance_limit), random.randint(-distance_limit, distance_limit))
        end = Point(origin.x+random.randint(-length_limit, length_limit),
                    origin.y+random.randint(-length_limit, length_limit))
        segment = Segment(origin, end)

        reflective_segments.append(segment)
    return reflective_segments



