from ursina import *
from world import create_world, create_targets, create_enemies
from weapons import Gun
from player import PlayerController

# Initialize the app
app = Ursina()

# Create the world environment
create_world()

# Add targets to shoot at
create_targets(5)

# Add enemies
enemies = create_enemies(3)

# Add a player controller with health system
player = PlayerController(y=2, speed=10, name='PlayerController')

# Create gun instance
gun = Gun()

# Create FPS counter
fps_counter = Text(
    text="FPS: 0",
    position=(0.7, 0.45),
    origin=(0, 0),
    scale=1.2,
    color=color.lime
)

def update():
    # Update FPS counter every frame
    fps_counter.text = f"FPS: {round(1/time.dt)}"

# Handle keyboard inputs
def input(key):
    if key == 'r':
        if player.is_dead:
            player.respawn()
        else:
            gun.reload()

# Run the app
app.run()
