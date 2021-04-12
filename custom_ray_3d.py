import math

from sympy import Point, Ray


class MyRay3D:

    def __init__(self, origin: Point, first_angle: int, second_angle: int):
        self.ray_length = 1
        # Intensity is calculated according to Lambertian distribution
        self.intensity = abs(math.sin(math.radians(abs(first_angle)))) + abs(math.sin(math.radians(abs(second_angle))))
        # End coordinates are calculated from ray angle
        x_coordinate = 10 * math.cos(math.radians(first_angle)) + origin.x
        y_coordinate = 10 * math.sin(math.radians(first_angle)) + origin.y
        z_coordinate = 10 * math.sin(math.radians(second_angle)) + origin.z
        # Ray goes from the origin in direction of end coordinates
        self.ray = Ray(origin, Point(x_coordinate, y_coordinate, z_coordinate))
        # Array used for storing segments of reflected ray
        self.ray_array = [Ray(origin, Point(x_coordinate, y_coordinate, z_coordinate))]
        self.road_intersection = []
