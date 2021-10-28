from pyglet.text import Label


class CollisionObserver:
    def __init__(self):
        self.collision_count = 0
        self.total_collision_count = 0

    def reset(self):
        self.total_collision_count += self.collision_count
        self.collision_count = 0

    def collision(self, arbiter):
        self.collision_count += 1
        arb_points_set = arbiter.contact_point_set
        print(arb_points_set)

    def draw(self, label_pos):
        collision_text = f"collision:{self.collision_count} \ntotal:{self.total_collision_count}"

        collision_label = Label(
            collision_text,
            font_name="Times New Roman",
            font_size=10,
            x=label_pos[0],
            y=label_pos[1],
        )

        collision_label.draw()
