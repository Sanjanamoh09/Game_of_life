# life.py

import pygame
import argparse
import random
import sys
import os

# --- Constants ---
CELL_SIZE = 15  # Pixel size of each cell
GRID_COLOR = (50, 50, 50)
DEAD_COLOR = (0, 0, 0)
ALIVE_COLOR = (255, 255, 255)
TEXT_COLOR = (200, 200, 200)
HUD_BG_COLOR = (30, 30, 30)
HUD_HEIGHT = 60  # Height for the HUD area

# --- Helper Functions ---

def create_board(width, height):
    """Creates an empty game board (all cells dead)."""
    return [[0 for _ in range(width)] for _ in range(height)]

def count_live_neighbors(board, r, c):
    """Counts live neighbors for a cell at (r, c)."""
    live_neighbors = 0
    rows, cols = len(board), len(board[0])
    for i in range(-1, 2):
        for j in range(-1, 2):
            if i == 0 and j == 0:
                continue  # Skip the cell itself
            nr, nc = r + i, c + j
            if 0 <= nr < rows and 0 <= nc < cols and board[nr][nc] == 1:
                live_neighbors += 1
    return live_neighbors

def next_board_state(board):
    """
    Calculates the next state of the board based on Conway's rules.
    Returns a NEW board, does not mutate the original.
    """
    rows, cols = len(board), len(board[0])
    new_board = create_board(cols, rows) # Note: width=cols, height=rows

    for r in range(rows):
        for c in range(cols):
            live_neighbors = count_live_neighbors(board, r, c)
            cell_state = board[r][c]

            if cell_state == 1:  # If cell is alive
                if live_neighbors < 2 or live_neighbors > 3:
                    new_board[r][c] = 0  # Dies
                else:
                    new_board[r][c] = 1  # Lives on
            else:  # If cell is dead
                if live_neighbors == 3:
                    new_board[r][c] = 1  # Becomes alive
    return new_board

def random_fill_board(board, density=0.2):
    """Fills the board randomly with a given density of live cells."""
    rows, cols = len(board), len(board[0])
    for r in range(rows):
        for c in range(cols):
            if random.random() < density:
                board[r][c] = 1
            else:
                board[r][c] = 0

def save_pattern(board, filename="patterns/custom_pattern.txt"):
    """Saves the current live cells to a file."""
    os.makedirs(os.path.dirname(filename), exist_ok=True) # Ensure 'patterns' directory exists
    with open(filename, "w") as f:
        f.write(f"# Pattern: Custom saved pattern\n")
        rows, cols = len(board), len(board[0])
        for r in range(rows):
            for c in range(cols):
                if board[r][c] == 1:
                    f.write(f"{c},{r}\n") # Save as x,y (col,row)
    print(f"Pattern saved to {filename}")

def load_pattern(filename, board_width, board_height):
    """Loads a pattern from a file into a new board."""
    new_board = create_board(board_width, board_height)
    try:
        with open(filename, "r") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                try:
                    x, y = map(int, line.split(','))
                    if 0 <= y < board_height and 0 <= x < board_width:
                        new_board[y][x] = 1 # Load from x,y (col,row) to board[row][col]
                except ValueError:
                    print(f"Warning: Could not parse line in pattern file: {line}")
        print(f"Pattern loaded from {filename}")
        return new_board
    except FileNotFoundError:
        print(f"Error: Pattern file not found: {filename}")
        return create_board(board_width, board_height) # Return empty board on error

def count_total_live_cells(board):
    """Counts the total number of live cells on the board."""
    count = 0
    for row in board:
        for cell in row:
            if cell == 1:
                count += 1
    return count

# --- Pygame Drawing Functions ---

def draw_grid(screen, board, cell_size, board_pixel_width, board_pixel_height):
    """Draws the game grid and cells."""
    screen.fill(DEAD_COLOR, (0, HUD_HEIGHT, board_pixel_width, board_pixel_height)) # Clear board area

    rows, cols = len(board), len(board[0])
    for r in range(rows):
        for c in range(cols):
            if board[r][c] == 1:
                pygame.draw.rect(screen, ALIVE_COLOR,
                                 (c * cell_size, r * cell_size + HUD_HEIGHT, cell_size, cell_size))

    # Draw grid lines (optional, can make it slower for large grids)
    for x in range(0, board_pixel_width + 1, cell_size):
        pygame.draw.line(screen, GRID_COLOR, (x, HUD_HEIGHT), (x, board_pixel_height + HUD_HEIGHT))
    for y in range(HUD_HEIGHT, board_pixel_height + HUD_HEIGHT + 1, cell_size):
        pygame.draw.line(screen, GRID_COLOR, (0, y), (board_pixel_width, y))

def draw_hud(screen, font, generation, live_cells, fps, paused, window_width):
    """Draws the Heads-Up Display (HUD) with game info."""
    screen.fill(HUD_BG_COLOR, (0, 0, window_width, HUD_HEIGHT))

    pause_state_text = "⏸ PAUSED" if paused else "▶ RUNNING"
    text_line1 = f"Space:{pause_state_text}  N:Step  R:Random  S:Save  L:Load  C:Clear  Q:Quit"
    text_line2 = f"Generation: {generation}   Live Cells: {live_cells}   Target FPS: {fps}"

    label1 = font.render(text_line1, True, TEXT_COLOR)
    label2 = font.render(text_line2, True, TEXT_COLOR)

    screen.blit(label1, (10, 10))
    screen.blit(label2, (10, 35))

# --- Main Game Function ---
def main(args):
    """Main game loop and setup."""
    board_width = args.width
    board_height = args.height
    fps = args.fps

    pygame.init()
    pygame.font.init() # Initialize font module

    font_size = 18 # Adjusted for better fit
    try:
        # Attempt to load a more common system font, fallback if not found
        font = pygame.font.SysFont("Consolas", font_size)
        if not font: # Some systems might return None if the font is "missing"
             font = pygame.font.SysFont("monospace", font_size)
    except:
         font = pygame.font.SysFont("monospace", font_size) # Fallback to generic monospace


    board_pixel_width = board_width * CELL_SIZE
    board_pixel_height = board_height * CELL_SIZE
    screen_width = board_pixel_width
    screen_height = board_pixel_height + HUD_HEIGHT

    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Conway's Game of Life")
    clock = pygame.time.Clock()

    board = create_board(board_width, board_height)
    # Example: Load a default pattern at start if you want
    # board = load_pattern("patterns/glider.txt", board_width, board_height)

    running = True
    paused = True # Start paused
    generation = 0

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    paused = not paused
                elif event.key == pygame.K_n: # Next step
                    if paused: # Only allow single step if paused for clarity
                        board = next_board_state(board)
                        generation += 1
                elif event.key == pygame.K_c: # Clear
                    board = create_board(board_width, board_height)
                    generation = 0
                    paused = True
                elif event.key == pygame.K_r: # Random fill
                    random_fill_board(board)
                    generation = 0
                    paused = True # Pause after randomizing to inspect
                elif event.key == pygame.K_s: # Save
                    save_pattern(board, f"patterns/gen_{generation}_cells_{count_total_live_cells(board)}.txt")
                elif event.key == pygame.K_l: # Load
                    # For simplicity, let's load a fixed name or use a dialog (advanced)
                    # You can modify this to ask for a filename in the console
                    loaded_board = load_pattern("patterns/glider.txt", board_width, board_height) # Example path
                    if loaded_board:
                        board = loaded_board
                        generation = 0
                        paused = True
                elif event.key == pygame.K_q: # Quit
                    running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1: # Left mouse button
                    # Check if click is within the board area
                    mouse_x, mouse_y = event.pos
                    if mouse_y > HUD_HEIGHT: # Click is below HUD
                        col = mouse_x // CELL_SIZE
                        row = (mouse_y - HUD_HEIGHT) // CELL_SIZE
                        if 0 <= row < board_height and 0 <= col < board_width:
                            board[row][col] = 1 - board[row][col] # Toggle cell state
                            paused = True # Pause to allow drawing


        if not paused:
            board = next_board_state(board)
            generation += 1

        # Drawing
        live_cells_count = count_total_live_cells(board)
        draw_hud(screen, font, generation, live_cells_count, fps, paused, screen_width)
        draw_grid(screen, board, CELL_SIZE, board_pixel_width, board_pixel_height)

        pygame.display.flip()
        clock.tick(fps)

    pygame.quit()
    sys.exit()


# --- Script Entry Point ---
if __name__ == "__main__":
    # 3.1 Bootstrap: Parse CLI args
    parser = argparse.ArgumentParser(description="Conway's Game of Life Interactive Visualiser")
    parser.add_argument("--width", type=int, default=60, help="Width of the game board in cells.")
    parser.add_argument("--height", type=int, default=40, help="Height of the game board in cells.")
    parser.add_argument("--fps", type=int, default=10, help="Frames per second for the simulation.")
    # Add --file argument later if needed for loading pattern at startup

    args = parser.parse_args()

    # Create patterns directory if it doesn't exist
    os.makedirs("patterns", exist_ok=True)

    main(args)