# Python_Programming_MOOC_2026_Final_Project
Final Project for the "Advanced Python Programming 2026" course from University of Helsinki, Finland. It consists of a game created with python + pygame.

---

## ROBOT IN A MAZE

---

### About the game

This game consists of a random maze generator, based on **Binary trees** (only one way from starting point to the exit point) and **Graphs** (more than one possible way to get to the exit).

In order to win and go to the next level, you have to take the Robot to the exit point while avoiding getting caught by the Monster. There are infinite levels, but the difficulty increases considerably for this demo version from level 3 onwards (actually, I haven't been able to go further than level 9).

---

### About the maze

The maze is generated with a recursive function, given a grid and a `Cell` object with its corresponding "wall" attributes. It determines if each cell should be a "neighbour" (there is no wall) or not (the wall stays in place) to the next cell.

This grid of `Cell` objects is then represented as an actual maze by drawing lines whenever there should be a wall. Both the Robot (player) and the Monster (enemy) can move through this maze as long as there is not a wall in the desired direction.

---

### About the enemy

The Monster uses another recursive function to determine the best path to get to the Robot's position, so that it follows the player through the maze. Depending on the level, the Monster will appear sooner and move faster towards the Robot. If it catches the Robot, the game is lost and we go back to level 1.
