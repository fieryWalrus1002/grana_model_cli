# -*- coding: utf-8 -*-
"""simulation environment

This module implements an the grana_model simulation environment, with object instantiation,
overlap detection. It does not produce any graphical output on its own.

Parameters:
    pos_csv_filename (Path): path to the csv file containing object positions in format:
        type, position.x, position.y, angle, area

Example:
    $ 
    $ 

Todo:
    * everything. abstract strategies, coding the overlap agent, etc.

.. _Google Python Style Guide:
   http://google.github.io/styleguide/pyguide.html

"""
import pymunk


# from grana_model.spawner import Spawner
# from grana_model.objectdata import ObjectDataExistingData, ObjectData
# from grana_model.collisionhandler import CollisionHandler

from .spawner import Spawner
from .objectdata import ObjectDataExistingData, ObjectData
from .collisionhandler import CollisionHandler


class SimulationEnvironment:
    """represents a simulation environment, with pymunk.Space, PSIIStructures instantiated within it by a Spawner instance from a provided coord file."""

    def __init__(
        self, pos_csv_filename: str, object_data_exists: bool, gui: bool = False
    ):
        self.space = pymunk.Space()

        self.batch = None

        if object_data_exists:
            object_data = ObjectDataExistingData(
                pos_csv_filename=pos_csv_filename
            )
        else:
            object_data = ObjectData(pos_csv_filename=pos_csv_filename)

        self.spawner = Spawner(
            object_data=object_data,
            spawn_type="psii_only",
            shape_type="complex",
            space=self.space,
            batch=self.batch,
            num_particles=0,
            num_psii=211,
        )

        self.collision_handler = CollisionHandler(self.space)
