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
        
        # Create the crosshair entity
        self.crosshair = Entity(
            parent=camera.ui,
            model=None,  # No model
            color=color.clear  # Transparent color
        )
        
        # Tiny crosshair parameters
        crosshair_thickness = 0.0001  # Very thin lines
        crosshair_length = 0.001      # Very short lines
        crosshair_gap = 0.001         # Small gap
        crosshair_color = color.white
        
        # Crosshair lines
        Entity(parent=self.crosshair, model='quad',
               scale=(crosshair_thickness, crosshair_length),
               position=(0, crosshair_gap/2),
               color=crosshair_color)
        Entity(parent=self.crosshair, model='quad',
               scale=(crosshair_thickness, crosshair_length),
               position=(0, -crosshair_gap/2),
               color=crosshair_color)
        Entity(parent=self.crosshair, model='quad',
               scale=(crosshair_length, crosshair_thickness),
               position=(-crosshair_gap/2, 0),
               color=crosshair_color)
        Entity(parent=self.crosshair, model='quad',
               scale=(crosshair_length, crosshair_thickness),
               position=(crosshair_gap/2, 0),
               color=crosshair_color)        
        
        # Improved ammo counter with background
        self.ammo_bg = Entity(
            parent=camera.ui,
            model='quad',
            scale=(0.2, 0.06),
            position=(0.7, -0.4),
            color=color.rgba(0, 0, 0, 0.7)
        )
        
        # Ammo counter with better visibility
        self.ammo_text = Text(
            parent=camera.ui,
            text=f"AMMO: {self.ammo}/{self.max_ammo}",
            position=(0.7, -0.4),
            origin=(0, 0),
            scale=1.5,
            color=color.white
        )
        
        # Out of ammo notification
        self.out_of_ammo_text = Text(
            parent=camera.ui,
            text="OUT OF AMMO! PRESS R TO RELOAD",
            position=(0, 0.15),  # Above crosshair
            origin=(0, 0),
            scale=2,
            color=color.red,
            visible=False  # Hidden by default
        )
        
        # Try to load sounds, use dummy if not found
        try:
            self.shoot_sound = Audio('shoot_sound.wav', loop=False, autoplay=False)
            self.empty_sound = Audio('empty_click.wav', loop=False, autoplay=False)
        except:
            print("Sound files not found, using silent audio")
            self.shoot_sound = None
            self.empty_sound = None
    
    def update(self):
        # Handle shooting cooldown
        if not self.can_shoot:
            self.shoot_cooldown -= time.dt
            if self.shoot_cooldown <= 0:
                self.can_shoot = True
                self.shoot_cooldown = self.fire_rate
        
        # Handle shooting input
        if mouse.left and self.can_shoot:
            if self.ammo > 0:
                self.shoot()
            else:
                self.empty_click()
    
    def shoot(self):
        # Consume ammo
        self.ammo -= 1
        self.ammo_text.text = f"AMMO: {self.ammo}/{self.max_ammo}"
        
        # Update ammo color based on amount
        if self.ammo == 0:
            self.ammo_text.color = color.red
        elif self.ammo <= 5:
            self.ammo_text.color = color.orange
        else:
            self.ammo_text.color = color.white
        
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
        
        # Hide "out of ammo" message if visible
        self.out_of_ammo_text.visible = False
        
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
    
    def empty_click(self):
        """Triggered when trying to shoot with no ammo"""
        # Show "out of ammo" message
        self.out_of_ammo_text.visible = True
        
        # Schedule it to disappear after 2 seconds
        invoke(setattr, self.out_of_ammo_text, 'visible', False, delay=2)
        
        # Play empty click sound if available
        if self.empty_sound:
            self.empty_sound.play()
        
        # Small gun movement for feedback
        self.animate_position(
            self.original_position + Vec3(0, 0, 0.02),  # Smaller movement than actual shot
            duration=0.05,
            curve=curve.linear
        )
        self.animate_position(
            self.original_position,
            duration=0.1,
            delay=0.05,
            curve=curve.linear
        )
        
        # Fire rate cooldown (shorter than normal shooting)
        self.can_shoot = False
        self.shoot_cooldown = 0.1
    
    def reload(self):
        """Reload the weapon to full ammo"""
        if self.ammo == self.max_ammo:
            return
            
        print("Reloading...")
        self.ammo = self.max_ammo
        self.ammo_text.text = f"AMMO: {self.ammo}/{self.max_ammo}"
        self.ammo_text.color = color.white  # Reset color
        self.out_of_ammo_text.visible = False  # Hide out of ammo message
        print("Reload complete!")
