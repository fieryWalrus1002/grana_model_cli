"""
functions to help out that don't really have any particular class they should belong to right now. 
"""

from random import random


def pos_in_circle(origin: tuple, radius: float):
    """ rejection sampling to return a position within the bounds of a circle defined by an origin and radius. """

    while True:
        x = random() * 2 - 1 * radius
        y = random() * 2 - 1 * radius

        if x * x + y * y < radius:
            return x + origin[0], y + origin[1]


def rand_angle(degree_range: float) -> float:
    """ takes a max degree shift, and returns a random angle within the range +/- half
         the provided degree_range, converted to radians. 
    """
    return (random() * 2 - 1) * (0.5 * degree_range) * 0.0174533

