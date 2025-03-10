from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
import random

# Initialize the app
app = Ursina()

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

# Gun class to handle weapon mechanics
class Gun(Entity):
    def __init__(self):
        super().__init__(
            parent=camera,
            model='cube',
            scale=(0.5, 0.2, 1),
            position=(0.6, -0.3, 1),
            color=color.black
        )
        
        # Gun properties
        self.max_ammo = 30
        self.ammo = self.max_ammo
        self.fire_rate = 0.15
        self.can_shoot = True
        self.shoot_cooldown = self.fire_rate
        
        # Store original position for recoil animation
        self.original_position = self.position
        
        # Muzzle flash
        self.muzzle_flash = Entity(
            parent=self,
            model='cube',
            scale=(0.2, 0.2, 0.2),
            position=(0, 0, -0.6),
            color=color.yellow,
            enabled=False
        )
        
        # Create a crosshair
        self.crosshair = Entity(parent=camera.ui)
        Entity(parent=self.crosshair, model='quad', scale=(0.01, 0.001), color=color.white)
        Entity(parent=self.crosshair, model='quad', scale=(0.001, 0.01), color=color.white)
        
        # Ammo counter
        self.ammo_text = Text(
            parent=camera.ui,
            text=f"Ammo: {self.ammo}/{self.max_ammo}",
            position=(-0.7, -0.4),
            scale=2
        )
        
        # Try to load sounds, use dummy if not found
        try:
            self.shoot_sound = Audio('shoot_sound.wav', loop=False, autoplay=False)
        except:
            print("Sound file not found, using silent audio")
            self.shoot_sound = None
    
    def update(self):
        # Handle shooting cooldown
        if not self.can_shoot:
            self.shoot_cooldown -= time.dt
            if self.shoot_cooldown <= 0:
                self.can_shoot = True
                self.shoot_cooldown = self.fire_rate
        
        # Handle shooting input
        if mouse.left and self.can_shoot and self.ammo > 0:
            self.shoot()
    
    def shoot(self):
        # Consume ammo
        self.ammo -= 1
        self.ammo_text.text = f"Ammo: {self.ammo}/{self.max_ammo}"
        
        # Fire rate cooldown
        self.can_shoot = False
        
        # Play sound if available
        if self.shoot_sound:
            self.shoot_sound.play()
        
        # Show muzzle flash briefly
        self.muzzle_flash.enabled = True
        invoke(setattr, self.muzzle_flash, 'enabled', False, delay=0.05)
        
        # Apply recoil animation
        self.animate_position(
            self.original_position + Vec3(0, 0, 0.05),  # Recoil back
            duration=0.05,
            curve=curve.linear
        )
        self.animate_position(
            self.original_position,  # Return to original position
            duration=0.1,
            delay=0.05,
            curve=curve.linear
        )
        
        # Perform raycast from camera position
        hit_info = raycast(camera.world_position, camera.forward, distance=100)
        
        if hit_info.hit:
            # Create hit effect
            hit_effect = Entity(
                model='sphere',
                scale=0.1,
                position=hit_info.world_point,
                color=color.yellow
            )
            destroy(hit_effect, delay=0.5)
            
            # Handle target hit
            if hasattr(hit_info.entity, 'on_hit'):
                hit_info.entity.on_hit()
    
    def reload(self):
        if self.ammo == self.max_ammo:
            return
            
        print("Reloading...")
        self.ammo = self.max_ammo
        self.ammo_text.text = f"Ammo: {self.ammo}/{self.max_ammo}"
        print("Reload complete!")

# Target class with physics response
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

# Add some targets to shoot at
for i in range(10):
    Target(position=(random.uniform(-20, 20), 1.5, random.uniform(-20, 20)))

# Add a first-person controller for camera and movement
player = FirstPersonController(y=2, speed=10)

# Create gun instance
gun = Gun()

# Add reload functionality with R key
def input(key):
    if key == 'r':
        gun.reload()

# Run the app
app.run()
