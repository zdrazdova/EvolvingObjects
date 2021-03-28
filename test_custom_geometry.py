from typing import List, Tuple

import pytest
from sympy import Rational, Ray, Segment, Point, cos, pi

from custom_geometry import compute_reflection, prepare_intersections, compute_intersections
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
    [[[(Rational(10 / 3), 0.8), (3, 0.2), (Rational(29 / 7), 0)], [(3, 0.2), (float(10 / 3), 0.8), (float(29 / 7), 0)]],
     [[], []],
     [[(Rational(10 / 7), 0.8), (3, 0.2), (Rational(10 / 7), 0.55)],
      [(float(10 / 7), 0.55), (float(10 / 7), 0.8), (3, 0.2)]]
     ]
)
def test_prepare_intersections(points: List[Tuple[Rational, float]], expected: List[Tuple[float, float]]):
    actual = prepare_intersections(points=points)
    for a, e in zip(actual, expected):
        assert a == e
