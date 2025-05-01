import sys
import time
import random
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *


WIDTH, HEIGHT = 800, 600
score = 0
game_over = False
paused = False
catcher_x = WIDTH // 2
catcher_width = 80  
diamond_x = random.randint(50, WIDTH-50)
diamond_y = HEIGHT - 50
diamond_speed = 0.5
last_time = time.time()
button_size = 40
pause_time = 0


WHITE = (1.0, 1.0, 1.0)
RED = (1.0, 0.0, 0.0)
TEAL = (0.0, 1.0, 1.0)
AMBER = (1.0, 0.75, 0.0)
diamond_color = (
    random.random() * 0.5 + 0.5,  
    random.random() * 0.5 + 0.5,
    random.random() * 0.5 + 0.5
)
#Midpoint Line Algorithm
def find_zone(x1, y1, x2, y2):
    dx = x2 - x1
    dy = y2 - y1
    if abs(dx) >= abs(dy):
        if dx >= 0 and dy >= 0: return 0
        if dx <= 0 and dy >= 0: return 3
        if dx <= 0 and dy <= 0: return 4
        if dx >= 0 and dy <= 0: return 7
    else:
        if dx >= 0 and dy >= 0: return 1
        if dx <= 0 and dy >= 0: return 2
        if dx <= 0 and dy <= 0: return 5
        if dx >= 0 and dy <= 0: return 6

def convert_to_zone0(x, y, zone):
    if zone == 0: return x, y
    if zone == 1: return y, x
    if zone == 2: return y, -x
    if zone == 3: return -x, y
    if zone == 4: return -x, -y
    if zone == 5: return -y, -x
    if zone == 6: return -y, x
    if zone == 7: return x, -y

def convert_from_zone0(x, y, zone):
    if zone == 0: return x, y
    if zone == 1: return y, x
    if zone == 2: return -y, x
    if zone == 3: return -x, y
    if zone == 4: return -x, -y
    if zone == 5: return -y, -x
    if zone == 6: return y, -x
    if zone == 7: return x, -y

def draw_pixel(x, y):
    glBegin(GL_POINTS)
    glVertex2f(x, y)
    glEnd()

def midpoint_line(x1, y1, x2, y2):
    zone = find_zone(x1, y1, x2, y2)
    x1_conv, y1_conv = convert_to_zone0(x1, y1, zone)
    x2_conv, y2_conv = convert_to_zone0(x2, y2, zone)
    
    dx = x2_conv - x1_conv
    dy = y2_conv - y1_conv
    d = 2 * dy - dx
    incE = 2 * dy
    incNE = 2 * (dy - dx)
    x, y = x1_conv, y1_conv
    
    while x <= x2_conv:
        orig_x, orig_y = convert_from_zone0(x, y, zone)
        draw_pixel(orig_x, orig_y)
        if d > 0:
            d += incNE
            y += 1
        else:
            d += incE
        x += 1

def draw_diamond(x, y, size=20):
    glColor3f(*diamond_color)
    
    midpoint_line(x, y, x + size, y - size*1.5)               #bottom to right
    midpoint_line(x + size, y - size*1.5, x, y - size*3)      #right to top
    midpoint_line(x, y - size*3, x - size, y - size*1.5)      #top to left
    midpoint_line(x - size, y - size*1.5, x, y)             #left to bottom

def draw_catcher(x, width=80):
    if game_over:
        glColor3f(*RED)
    else:
        glColor3f(*WHITE)
    
    y = 20
    midpoint_line(x - width//2, y, x + width//2, y)           #bottom line
    midpoint_line(x - width//2, y, x - width//4, y + 20)       #left line
    midpoint_line(x + width//2, y, x + width//4, y + 20)        #right line
    midpoint_line(x - width//4, y + 20, x + width//4, y + 20)   #    #top line

def draw_button(x, y, shape, color):
    glColor3f(*color)
    size = button_size
    if shape == 'left_arrow':
        midpoint_line(x, y, x, y + size)
        midpoint_line(x, y + size//2, x + size//2, y)
        midpoint_line(x, y + size//2, x + size//2, y + size)
    elif shape == 'play_pause':
        if paused:
            midpoint_line(x, y, x, y + size)
            midpoint_line(x + size//2, y, x + size//2, y + size)
        else:
            midpoint_line(x, y, x, y + size)
            midpoint_line(x, y, x + size, y + size//2)
            midpoint_line(x, y + size, x + size, y + size//2)
    elif shape == 'cross':
        midpoint_line(x, y, x + size, y + size)
        midpoint_line(x + size, y, x, y + size)

def check_collision():
    diamond_box = (diamond_x - 15, diamond_y - 45, 30, 45)  
    catcher_box = (catcher_x - catcher_width//2, 20, catcher_width, 20)
    
    return (diamond_box[0] < catcher_box[0] + catcher_box[2] and
            diamond_box[0] + diamond_box[2] > catcher_box[0] and
            diamond_box[1] < catcher_box[1] + catcher_box[3] and
            diamond_box[1] + diamond_box[3] > catcher_box[1])

def keyboard(key, x, y):
    global catcher_x
    if not game_over and not paused:
        if key == GLUT_KEY_LEFT and catcher_x > catcher_width//2 + 10:
            catcher_x -= 20
        elif key == GLUT_KEY_RIGHT and catcher_x < WIDTH - catcher_width//2 - 10:
            catcher_x += 20
    glutPostRedisplay()

def mouse(button, state, x, y):
    global score, game_over, paused, diamond_speed, diamond_x, diamond_y, last_time, pause_time, diamond_color
    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        y = HEIGHT - y 
        
        if 10 < x < 10 + button_size and HEIGHT - 10 - button_size < y < HEIGHT - 10:
            score = 0
            game_over = False
            paused = False
            diamond_speed = 0.5
            diamond_x = random.randint(50, WIDTH-50)
            diamond_y = HEIGHT - 50
            # Generate new bright color on restart
            diamond_color = (
                random.random() * 0.5 + 0.5,
                random.random() * 0.5 + 0.5,
                random.random() * 0.5 + 0.5
            )
            print("Starting Over")
        # Play/Pause Button (Top-Center)
        elif WIDTH//2 - button_size//2 < x < WIDTH//2 + button_size//2 and HEIGHT - 10 - button_size < y < HEIGHT - 10:
            paused = not paused
            if paused:
                pause_time = time.time()
            else:
                last_time += time.time() - pause_time
        # Exit Button (Top-Right)
        elif WIDTH - 10 - button_size < x < WIDTH - 10 and HEIGHT - 10 - button_size < y < HEIGHT - 10:
            print(f"Goodbye! Score: {score}")
            glutLeaveMainLoop()
    glutPostRedisplay()

def update(value):
    global diamond_y, game_over, score, diamond_speed, last_time, diamond_x, diamond_color
    if not game_over and not paused:
        current_time = time.time()
        delta = current_time - last_time
        last_time = current_time
        
        diamond_y -= diamond_speed * delta * 100
        diamond_speed += 0.002
        
        if diamond_y < 0:
            game_over = True
            print(f"Game Over! Score: {score}")
        
        if check_collision():
            score += 1
            print(f"Score: {score}")
            diamond_x = random.randint(50, WIDTH-50)
            diamond_y = HEIGHT - 50
            
            diamond_color = (
                random.random() * 0.5 + 0.5,
                random.random() * 0.5 + 0.5,
                random.random() * 0.5 + 0.5
            )
        
    glutTimerFunc(16, update, 0)
    glutPostRedisplay()

def display():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glViewport(0, 0, WIDTH, HEIGHT)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluOrtho2D(0, WIDTH, 0, HEIGHT)
    
    # Draw buttons at top
    top_y = HEIGHT - 10 - button_size
    draw_button(10, top_y, 'left_arrow', TEAL)
    draw_button(WIDTH//2 - button_size//2, top_y, 'play_pause', AMBER)
    draw_button(WIDTH - 10 - button_size, top_y, 'cross', RED)
    
    # Draw game elements
    if not game_over:
        draw_diamond(diamond_x, diamond_y)
    draw_catcher(catcher_x)
    
    glutSwapBuffers()

def main():
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_DEPTH)
    glutInitWindowSize(WIDTH, HEIGHT)
    glutCreateWindow(b"Catch the Diamonds!")
    glClearColor(0.0, 0.0, 0.0, 1.0)
    
    glutDisplayFunc(display)
    glutSpecialFunc(keyboard)
    glutMouseFunc(mouse)
    glutTimerFunc(0, update, 0)
    
    glutMainLoop()

if __name__ == "__main__":
    main()