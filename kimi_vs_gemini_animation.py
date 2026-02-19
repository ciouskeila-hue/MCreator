import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from moviepy import *
import math

# Constants
WIDTH, HEIGHT = 1920, 1080
DURATION = 8
FPS = 24

# Colors
BG_COLOR_START = (20, 20, 30)
BG_COLOR_END = (5, 5, 10)
GEMINI_BLUE = (7, 142, 250)
GEMINI_PURPLE = (173, 137, 235)
KIMI_DARK = (26, 26, 46)
KIMI_MOON = (233, 233, 240) # Off-white moon
KIMI_TEXT_COLOR = (255, 255, 255)
VS_COLOR = (255, 50, 50)

def create_gradient_background(width, height):
    """Creates a vertical gradient background."""
    base = Image.new('RGB', (width, height), BG_COLOR_START)
    top = Image.new('RGB', (width, height), BG_COLOR_END)
    mask = Image.new('L', (width, height))
    mask_data = []
    for y in range(height):
        mask_data.extend([int(255 * (y / height))] * width)
    mask.putdata(mask_data)
    base.paste(top, (0, 0), mask)
    return np.array(base)

def draw_star(draw, center, radius, inner_radius, angle, fill):
    """Draws a 4-pointed star."""
    cx, cy = center
    points = []
    for i in range(8):
        r = radius if i % 2 == 0 else inner_radius
        a = angle + i * (math.pi / 4)
        x = cx + r * math.cos(a)
        y = cy + r * math.sin(a)
        points.append((x, y))
    draw.polygon(points, fill=fill)

def get_gemini_frame(t):
    """Generates the Gemini logo frame."""
    size = 400
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Rotation
    angle = t * 0.5  # Rotates over time

    # Gradient approximation (simpler: draw multiple stars with different colors/opacity)
    # Outer glow
    draw_star(draw, (size//2, size//2), size//2, size//6, angle, GEMINI_PURPLE + (100,))
    # Inner star
    draw_star(draw, (size//2, size//2), size//2.2, size//6.5, angle, GEMINI_BLUE + (255,))

    return np.array(img)

def get_kimi_frame(t):
    """Generates the Kimi logo frame."""
    size = 400
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Moon shape
    cx, cy = size // 2, size // 2
    radius = 150

    # Main circle
    draw.ellipse((cx - radius, cy - radius, cx + radius, cy + radius), fill=KIMI_MOON + (255,))

    # Subtract circle to make crescent
    offset = 40
    draw.ellipse((cx - radius + offset, cy - radius - offset/2, cx + radius + offset, cy + radius - offset/2), fill=(0, 0, 0, 0), outline=None)

    # We need to use a mask to subtract properly in RGBA
    # Create a moon mask
    mask = Image.new('L', (size, size), 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.ellipse((cx - radius, cy - radius, cx + radius, cy + radius), fill=255)

    subtract_mask = Image.new('L', (size, size), 0)
    sub_draw = ImageDraw.Draw(subtract_mask)
    sub_draw.ellipse((cx - radius + offset, cy - radius, cx + radius + offset, cy + radius), fill=255)

    # Combine masks: mask - subtract_mask
    final_mask = np.array(mask)
    sub_arr = np.array(subtract_mask)
    final_mask = np.clip(final_mask.astype(int) - sub_arr.astype(int), 0, 255).astype(np.uint8)

    # Create final moon image
    moon_img = Image.new('RGBA', (size, size), KIMI_MOON + (255,))
    moon_img.putalpha(Image.fromarray(final_mask))

    # Add Text "Kimi"
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 80)
    except:
        font = ImageFont.load_default()

    draw_final = ImageDraw.Draw(moon_img)
    text = "Kimi"

    # Text position (centered below or inside)
    # Using textbbox if available (Pillow >= 9.2.0)
    try:
        bbox = draw_final.textbbox((0, 0), text, font=font)
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]
    except:
        text_w, text_h = draw_final.textsize(text, font=font)

    draw_final.text((cx - text_w // 2, cy + radius - 20), text, font=font, fill=KIMI_TEXT_COLOR + (255,))

    return np.array(moon_img)

def make_frame(t):
    """Composes the full frame."""
    # Background
    bg = create_gradient_background(WIDTH, HEIGHT)
    bg_img = Image.fromarray(bg)

    # Calculate positions based on time
    # Intro: 0-2s
    kimi_x_start = -500
    kimi_x_end = WIDTH // 4 - 200

    gemini_x_start = WIDTH + 500
    gemini_x_end = 3 * WIDTH // 4 - 200

    if t < 2:
        progress = t / 2
        # Ease out cubic
        progress = 1 - pow(1 - progress, 3)
        kimi_x = kimi_x_start + (kimi_x_end - kimi_x_start) * progress
        gemini_x = gemini_x_start + (gemini_x_end - gemini_x_start) * progress
    else:
        kimi_x = kimi_x_end
        gemini_x = gemini_x_end

        # Idle animation (floating)
        kimi_x += 10 * math.sin(t * 2)
        gemini_x -= 10 * math.sin(t * 2)

    y_pos = HEIGHT // 2 - 200

    # Draw Elements
    kimi_arr = get_kimi_frame(t)
    kimi_pil = Image.fromarray(kimi_arr)
    bg_img.paste(kimi_pil, (int(kimi_x), int(y_pos)), kimi_pil)

    gemini_arr = get_gemini_frame(t)
    gemini_pil = Image.fromarray(gemini_arr)
    bg_img.paste(gemini_pil, (int(gemini_x), int(y_pos)), gemini_pil)

    # Draw "VS"
    if t > 2.5:
        # Scale effect for entrance
        scale = 1.0
        if t < 3.0:
            scale = (t - 2.5) / 0.5 # 0 to 1
            scale = scale * scale # Ease in

        try:
            font_size = int(150 * scale)
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
        except:
            font = ImageFont.load_default()

        draw = ImageDraw.Draw(bg_img)
        text = "VS"

        try:
            bbox = draw.textbbox((0, 0), text, font=font)
            text_w = bbox[2] - bbox[0]
            text_h = bbox[3] - bbox[1]
        except:
             text_w, text_h = draw.textsize(text, font=font)

        # Pulse effect
        pulse = 1.0 + 0.1 * math.sin((t - 3.0) * 5)

        # If scaling is done, apply pulse
        if t >= 3.0:
             # Re-create font with pulse size
             try:
                font_size = int(150 * pulse)
                font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
                # Recalculate size
                bbox = draw.textbbox((0, 0), text, font=font)
                text_w = bbox[2] - bbox[0]
                text_h = bbox[3] - bbox[1]
             except:
                pass

        draw.text((WIDTH // 2 - text_w // 2, HEIGHT // 2 - text_h // 2 - 20), text, font=font, fill=VS_COLOR)

    # Fade out at the end
    if t > DURATION - 1:
        fade = (t - (DURATION - 1)) # 0 to 1
        black = Image.new('RGB', (WIDTH, HEIGHT), (0, 0, 0))
        bg_img = Image.blend(bg_img, black, fade)

    return np.array(bg_img)

# Generate Video
clip = VideoClip(make_frame, duration=DURATION)
clip.write_videofile("kimi_vs_gemini.mp4", fps=FPS, codec="libx264")
