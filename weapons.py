from ursina import *

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
        
        # Create a Minecraft-style crosshair
        self.crosshair = Entity(parent=camera.ui)
        
        # Create the four lines of the crosshair with a gap in the middle
        crosshair_thickness = 0.002
        crosshair_length = 0.008
        crosshair_gap = 0.004
        crosshair_color = color.white
        
        # Top line
        Entity(parent=self.crosshair, model='quad', 
               scale=(crosshair_thickness, crosshair_length), 
               position=(0, crosshair_gap/2), 
               color=crosshair_color)
        
        # Bottom line
        Entity(parent=self.crosshair, model='quad', 
               scale=(crosshair_thickness, crosshair_length), 
               position=(0, -crosshair_gap/2), 
               color=crosshair_color)
        
        # Left line
        Entity(parent=self.crosshair, model='quad', 
               scale=(crosshair_length, crosshair_thickness), 
               position=(-crosshair_gap/2, 0), 
               color=crosshair_color)
        
        # Right line
        Entity(parent=self.crosshair, model='quad', 
               scale=(crosshair_length, crosshair_thickness), 
               position=(crosshair_gap/2, 0), 
               color=crosshair_color)
        
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
    
    # Rest of the class remains the same...
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
