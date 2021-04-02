import math
from typing import List, Tuple

import pytest
from sympy import Rational, Point, Segment

from custom_ray import MyRay
from quality_precalculations import intensity_of_intersections, sum_intensity, compute_proportional_intensity, \
    compute_segments_intensity, rays_upwards


@pytest.mark.parametrize(
    ['road_intersections', 'expected'],
    [
        [[(Rational(10 / 3), 0.8), (3, 0.2), (Rational(29 / 7), 0)], 1.0],
        [[], 0],
        [[(Rational(783/8), 0.398)], 0.398]
    ]
)
def test_intensity_of_intersections(road_intersections: List[Tuple[Rational, float]], expected: float):
    actual = intensity_of_intersections(road_intersections=road_intersections)
    assert actual == expected


@pytest.mark.parametrize(
    ['rays', 'expected'],
    [
        [[MyRay(Point(0, 0), 180+60, 60)], abs(math.sin(math.radians(abs(180))))],
        [[MyRay(Point(0, 0), 180+30, 30), MyRay(Point(0, 0), 200+30, 30)],
         abs(math.sin(math.radians(abs(180))))+abs(math.sin(math.radians(abs(200))))],
        [[], 0]
    ]
)
def test_sum_intensity(rays: List[MyRay], expected: float):
    actual = sum_intensity(rays=rays)
    assert actual == expected


@pytest.mark.parametrize(
    ['intersections_on', 'road_sections', 'road_start', 'road_length', 'expected'],
    [
        [[(Rational(21/10), 0.5), (Rational(400), 0.89), (Rational(180000/31), 0.22)], 4, 0, 8000, [1.39, 0, 0.22, 0]],
        [[], 8, 100, 19000, []]
    ]
)
def test_compute_segments_intensity(intersections_on: List[Tuple[Rational, float]], road_sections: int, road_start: int,
                                    road_length: int, expected: List[float]):
    actual = compute_segments_intensity(intersections_on=intersections_on, road_sections=road_sections,
                                        road_start=road_start, road_length=road_length)
    for a, e in zip(actual, expected):
        assert abs(a - e) < 0.0001


@pytest.mark.parametrize(
    ['segments_intensity', 'expected'],
    [
        [[2.4, 0.6, 0.0], [1.0, 0.25, 0.0]],
        [[4], [1]],
        [[0.9, 0.9], [1, 1]],
        [[0.0, 0.0, 0.0], [0.0, 0.0, 0.0]]
    ]
)
def test_compute_proportional_intensity(segments_intensity: List[float], expected: List[float]):
    actual = compute_proportional_intensity(segments_intensity=segments_intensity)
    assert actual == expected


@pytest.mark.parametrize(
    ['rays', 'expected'],
    [
        [[], 0],
        [[[Segment(Point(0, 0), Point(1, 1))]], 1],
        [[[Segment(Point(0, 0), Point(1, 1)), Segment(Point(1, 1), Point(0, -3))]], 0],

    ]
)
def test_rays_upwards(rays: List[List[Segment]], expected: int):
    actual = rays_upwards(rays=rays)
    assert actual == expected
