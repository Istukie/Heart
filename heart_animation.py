import pygame
import math
import random
import sys

# Initialization
pygame.init()
is_mobile = False  # Can't detect device in Python easily; assume desktop
koef = 0.5 if is_mobile else 1
width, height = int(koef * 800), int(koef * 600)
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Heart Animation")
clock = pygame.time.Clock()

# Utilities
def heart_position(rad):
    return (
        math.sin(rad) ** 3,
        -(15 * math.cos(rad) - 5 * math.cos(2 * rad) - 2 * math.cos(3 * rad) - math.cos(4 * rad))
    )

def scale_and_translate(pos, sx, sy, dx, dy):
    return dx + pos[0] * sx, dy + pos[1] * sy

# Heart setup
trace_count = 20 if is_mobile else 50
dr = 0.3 if is_mobile else 0.1
points_origin = []

for scale in [(210, 13), (150, 9), (90, 5)]:
    r = 0
    while r < math.pi * 2:
        points_origin.append(scale_and_translate(heart_position(r), *scale, 0, 0))
        r += dr

heart_points_count = len(points_origin)

def pulse(kx, ky):
    return [(kx * x + width // 2, ky * y + height // 2) for (x, y) in points_origin]

# Particle setup
particles = []
for i in range(heart_points_count):
    x = random.random() * width
    y = random.random() * height
    trace = [{"x": x, "y": y} for _ in range(trace_count)]
    particles.append({
        "vx": 0,
        "vy": 0,
        "R": 2,
        "speed": random.random() + 5,
        "q": int(random.random() * heart_points_count),
        "D": 2 * (i % 2) - 1,
        "force": 0.2 * random.random() + 0.7,
        "f": (random.randint(153, 255), random.randint(51, 153), random.randint(51, 153)),
        "trace": trace
    })

config = {"traceK": 0.4, "timeDelta": 0.01}
time = 0

# Main loop
running = True
while running:
    screen.fill((0, 0, 0, 10))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    n = -math.cos(time)
    target_points = pulse((1 + n) * 0.5, (1 + n) * 0.5)
    time += ((math.sin(time) < 0) and 9 or ((n > 0.8) and 0.2 or 1)) * config["timeDelta"]

    for u in particles:
        q = target_points[u["q"]]
        dx = u["trace"][0]["x"] - q[0]
        dy = u["trace"][0]["y"] - q[1]
        length = math.hypot(dx, dy)
        if length < 10:
            if random.random() > 0.95:
                u["q"] = int(random.random() * heart_points_count)
            else:
                if random.random() > 0.99:
                    u["D"] *= -1
                u["q"] = (u["q"] + u["D"]) % heart_points_count

        u["vx"] += -dx / length * u["speed"]
        u["vy"] += -dy / length * u["speed"]
        u["trace"][0]["x"] += u["vx"]
        u["trace"][0]["y"] += u["vy"]
        u["vx"] *= u["force"]
        u["vy"] *= u["force"]

        for k in range(len(u["trace"]) - 1):
            T = u["trace"][k]
            N = u["trace"][k + 1]
            N["x"] -= config["traceK"] * (N["x"] - T["x"])
            N["y"] -= config["traceK"] * (N["y"] - T["y"])

        for point in u["trace"]:
            pygame.draw.rect(screen, u["f"], (point["x"], point["y"], 1, 1))

    for i in range(min(len(target_points), 13)):
        pygame.draw.rect(screen, (255, 255, 255), (*target_points[i], 2, 2))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
