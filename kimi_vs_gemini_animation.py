import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import math
import random
import os

# Import MoviePy safely
try:
    from moviepy.editor import *
except ImportError:
    # Fallback for newer MoviePy versions (v2.0+) where structure might differ
    from moviepy import *

# Constants for 4K
WIDTH, HEIGHT = 3840, 2160
DURATION = 8
FPS = 24

# Colors
BG_COLOR_START = (10, 10, 20)
BG_COLOR_END = (0, 0, 5)
GEMINI_CYAN = (0, 255, 255)
GEMINI_BLUE = (7, 142, 250)
GEMINI_PURPLE = (173, 137, 235)
KIMI_DARK_BLUE = (10, 20, 40)
KIMI_NEON_BLUE = (50, 150, 255)
KIMI_MOON_GLOW = (200, 220, 255)
TEXT_COLOR = (255, 255, 255)
VS_COLOR_1 = (255, 50, 50)
VS_COLOR_2 = (255, 100, 50)

def create_gradient_background(width, height):
    """Creates a deep space gradient background."""
    base = Image.new('RGB', (width, height), BG_COLOR_START)
    top = Image.new('RGB', (width, height), BG_COLOR_END)
    mask = Image.new('L', (width, height))
    mask_data = []
    for y in range(height):
        mask_data.extend([int(255 * (y / height))] * width)
    mask.putdata(mask_data)
    base.paste(top, (0, 0), mask)
    return np.array(base)

# Optimization: Generate background once
BG_ARRAY = create_gradient_background(WIDTH, HEIGHT)
BG_IMAGE_STATIC = Image.fromarray(BG_ARRAY)

def get_font(size):
    """Tries to load a font from a list of common paths."""
    font_paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", # Linux
        "/usr/share/fonts/liberation/LiberationSans-Bold.ttf", # Linux
        "C:\\Windows\\Fonts\\arialbd.ttf", # Windows
        "/Library/Fonts/Arial Bold.ttf", # macOS
        "/System/Library/Fonts/HelveticaNeue.ttc" # macOS
    ]

    for path in font_paths:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except:
                continue

    # Fallback to default if nothing found
    print("Warning: No custom font found, using default. Text may be small.")
    return ImageFont.load_default()

def draw_crystallized_star(draw, center, size, angle, t):
    """Draws a futuristic, crystallized Gemini star."""
    cx, cy = center
    # Multiple layers for "crystal" effect
    for i in range(3):
        # Pulsating size
        pulse = 1.0 + 0.05 * math.sin(t * 3 + i)
        current_size = size * (1.0 - i * 0.2) * pulse

        # Colors shift slightly
        if i == 0: color = GEMINI_PURPLE + (150,)
        elif i == 1: color = GEMINI_BLUE + (200,)
        else: color = GEMINI_CYAN + (255,)

        points = []
        for j in range(8):
            # Sharp points, deep indents
            r = current_size if j % 2 == 0 else current_size * 0.25
            a = angle + j * (math.pi / 4)
            x = cx + r * math.cos(a)
            y = cy + r * math.sin(a)
            points.append((x, y))
        draw.polygon(points, fill=color)

        # Add "shimmer" lines
        if i == 2:
             draw.line(points + [points[0]], fill=(255, 255, 255, 200), width=3)

def draw_neural_moon(draw, center, size, t):
    """Draws a 'neural network' moon for Kimi."""
    cx, cy = center
    radius = size * 0.4

    # Base Crescent (subtle)
    # We want a techy wireframe look

    # Generate nodes along the crescent shape
    nodes = []
    num_nodes = 15
    for i in range(num_nodes):
        # Crescent arc: from -PI/2 to PI/2 (right side) roughly
        # Actually standard crescent is full circle minus offset circle.
        # Let's parametric the crescent surface.

        # Simpler: scattered points that form a crescent
        angle = -math.pi/2 + (math.pi * i / num_nodes)

        # Outer rim
        r_outer = radius
        x = cx + r_outer * math.cos(angle)
        y = cy + r_outer * math.sin(angle)
        nodes.append((x, y))

        # Inner rim (approximate)
        r_inner = radius * 0.7
        x2 = cx + (r_inner * math.cos(angle)) + (radius*0.2) # Offset
        y2 = cy + r_inner * math.sin(angle)
        nodes.append((x2, y2))

    # Draw connections
    for n1 in nodes:
        for n2 in nodes:
            dist = math.hypot(n1[0]-n2[0], n1[1]-n2[1])
            if dist < size * 0.15:
                # Alpha based on time
                alpha = int(100 + 155 * math.sin(t * 5 + dist))
                draw.line([n1, n2], fill=KIMI_NEON_BLUE + (alpha,), width=2)

    # Draw nodes
    for n in nodes:
        draw.ellipse((n[0]-3, n[1]-3, n[0]+3, n[1]+3), fill=KIMI_MOON_GLOW + (255,))

def get_gemini_frame(t):
    """Generates the 2026 Gemini frame."""
    size = 800 # Higher res for 4K
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    angle = t * 0.2
    draw_crystallized_star(draw, (size//2, size//2), size//2, angle, t)

    return np.array(img)

def get_kimi_frame(t):
    """Generates the 2026 Kimi frame."""
    size = 800 # Higher res for 4K
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    draw_neural_moon(draw, (size//2, size//2), size, t)

    # Text "Kimi 2026"
    font = get_font(120)

    text = "Kimi 2026"

    # Bbox logic for Kimi text
    try:
        bbox = draw.textbbox((0, 0), text, font=font)
        text_w = bbox[2] - bbox[0]
    except:
        text_w, _ = draw.textsize(text, font=font)

    # Draw text
    draw.text((size//2 - text_w // 2, size - 200), text, font=font, fill=KIMI_MOON_GLOW + (255,))

    return np.array(img)

def make_frame(t):
    """Composes the 4K frame."""
    # Background (Optimization: Copy from static image)
    bg_img = BG_IMAGE_STATIC.copy()

    # 4K coordinates
    # Center: 1920, 1080

    # Intro: 0-2s
    kimi_x_start = -800
    kimi_x_end = WIDTH // 4 - 400

    gemini_x_start = WIDTH + 800
    gemini_x_end = 3 * WIDTH // 4 - 400

    if t < 2:
        progress = t / 2
        progress = 1 - pow(1 - progress, 3) # Ease out
        kimi_x = kimi_x_start + (kimi_x_end - kimi_x_start) * progress
        gemini_x = gemini_x_start + (gemini_x_end - gemini_x_start) * progress
    else:
        kimi_x = kimi_x_end
        gemini_x = gemini_x_end

        # Idle float
        kimi_x += 20 * math.sin(t * 1.5)
        gemini_x -= 20 * math.sin(t * 1.5)

    y_pos = HEIGHT // 2 - 400

    # Draw Kimi
    kimi_arr = get_kimi_frame(t)
    kimi_pil = Image.fromarray(kimi_arr)
    bg_img.paste(kimi_pil, (int(kimi_x), int(y_pos)), kimi_pil)

    # Draw Gemini
    gemini_arr = get_gemini_frame(t)
    gemini_pil = Image.fromarray(gemini_arr)
    bg_img.paste(gemini_pil, (int(gemini_x), int(y_pos)), gemini_pil)

    # VS Text
    if t > 2.0:
        scale = 1.0
        if t < 2.5:
            scale = (t - 2.0) / 0.5
            scale = scale * scale

        font_size = int(300 * scale)
        font = get_font(font_size)

        draw = ImageDraw.Draw(bg_img)
        text = "VS"

        # Bbox logic
        try:
            bbox = draw.textbbox((0, 0), text, font=font)
            text_w = bbox[2] - bbox[0]
            text_h = bbox[3] - bbox[1]
        except:
             text_w, text_h = draw.textsize(text, font=font)

        # Dynamic color for VS
        vs_color = VS_COLOR_1 if int(t * 10) % 2 == 0 else VS_COLOR_2

        draw.text((WIDTH // 2 - text_w // 2, HEIGHT // 2 - text_h // 2), text, font=font, fill=vs_color)

    # Fade out
    if t > DURATION - 1:
        fade = (t - (DURATION - 1))
        black = Image.new('RGB', (WIDTH, HEIGHT), (0, 0, 0))
        bg_img = Image.blend(bg_img, black, fade)

    return np.array(bg_img)

# Generate Video
# Note: 4K rendering is resource intensive.
clip = VideoClip(make_frame, duration=DURATION)
clip.write_videofile("kimi_vs_gemini_4k.mp4", fps=FPS, codec="libx264")
