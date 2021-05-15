import math

from sympy import Point, Ray


class MyRay:

    def __init__(self, origin: Point, ray_angle: float, base_angle: int):
        self.ray_length = 1
        # Intensity is calculated according to Lambertian distribution
        self.intensity = abs(math.sin(math.radians(abs(ray_angle - base_angle))))
        self.original_intensity = abs(math.sin(math.radians(abs(ray_angle - base_angle))))
        self.end_intensity = self.intensity * 1 / (self.ray_length * self.ray_length)
        # End coordinates are calculated from ray angle
        x_coordinate = 10000 * math.cos(math.radians(ray_angle)) + origin.x
        y_coordinate = 10000 * math.sin(math.radians(ray_angle)) + origin.y
        # Ray goes from the origin in direction of end coordinates
        self.ray = Ray(origin, Point(x_coordinate, y_coordinate))
        # Array used for storing segments of reflected ray
        self.ray_array = [Ray(origin, Point(x_coordinate, y_coordinate))]
        self.road_intersection = []
        self.terminated = False
