import os
import io
import math
import random
import requests
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance

# MoviePy Import: Compatibility for v1.x and v2.x
try:
    from moviepy.editor import VideoClip
except ImportError:
    try:
        from moviepy import VideoClip
    except ImportError:
        print("Error: MoviePy not found. Please install via 'pip install moviepy'")
        exit(1)

# ==========================================
# CONFIGURATION
# ==========================================
WIDTH, HEIGHT = 3840, 2160
FPS = 60
DURATION = 4
OUTPUT_FILE = "kimi_vs_gemini_4k.mp4"

# Fonts: List of candidates for cross-platform compatibility
FONT_CANDIDATES = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "arial.ttf",
    "Arial.ttf",
    "/System/Library/Fonts/HelveticaNeue-Bold.ttf",
    "C:\\Windows\\Fonts\\arial.ttf"
]

# URLs
KIMI_LOGO_URL = "https://upload.wikimedia.org/wikipedia/en/8/87/Kimi-logo-2025.png"
GEMINI_URLS = [
    "https://uxwing.com/wp-content/themes/uxwing/download/brands-and-social-media/google-gemini-icon.png",
    "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8a/Google_Gemini_logo.svg/1024px-Google_Gemini_logo.svg.png",
    "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1d/Google_Gemini_icon_2025.svg/480px-Google_Gemini_icon_2025.svg.png"
]

# Colors
BG_COLOR_INNER = (26, 26, 46)     # #1a1a2e
BG_COLOR_OUTER = (0, 0, 0)        # #000000
KIMI_COLOR = (45, 212, 191)       # Teal
GEMINI_COLOR = (168, 85, 247)     # Purple

# ==========================================
# ASSET LOADING
# ==========================================
def load_image_from_url(url, size=None):
    try:
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
        response.raise_for_status()
        img = Image.open(io.BytesIO(response.content)).convert("RGBA")
        if size:
            img = img.resize(size, Image.Resampling.LANCZOS)
        return img
    except Exception as e:
        print(f"Error loading {url}: {e}")
        # Return a placeholder colored square
        img = Image.new("RGBA", size if size else (100, 100), (128, 128, 128, 255))
        return img

print("Downloading assets...")
kimi_img_orig = load_image_from_url(KIMI_LOGO_URL)

gemini_img_orig = None
for url in GEMINI_URLS:
    print(f"Trying Gemini URL: {url}")
    img = load_image_from_url(url)
    # Check if placeholder (simple check: if pixel 0,0 is gray vs something else? Or just rely on previous logic)
    # The previous logic was `img.size != (100, 100)` because `load_image_from_url` returns 100x100 on error.
    if img.size != (100, 100):
        gemini_img_orig = img
        print("Success.")
        break

if gemini_img_orig is None or gemini_img_orig.size == (100, 100):
     print("Failed to load Gemini logo from all sources. Using placeholder.")
     if gemini_img_orig is None:
         gemini_img_orig = Image.new("RGBA", (100, 100), (128, 128, 128, 255))

print("Assets loaded.")

# Font Loading
font_path = None
for f in FONT_CANDIDATES:
    if os.path.exists(f):
        font_path = f
        break

try:
    if font_path:
        font_large = ImageFont.truetype(font_path, 180)
        font_medium = ImageFont.truetype(font_path, 80)
        font_small = ImageFont.truetype(font_path, 40)
        font_vs = ImageFont.truetype(font_path, 300)
    else:
        # Fallback to default if none found
        raise IOError("No font found")
except IOError:
    print("Warning: Custom font not found, using default.")
    font_large = ImageFont.load_default()
    font_medium = ImageFont.load_default()
    font_small = ImageFont.load_default()
    font_vs = ImageFont.load_default()

# ==========================================
# PARTICLE SYSTEM
# ==========================================
class Particle:
    def __init__(self, w, h):
        self.w = w
        self.h = h
        self.x = random.random() * w
        self.y = random.random() * h
        self.vx = (random.random() - 0.5) * 1.0 # Faster for 4k
        self.vy = (random.random() - 0.5) * 1.0
        self.size = random.random() * 4 # Larger for 4k
        self.color = KIMI_COLOR if random.random() > 0.5 else GEMINI_COLOR
        self.alpha = 0.5

    def update(self):
        self.x += self.vx
        self.y += self.vy
        if self.x < 0 or self.x > self.w: self.vx *= -1
        if self.y < 0 or self.y > self.h: self.vy *= -1

    def draw(self, draw):
        fill = self.color + (int(255 * self.alpha),)
        draw.ellipse([self.x - self.size, self.y - self.size,
                      self.x + self.size, self.y + self.size], fill=fill)

particles = [Particle(WIDTH, HEIGHT) for _ in range(80)]

# ==========================================
# HELPERS
# ==========================================
def create_radial_gradient(width, height, center_color, edge_color):
    Y, X = np.ogrid[:height, :width]
    center_x, center_y = width / 2, height / 2
    dist_from_center = np.sqrt((X - center_x)**2 + (Y - center_y)**2)
    max_dist = np.sqrt((width/2)**2 + (height/2)**2)

    mask = dist_from_center / max_dist
    mask = np.clip(mask, 0, 1)

    r = center_color[0] * (1 - mask) + edge_color[0] * mask
    g = center_color[1] * (1 - mask) + edge_color[1] * mask
    b = center_color[2] * (1 - mask) + edge_color[2] * mask

    arr = np.dstack((r, g, b)).astype(np.uint8)
    return Image.fromarray(arr, "RGB")

bg_base = create_radial_gradient(WIDTH, HEIGHT, BG_COLOR_INNER, BG_COLOR_OUTER)

def ease_out_cubic(t):
    return 1 - pow(1 - t, 3)

def draw_grid(draw, w, h):
    grid_size = int(w * 0.04)
    color = (255, 255, 255, 8)
    for x in range(0, w, grid_size):
        draw.line([(x, 0), (x, h)], fill=color, width=1)
    for y in range(0, h, grid_size):
        draw.line([(0, y), (w, y)], fill=color, width=1)

def draw_lighting(overlay, w, h):
    draw = ImageDraw.Draw(overlay)
    left_color = (20, 184, 166, 40)
    draw.ellipse([-w*0.1, -h*0.5, w*0.5, h*1.5], fill=left_color)
    right_color = (79, 70, 229, 50)
    draw.ellipse([w*0.5, -h*0.5, w*1.1, h*1.5], fill=right_color)

def draw_tech_lines(draw, w, h):
    color = (255, 255, 255, 25)
    draw.line([(w*0.05, h*0.1), (w*0.95, h*0.1)], fill=color, width=1)
    draw.line([(w*0.05, h*0.9), (w*0.95, h*0.9)], fill=color, width=1)

# ==========================================
# RENDER FRAME
# ==========================================
def make_frame(t):
    # Convert to RGBA for proper alpha blending of draw operations
    frame = bg_base.copy().convert("RGBA")

    draw = ImageDraw.Draw(frame, "RGBA")
    draw_grid(draw, WIDTH, HEIGHT)

    overlay = Image.new("RGBA", (WIDTH, HEIGHT), (0,0,0,0))
    draw_lighting(overlay, WIDTH, HEIGHT)
    frame.paste(overlay, (0,0), overlay)

    draw = ImageDraw.Draw(frame, "RGBA")
    draw_tech_lines(draw, WIDTH, HEIGHT)

    # Update and draw particles
    for i, p in enumerate(particles):
        p.update()
        p.draw(draw)

        # Connect particles
        for j in range(i + 1, len(particles)):
            p2 = particles[j]
            dx = p.x - p2.x
            dy = p.y - p2.y
            dist = math.sqrt(dx*dx + dy*dy)

            if dist < 200: # Increase connection distance for 4k
                # Opacity: 0.1 - dist/2000.
                alpha = max(0, 0.1 - dist/2000)
                if alpha > 0:
                    alpha_int = int(255 * alpha)
                    if alpha_int > 0:
                        draw.line([(p.x, p.y), (p2.x, p2.y)], fill=(255, 255, 255, alpha_int), width=2)

    # --- KIMI (Left) ---
    kimi_start = 0.5
    if t > kimi_start:
        progress = min((t - kimi_start) / 1.2, 1)
        eased = ease_out_cubic(progress)
        alpha = int(255 * eased)
        offset_x = -200 * (1 - eased) # Scale movement
        logo_size = 280 # Scale logo
        lx = WIDTH * 0.25 + offset_x - logo_size/2
        ly = HEIGHT/2 - logo_size/2 - 80 # Scale Y offset

        if alpha > 0:
            glow_intensity = int(76 + 76 * math.sin(t * 2))
            glow_color = (45, 212, 191, glow_intensity)
            draw.rounded_rectangle([lx-10, ly-10, lx+logo_size+10, ly+logo_size+10], radius=48, fill=None, outline=glow_color, width=4)

            k_logo = kimi_img_orig.resize((logo_size, logo_size), Image.Resampling.LANCZOS)
            if alpha < 255:
                k_logo.putalpha(int(alpha))
            frame.paste(k_logo, (int(lx), int(ly)), k_logo)

            txt_x = WIDTH * 0.25 + offset_x
            txt_y = ly + logo_size + 160 # Scale text offset
            def draw_text_centered(txt, x, y, font, fill):
                bbox = draw.textbbox((0, 0), txt, font=font)
                w = bbox[2] - bbox[0]
                draw.text((x - w/2, y), txt, font=font, fill=fill)

            draw_text_centered("Kimi", txt_x, txt_y, font_large, (45, 212, 191, int(128 * eased)))
            draw_text_centered("Kimi", txt_x, txt_y, font_large, (248, 250, 252, alpha))
            draw_text_centered("MOONSHOT AI", txt_x, ly + logo_size + 360, font_small, (45, 212, 191, int(180 * eased)))

    # --- GEMINI (Right) ---
    gemini_start = 0.8
    if t > gemini_start:
        progress = min((t - gemini_start) / 1.2, 1)
        eased = ease_out_cubic(progress)
        alpha = int(255 * eased)
        offset_x = 200 * (1 - eased) # Scale movement
        float_y = -30 * math.sin(t * 2) # Scale float
        logo_size = 280 # Scale logo
        lx = WIDTH * 0.75 + offset_x - logo_size/2
        ly = HEIGHT/2 - logo_size/2 - 80 + float_y # Scale Y offset

        if alpha > 0:
            g_logo = gemini_img_orig.resize((logo_size, logo_size), Image.Resampling.LANCZOS)
            if alpha < 255:
                r, g, b, a = g_logo.split()
                a = a.point(lambda p: p * (alpha / 255))
                g_logo.putalpha(a)
            frame.paste(g_logo, (int(lx), int(ly)), g_logo)

            txt_x = WIDTH * 0.75 + offset_x
            txt_y = ly + logo_size + 160 # Scale text offset
            draw_text_centered("Gemini", txt_x, txt_y, font_large, (192, 132, 252, alpha))
            draw_text_centered("GOOGLE DEEPMIND", txt_x, ly + logo_size + 360, font_small, (168, 85, 247, int(180 * eased)))

    # --- VS BADGE ---
    vs_start = 1.5
    if t > vs_start:
        progress = min((t - vs_start) / 0.8, 1)
        scale = 1.0
        if progress < 0.5:
            scale = 5 - (5 - 0.8) * (progress / 0.5)
        elif progress < 0.7:
            scale = 0.8 + (1.1 - 0.8) * ((progress - 0.5) / 0.2)
        else:
            scale = 1.1 - (1.1 - 1.0) * ((progress - 0.7) / 0.3)

        alpha_val = int(255 * (progress * 10)) if progress < 0.1 else 255

        if alpha_val > 0:
            badge_size = 800 # Double badge base size for 4k quality
            badge_img = Image.new("RGBA", (badge_size, badge_size), (0,0,0,0))
            slash_img = Image.new("RGBA", (badge_size, badge_size), (0,0,0,0))
            slash_draw = ImageDraw.Draw(slash_img)
            slash_draw.rectangle([0, 300, 800, 500], fill=(255, 255, 255, 25)) # Scale rectangle
            slash_img = slash_img.rotate(15, center=(400, 400), resample=Image.BICUBIC)
            badge_img.paste(slash_img, (0,0), slash_img)

            badge_draw = ImageDraw.Draw(badge_img)
            text = "VS"
            bbox = badge_draw.textbbox((0,0), text, font=font_vs)
            tw, th = bbox[2]-bbox[0], bbox[3]-bbox[1]
            cx, cy = 400, 400

            badge_draw.text((cx - tw/2 + 8, cy - th/2 - 40 + 8), text, font=font_vs, fill=(0,0,0,alpha_val))
            badge_draw.text((cx - tw/2, cy - th/2 - 40), text, font=font_vs, fill=(255,255,255,alpha_val))

            final_w = int(badge_size * scale)
            final_h = int(badge_size * scale)
            if final_w > 0 and final_h > 0:
                badge_scaled = badge_img.resize((final_w, final_h), Image.Resampling.BILINEAR)
                bx = WIDTH/2 - final_w/2
                by = HEIGHT/2 - final_h/2
                frame.paste(badge_scaled, (int(bx), int(by)), badge_scaled)

    # Convert back to RGB for moviepy (optional but safe)
    return np.array(frame.convert("RGB"))

# ==========================================
# EXECUTION
# ==========================================
print(f"Generating video {WIDTH}x{HEIGHT} @ {FPS}fps for {DURATION}s...")
clip = VideoClip(make_frame, duration=DURATION)
clip.write_videofile(OUTPUT_FILE, fps=FPS, codec="libx264", audio=False)
print("Done.")
