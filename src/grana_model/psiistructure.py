from math import degrees, sqrt
import random
from pymunk import Vec2d, Body, moment_for_circle, Poly, Space
import os
from pathlib import Path


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

        # print(str_out)

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

    # def action(self, action_num):
    #     if action_num == 0:
    #         # up
    #         self.move("up")
    #         pass
    #     if action_num == 1:
    #         # down
    #         self.move("down")
    #         pass
    #     if action_num == 2:
    #         # right
    #         self.move("right")
    #         pass
    #     if action_num == 3:
    #         # left
    #         self.move("left")
    #         pass
    #     if action_num == 4:
    #         # rotate left
    #         self.rotate(direction=0)
    #         pass
    #     if action_num == 5:
    #         # rotate right
    #         self.rotate(direction=1)
    #         pass

    def action(self, action_num):
        if action_num <= 4:
            self.move(random.randint(0, 3), step_dist=0.25)
        if action_num == 5:
            # rotate left
            self.rotate(direction=0)
            pass
        if action_num == 6:
            # rotate right
            self.rotate(direction=1)
            pass

    def rotate(self, direction):
        current_angle = self.body.angle
        # random_angle = random() * 2 * 0.0174533
        random_angle = random.random() * 15 * 0.0174533  # up to 15 degrees
        if direction == 0:
            # rotate left
            new_angle = current_angle + random_angle

            self.last_action = {
                "action": "rotate",
                "old_value": current_angle,
                "new_value": new_angle,
            }
        else:
            # rotate right
            new_angle = current_angle - random_angle

            self.last_action = {
                "action": "rotate",
                "old_value": current_angle,
                "new_value": new_angle,
            }
        # set the new angle
        self.body.angle = new_angle

    def move(self, direction, step_dist=1):
        step_distance = random.random() * step_dist

        # move in a direction but end within the tether distance
        # body.position.x and body.position.y can be modified, but the new position has to be within the distance of 1nm in any direction from the origin point.
        x0, y0 = self.origin_xy
        start_pos = self.body.position
        tether_radius = 1

        # the current dist from tether, starts too high because it is updated
        dist = 1000.0

        # is this a valid location?
        while dist > tether_radius and step_distance > 0:
            # will start as current pos
            x1, y1 = self.body.position

            # move in a direction the step distance
            if direction == 0:
                y1 += step_distance
            if direction == 1:
                y1 -= step_distance
            if direction == 2:
                x1 += step_distance
            if direction == 3:
                x1 -= step_distance

            # calculate the new distance from the tether point
            dist = sqrt(((x0 - x1) ** 2) + ((y0 - y1) ** 2))

            # each attempt will reduce the step distance a tiny amount
            step_distance -= 0.01

        # the new position is within the tether range, so lets assign it
        # if you didn't move at all, then you didn't move so keep your existing position
        if step_distance > 0:
            self.body.position = (x1, y1)

        # save the action so we can undo it later if needed
        self.last_action = {
            "action": "move",
            "old_value": start_pos,
            "new_value": self.body.position,
        }

    # ### random position
    #     # generate a new position within range of the origin, and move the object to that location
    #     # new position
    #     # random angle
    #     alpha = 2 * pi * random()

    #     # random radius, random float between 0 to 1 * tether_radius
    #     r = random() * tether_radius

    #     t = 2 * pi * random()

    #     # new (x, y) tuple
    #     random_pos = ((r*cos(t)) + x0, y0 + (r*sin(t)))
    #     # x1, y1 = obstacle.body.position

    #     #     # calculate distance from given point
    #     #     euc_dist = sqrt((x1-x)**2 + (y1-y)**2)

    #     #     # if the distance is less than the radius
    #     #     # add it to the selected obj list
    #     #     if euc_dist <= radius:
    #     #         sel_obj.append(obstacle)
