import random
from typing import List

from numpy import arccos
from sympy.geometry import Ray, Point, Segment
from sympy import pi, sin, cos, Plane

from custom_ray import MyRay
from custom_ray_3d import MyRay3D
from environment import Environment


class Component3D:

    def __init__(self, number_of_rays: int, ray_distribution: str,  base_length: int, base_width: int):

        self.origin = Point(0, 0, 0)

        # Sampling light rays for given base slope
        self.original_rays = self.sample_rays_3d(number_of_rays, ray_distribution)

        self.reflective_segments = generate_reflective_segments(1, base_length, base_width)

        self.road_intersections = []
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
        for a in range(number_of_rays):
            for b in range(number_of_rays):
                if distribution == "uniform":
                    theta = pi * 1/number_of_rays*a
                    phi = pi * 1/number_of_rays*b

                    u = 1/number_of_rays*a
                    v = 1/number_of_rays*b
                    phi = pi * u
                    theta = arccos(2*v - 1)
                else:
                    u = random.random()
                    v = random.random()
                    phi = pi * u
                    theta = arccos(2*v - 1)
                    #theta = random.random()*pi
                    #phi = random.random()*pi
                #print(float(theta), float(phi))
                new_ray = MyRay3D(self.origin, phi, theta)
                ray_array.append(new_ray)
        return ray_array


def generate_reflective_segments(number_of_segments: int, base_length: int, base_width: int):
    reflective_segments = []
    reflective_plane = Plane(Point(10, 0, base_length / 2),
                             Point(10, 0, -base_length / 2),
                             Point(10, 10, -base_length / 2)
                             )
    reflective_segments.append(reflective_plane)
    return reflective_segments

