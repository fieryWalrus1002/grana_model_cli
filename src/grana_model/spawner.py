from pymunk.space import Space
from .psiistructure import PSIIStructure
from .particle import Particle
from .objectdata import ObjectData
from random import random
from math import cos, sin, pi


class Spawner:
    """handles instantiation of objects into the simulation window, and for now
    has a random_pos_in_circle function because where else should it go"""

    def __init__(
        self,
        object_data: ObjectData,
        shape_type: str,
        space: Space,
        batch: None,
        spawn_type: str,
        num_particles: int = 1000,
        num_psii: int = 1000,
    ):
        self.object_data = object_data
        self.num_psii = num_psii
        self.num_particles = num_particles
        self.ratio_free_LHC = 2.0  # Helmut says "Assuming that you have 212 PSII (dimer =C2) particles then LHCII should be 424 (2xPSII)"
        self.ratio_cytb6f = 0.3  # 083021: Helmut says cyt b6f 70 (1/3 x PSII)
        self.shape_type = shape_type
        self.spawn_type = spawn_type
        self.space = space
        self.batch = batch

    def random_angle(self) -> float:
        """returns a random angle in radians"""
        return 2 * pi * random()

    def random_pos_in_circle(
        self, max_radius: float = 200, center: tuple[float, float] = (200, 200)
    ) -> tuple[float, float]:
        """return a random position in the circle"""
        rand_roll = random() + random()

        if rand_roll > 1:
            r = (2 - rand_roll) * max_radius
        else:
            r = rand_roll * max_radius

        t = self.random_angle()

        return ((r * cos(t)) + center[0], center[1] + (r * sin(t)))

    def setup_model(self):
        """instantiates particles and obstacles according to spawner provided spawn_type"""

        if self.spawn_type == "psii_only":
            return self.spawn_psii(), self.spawn_particles_empty()

        if self.spawn_type == "psii_secondary_noparticles":
            return (
                self.spawn_psii() + self.spawn_cytb6f() + self.spawn_lhcii(),
                self.spawn_particles_empty(),
            )
        else:
            return (
                self.spawn_psii() + self.spawn_cytb6f() + self.spawn_lhcii(),
                self.spawn_particles(),
            )

    def spawn_psii(self):
        """spawns only psii obstacles into the simulation space to be rendered
        as part of the provided batch, and appends them to the list provided
        for later usage in the simulation model, up to a limit of self.num_psii"""

        object_list = []

        while len(object_list) < self.num_psii:
            try:
                obj = next(self.object_data.object_list)
            except StopIteration:
                return object_list
            # #print(obj)
            # if obj.get("obj_type") == "C2S2M2":
            object_list.append(
                PSIIStructure(
                    self.space,
                    obj,
                    self.batch,
                    self.shape_type,
                    pos=obj.get("pos"),
                    angle=obj.get("angle"),
                )
            )

        return object_list

    def spawn_particles(self):
        """Instantiates particles into the simulation space and returns a list
        of the particles for later usage in the simulation model
        """
        object_list = [
            Particle(
                space=self.space,
                batch=self.batch,
                pos=self.random_pos_in_circle(),
            )
            for _ in range(0, self.num_particles)
        ]

        return object_list

    def spawn_particles_empty(self):
        """return an empty list for when you don't want to spawn particles"""
        return []

    def spawn_lhcii(self):
        """spawns LHCII and cytb6f objects into the simulation space"""
        lhcii_list = [
            PSIIStructure(
                self.space,
                self.object_data.type_dict["LHCII"],
                self.batch,
                self.shape_type,
                pos=self.random_pos_in_circle(),
                angle=self.random_angle(),
            )
            for _ in range(0, int(self.ratio_free_LHC * self.num_psii))
        ]
        return lhcii_list

    def spawn_cytb6f(self):
        """spawns cytb6f objects into the simulation space"""
        cytb6f_list = [
            PSIIStructure(
                self.space,
                self.object_data.type_dict["cytb6f"],
                self.batch,
                self.shape_type,
                pos=self.random_pos_in_circle(),
                angle=self.random_angle(),
            )
            for _ in range(0, int(self.ratio_free_LHC * self.num_psii))
        ]
        return cytb6f_list
