import math

from sympy.geometry import Line, Ray, Point, Segment
from sympy import pi, sin, cos

import custom_classes as cc


class MyRay:

    def __init__(self, origin: Point, ray_angle: int, base_angle: int):
        self.ray_length = 1
        # Intensity is calculated according to Lambertian distribution
        self.intensity = abs(math.sin(math.radians(abs(ray_angle-base_angle))))
        self.end_intensity = self.intensity * 1/(self.ray_length*self.ray_length)
        # End coordinates are calculated from ray angle
        x_coordinate = 10000 * math.cos(math.radians(ray_angle)) + origin.x
        y_coordinate = 10000 * math.sin(math.radians(ray_angle)) + origin.y
        # Ray goes from the origin in direction of end coordinates
        self.ray = Ray(origin, Point(x_coordinate, y_coordinate))
        # Array used for storing segments of reflected ray
        self.ray_array = [Ray(origin, Point(x_coordinate, y_coordinate))]
        self.road_intersection = []


def compute_reflection(ray: Ray, surface: Segment, intersection: Point) -> Ray:
    orig_point = ray.p1
    parallel = surface.parallel_line(orig_point)
    perpendicular = surface.perpendicular_line(intersection)
    meet_point = parallel.intersection(perpendicular)[0]
    x_diff = (meet_point.x - orig_point.x)
    y_diff = (meet_point.y - orig_point.y)
    new_point = Point(meet_point.x + x_diff, meet_point.y + y_diff)
    reflected_ray = Ray(intersection, new_point)
    return reflected_ray


# computes intersections of rays from LED and road below the lamp
def compute_intersections(ind, env):
    inter_array = []
    intensity_sum = 0
    for ray in ind.original_rays:
        inter_point = env.road.intersection(ray.ray_array[-1])
        if inter_point != []:
            intensity_sum += ray.intensity
            inter_array.append([inter_point[0].x, ray.intensity])
            ray.road_intersection = inter_point[0].x
    # print(len(ind.original_rays))
    # print(inter_array)
    ind.intersections_on = inter_array
    ind.intersections_on_intensity = intensity_sum


def compute_reflections_two_segments(ind):
    ind.compute_right_segment()
    ind.compute_left_segment()
    no_of_reflections = 0
    for ray in ind.original_rays:
        #print("NEW ")
        continue_left = True
        continue_right = True
        previous_i_r = Point(0, 0)
        previous_i_l = Point(0, 0)
        ray.ray_array=[ray.ray]
        while continue_left or continue_right:
            continue_left = False
            continue_right = False
            last_ray = ray.ray_array[-1]
            intersection_r = last_ray.intersection(ind.right_segment)
            #print("right ", len(intersection_r))

            if intersection_r and intersection_r[0] != previous_i_r:
                #ax.print_ray(last_ray)
                #ax.print_point(intersection_r[0])
                previous_i_r = intersection_r[0]
                intersection = intersection_r[0]
                reflected_ray = compute_reflection(last_ray, ind.right_segment, intersection)
                no_of_reflections += 1
                new_ray_array = ray.ray_array[:-1]
                new_ray_array.append(Ray(last_ray.p1, intersection_r[0]))
                new_ray_array.append(reflected_ray)
                ray.ray_array = new_ray_array
                continue_left = True
            last_ray = ray.ray_array[-1]
            intersection_l = last_ray.intersection(ind.left_segment)
            #print("left ", len(intersection_l))
            if intersection_l and intersection_l[0] != previous_i_l:
                #ax.print_ray(last_ray)
                #ax.print_point(intersection_l[0])
                previous_i_l = intersection_l[0]
                intersection = intersection_l[0]
                reflected_ray = compute_reflection(last_ray, ind.left_segment, intersection)
                no_of_reflections += 1
                new_ray_array = ray.ray_array[:-1]
                new_ray_array.append(Ray(last_ray.p1, intersection_l[0]))
                new_ray_array.append(reflected_ray)
                ray.ray_array = new_ray_array
                continue_right = True
    ind.no_of_reflections = no_of_reflections


def prepare_intersections(points):
    x_coordinates = []
    for point in points:
        x_coordinates.append([float(point[0]), point[1]])
    return sorted(x_coordinates)


