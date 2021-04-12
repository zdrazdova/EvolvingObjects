import math

from sympy import Point, Ray


class MyRay3D:

    def __init__(self, origin: Point, theta: float, phi: float):
        self.intensity = (abs(math.sin(abs(theta))) + abs(math.sin(abs(phi)))) / 2
        x = math.sin(phi) * math.cos(theta)
        y = math.sin(phi) * math.sin(theta)
        z = math.cos(phi)
        self.ray = Ray(origin, Point(x, -y, z))
        # Array used for storing segments of reflected ray
        self.ray_array = [Ray(origin, Point(x, -y, z))]
        self.road_intersection = []

def print_ray_3d(ray: Ray):
    point1 = ray.p1
    x = round(float(point1.x), 2)
    y = round(float(point1.y), 2)
    z = round(float(point1.z), 2)
    point2 = ray.p2
    x2 = round(float(point2.x), 2)
    y2 = round(float(point2.y), 2)
    z2 = round(float(point2.z), 2)
    print("X: ", x, "Y: ", y, " Z: ", z, "      -- X: ", x2, "        Y: ", y2, "       Z: ", z2)

