from typing import List, Tuple

import pytest
from sympy import Rational, Ray, Segment, Point, cos, pi

from custom_geometry import compute_reflection, prepare_intersections, compute_intersections, rotate_segment, \
    change_size_segment
from custom_ray import MyRay


@pytest.mark.parametrize(
    ['ray', 'surface', 'intensity', 'r_factor', 'expected'],
    [
        [Ray(Point(0, 0), Point(1, 1)), Segment(Point(2, 0), Point(2, 4)), 1, 1, (Ray(Point(2, 2), Point(0, 4)), 1)],
        [Ray(Point(0, 0), Point(1, 0)), Segment(Point(2, 0), Point(2, 4)), 0.5, 0.98,
         (Ray(Point(2, 0), Point(0, 0)), 0.49)],
        [Ray(Point(0, 0), Point(1, 0)), Segment(Point(1, 1), Point(3, 3)), 1, 0.9, None],
        [Ray(Point(2, 4), Point(4, 0)), Segment(Point(2, 2), Point(3, 0)), 0.78, 0.5, None],
    ]
)
def test_compute_reflection(ray: Ray, surface: Segment, intensity: float, r_factor: float, expected: (Ray, float)):
    actual = compute_reflection(ray=ray, surface=surface, intensity=intensity, reflective_factor=r_factor)
    assert actual == expected


@pytest.mark.parametrize(
    ['rays', 'road', 'cosine_error', 'expected'],
    [
        [[MyRay(Point(0, 0), 270+45, 45)], Segment(Point(0, -4000), Point(8000, -4000)), "No", [(Rational(4000), 1.0)]],
        [[MyRay(Point(0, 0), 270+45, 45)], Segment(Point(0, -4000), Point(8000, -4000)), "Yes",
         [(Rational(4000), cos(pi/4))]],
        [[MyRay(Point(0, 0), 270, 0)], Segment(Point(-1000, -2000), Point(8000, -2000)), "No", [(Rational(0), 1.0)]],
    ]
)
def test_compute_intersections(rays: List[MyRay], road: Segment, cosine_error: str,
                               expected: List[Tuple[Rational, float]]):
    actual = compute_intersections(rays=rays, road=road, cosine_error=cosine_error)
    for a, e in zip(actual, expected):
        assert abs(a[0] - e[0]) < 0.0001 and abs(a[1] - e[1]) < 0.0001


@pytest.mark.parametrize(
    ['points', 'expected'],
    [
        [[(Rational(10 / 3), 0.8), (3, 0.2), (Rational(29 / 7), 0)],
         [(3, 0.2), (float(10 / 3), 0.8), (float(29 / 7), 0)]],
        [[], []],
        [[(Rational(10 / 7), 0.8), (3, 0.2), (Rational(10 / 7), 0.55)],
         [(float(10 / 7), 0.55), (float(10 / 7), 0.8), (3, 0.2)]]
     ]
)
def test_prepare_intersections(points: List[Tuple[Rational, float]], expected: List[Tuple[float, float]]):
    actual = prepare_intersections(points=points)
    for a, e in zip(actual, expected):
        assert a == e


@pytest.mark.parametrize(
    ['segment', 'angle', 'expected'],
    [
        [Segment(Point(0, 0), Point(10, 30)), 0, Segment(Point(0, 0), Point(10, 30))],
        [Segment(Point(0, 0), Point(10, 30)), 180, Segment(Point(10, 30), Point(0, 0))],
        [Segment(Point(0, 0), Point(10, 30)), 90, Segment(Point(20, 10), Point(-10, 20))]
    ]
)
def test_rotate_segment(segment: Segment, angle: int, expected: Segment):
    actual = rotate_segment(segment=segment, angle=angle)
    assert actual == expected


@pytest.mark.parametrize(
    ['segment', 'coefficient', 'expected'],
    [
        [Segment(Point(0, 0), Point(10, 30)), 0.0, Segment(Point(5, 15), Point(5, 15))],
        [Segment(Point(20, 50), Point(60, 30)), 0.25, Segment(Point(35, 42), Point(45, 37))],
        [Segment(Point(20, 50), Point(60, 30)), 1.0, Segment(Point(20, 50), Point(60, 30))]
    ]
)
def test_change_size_segment(segment: Segment, coefficient: float, expected: Segment):
    actual = change_size_segment(segment=segment, coefficient=coefficient)
    assert actual == expected
