import pygame

from constants import width, height, frame_rate
import game


def main():
    # Initialize stuff.
    pygame.init()
    clock = pygame.time.Clock()
    screen = pygame.display.set_mode((width, height))
    state = game.GameState(game.make_matrix())

    while True:
        # Call `update`. If it returns `True`, we should quit so we break out
        # of the loop.
        if state.update():
            break

        # Draw the state to the screen.
        state.draw_to(screen)

        # Wait a bit.
        clock.tick(frame_rate)

    pygame.quit()


if __name__ == "__main__":
    main()
