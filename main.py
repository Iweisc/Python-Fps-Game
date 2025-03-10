from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController

# Initialize the Ursina app
app = Ursina()

# Create a flat ground
ground = Entity(
    model='plane',           # Using a plane model for the ground
    scale=(100, 1, 100),     # Making it large enough to explore
    color=color.green,       # Green color for grass-like appearance
    texture='grass',         # Apply a grass texture
    texture_scale=(100, 100),# Scale the texture appropriately
    collider='box'           # Add collision so player doesn't fall through
)

# Add a basic skybox
sky = Sky()

# Add a first-person controller for camera and movement
player = FirstPersonController(y=2, speed=10)

# Run the app
app.run()
