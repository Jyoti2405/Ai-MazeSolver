import pygame
import random
from collections import deque
import heapq
import traceback


WINDOW_SIZE = 600
BUTTON_HEIGHT = 40
GRID_SIZE = 31
CELL_SIZE = WINDOW_SIZE // GRID_SIZE


WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 200, 0)
RED = (200, 0, 0)
BLUE = (0, 120, 255)
YELLOW = (255, 215, 0)
AGENT_COLOR = (255, 140, 0)  # Bright orange for agent


FONT_SIZE = 20
STEP_DELAY = 10


pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE + BUTTON_HEIGHT))
pygame.display.set_caption("Maze Solver with Animated Agent and Colored Buttons")
font = pygame.font.SysFont(None, FONT_SIZE)
clock = pygame.time.Clock()

path_found_sound = pygame.mixer.Sound("path_found.wav")


button_labels = ['Start', 'Pause', 'Randomize', 'Undo', 'Redo', 'Quit', 'BFS', 'DFS', 'A*']
button_colors = [
    (34, 177, 76),      # Start green
    (255, 165, 0),      # Pause orange
    (70, 130, 180),     # Randomize steel blue
    (135, 206, 235),    # Undo sky blue
    (255, 20, 147),     # Redo pink
    (255, 41, 41),      # Quit red
    (30, 144, 255),     # BFS blue
    (0, 200, 0),        # DFS green
    (255, 105, 180)     # A* pink
]


undo_stack = []
redo_stack = []


def save_state(maze, start_point, end_point, current_algo):
    undo_stack.append(([row[:] for row in maze], start_point, end_point, current_algo))
    if len(undo_stack) > 50:
        undo_stack.pop(0)
    redo_stack.clear()


def undo(maze, start_point, end_point, current_algo):
    if undo_stack:
        item = undo_stack.pop()
        redo_stack.append(([row[:] for row in maze], start_point, end_point, current_algo))
        if len(item) == 4:
            return item
        elif len(item) == 3:
            return item[0], item[1], item[2], current_algo
    return maze, start_point, end_point, current_algo


def redo(maze, start_point, end_point, current_algo):
    if redo_stack:
        item = redo_stack.pop()
        undo_stack.append(([row[:] for row in maze], start_point, end_point, current_algo))
        if len(item) == 4:
            return item
        elif len(item) == 3:
            return item[0], item[1], item[2], current_algo
    return maze, start_point, end_point, current_algo


def random_border_point(exclude=None, min_distance=3):
    while True:
        borders = (
            [(x, 0) for x in range(GRID_SIZE)] +
            [(x, GRID_SIZE-1) for x in range(GRID_SIZE)] +
            [(0, y) for y in range(GRID_SIZE)] +
            [(GRID_SIZE-1, y) for y in range(GRID_SIZE)]
        )
        point = random.choice(borders)
        if not exclude or abs(point[0]-exclude[0]) + abs(point[1]-exclude[1]) >= min_distance:
            return point


def is_solvable(maze, start, end):
    q = deque([start])
    seen = {start}
    while q:
        x, y = q.popleft()
        if (x,y) == end:
            return True
        for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
            nx, ny = x+dx, y+dy
            if 0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE and maze[ny][nx] == 0 and (nx, ny) not in seen:
                seen.add((nx, ny))
                q.append((nx, ny))
    return False


def generate_maze():
    maze = [[1]*GRID_SIZE for _ in range(GRID_SIZE)]
    start_point = random_border_point()
    end_point = random_border_point(exclude=start_point)
    maze[start_point[1]][start_point[0]] = 0
    maze[end_point[1]][end_point[0]] = 0
    walls = []
    def add_walls(cx, cy):
        for dx, dy in [(2,0),(-2,0),(0,2),(0,-2)]:
            nx, ny = cx+dx, cy+dy
            if 1 <= nx < GRID_SIZE-1 and 1 <= ny < GRID_SIZE-1:
                if maze[ny][nx] == 1:
                    walls.append((nx, ny, cx, cy))
    sx, sy = (random.randrange(1, GRID_SIZE-1, 2), random.randrange(1, GRID_SIZE-1, 2))
    maze[sy][sx] = 0
    add_walls(sx, sy)
    while walls:
        wx, wy, px, py = walls.pop(random.randint(0,len(walls)-1))
        if maze[wy][wx] == 1:
            maze[wy][wx] = 0
            maze[(wy+py)//2][(wx+px)//2] = 0
            add_walls(wx, wy)
    maze[start_point[1]][start_point[0]] = 0
    maze[end_point[1]][end_point[0]] = 0
    if is_solvable(maze, start_point, end_point):
        return maze, start_point, end_point
    else:
        return generate_maze()


def draw_maze(maze, start, end, explored=None, hover=None, agent_pos=None):
    for y in range(GRID_SIZE):
        for x in range(GRID_SIZE):
            color = BLACK if maze[y][x] == 1 else WHITE
            pygame.draw.rect(screen, color, (x*CELL_SIZE, y*CELL_SIZE, CELL_SIZE, CELL_SIZE))
    if explored:
        for ex, ey in explored:
            pygame.draw.rect(screen, (140,255,140), (ex*CELL_SIZE, ey*CELL_SIZE, CELL_SIZE, CELL_SIZE))
    if hover:
        x, y = hover
        pygame.draw.rect(screen, (200,200,255), (x*CELL_SIZE, y*CELL_SIZE, CELL_SIZE, CELL_SIZE))
        for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
            nx, ny = x+dx, y+dy
            if 0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE and maze[ny][nx] == 0:
                pygame.draw.rect(screen, (150,150,255), (nx*CELL_SIZE, ny*CELL_SIZE, CELL_SIZE, CELL_SIZE))
    pygame.draw.rect(screen, GREEN, (start[0]*CELL_SIZE, start[1]*CELL_SIZE, CELL_SIZE, CELL_SIZE))
    pygame.draw.rect(screen, RED, (end[0]*CELL_SIZE, end[1]*CELL_SIZE, CELL_SIZE, CELL_SIZE))
    if agent_pos:
        pygame.draw.rect(screen, AGENT_COLOR, (agent_pos[0]*CELL_SIZE, agent_pos[1]*CELL_SIZE, CELL_SIZE, CELL_SIZE))


def draw_buttons(current_algo, paused, hovered_btn):
    bw = WINDOW_SIZE // len(button_labels)
    for i, label in enumerate(button_labels):
        base = button_colors[i]
        color = base
        label_to_show = 'Resume' if label == 'Pause' and paused else label
        if hovered_btn == i:
            color = tuple(min(255, c + 40) for c in base)
        if label in ['BFS','DFS','A*'] and label == current_algo:
            color = tuple(min(255, c + 60) for c in base)
        pygame.draw.rect(screen, color, (i*bw, WINDOW_SIZE, bw, BUTTON_HEIGHT))
        text = font.render(label_to_show, True, (255,255,255))
        tx = i*bw + (bw - text.get_width())//2
        ty = WINDOW_SIZE + (BUTTON_HEIGHT - text.get_height())//2
        screen.blit(text, (tx, ty))


def reconstruct_path(parent, start, end):
    path = []
    node = end
    while node != start:
        path.append(node)
        node = parent[node]
    path.reverse()
    return path


def bfs_solver_gen(maze, start, end):
    queue = deque([start])
    visited = {start}
    parent = {}
    while queue:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
        x, y = queue.popleft()
        yield ('explore', (x, y), visited)
        if (x, y) == end:
            path = reconstruct_path(parent, start, end)
            yield ('done', path, None)
            return
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE and maze[ny][nx] == 0 and (nx, ny) not in visited:
                visited.add((nx, ny))
                parent[(nx, ny)] = (x, y)
                queue.append((nx, ny))


def dfs_solver_gen(maze, start, end):
    stack = [start]
    visited = {start}
    parent = {}
    while stack:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
        x, y = stack.pop()
        yield ('explore', (x, y), visited)
        if (x, y) == end:
            path = reconstruct_path(parent, start, end)
            yield ('done', path, None)
            return
        neighbors = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        random.shuffle(neighbors)
        for dx, dy in neighbors:
            nx, ny = x + dx, y + dy
            if 0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE and maze[ny][nx] == 0 and (nx, ny) not in visited:
                visited.add((nx, ny))
                parent[(nx, ny)] = (x, y)
                stack.append((nx, ny))


def a_star_solver_gen(maze, start, end):
    def heuristic(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])
    open_set = []
    heapq.heappush(open_set, (heuristic(start, end), 0, start))
    came_from = {}
    g_score = {start: 0}
    visited = set()
    while open_set:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
        _, cost, current = heapq.heappop(open_set)
        visited.add(current)
        yield ('explore', current, visited)
        if current == end:
            path = reconstruct_path(came_from, start, end)
            yield ('done', path, None)
            return
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            neighbor = (current[0] + dx, current[1] + dy)
            if 0 <= neighbor[0] < GRID_SIZE and 0 <= neighbor[1] < GRID_SIZE:
                if maze[neighbor[1]][neighbor[0]] == 0:
                    tentative_g_score = g_score[current] + 1
                    if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                        g_score[neighbor] = tentative_g_score
                        priority = tentative_g_score + heuristic(neighbor, end)
                        heapq.heappush(open_set, (priority, tentative_g_score, neighbor))
                        came_from[neighbor] = current


def main():
    maze, start_point, end_point = generate_maze()
    current_algo = 'BFS'
    save_state(maze, start_point, end_point, current_algo)
    running = True
    solving = False
    paused = False
    explored_set = set()
    path_cells = []
    hover_cell = None
    hovered_btn = None
    agent_pos = None
    solver_gen = None

    while running:
        try:
            screen.fill(WHITE)
            draw_maze(maze, start_point, end_point, explored_set, hover_cell, agent_pos)
            if path_cells:
                color_map = {'BFS': BLUE, 'DFS': GREEN, 'A*': YELLOW}
                for node in path_cells:
                    pygame.draw.rect(screen, color_map.get(current_algo, BLUE),
                                    (node[0]*CELL_SIZE, node[1]*CELL_SIZE, CELL_SIZE, CELL_SIZE))
            draw_buttons(current_algo, paused, hovered_btn)
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEMOTION:
                    mx, my = event.pos
                    if my < WINDOW_SIZE:
                        hover_cell = (mx//CELL_SIZE, my//CELL_SIZE)
                        hovered_btn = None
                    else:
                        bw = WINDOW_SIZE//len(button_labels)
                        hovered_btn = mx//bw
                        hover_cell = None
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mx, my = event.pos
                    bw = WINDOW_SIZE//len(button_labels)
                    if my > WINDOW_SIZE:
                        i = mx//bw
                        if i < len(button_labels):
                            label = button_labels[i]
                            if label == 'Start':
                                if not solving:
                                    solving = True
                                    paused = False
                                    agent_pos = None
                                    if current_algo == 'BFS':
                                        solver_gen = bfs_solver_gen(maze, start_point, end_point)
                                    elif current_algo == 'DFS':
                                        solver_gen = dfs_solver_gen(maze, start_point, end_point)
                                    else:
                                        solver_gen = a_star_solver_gen(maze, start_point, end_point)
                                    explored_set.clear()
                                    path_cells.clear()
                            elif label == 'Pause' or label == 'Resume':
                                paused = not paused
                            elif label == 'Randomize':
                                maze, start_point, end_point = generate_maze()
                                save_state(maze, start_point, end_point, current_algo)
                                solving = False
                                paused = False
                                explored_set.clear()
                                path_cells.clear()
                                solver_gen = None
                                undo_stack.clear()
                                redo_stack.clear()
                                save_state(maze, start_point, end_point, current_algo)
                            elif label == 'Undo':
                                maze, start_point, end_point, current_algo = undo(maze, start_point, end_point, current_algo)
                                solving = False
                                paused = False
                                explored_set.clear()
                                path_cells.clear()
                                agent_pos = None
                            elif label == 'Redo':
                                maze, start_point, end_point, current_algo = redo(maze, start_point, end_point, current_algo)
                                solving = False
                                paused = False
                                explored_set.clear()
                                path_cells.clear()
                                agent_pos = None
                            elif label == 'Quit':
                                print("Quit button clicked. Press Enter to close.")
                                input()
                                running = False
                            elif label in ['BFS','DFS','A*']:
                                if current_algo != label:
                                    current_algo = label
                                    solving = False
                                    paused = False
                                    solver_gen = None
                                    explored_set.clear()
                                    path_cells.clear()
                                    agent_pos = None
                    elif my < WINDOW_SIZE and not solving:
                        cx = mx//CELL_SIZE
                        cy = my//CELL_SIZE
                        if (cx, cy) != start_point and (cx, cy) != end_point:
                            save_state(maze, start_point, end_point, current_algo)
                            maze[cy][cx] = 1 - maze[cy][cx]

            if solving and not paused and solver_gen:
                try:
                    action, data, visited_or_none = next(solver_gen)
                    if action == 'explore':
                        explored_set = visited_or_none
                        agent_pos = data
                    elif action == 'done':
                        path_cells = list(data)
                        agent_pos = None
                        solving = False
                        solver_gen = None
                        path_found_sound.play()
                    pygame.time.delay(STEP_DELAY)
                except StopIteration:
                    solving = False
                    solver_gen = None

            clock.tick(60)
        except Exception as e:
            print("Exception occurred:", e)
            traceback.print_exc()
            input("Press Enter to exit...")

    pygame.quit()


if __name__ == "__main__":
    main()
