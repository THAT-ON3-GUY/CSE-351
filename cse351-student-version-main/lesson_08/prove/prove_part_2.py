"""
Course: CSE 351 
Assignment: 08 Prove Part 2
File:   prove_part_2.py
Author: Jayden Pope

Purpose: Part 2 of assignment 8, finding the path to the end of a maze using recursion.

Instructions:
- Do not create classes for this assignment, just functions.
- Do not use any other Python modules other than the ones included.
- You MUST use recursive threading to find the end of the maze.
- Each thread MUST have a different color than the previous thread:
    - Use get_color() to get the color for each thread; you will eventually have duplicated colors.
    - Keep using the same color for each branch that a thread is exploring.
    - When you hit an intersection spin off new threads for each option and give them their own colors.

This code is not interested in tracking the path to the end position. Once you have completed this
program however, describe how you could alter the program to display the found path to the exit
position:

What would be your strategy?

I would give each thread an id using a variable in solve_find_end. The variable would
start at 0 and be passed with the first call of search. From their each time a new thread is
created I'd increment the variable by 1 and pass it to that thread. This would give each thread
a unique ID I could identify them by. Then I'd modify the program so the end stage returns true 
like my solution from part 1 but instead of just returning True. I'd have an instance variable
for each thread that add's every move it makes to a list. When the end is found I'd remove from
the end of that list until it was empty adding each removal to a stack in solve_find_end.

Why would it work?

I think this would work because by adding the path taken by a thread into a stack starting
from the end, and by following the threads back to the start using the parent ID bassed to
every child thread, you could successfully reconstruct the path to the end in reverse order in
the stack, and if you just want it in a list for example, you'd pop the stack into a list,
giving you the path from start to finish.

"""

import math
import threading 
from screen import Screen
from maze import Maze
import sys
import cv2

# Include cse 351 files
from cse351 import *

SCREEN_SIZE = 700
COLOR = (0, 0, 255)
COLORS = (
    (0,0,255),
    (0,255,0),
    (255,0,0),
    (255,255,0),
    (0,255,255),
    (255,0,255),
    (128,0,0),
    (128,128,0),
    (0,128,0),
    (128,0,128),
    (0,128,128),
    (0,0,128),
    (72,61,139),
    (143,143,188),
    (226,138,43),
    (128,114,250)
)
SLOW_SPEED = 100
FAST_SPEED = 0

# Globals
current_color_index = 0
thread_count = 0
stop = False
speed = SLOW_SPEED

def get_color():
    """ Returns a different color when called """
    global current_color_index
    if current_color_index >= len(COLORS):
        current_color_index = 0
    color = COLORS[current_color_index]
    current_color_index += 1
    return color


# TODO: Add any function(s) you need, if any, here.
def try_move(maze, row, col, color, lock):
    with lock:
        if maze.can_move_here(row, col):
            maze.move(row, col, color)
            return True
        return False


def solve_find_end(maze):
    """ Finds the end position using threads. Nothing is returned. """
    # When one of the threads finds the end position, stop all of them.
    global stop
    stop = False

    move_lock = threading.Lock()
    end = None

    def search(row, col, color):
        global stop 

        if stop:
            return
        if maze.at_end(row, col):
            stop = True

            nonlocal end 
            end = (row, col)
            return

        moves = maze.get_possible_moves(row, col)

        if not moves:
            return

        origin, *clones = moves

        clone_list = []
        for r, c in clones:
            new_color = get_color()
            if try_move(maze, r, c, new_color, move_lock):
                t = threading.Thread(target=search, args=(r, c, new_color))
                clone_list.append(t)
                t.start()

        if try_move(maze, origin[0], origin[1], color, move_lock):
            search(origin[0], origin[1], color)

        for t in clone_list:
            t.join()

    row, col = maze.get_start_pos()
    color = get_color()
    try_move(maze, row, col, color, move_lock)
    search(row, col, color)

    return end







def find_end(log, filename, delay):
    """ Do not change this function """

    global thread_count
    global speed

    # create a Screen Object that will contain all of the drawing commands
    screen = Screen(SCREEN_SIZE, SCREEN_SIZE)
    screen.background((255, 255, 0))

    maze = Maze(screen, SCREEN_SIZE, SCREEN_SIZE, filename, delay=delay)

    solve_find_end(maze)

    log.write(f'Number of drawing commands = {screen.get_command_count()}')
    log.write(f'Number of threads created  = {thread_count}')

    done = False
    while not done:
        if screen.play_commands(speed): 
            key = cv2.waitKey(0)
            if key == ord('1'):
                speed = SLOW_SPEED
            elif key == ord('2'):
                speed = FAST_SPEED
            elif key == ord('q'):
                exit()
            elif key != ord('p'):
                done = True
        else:
            done = True


def find_ends(log):
    """ Do not change this function """

    files = (
        ('very-small.bmp', True),
        ('very-small-loops.bmp', True),
        ('small.bmp', True),
        ('small-loops.bmp', True),
        ('small-odd.bmp', True),
        ('small-open.bmp', False),
        ('large.bmp', False),
        ('large-loops.bmp', False),
        ('large-squares.bmp', False),
        ('large-open.bmp', False)
    )

    log.write('*' * 40)
    log.write('Part 2')
    for filename, delay in files:
        filename = f'./mazes/{filename}'
        log.write()
        log.write(f'File: {filename}')
        find_end(log, filename, delay)
    log.write('*' * 40)


def main():
    """ Do not change this function """
    sys.setrecursionlimit(5000)
    log = Log(show_terminal=True)
    find_ends(log)


if __name__ == "__main__":
    main()