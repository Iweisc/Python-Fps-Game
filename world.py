from ursina import *
import random
from target import Target
from enemy import Enemy

def create_world():
    # Create a flat ground
    ground = Entity(
        model='plane',
        scale=(100, 1, 100),
        color=color.green,
        texture='grass',
        texture_scale=(100, 100),
        collider='box'
    )
    
    # Add a basic skybox
    sky = Sky()
    
    return ground, sky

def create_targets(count):
    targets = []
    for i in range(count):
        target = Target(position=(random.uniform(-20, 20), 1.5, random.uniform(-20, 20)))
        targets.append(target)
    return targets

def create_enemies(count):
    enemies = []
    for i in range(count):
        # Create a patrol path around a random position
        center = Vec3(random.uniform(-20, 20), 1, random.uniform(-20, 20))
        enemy = Enemy(position=center)
        enemies.append(enemy)
    
    return enemies
