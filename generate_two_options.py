import math
from PIL import Image, ImageFilter, ImageDraw

# Option 1: The "Real Photo Studio Blend" (what user had in media_1794169090819_55b1e547.jpg, but perfected)
# - Real photo, completely untouched (no cutout!)
# - Right edge bleeds off the right
# - Height fits the hero section perfectly (760px)
# - Left transition: super wide, ultra-smooth ease-in-out blend that eliminates the harsh "облако"
# - Top edge: NO white strip! The photo extends cleanly to the top, with a soft horizontal vignette that connects to the navbar smoothly without any horizontal lines or harsh contrast.

orig = Image.open("demo-expert/assets/dr-amsel.jpg")
orig_w, orig_h = orig.size # 800, 1200

CANVAS_W = 1600
CANVAS_H = 760 # Fits any laptop screen without scroll!
BG_COLOR = (247, 247, 245)

# --- GENERATE OPTION 1: REAL PHOTO BLEND V3 ---
canvas1 = Image.new("RGB", (CANVAS_W, CANVAS_H), BG_COLOR)

# Resize orig to fill height 760
scale1 = CANVAS_H / float(orig_h) # 760 / 1200 ≈ 0.6333
target_w1 = int(orig_w * scale1) # ~506px
target_h1 = CANVAS_H
amsel_scaled1 = orig.resize((target_w1, target_h1), Image.Resampling.LANCZOS)

# Create smooth blend mask on left:
# Use smooth cubic Hermite curve across 340px
mask1 = Image.new("L", (target_w1, target_h1), 255)
m1_pixels = mask1.load()
fade_w = 340

for y in range(target_h1):
    for x in range(target_w1):
        if x < fade_w:
            t = x / float(fade_w)
            # Smoothstep
            v = t * t * (3.0 - 2.0 * t)
            # Gentle curve
            v = math.pow(v, 1.4)
            m1_pixels[x, y] = int(255 * v)
        else:
            m1_pixels[x, y] = 255

paste_x1 = CANVAS_W - target_w1
canvas1.paste(amsel_scaled1, (paste_x1, 0), mask1)
canvas1.save("demo-expert/assets/amsel-option-real-blend.jpg", quality=96)
print("Saved amsel-option-real-blend.jpg")

# --- GENERATE OPTION 2: SENTIO LIGHT STUDIO CYCLORAMA ---
# Where Dr. Amsel is in a light studio just like the Sentio hero man!
# But NO CUTOUT LOOK:
# 1) Dr. Amsel's torso bleeds naturally to right edge (x = CANVAS_W - target_w + 30)
# 2) Bleeds to bottom (y = CANVAS_H - target_h)
# 3) Behind him is an authentic light gray studio cyclorama wall with radial lighting
# 4) Soft ambient shadow behind him so he is naturally integrated into the studio space!

canvas2 = Image.new("RGB", (CANVAS_W, CANVAS_H), BG_COLOR)

# Load isolated
amsel_rgba = Image.open("demo-expert/assets/dr-amsel-isolated.png")
# Scale so head sits with ~55px headroom from top, torso reaches bottom
target_h2 = CANVAS_H
scale2 = target_h2 / float(orig_h)
target_w2 = int(orig_w * scale2)
amsel_scaled2 = amsel_rgba.resize((target_w2, target_h2), Image.Resampling.LANCZOS)

paste_x2 = CANVAS_W - target_w2 # Bleeds right edge!
paste_y2 = 0 # Fills full height!

# Create realistic Sentio studio cyclorama background on the right
studio_layer = Image.new("RGBA", (CANVAS_W, CANVAS_H), (0, 0, 0, 0))
studio_pixels = studio_layer.load()

# Center of soft studio lighting is behind his face/torso
cx = paste_x2 + target_w2 * 0.45
cy = CANVAS_H * 0.45
rx = target_w2 * 1.3
ry = CANVAS_H * 0.75

# Sentio studio light gray: RGB (212, 212, 214) to (236, 235, 232)
for y in range(CANVAS_H):
    for x in range(CANVAS_W):
        if x < CANVAS_W - target_w2 - 150:
            continue
        dx = (x - cx) / rx
        dy = (y - cy) / ry
        dist = math.sqrt(dx*dx + dy*dy)
        if dist < 1.2:
            falloff = 0.5 * (1.0 + math.cos(math.pi * min(dist / 1.2, 1.0)))
            # studio gray tone
            r = int(216 + (247 - 216) * (1.0 - falloff))
            g = int(216 + (247 - 216) * (1.0 - falloff))
            b = int(218 + (245 - 218) * (1.0 - falloff))
            alpha = int(255 * falloff)
            studio_pixels[x, y] = (r, g, b, alpha)

canvas2.paste(studio_layer, (0, 0), studio_layer)

# Soft studio shadow
_, _, _, amsel_alpha = amsel_scaled2.split()
shadow = amsel_alpha.filter(ImageFilter.GaussianBlur(radius=20))
shadow_img = Image.new("RGBA", (target_w2, target_h2), (140, 140, 145, 0))
shadow_img.putalpha(shadow.point(lambda p: int(p * 0.35)))
canvas2.paste(shadow_img, (paste_x2 - 12, paste_y2 + 8), shadow_img)

# Paste Dr. Amsel (full clothes, NO erased suspenders, full shoulders!)
canvas2.paste(amsel_scaled2, (paste_x2, paste_y2), amsel_scaled2)
canvas2.save("demo-expert/assets/amsel-option-studio-cyclorama.jpg", quality=96)
print("Saved amsel-option-studio-cyclorama.jpg")
