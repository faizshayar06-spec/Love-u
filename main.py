import cv2
import mediapipe as mp
import pygame
import random
import math

# Pygame Initialization
pygame.init()
WIDTH, HEIGHT = 900, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Hand Gesture Particle Effect")

# MediaPipe Hands Setup
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.75)

# Webcam Capture
cap = cv2.VideoCapture(0)

# Particle Class
class Particle:
    def __init__(self, x, y, target_x, target_y):
        self.x = x
        self.y = y
        self.target_x = target_x
        self.target_y = target_y
        self.color = (random.randint(200, 255), random.randint(100, 200), random.randint(220, 255))

    def update(self):
        dx = self.target_x - self.x
        dy = self.target_y - self.y
        self.x += dx * 0.1
        self.y += dy * 0.1

    def draw(self, surface):
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), 3)

# Function to generate target coordinates based on gesture state
def get_target_points(state):
    points = []
    
    if state == 1:
        for y in range(180, 420, 12):
            points.append((450, y))
        for x in range(410, 451, 12):
            points.append((x, 180))
            
    elif state == 2:
        for x in range(380, 520, 12):
            points.append((x, 180))
        for y in range(180, 300, 12):
            points.append((520, y))
        for x in range(380, 521, 12):
            points.append((x, 300))
        for y in range(300, 420, 12):
            points.append((380, y))
        for x in range(380, 521, 12):
            points.append((x, 420))
            
    elif state == 3:
        for x in range(380, 520, 12):
            points.append((x, 180))
            points.append((x, 300))
            points.append((x, 420))
        for y in range(180, 421, 12):
            points.append((520, y))
            
    elif state >= 5:
        for t in range(0, 628, 8):
            t_rad = t / 100.0
            hx = 16 * (math.sin(t_rad) ** 3)
            hy = -(13 * math.cos(t_rad) - 5 * math.cos(2*t_rad) - 2 * math.cos(3*t_rad) - math.cos(4*t_rad))
            points.append((int(450 + hx * 18), int(300 + hy * 18)))
    else:
        for _ in range(300):
            points.append((random.randint(150, 750), random.randint(100, 500)))
            
    return points

# Finger Counting Logic
def count_fingers(hand_landmarks):
    tips_ids = [4, 8, 12, 16, 20]
    fingers = []
    
    if hand_landmarks.landmark[tips_ids[0]].x < hand_landmarks.landmark[tips_ids[0] - 1].x:
        fingers.append(1)
    else:
        fingers.append(0)
        
    for id in range(1, 5):
        if hand_landmarks.landmark[tips_ids[id]].y < hand_landmarks.landmark[tips_ids[id] - 2].y:
            fingers.append(1)
        else:
            fingers.append(0)
            
    return sum(fingers)

# Initialize Particles
particles = [Particle(random.randint(0, WIDTH), random.randint(0, HEIGHT), random.randint(0, WIDTH), random.randint(0, HEIGHT)) for _ in range(400)]

current_state = 0
running = True
clock = pygame.time.Clock()

while running:
    screen.fill((15, 15, 25))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    success, img = cap.read()
    if success:
        img = cv2.flip(img, 1)
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = hands.process(img_rgb)

        detected_state = 0
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                detected_state = count_fingers(hand_landmarks)

        if detected_state != current_state:
            current_state = detected_state
            targets = get_target_points(current_state)
            
            for i, p in enumerate(particles):
                if i < len(targets):
                    p.target_x, p.target_y = targets[i]
                else:
                    p.target_x, p.target_y = random.randint(100, 800), random.randint(100, 500)

    for p in particles:
        p.update()
        p.draw(screen)

    pygame.display.flip()
    clock.tick(60)

cap.release()
pygame.quit()

