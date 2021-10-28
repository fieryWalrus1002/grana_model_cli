# -*- coding: utf-8 -*-
"""Overlap reduction agent

This module implements an agent that attempts to reduce overlap between objects
in the simulation, and strategies that it can follow to perform this duty. 

Can be run from the command line by calling a SimulationEnvironment, or used as part of the SimulationWindow.
No command line arguments are required, but are going to be implemented so I can run this on Kamiak in the future.

Example:
    $ overlap_agent = OverlapAgent(area_strategy=chosen_strategy, time_limit=1000,
        space=space)
    $ overlap_agent.run()

    or 

    $ py3 -m overlap_agent.py
    

Todo:
    * everything. abstract strategies, coding the overlap agent, etc.

.. _Google Python Style Guide:
   http://google.github.io/styleguide/pyguide.html

"""
import argparse
import csv
import math
import random
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path

import pymunk

from .collisionhandler import CollisionHandler
from .psiistructure import PSIIStructure
from .simulationenv import SimulationEnvironment

# from time import process_time, strftime


class AreaStrategy(ABC):
    """Strategy interface: abstract base class for area selection strategies."""

    @abstractmethod
    def __init__(self, object_list, origin_point):
        pass

    @classmethod
    def reset(self):
        pass

    @abstractmethod
    def total_zones(self):
        pass


class Rings(AreaStrategy):
    """divides all the objects into fives bands and will return band lists as requested"""

    def __init__(
        self, object_list: list, origin_point: tuple[float, float] = (200, 200)
    ):
        self.object_list = object_list
        self.origin_point = origin_point
        self.index = -1
        self.zone_distances = [
            (0.0, 89.0),
            (89.0, 127.0),
            (127.0, 155.0),
            (155.0, 178.0),
            (178.0, 200.0),
            (0.0, 200.0),
        ]
        self.zone_list = self.create_zones(self.object_list)

    def reset(self):
        self.zone_list = self.create_zones(self.object_list)
        self.index = -1

    def create_zones(self, object_list: list) -> list:
        """sorts the objects into bands according to their distance from origin_point and return a list of lists
        The final ring is actually ALL of the objects in the full object_list, so we can reuse it later

        """
        zone_list = [
            [
                object
                for object in object_list
                if self._object_in_ring(object=object, band=ring)
            ]
            for ring in self.zone_distances
        ]
        print(
            f"len(zone_list): {len(zone_list)}, len(zone_list[0]): {len(zone_list[0])}"
        )

        return zone_list

    def get_next_zone(self):
        return self.__next__()

    def __iter__(self):
        return self

    def __next__(self):
        """returns the list of objects for the next zone"""
        self.index += 1
        if self.index >= len(self.zone_list):
            raise StopIteration
        return self.zone_list[self.index]

    def _object_in_ring(self, object, band: tuple[float, float]):
        """Check if the object is within the given range band"""

        x0, y0 = self.origin_point
        x1, y1 = object.body.position
        obj_dist = math.sqrt((x0 - x1) ** 2 + (y0 - y1) ** 2)

        if obj_dist > band[0] and obj_dist < band[1]:
            return True
        else:
            return False

    @property
    def total_zones(self):
        return len(self.zone_distances)


class ExpandingCircle(AreaStrategy):
    """divides all the objects into four bands and will return lists as requested"""

    def __init__(
        self, object_list: list, origin_point: tuple[float, float] = (200, 200)
    ):
        self.origin_point = origin_point
        self.index = -1
        self.zone_distances = [89, 127, 155, 178, 200]
        self.object_list = object_list
        self.zone_list = self.create_zones(self.object_list)

    @property
    def total_zones(self):
        return len(self.zone_distances)

    def reset(self):
        self.zone_list = self.create_zones(self.object_list)
        self.index = -1

    def create_zones(self, object_list: list) -> list:
        """sorts the objects into bands according to their distance from origin_point and return a list of lists"""
        zone_list = [
            [
                object
                for object in object_list
                if self._object_in_zone(object=object, distance=distance)
            ]
            for distance in self.zone_distances
        ]
        return zone_list

    def get_next_zone(self):
        return self.__next__()

    def __iter__(self):
        return self

    def __next__(self):
        """returns the list of objects for the next zone"""
        self.index += 1
        if self.index >= len(self.zone_list):
            raise StopIteration
        return self.zone_list[self.index]

    def _object_in_zone(self, object, distance: float):
        """Check if the object is within the given distance from origin_point, returns"""
        x0, y0 = self.origin_point
        x1, y1 = object.body.position
        obj_dist = math.sqrt((x0 - x1) ** 2 + (y0 - y1) ** 2)

        if obj_dist < distance:
            return True
        else:
            return False


class OverlapAgent:
    """The overlap_agent acts to reduce overlap between objects.

    overlap_agent:
        - calls objects in successive areas (area chosen via strategy),
        one by one, with a function such as below for a certain period of time
        - call_object(object):
            1. tell object to take an action (random choice? or decide?)
            2. step simulation/refresh shape states
            3. evaluate the action effect on overlap
            4. either keep or undo action
        - agent has a limited amount of time to make improvement.
            - If rate of improvement is less than a threshold in strategy:
                1. give up trying in this area. Expand area.
                2. If all areas have already been included, simulation ends.

    Parameters:
        time_limit (int): maximum number of actions before simulation moves to next
        period or ends. Default=1000

        object_list (list of PSIIStructure): divides this list

        area_strategy (AreaStrategy): defines how the object in object_list are
        divided into multiple lists, one for each zone

    Attributes:
        self.time_limit (int): as above
        self.time_left (int): starts equal to self.time_limit, is reduced by one for each action taken


    """

    area_strategy = AreaStrategy

    def __init__(
        self,
        space: pymunk.Space,
        object_list: list,
        collision_handler: CollisionHandler,
        time_limit: int = 1000,
        area_strategy: AreaStrategy = None,
    ):
        self.time_limit = time_limit
        self.time_left = time_limit
        self.space = space
        self.overlap_distance = 0.0
        self.collision_handler = collision_handler

        if area_strategy is not None:
            print(f"using {area_strategy}")
            self.area_strategy = area_strategy
        else:
            print("no area strategy provided, using ExpandingCircle")
            self.area_strategy = ExpandingCircle(
                object_list, origin_point=(200, 200),
            )

    def run(self, debug=False):
        """runs the overlap agent through the zone list"""
        overlap_values = []
        for zone_num, zone_list in enumerate(self.area_strategy):
            for i in range(0, self.time_limit):
                overlap = self._call_object(object=random.choice(zone_list))
                overlap_values.append(overlap)

            mean_overlap = sum(overlap_values[-10:-1]) / 10

            if debug:
                print(
                    f"zone: {zone_num + 1}/5 finished, time_limit: {self.time_limit}, overlap: {round(mean_overlap, 2)}"
                )

            if zone_num == self.area_strategy.total_zones - 1:
                self.export_coordinates(zone_num, zone_list, mean_overlap)

        self.area_strategy.reset()
        return overlap_values

    def _call_object(self, object):
        """calls object to perform an action, evaluate it, and either keep it or undo it"""
        if type(object) is not PSIIStructure:
            print("not a PSIIStructure")
            return

        object.action(random.randint(1, 6))

        new_overlap_distance = self._update_space()

        if self.overlap_distance < new_overlap_distance:
            object.undo()
            new_overlap_distance = self._update_space()

        self.overlap_distance = new_overlap_distance
        return self.overlap_distance

    def _update_space(self):
        self.collision_handler.reset_collision_count()
        self.space.step(0.1)
        return self.collision_handler.overlap_distance

    def initialize_space(self):
        self.space.step(0.01)
        self.overlap_distance = self.collision_handler.overlap_distance

    def export_coordinates(self, zone_num, zone_list, mean_overlap):
        now = datetime.now()
        dt_string = now.strftime("%d%m%Y_%H%M%S")
        filename = (
            Path.cwd()
            / "src"
            / "grana_model"
            / "res"
            / "grana_coordinates"
            / f"{dt_string}_{zone_num}_overlap_{int(mean_overlap)}_data.csv"
        )

        with open(filename, "w", newline="") as f:
            write = csv.writer(f)
            # write the headers
            write.writerow(["type", "x", "y", "angle", "area"])
            for object in zone_list:
                write.writerow(
                    (
                        object.type,
                        object.body.position[0],
                        object.body.position[1],
                        object.body.angle,
                        object.area,
                    )
                )
