from ursina import *
import math
import random

class Enemy(Entity):
    def __init__(self, position, waypoints=None):
        super().__init__(
            model='cube',
            scale=(1, 2, 1),  # Taller than wide for humanoid shape
            position=position,
            color=color.rgb(220, 50, 50),  # Reddish color
            collider='box'
        )
        
        # States
        self.IDLE = 0
        self.PATROL = 1
        self.CHASE = 2
        self.ATTACK = 3  # New attack state
        self.current_state = self.IDLE
        self.state_timer = 0
        
        # Movement properties
        self.speed = 2
        self.rotation_speed = 100
        self.detection_range = 15  # How far the enemy can see
        self.detection_angle = 60  # Field of view in degrees
        self.attack_range = 3      # Range at which enemy will attack
        
        # Combat properties
        self.damage = 10           # Damage per attack
        self.attack_cooldown = 1.5  # Seconds between attacks
        self.can_attack = True
        self.attack_timer = 0
        
        # Health and waypoints from the original code
        self.health = 3
        self.is_dead = False
        
        if waypoints:
            self.waypoints = waypoints
        else:
            # Create random patrol path if none provided
            self.waypoints = []
            center = position
            for i in range(4):
                angle = i * 90
                distance = random.uniform(5, 8)
                x = center.x + math.cos(math.radians(angle)) * distance
                z = center.z + math.sin(math.radians(angle)) * distance
                self.waypoints.append(Vec3(x, position.y, z))
        
        self.current_waypoint = 0
        self.waypoint_threshold = 0.5
        
        # Add visual elements (head, eyes like in original)
        self.head = Entity(
            parent=self,
            model='sphere',
            scale=(0.7, 0.7, 0.7),
            position=(0, 0.6, 0),
            color=color.rgb(160, 30, 30)
        )
        
        self.eyes = Entity(
            parent=self.head,
            model='sphere',
            scale=(0.2, 0.1, 0.1),
            position=(0, 0, 0.35),
            color=color.black
        )
        
        # Add a weapon for visual effect
        self.weapon
