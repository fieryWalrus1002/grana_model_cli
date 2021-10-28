import pymunk
from math import degrees


class Particle(pymunk.Body):
    def __init__(self, space, pos, batch, particle_radius=1.5):
        self.max_movement = 1
        self.body = pymunk.Body(0, 0, body_type=pymunk.Body.DYNAMIC)
        c1 = pymunk.Circle(self.body, particle_radius)
        c1.color = (255, 0, 0, 255)
        self.shape = c1
        self.body.position = pos
        space.add(self.body, c1)
        self.diffusion_distance = 10

        self.img = None
        # TODO: get a better sprite
        # img.anchor_x = img.width // 2
        # img.anchor_y = img.height // 2

        # self.sprite = sprite.Sprite(
        #     img, x=self.body.position.x, y=self.body.position.y, batch=batch
        # )
        # self.sprite.scale = 0.003
        # self.sprite.color = (255, 255, 255)
        # self.sprite.rotation = degrees(-self.body.angle)

        # create the sprite
        self._assign_sprite(batch=batch)

    @property
    def area(self):
        """gets the total area of the object, by adding up the area of
        all of its indiviudal shapes. called as a property"""
        total_area = 0.0

        for shape in self.body.shapes:
            total_area += shape.area
        return total_area

    def __call__(self):
        return self.shape

    def update_sprite(self, sprite_scale_factor, rotation_factor):
        self.sprite.rotation = degrees(-self.body.angle) + rotation_factor
        self.sprite.position = self.body.position
        if self.sprite.scale == sprite_scale_factor:
            return
        self.sprite.scale = sprite_scale_factor

    def diffusion_move(self, diffusion_distance, **kwargs):
        pass
        # ''' generates movement in a random direction, up to 1 nm per timestep, which represents 12.5ns of time passed'''
        # # what direction will this particule move? in radians
        # theta = 2 * pi * random()

        # # radius of our possible movement circle. random float between 0 and self.max_movement
        # # OR whatever value is given by step_distance
        # step_distance = kwargs.get('step_distance', random() * self.max_movement)

        # # move in the random direction theta a distance equal to step_distance
        # x1, y1 = (step_distance*cos(theta)) + self.body.position.x, self.body.position.y + (step_distance*sin(theta))

        # # the distance traveled

        # dist = sqrt((self.body.position.x - x1)**2 + (self.body.position.y - y1)**2)

        # # the new position
        # self.body.position = (x1, y1)

        # # save the distance traveled
        # self.travel_distance.append(dist)
