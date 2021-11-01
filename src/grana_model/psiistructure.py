from math import degrees, sqrt
import random
from pymunk import Vec2d, Body, moment_for_circle, Poly, Space
import os
from pathlib import Path
from .utils import pos_in_circle, rand_angle


class PSIIStructure:
    def __init__(
        self,
        space: Space,
        obj_dict: dict,
        batch: None,
        shape_type: str,
        pos: tuple[float, float],
        angle: float,
        mass=100,
    ):
        self.obj_dict = obj_dict
        self.type = obj_dict["obj_type"]
        self.origin_xy = pos
        self.current_xy = pos
        self.last_action = {
            "action": "rotate",
            "old_value": angle,
            "new_value": angle,
        }
        self.new_scale = 100

        self.body = self._create_body(mass=mass, angle=angle)

        shape_list, shape_str = self._create_shape_string(shape_type=shape_type)
        eval(shape_str)

    def _create_body(self, mass: float, angle: float):
        """create a pymunk.Body object with given mass, position, angle"""

        inertia = moment_for_circle(
            mass=mass, inner_radius=0, outer_radius=10, offset=(0, 0)
        )

        if self.type in ["C2S2M2", "C2S2M", "C2S2", "C2", "C1"]:
            body = Body(mass=mass, moment=inertia, body_type=Body.KINEMATIC)
        else:
            body = Body(mass=mass, moment=inertia, body_type=Body.DYNAMIC)

        body.position = self.origin_xy  # given pos
        body.angle = angle
        body.velocity_func = self.limit_velocity  # limit velocity

        return body

    @property
    def area(self):
        """gets the total area of the object, by adding up the area of
        all of its indiviudal shapes. called as a property"""
        total_area = 0.0

        for shape in self.body.shapes:
            total_area += shape.area
        return total_area

    def _create_shape_string(self, shape_type: str):
        """create a shape_string that when provided as
        an argument to eval(), will create all the compound or simple
        shapes needed to define complex structures and
        add them to the space along with self.body"""

        if shape_type == "simple":
            coord_list = self.obj_dict["shapes_simple"]
        else:
            coord_list = self.obj_dict["shapes_compound"]
        shape_list = [
            self._create_shape(shape_coord=shape_coord)
            for shape_coord in coord_list
        ]

        return (
            shape_list,
            f"space.add(self.body, {','.join([str(f'shape_list[{i}]') for i, shape in enumerate(shape_list)])})",
        )

        # str_out = f"space.add({str_command})"

        # #print(str_out)

        # return shape_list, str_out

    def _create_shape(self, shape_coord: tuple):
        """creates a shape"""
        my_shape = Poly(self.body, vertices=shape_coord)

        my_shape.color = self.obj_dict["color"]

        my_shape.collision_type = 1

        return my_shape

    def update_sprite(self, sprite_scale_factor, rotation_factor):
        self.sprite.rotation = degrees(-self.body.angle) + rotation_factor
        self.sprite.position = self.body.position
        if self.sprite.scale == sprite_scale_factor:
            return
        self.sprite.scale = sprite_scale_factor

    def get_current_pos(self):
        self.current_xy = (self.body.x, self.body.y)

    def go_home(self):
        direction = Vec2d(
            x=self.origin_xy[0] / 10000, y=self.origin_xy[1] / 10000
        )
        self.body.apply_force_at_local_point(force=direction, point=(0, 0))

    def limit_velocity(self, body, gravity, damping, dt):
        max_velocity = 1
        Body.update_velocity(body, gravity, damping, dt)
        body_velocity_length = body.velocity.length
        if body_velocity_length > max_velocity:
            scale = max_velocity / body_velocity_length
            body.velocity = body.velocity * scale

    def undo(self):
        if self.last_action["action"] == "rotate":
            self.body.angle = self.last_action["old_value"]
        if self.last_action["action"] == "move":
            self.body.position = self.last_action["old_value"]

    def action(self, action_num):
        if action_num == 1:
            self.move()

        if action_num == 2:
            self.rotate(degree_range=90.0)

    def _save_action(self, action: str, old_value, new_value):
        self.last_action = {
            "action": action,
            "old_value": old_value,
            "new_value": new_value,
        }

    def rotate(self, degree_range: float):
        """ rotates the object to a random angle, plus or minus half degree_range"""
        current_angle = self.body.angle

        self.body.angle = current_angle + rand_angle(degree_range=degree_range)

        self._save_action("rotate", current_angle, self.body.angle)

    def move(self, tether_radius: float = 1.0):
        """ handles moving the object to a new location within its tether_radius.

            Also saves the current position of the object before moving it, so we can restore it if 
            necessary, via undo()
            
            Parameters:
            tether_radius: the maximum distance from the original location of the object upon instantiation.
        """
        start_pos = self.body.position

        self.body.position = pos_in_circle(
            origin=self.body.position, radius=tether_radius
        )

        self._save_action("move", start_pos, self.body.position)

