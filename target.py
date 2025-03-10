from ursina import *

class Target(Entity):
    def __init__(self, position):
        super().__init__(
            model='cube',
            scale=(1, 1, 1),
            position=position,
            color=color.red,
            collider='box'
        )
        self.health = 3
    
    def on_hit(self):
        # Visual feedback
        self.color = color.yellow
        invoke(setattr, self, 'color', color.red, delay=0.1)
        
        # Physical response
        hit_direction = (self.position - camera.world_position).normalized()
        hit_direction.y = 0
        force = hit_direction * 1 + Vec3(0, 0.5, 0)
        
        # Animate the movement
        self.animate_position(
            self.position + force,
            duration=0.2,
            curve=curve.linear
        )
        
        # Reduce health
        self.health -= 1
        if self.health <= 0:
            destroy(self)
