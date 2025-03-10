from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController

class PlayerController(FirstPersonController):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        self.name = 'PlayerController'
        self.cursor.visible = False
        
        # Health system
        self.max_health = 100
        self.health = self.max_health
        self.is_dead = False
        
        # Health bar
        self.health_bar_bg = Entity(
            parent=camera.ui,
            model='quad',
            scale=(0.3, 0.03),
            position=(-0.6, -0.4),
            color=color.rgba(0, 0, 0, 0.8)
        )
        
        self.health_bar = Entity(
            parent=camera.ui,
            model='quad',
            scale=(0.3, 0.03),
            position=(-0.6, -0.4),
            color=color.rgba(0, 1, 0, 0.8)
        )
        
        self.health_text = Text(
            parent=camera.ui,
            text=f"Health: {self.health}/{self.max_health}",
            position=(-0.6, -0.35),
            origin=(0, 0),
            scale=1.5,
            color=color.white
        )
        
        # Damage overlay (red flash when taking damage)
        self.damage_overlay = Entity(
            parent=camera.ui,
            model='quad',
            scale=(2, 1),
            color=color.rgba(1, 0, 0, 0),
            z=-1
        )
        
        # Death screen
        self.death_screen = Entity(
            parent=camera.ui,
            model='quad',
            texture='white_cube',
            scale=(2, 1),
            color=color.rgba(0, 0, 0, 0.85),
            z=-1,
            enabled=False
        )
        
        self.death_text = Text(
            parent=camera.ui,
            text="YOU DIED",
            origin=(0, 0),
            scale=5,
            color=color.red,
            position=(0, 0.1),
            enabled=False
        )
        
        self.restart_text = Text(
            parent=camera.ui,
            text="Press R to restart",
            origin=(0, 0),
            scale=2,
            color=color.white,
            position=(0, -0.1),
            enabled=False
        )
    
    def update(self):
        if not self.is_dead:
            super().update()
            
            # Update health bar
            self.health_bar.scale_x = 0.3 * (self.health / self.max_health)
            self.health_bar.x = self.health_bar_bg.x - (0.3 - self.health_bar.scale_x) / 2
            
            # Update health bar color
            if self.health < self.max_health * 0.2:  # Below 20%
                self.health_bar.color = color.rgba(1, 0, 0, 0.8)  # Red
            elif self.health < self.max_health * 0.5:  # Below 50%
                self.health_bar.color = color.rgba(1, 0.5, 0, 0.8)  # Orange
            else:
                self.health_bar.color = color.rgba(0, 1, 0, 0.8)  # Green
    
    def take_damage(self, amount):
        """Handle player taking damage"""
        if self.is_dead:
            return
            
        # Reduce health
        self.health = max(0, self.health - amount)
        
        # Update health text
        self.health_text.text = f"Health: {self.health}/{self.max_health}"
        
        # Show damage effect
        self.damage_overlay.color = color.rgba(1, 0, 0, 0.3)  # Show red flash
        self.damage_overlay.animate_color(
            color.rgba(1, 0, 0, 0),
            duration=0.5,
            curve=curve.linear
        )
        
        # Check for death
        if self.health <= 0:
            self.die()
    
    def heal(self, amount):
        """Handle player healing"""
        if self.is_dead:
            return
            
        # Increase health
        self.health = min(self.max_health, self.health + amount)
        
        # Update health text
        self.health_text.text = f"Health: {self.health}/{self.max_health}"
    
    def die(self):
        """Handle player death"""
        if self.is_dead:
            return
            
        self.is_dead = True
        print("Player died!")
        
        # Disable movement
        self.speed = 0
        self.jump_height = 0
        self.mouse_sensitivity = (0, 0)
        
        # Show death screen
        self.death_screen.enabled = True
        self.death_text.enabled = True
        self.restart_text.enabled = True
        
        # Animate death text appearance
        self.death_text.scale = 0
        self.death_text.animate_scale(5, duration=1, curve=curve.out_expo)
        
        # Play death animation
        camera.animate_position(
            camera.position + Vec3(0, -0.5, 0),
            duration=1,
            curve=curve.out_expo
        )
        camera.animate_rotation(
            camera.rotation + Vec3(90, 0, 0),
            duration=1,
            curve=curve.out_expo
        )
    
    def respawn(self):
        """Reset player after death"""
        if not self.is_dead:
            return
            
        # Reset health
        self.health = self.max_health
        self.health_text.text = f"Health: {self.health}/{self.max_health}"
        self.is_dead = False
        
        # Reset position and movement
        self.position = Vec3(0, 2, 0)
        self.speed = 10
        self.jump_height = 2
        self.mouse_sensitivity = (40, 40)
        
        # Reset camera
        camera.rotation = Vec3(0, 0, 0)
        
        # Hide death screen
        self.death_screen.enabled = False
        self.death_text.enabled = False
        self.restart_text.enabled = False
