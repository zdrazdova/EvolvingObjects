from typing import List, Tuple

import pytest
from sympy import Rational, Ray, Segment, Point

from custom_geometry import compute_reflection, prepare_intersections


@pytest.mark.parametrize(
    ['ray', 'surface', 'expected'],
    [
        [Ray(Point(0, 0), Point(1, 1)), Segment(Point(2, 0), Point(2, 4)), Ray(Point(2, 2), Point(0, 4))],
        [Ray(Point(0, 0), Point(1, 0)), Segment(Point(2, 0), Point(2, 4)), Ray(Point(2, 0), Point(0, 0))],
        [Ray(Point(0, 0), Point(1, 0)), Segment(Point(1, 1), Point(3, 3)), None],
        [Ray(Point(2, 4), Point(4, 0)), Segment(Point(2, 2), Point(3, 0)), None],
    ]
)
def test_compute_reflection(ray: Ray, surface: Segment, expected: Ray):
    actual = compute_reflection(ray=ray, surface=surface)
    assert actual == expected


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
