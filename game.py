from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum, auto
from random import random, choice
from typing import Self

import pygame

from constants import (
    columns,
    rows,
    paddle_width,
    paddle_height,
    ball_slowness,
    padding,
    cell_size,
    paddle_split,
    background_color,
    border_color,
    paddle_color,
    ball_color,
    brick_colors,
)

Coord = tuple[int, int]


class Direction(Enum):
    """
    The `Direction` enum represents the ball's direction. Note that the ball
    can't move horizontally.
    """

    UP = auto()
    UP_RIGHT = auto()
    DOWN_RIGHT = auto()
    DOWN = auto()
    DOWN_LEFT = auto()
    UP_LEFT = auto()

    def is_down(self) -> bool:
        """
        This function returns `True` if the direction points down.

        Inputs:

        Returns:
            `True` if `self` points down.
        """
        return (
            self == Direction.DOWN_LEFT
            or self == Direction.DOWN
            or self == Direction.DOWN_RIGHT
        )

    def delta(self) -> tuple[int, int]:
        """
        This functions returns the change in `x` and change in `y` associated
        with `self`'s direction.

        Inputs:

        Returns:
            A tuple containing the change in x and change in y.
        """
        match self:
            case Direction.UP:
                return 0, -1
            case Direction.UP_RIGHT:
                return 1, -1
            case Direction.DOWN_RIGHT:
                return 1, 1
            case Direction.DOWN:
                return 0, 1
            case Direction.DOWN_LEFT:
                return -1, 1
            case Direction.UP_LEFT:
                return -1, -1

    # This function gives us the coordinates that we have to check when we do a
    # collision test (based on the ball's direction). The coordinates are
    # returned in clockwise order. Also notice that `Direction.UP` and
    # `Direction.DOWN` only really need to check a single coordinate, but we have
    # to return three. The code that calls this function ignores two of those
    # values.
    #
    # For example, if direction is UP_RIGHT, we have
    #
    #
    #        ################ ################
    #        #              # #              #
    #        #              # #              #
    #        #   x, y - 1   # # x + 1, y - 1 #
    #        #              # #              #
    #        #              # #              #
    #        ################ ################
    #
    #                         ################
    #                         #              #
    #                         #              #
    #              x, y       #   x + 1, y   #
    #             (ball)      #              #
    #                         #              #
    #                         ################
    def get_adjacent_coords(self, x: int, y: int) -> tuple[Coord, Coord, Coord]:
        if self == Direction.UP:
            return ((x - 1, y - 1), (x, y - 1), (x + 1, y - 1))
        elif self == Direction.UP_RIGHT:
            return ((x, y - 1), (x + 1, y - 1), (x + 1, y))
        elif self == Direction.DOWN_RIGHT:
            return ((x + 1, y), (x + 1, y + 1), (x, y + 1))
        elif self == Direction.DOWN:
            return ((x - 1, y + 1), (x, y + 1), (x + 1, y + 1))
        elif self == Direction.DOWN_LEFT:
            return ((x, y + 1), (x - 1, y + 1), (x - 1, y))
        else:  # self == Direction.UP_LEFT
            return ((x - 1, y), (x - 1, y - 1), (x, y - 1))

    # This gives us a new direction based on the current direction and whether or
    # not there are blocks in the three coordinates in front of us.
    #
    # For example, consider the case that I've annoted with the *HERE*. Starting
    # with Direction.UP_RIGHT, we have
    #
    #        + - - - - - - -+ ################
    #                         #              #
    #        | nothing here | #  block here  #
    #          (so on_left    # (so in_front #
    #        |   is False)  | #    is True)  #
    #                         #              #
    #        +- - - - - - - + ################
    #
    #                         ################
    #                         #              #
    #              ball       #  block here  #
    #           (moving up    # (so on_right #
    #            and right)   #    is True)  #
    #                         #              #
    #                         ################
    #
    # This results in a new direction of Direction.UP_LEFT.
    def new_direction(
        self, on_left: bool, in_front: bool, on_right: bool
    ) -> "Direction":
        if self == Direction.UP:
            if in_front:
                return Direction.DOWN
            else:
                return Direction.UP
        elif self == Direction.UP_RIGHT:
            if on_left and in_front and on_right:
                return Direction.DOWN_LEFT
            elif on_left and in_front and not on_right:
                return Direction.DOWN_RIGHT
            elif on_left and not in_front and on_right:
                return Direction.DOWN_LEFT
            elif on_left and not in_front and not on_right:
                return Direction.DOWN_RIGHT
            elif not on_left and in_front and on_right:  # *HERE*
                return Direction.UP_LEFT
            elif not on_left and in_front and not on_right:
                return Direction.DOWN_LEFT
            elif not on_left and not in_front and on_right:
                return Direction.UP_LEFT
            else:  # all False
                return Direction.UP_RIGHT
        elif self == Direction.DOWN_RIGHT:
            if on_left and in_front and on_right:
                return Direction.UP_LEFT
            elif on_left and in_front and not on_right:
                return Direction.DOWN_LEFT
            elif on_left and not in_front and on_right:
                return Direction.UP_LEFT
            elif on_left and not in_front and not on_right:
                return Direction.DOWN_LEFT
            elif not on_left and in_front and on_right:
                return Direction.UP_RIGHT
            elif not on_left and in_front and not on_right:
                return Direction.UP_LEFT
            elif not on_left and not in_front and on_right:
                return Direction.UP_RIGHT
            else:  # all False
                return Direction.DOWN_RIGHT
        elif self == Direction.DOWN:
            if in_front:
                return Direction.UP
            else:
                return Direction.DOWN
        elif self == Direction.DOWN_LEFT:
            if on_left and in_front and on_right:
                return Direction.UP_RIGHT
            elif on_left and in_front and not on_right:
                return Direction.UP_LEFT
            elif on_left and not in_front and on_right:
                return Direction.UP_RIGHT
            elif on_left and not in_front and not on_right:
                return Direction.UP_LEFT
            elif not on_left and in_front and on_right:
                return Direction.DOWN_RIGHT
            elif not on_left and in_front and not on_right:
                return Direction.UP_RIGHT
            elif not on_left and not in_front and on_right:
                return Direction.DOWN_RIGHT
            else:  # all False
                return Direction.DOWN_LEFT
        else:  # self == Direction.UP_LEFT
            if on_left and in_front and on_right:
                return Direction.DOWN_RIGHT
            elif on_left and in_front and not on_right:
                return Direction.UP_RIGHT
            elif on_left and not in_front and on_right:
                return Direction.DOWN_RIGHT
            elif on_left and not in_front and not on_right:
                return Direction.UP_RIGHT
            elif not on_left and in_front and on_right:
                return Direction.DOWN_LEFT
            elif not on_left and in_front and not on_right:
                return Direction.DOWN_RIGHT
            elif not on_left and not in_front and on_right:
                return Direction.DOWN_LEFT
            else:  # all False
                return Direction.UP_LEFT


@dataclass
class Block:
    """
    This class represents a block in a `Matrix`. Each `Block` has a color and a
    list of coordinates that it occupies.
    """

    color: tuple[int, int, int]
    coords: list[Coord]


Matrix = dict[tuple[int, int], Block | None]


def make_matrix() -> Matrix:
    """
    This function creates a `Matrix` populated with `Block`s. The top 1/3 of the
    `Matrix` is filled with `Block`s, the 1/3 of the way down to 1/4 of the way
    down has a gradient of probabilities so that fewer blocks appear near the
    bottom. This function also adds the `None` borderes around the `Matrix`.

    Inputs:

    Returns:
        The generated `Matrix`.
    """
    raise NotImplementedError

@dataclass
class GameState:
    matrix: Matrix
    frame_count: int = 0
    paddle_pos: int = (columns - paddle_width) // 2
    ball_x: int = columns // 2
    ball_y: int = rows - 2
    ball_direction: Direction = Direction.UP_RIGHT

    def update(self) -> bool:
        """
        This functions handles key presses, updates the ball direction and
        position and deletes any `Block`s that get destroyed.

        Inputs:

        Returns:
            `True` if the program should exit and `False` if it should continue.
        """
        raise NotImplementedError

    def move_ball(self) -> None:
        """
        This function updates the ball's position and direction

        Inputs:

        Returns:
            None
        """
        """
        This function removes the block at the given coordinates. If no
        `Block` exists at this position, then nothing happens.

        Inputs:
            coords: The coordinates to check.

        Returns:
            None
        """
        raise NotImplementedError
        `
    def handle_events(self) -> bool:
        """
        This function handles paddle movement and check if the player pressed
        the button to close the game.

        Inputs:

        Returns:
            `True` if we should exit.
        """
        raise NotImplementedError

    def draw_to(self, screen: pygame.Surface) -> None:
        """
        This function draws the game to the surface.

        Inputs:
            screen: the screen that we should draw to.

        Returns:
            None
        """

        # First, create the border and game area.
        screen.fill(border_color)
        pygame.draw.rect(
            screen,
            background_color,
            pygame.Rect(padding, padding, columns * cell_size, rows * cell_size),
        )

        # Next, iterate over the matrix and draw squares wherever there are `Block`s.
        for (x, y), block in self.matrix.items():
            # We have to check for `None` because the borders are `None` (not
            # `Block`s)
            if block is not None:
                pygame.draw.rect(
                    screen,
                    block.color,
                    pygame.Rect(
                        padding + x * cell_size,
                        padding + y * cell_size,
                        cell_size,
                        cell_size,
                    ),
                )

        # Next, we draw the paddle.
        pygame.draw.rect(
            screen,
            paddle_color,
            pygame.Rect(
                padding + self.paddle_pos * cell_size,
                padding + (rows - paddle_height) * cell_size,
                paddle_width * cell_size,
                paddle_height * cell_size,
            ),
        )

        # Finally, we draw the ball. The `t` variable is how we smooth out the
        # ball's movement. The ball only ever exists at integer coordinates, but
        # we draw it a little bit "behind" where it actually is. `t` is 0 when
        # `frame_count` is a multiple of `ball_slowness` and closest to 1.0 on
        # the frame just after.
        t = (ball_slowness - self.frame_count % ball_slowness - 1) / ball_slowness
        dx, dy = self.ball_direction.delta()
        pygame.draw.rect(
            screen,
            ball_color,
            pygame.Rect(
                padding + (self.ball_x - dx * t) * cell_size,
                padding + (self.ball_y - dy * t) * cell_size,
                cell_size,
                cell_size,
            ),
        )

        pygame.display.flip()

    def reset(self) -> None:
        """
        This function resets the state of the game to it's default values.

        Inputs:

        Returns:
            None
        """
        raise NotImplementedError
