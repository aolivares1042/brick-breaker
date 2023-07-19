# Dimensions of everything.
padding = 20
rows = 50
columns = 40
cell_size = 10

# How many frames we wait between ball udpates.
ball_slowness = 5

# Size of screen.
width = 2 * padding + cell_size * columns
height = 2 * padding + cell_size * rows

# Paddle info.
paddle_width = 9
paddle_height = 1
paddle_split = 3

frame_rate = 60

# Colors
background_color = (15, 23, 42)
border_color = (0, 0, 0)
paddle_color = (255, 255, 255)
ball_color = (255, 0, 0)
brick_colors = [
    (158, 227, 98),
    (0, 192, 208),
    (255, 212, 3),
    (255, 147, 86),
    (126, 116, 212),
    (254, 130, 170),
]
