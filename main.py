from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
from world import create_world, create_targets, create_enemies
from weapons import Gun

# Initialize the app
app = Ursina()

# Create the world environment
create_world()

# Add targets to shoot at
create_targets(5)

# Add enemies
enemies = create_enemies(3)

# Add a first-person controller for camera and movement
player = FirstPersonController(y=2, speed=10, name='FirstPersonController')

# Create gun instance
gun = Gun()

# Add reload functionality with R key
def input(key):
    if key == 'r':
        gun.reload()

# Run the app
app.run()
