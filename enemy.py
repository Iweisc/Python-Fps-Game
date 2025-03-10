from ursina import *
import math
import random

class Enemy(Entity):
    def __init__(self, position, waypoints=None):
        # Base entity setup
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
        self.current_state = self.IDLE
        self.state_timer = 0
        
        # Movement properties
        self.speed = 2
        self.rotation_speed = 100
        self.detection_range = 15  # How far the enemy can see
        self.detection_angle = 60  # Field of view in degrees
        
        # Patrol properties
        if waypoints:
            self.waypoints = waypoints
        else:
            # Create random patrol path if none provided
            self.waypoints = []
            center = position
            for i in range(4):  # Create 4 waypoints
                angle = i * 90  # Evenly space waypoints
                distance = random.uniform(5, 8)
                x = center.x + math.cos(math.radians(angle)) * distance
                z = center.z + math.sin(math.radians(angle)) * distance
                self.waypoints.append(Vec3(x, position.y, z))
        
        self.current_waypoint = 0
        self.waypoint_threshold = 0.5  # How close to get to a waypoint before moving to next
        
        # Health
        self.health = 3
        self.is_dead = False
        
        # Add visual elements to make it look more like an enemy
        self.head = Entity(
            parent=self,
            model='sphere',
            scale=(0.7, 0.7, 0.7),
            position=(0, 0.6, 0),
            color=color.rgb(160, 30, 30)
        )
        
        # Eyes to show which way the enemy is facing
        self.eyes = Entity(
            parent=self.head,
            model='sphere',
            scale=(0.2, 0.1, 0.1),
            position=(0, 0, 0.35),
            color=color.black
        )
        
        # Start in patrol state
        self.change_state(self.PATROL)
    
    def update(self):
        if self.is_dead:
            return
            
        # Update state timer
        self.state_timer += time.dt
        
        # State behaviors
        if self.current_state == self.IDLE:
            self.idle_behavior()
        elif self.current_state == self.PATROL:
            self.patrol_behavior()
        elif self.current_state == self.CHASE:
            self.chase_behavior()
        
        # Always check for player detection
        self.check_player_detection()
    
    def idle_behavior(self):
        # Just stand around, occasionally look around
        if self.state_timer > 3:  # After 3 seconds, go back to patrolling
            self.change_state(self.PATROL)
    
    def patrol_behavior(self):
        if len(self.waypoints) == 0:
            return
            
        # Move toward current waypoint
        target = self.waypoints[self.current_waypoint]
        self.look_at_2d(target)
        
        # Move forward
        distance = (target - self.position).length()
        if distance > self.waypoint_threshold:
            move_direction = (target - self.position).normalized()
            self.position += move_direction * self.speed * time.dt
        else:
            # Reached waypoint, move to next
            self.current_waypoint = (self.current_waypoint + 1) % len(self.waypoints)
            # Take a short break
            self.change_state(self.IDLE)
    
    def chase_behavior(self):
        # Find player if we don't have a reference
        if not hasattr(self, 'player') or not self.player:
            self.find_player()
            if not hasattr(self, 'player') or not self.player:
                self.change_state(self.PATROL)
                return
                
        player = self.player
        
        # Look at player
        self.look_at_2d(player.position)
        
        # Move toward player
        distance = (player.position - self.position).length()
        if distance > 2:  # Don't get too close
            move_direction = (player.position - self.position).normalized()
            self.position += move_direction * self.speed * 1.5 * time.dt  # Move faster when chasing
            
        # If lost sight, return to patrol
        if distance > self.detection_range:
            self.state_timer += time.dt
            if self.state_timer > 3:  # Give up after 3 seconds
                self.change_state(self.PATROL)
    
    def check_player_detection(self):
        # Skip detection checks if already chasing
        if self.current_state == self.CHASE:
            return
            
        # Find the player entity
        if not hasattr(self, 'player') or not self.player:
            self.find_player()
            
        if not hasattr(self, 'player') or not self.player:
            return
            
        player = self.player
        
        # Check if player is in range
        distance = (player.position - self.position).length()
        if distance <= self.detection_range:
            # Check if player is in field of view
            direction_to_player = (player.position - self.position).normalized()
            forward_dot_player = self.forward.dot(direction_to_player)
            angle_to_player = math.acos(max(min(forward_dot_player, 1), -1)) * 57.3  # Convert to degrees
            
            if angle_to_player <= self.detection_angle / 2:
                # Check if there's a clear line of sight
                hit_info = raycast(self.position + Vec3(0, 0.5, 0), direction_to_player, distance=distance)
                if hit_info.hit and hit_info.entity == player:
                    # Player detected!
                    print("Enemy spotted player!")
                    self.change_state(self.CHASE)
    
    def find_player(self):
        # Find the player in the scene
        for entity in scene.entities:
            if hasattr(entity, 'name') and entity.name == 'FirstPersonController':
                self.player = entity
                break
    
    def look_at_2d(self, target_pos):
        # Look at target but only rotate on Y axis (no tilting up/down)
        direction = Vec3(target_pos.x - self.x, 0, target_pos.z - self.z).normalized()
        target_rot = Vec3(0, math.degrees(math.atan2(direction.z, direction.x)) - 90, 0)
        
        # Smooth rotation
        self.rotation = lerp(self.rotation, target_rot, time.dt * self.rotation_speed)
    
    def change_state(self, new_state):
        self.current_state = new_state
        self.state_timer = 0
    
    def on_hit(self):
        # Visual feedback
        self.color = color.yellow
        invoke(setattr, self, 'color', color.rgb(220, 50, 50), delay=0.1)
        
        # Reduce health
        self.health -= 1
        if self.health <= 0 and not self.is_dead:
            self.die()
    
    def die(self):
        self.is_dead = True
        self.animate_scale((1, 0.1, 1), duration=0.3)
        destroy(self, delay=0.5)
