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

# Create FPS counter with simpler settings
fps_counter = Text(
    text="FPS: 0",
    position=(-0.85, 0.45),  # Top left position
    scale=2,
    color=color.yellow
)

# Add a debug text to confirm text rendering is working
debug_text = Text(
    text="DEBUG: TEXT VISIBLE",
    position=(0, 0),  # Center of screen
    scale=2,
    color=color.red
)

def update():
    # Update FPS counter every frame
    if fps_counter:
        fps_counter.text = f"FPS: {round(1/time.dt)}"
    
    # Print once to confirm update is running
    if not hasattr(update, 'has_run'):
        print("Update function is running")
        update.has_run = True

# Add reload functionality with R key
def input(key):
    if key == 'r':
        gun.reload()
    # Debug key to test text visibility
    if key == 't':
        print("Text test triggered")
        if debug_text:
            debug_text.text = f"DEBUG: TEXT VISIBLE {time.time()}"
            debug_text.color = color.random_color()

# Run the app
app.run()
