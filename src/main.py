

################## ROBOT IN A MAZE ##################
########### by Aldo Egea Lopez (aldoegea) ###########

# About the game
# This game consists of a random maze generator, based on binary tres (only one way from starting point to the exit point)
# and graphs (more than one posible way to get to the exit). In order to win and go to the next level, you have to take the
# Robot to the exit point while avoiding getting caught by the Monster. There are infinite levels but the difficulty increases
# considerably for this demo versión from level 3 onwards (actually, I haven't been able to go further than level 9).

# About the maze
# The maze is generated with a recursive function, given a grid and a Cell object with its corresponding "wall" attributes.
# It determines if each cell should be a "neighbour" (there is no wall) or not (the wall stays in place) to the next cell.
# This grid of Cells is then represented as an actual maze by drawing lines whenever there should be a wall.
# Both the Robot (player) or the Monster (enemy) can move through this maze as long as there is not a wall in the desired direction.

# About the enemy
# The Monster uses another recursive function to determine the best path to get to the Robot's position,
# so that if follows the player through the maze. If it catches the Robot, the game is lost and we go back to level 1.
# Depending on the level, the Monster will appear sooner and move faster towards the Robot.




import pygame, random


################## Cell grid ##################

#Cell class
class Cell:
    def __init__(self):
        self.visited = False
        self.walls = {
            "top": True,
            "right": True,
            "bottom": True,
            "left": True
        }

#Explore neighbours and randomize list so that we get different maze designs each time
def neighbours(row, col, rows, cols):
    directions = []

    if row > 0:
        directions.append(("top", row - 1, col))

    if row < rows - 1:
        directions.append(("bottom", row + 1, col))

    if col > 0:
        directions.append(("left", row, col - 1))

    if col < cols - 1:
        directions.append(("right", row, col + 1))

    random.shuffle(directions)
    return directions

#Recursive function to determine the directions the maze will take
def generate_maze(grid, row, col, rows, cols):
    #Origin point (marked as visited to avoid infinte loops)
    grid[row][col].visited = True

    #Choose random neighbours and remove wall between them
    for direction, next_row, next_col in neighbours(row, col, rows, cols):
        #Avoid already visited
        if grid[next_row][next_col].visited:
            continue

        #Remove walls between (row,col) and (next_row,next_col)
        #1st: remove the wall from (row,col)
        grid[row][col].walls[direction] = False

        #2nd: remove the corresponding wall (the opposite) from (next_row,next_col)
        opposite = {"top": "bottom", "right": "left", "bottom": "top", "left": "right"}
        grid[next_row][next_col].walls[opposite[direction]] = False

        #Move on to next cell
        generate_maze(grid, next_row, next_col, rows, cols)

#Depth-First Search (DFS) as seen on https://medium.com/omarelgabrys-blog/path-finding-algorithms-f65a8902eb40
#Generate maze creates a perfect A-Z binary tree. With this function we want to open random walls so that the labrynth feels a bit more difficult (not just 1 obvious way to the target anymore)
def open_random_walls(grid, rows, cols, level):
    #Do nothing if level == 1
    if level < 2:
        return

    #Detect all the posibilities
    wall_list = []

    for row in range(rows):
        for col in range(cols):
            # Right wall + neighbour's left wall (except last column)
            if col < cols - 1:
                if grid[row][col].walls["right"]:
                    wall_list.append( (row, col, "right", row, col + 1, "left") )

            # Bottom walls + neighbour's top wall (except last row)
            if row < rows - 1:
                if grid[row][col].walls["bottom"]:
                    wall_list.append( (row, col, "bottom", row + 1, col, "top") )

            #No need to do more walls because doing left and removing right from neighbours would result in the same!

    #Randomize
    random.shuffle(wall_list)

    #Calculate number of openings according to current level (min 5, max 30)
    number_of_openings = min( 5 + (level - 2) * 2, 30 )
    number_of_openings = min( number_of_openings, len(wall_list) )

    #Remove the walls
    for i in range(number_of_openings):
        row1, col1, wall1, row2, col2, wall2 = wall_list[i]

        grid[row1][col1].walls[wall1] = False
        grid[row2][col2].walls[wall2] = False



################## Game ##################

class MazeGame:
    def __init__(self):
        pygame.init()

        #Grid definition
        self.ROWS = 15
        self.COLS = 20
        self.CELL_SIZE = 50
        self.BANNER_HEIGHT = 50

        #Window definition
        self.WIDTH = self.COLS * self.CELL_SIZE
        self.HEIGHT = self.ROWS * self.CELL_SIZE + self.BANNER_HEIGHT
        self.window = pygame.display.set_mode((self.WIDTH, self.HEIGHT))

        #Pygame variables
        pygame.display.set_caption("Robot in a Maze")
        self.font = pygame.font.SysFont("Arial", 24)
        self.clock = pygame.time.Clock()

        #Images
        self.robot_image = self.load_image("robot.png")
        self.monster_image = self.load_image("monster.png")

        #Game variables
        self.level = 1
        self.running = True
        self.game_over = False
        self.new_level()

        #Run game loop
        self.run()


    def load_image(self, filename: str):
        image = pygame.image.load(filename).convert_alpha()

        #Adjust size with padding
        cell_padding = 10
        max_size = self.CELL_SIZE - cell_padding

        original_width, original_height = image.get_width(), image.get_height()

        #The images are not square, so we need to fit their minimum size in our cell
        scale = min(max_size / original_width, max_size / original_height)
        new_size = (int(original_width * scale), int(original_height * scale))

        image = pygame.transform.scale(image, new_size)

        #Color mask for monster
        if not filename.startswith("monster"):
            return image
        else:
            result = image.copy()
            new_color = (220, 30, 30)

            for x in range(result.get_width()):
                for y in range(result.get_height()):
                    red, green, blue, alpha = result.get_at((x, y))

                    # Ignore transparent pixels
                    if alpha == 0:
                        continue

                    # Recolour dark pixels but leave white eyes unchanged
                    if red < 20 and green < 20 and blue < 20:
                        result.set_at(
                            (x, y),
                            (*new_color, alpha)
                        )

            return result
    

    #Generate a new level everytime we call it
    def new_level(self):
        #Generate grid o Cell() objects with a double list comprehension for rows and columns
        self.grid = [[Cell() for i in range(self.COLS)] for i in range(self.ROWS)]

        #Create random maze with this grid and open random walls if necessary
        generate_maze(self.grid, 0, 0, self.ROWS, self.COLS)
        open_random_walls(self.grid, self.ROWS, self.COLS, self.level)

        #Set goal cell
        self.goal_row = self.ROWS - 1
        self.goal_col = self.COLS - 1 

        #Shortest path from start to target and its length
        path = self.find_path( (0, 0), (self.goal_row, self.goal_col) )
        self.path_length = len(path)

        #Robot: initial position and move counter
        self.robot_row = 0
        self.robot_col = 0
        self.robot_moves = 0

        #Monster: initial position (same as robot), active flag, timer and monster spawn/move settings
        self.monster_row = self.robot_row
        self.monster_col = self.robot_col
        self.monster_active = False
        self.monster_move_timer = 0
        spawn_divisor = min( 3 + self.level - 1, 5)
        self.monster_spawn_threshold = max( 3, self.path_length // spawn_divisor ) #The enemy will spawn when the robot has moved along from 1/3 to 1/5 of the path, depending on level. The smaller the spawn_divisor, the sooner the monster appears
        #Monster: faster move interval depending also on current level
        self.monster_move_interval = max(0, 450 - (self.level - 1) * 25)  # 500, 450, 400, 350...

        #Reset gameover
        self.game_over = False

         

    #Check if there are walls in that direction to determine if the player/enemy can move to the next cell
    def can_move(self, row, col, direction):
        return not self.grid[row][col].walls[direction]

    #Get next cell position
    def next_position(self, row, col, direction):
        if direction == "top":
            row -= 1
        elif direction == "right":
            col += 1
        elif direction == "bottom":
            row += 1
        elif direction == "left":
            col -= 1

        return row, col


    #Check if we win the game and, if so, increase level and generate new maze
    def win_game(self):
        if self.robot_row == self.goal_row and self.robot_col == self.goal_col:
            self.level += 1
            self.new_level()

    #Check if we lose the game when the enemy catches us
    def lose_game(self):
        if self.monster_active and self.monster_row == self.robot_row and self.monster_col == self.robot_col:
            #Reset
            # self.level = 1
            # self.new_level()

            #Game over
            self.game_over = True

    #Check if enemy should spawn
    def spawn_monster(self):
        if not self.monster_active and self.robot_moves >= self.monster_spawn_threshold:
            self.monster_active = True


    #Move robot
    def move_robot(self, direction):
        #Check if gameover
        if self.game_over:
            return
        
        #Check if it can move towards that direction
        if not self.can_move( self.robot_row, self.robot_col, direction ):
            return

        #Move robot to next position
        self.robot_row, self.robot_col = self.next_position( self.robot_row, self.robot_col, direction )
        self.robot_moves += 1

        #Check for spawn_monster and win_game
        self.spawn_monster()
        self.win_game()


    #Retrieve valid movements
    def valid_neighbours(self, row, col):
        directions = ["top", "right", "bottom", "left"]
        valid_neighbours_list = []

        for direction in directions:
            if self.can_move(row, col, direction):
                next_row, next_col = self.next_position(row, col, direction)
                valid_neighbours_list.append((next_row, next_col))

        return valid_neighbours_list
    

    #Breadth-First Search (BFS) as seen on https://medium.com/omarelgabrys-blog/path-finding-algorithms-f65a8902eb40
    def find_path(self, start, target):
        # 1. Add origin node to the queue and save previous node (this means it was already visited)
        queue = [start]
        previous = {start: None}

        # 2. Loop on the queue as long as it's not empty.
        while queue:
            # Get and remove the first node of the queue (current node).
            current = queue.pop(0)

            #Check if it's the goal node to stop the search
            if current == target:
                break
            else:
                row, col = current

            #Explore unvisited neighbours
            for neighbour in self.valid_neighbours(row, col):
                if neighbour in previous:
                    continue
                #Mark as visited and add it to the list
                previous[neighbour] = current
                queue.append(neighbour)

        #No available way to the target
        if target not in previous:
            return []

        #Build path from start to target (it has to be reversed because we go from target to its previous node, and so on)
        path = []
        current = target

        while current is not None:
            path.append(current)
            current = previous[current]

        path.reverse()
        return path


    #Move enemy
    def update_monster(self, milliseconds):
        #Check gameover or if it's not active
        if not self.monster_active or self.game_over:
            return

        #Update move timer and check if it should move already -- then reset it to 0
        self.monster_move_timer += milliseconds
        if self.monster_move_timer < self.monster_move_interval:
            return
        self.monster_move_timer = 0

        #Determine monster and robot current position
        monster_position = (self.monster_row, self.monster_col)
        robot_position = (self.robot_row, self.robot_col)

        #Determine path from monster to robot
        path = self.find_path(monster_position, robot_position)

        #Move only if we are not there yet
        if len(path) > 1:
            self.monster_row, self.monster_col = path[1]

        #Check if the enemy caught the robot
        self.lose_game()


    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_q):
                #Quit game
                self.running = False

            elif event.type == pygame.KEYDOWN:
                #Restart game
                if event.key == pygame.K_r:
                    self.level = 1
                    self.new_level()

                #Handle movement (if not gameover)
                elif not self.game_over:
                    if event.key == pygame.K_UP:
                        self.move_robot("top")

                    elif event.key == pygame.K_RIGHT:
                        self.move_robot("right")

                    elif event.key == pygame.K_DOWN:
                        self.move_robot("bottom")

                    elif event.key == pygame.K_LEFT:
                        self.move_robot("left")


    def draw_maze(self):
        wall_color = (255, 255, 255)
        wall_width = 2

        for row in range(self.ROWS):
            for col in range(self.COLS):
                cell = self.grid[row][col]

                x = col * self.CELL_SIZE
                y = row * self.CELL_SIZE

                if cell.walls["top"]:
                    pygame.draw.line( self.window, wall_color, (x, y), (x + self.CELL_SIZE, y), wall_width )

                if cell.walls["right"]:
                    pygame.draw.line( self.window, wall_color, (x + self.CELL_SIZE, y), (x + self.CELL_SIZE, y + self.CELL_SIZE), wall_width )

                if cell.walls["bottom"]:
                    pygame.draw.line( self.window, wall_color, (x, y + self.CELL_SIZE), (x + self.CELL_SIZE, y + self.CELL_SIZE), wall_width )

                if cell.walls["left"]:
                    pygame.draw.line( self.window, wall_color, (x, y), (x, y + self.CELL_SIZE), wall_width )


    def draw_goal(self):
        padding = 10

        goal_rect = pygame.Rect(
            self.goal_col * self.CELL_SIZE + padding,
            self.goal_row * self.CELL_SIZE + padding,
            self.CELL_SIZE - 2 * padding,
            self.CELL_SIZE - 2 * padding
        )

        pygame.draw.rect( self.window, (40, 220, 100), goal_rect )


    def draw_start(self):
        padding = 10
    
        start_rect = pygame.Rect(
            0 * self.CELL_SIZE + padding,
            0 * self.CELL_SIZE + padding,
            self.CELL_SIZE - 2 * padding,
            self.CELL_SIZE - 2 * padding
        )
    
        pygame.draw.rect( self.window, (255, 0, 0), start_rect )


    def draw_image(self, image, row, col):
        cell_rect = pygame.Rect(
            col * self.CELL_SIZE,
            row * self.CELL_SIZE,
            self.CELL_SIZE,
            self.CELL_SIZE
        )

        image_rect = image.get_rect(center=cell_rect.center)
        self.window.blit(image, image_rect)


    def draw_banner(self):
        level_text = self.font.render(
            f"Level: {self.level}",
            True,
            (255, 255, 255)
        )

        self.window.blit(level_text, (10, self.HEIGHT - 40))

        # status = "Monster: waiting"

        # if self.monster_active:
        #     status = "Monster: chasing"

        # status_text = self.font.render(
        #     status,
        #     True,
        #     (255, 100, 100)
        # )

        # self.window.blit(
        #     status_text,
        #     (180, self.HEIGHT - 40)
        # )

        help_text = self.font.render(
            "R: Restart    Q: Quit",
            True,
            (255, 255, 255)
        )

        self.window.blit(
            help_text,
            (self.WIDTH - help_text.get_width() - 10, self.HEIGHT - 40)
        )


    def draw_game_over(self):
        game_text = self.font.render(
            "Oh no, you got caught!",
            True,
            (255, 0, 0)
        )

        text_rect = game_text.get_rect(
            center=(
                self.WIDTH // 2,
                (self.ROWS * self.CELL_SIZE) // 2
            )
        )

        background_rect = text_rect.inflate(30, 20)

        pygame.draw.rect(
            self.window,
            (0, 0, 0),
            background_rect
        )

        self.window.blit(
            game_text,
            text_rect
        )

        restart_text = self.font.render(
            "Press R to restart or Q to quit",
            True,
            # (255, 255, 255)
            (40, 220, 100)
        )

        restart_rect = restart_text.get_rect(
            center=(
                self.WIDTH // 2,
                text_rect.bottom + 35
            )
        )

        self.window.blit(
            restart_text,
            restart_rect
        )


    def draw_all(self):
        self.window.fill((30, 30, 30))

        self.draw_maze()
        # self.draw_start()
        self.draw_goal()
        self.draw_image(self.robot_image, self.robot_row, self.robot_col)
        if self.monster_active:
            self.draw_image(self.monster_image, self.monster_row, self.monster_col)

        
        self.draw_banner()

        if self.game_over:
            self.draw_game_over()

        pygame.display.flip()
        

    #Game loop
    def run(self):
        while self.running:
            milliseconds = self.clock.tick(60)

            self.handle_events()
            self.update_monster(milliseconds)
            self.draw_all()

        pygame.quit()



################## EXECUTION ##################

if __name__ == "__main__":
    game = MazeGame()
