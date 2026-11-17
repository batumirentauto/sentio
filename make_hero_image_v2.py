import math
from PIL import Image, ImageFilter

CANVAS_W = 1600
CANVAS_H = 860
BG_COLOR = (247, 247, 245) # #f7f7f5

canvas = Image.new("RGB", (CANVAS_W, CANVAS_H), BG_COLOR)

# Load isolated Dr. Amsel
amsel_rgba = Image.open("demo-expert/assets/dr-amsel-isolated.png")
orig_w, orig_h = amsel_rgba.size

# We want his head to start around y=70px (headroom of ~70px)
# Original bounding box: top of head at y=52
# Desired head top at y=70px, torso bottom reaches canvas bottom y=CANVAS_H
# Person height in original image = 1200 - 52 = 1148px
# We have 860 - 70 = 790px available for person
target_person_h = 790
scale = target_person_h / 1148.0
target_w = int(orig_w * scale)
target_h = int(orig_h * scale)

amsel_scaled = amsel_rgba.resize((target_w, target_h), Image.Resampling.LANCZOS)

# Position:
# In scaled image, top of head is at 52 * scale ≈ 35px
# So to have head at y=70px, paste_y = 70 - 35 = 35px
# Then bottom of image will be at 35 + target_h ≈ 860px (exact canvas bottom!)
paste_y = CANVAS_H - target_h
paste_x = CANVAS_W - target_w - 60 # 60px padding from right edge

# Soft studio backdrop layer
studio_light = Image.new("RGBA", (CANVAS_W, CANVAS_H), (0, 0, 0, 0))
studio_pixels = studio_light.load()

# Center of soft warm ambient studio tone
center_x = paste_x + target_w * 0.52
center_y = paste_y + target_h * 0.42
rx = target_w * 1.05
ry = target_h * 0.85

# Warm neutral studio tint (Loro Piana / Sentio warm paper greige)
tint_r, tint_g, tint_b = (228, 226, 221)

for y in range(CANVAS_H):
    for x in range(CANVAS_W):
        dx = (x - center_x) / rx
        dy = (y - center_y) / ry
        dist = math.sqrt(dx*dx + dy*dy)
        if dist < 1.0:
            falloff = 0.5 * (1.0 + math.cos(math.pi * dist))
            # Peak alpha is gentle (~85) so it's a whisper-soft studio ambient light
            alpha = int(85 * (falloff ** 1.8))
            studio_pixels[x, y] = (tint_r, tint_g, tint_b, alpha)

canvas.paste(studio_light, (0, 0), studio_light)

# Feather the left edge of Dr. Amsel's torso so it melts seamlessly into the background
r, g, b, a = amsel_scaled.split()
a_pixels = a.load()

for y in range(target_h):
    for x in range(target_w):
        curr_a = a_pixels[x, y]
        if curr_a > 0:
            # Soften left edge of torso
            if x < 100 and y > target_h * 0.35:
                factor = (x / 100.0) ** 1.3
                a_pixels[x, y] = int(curr_a * factor)

amsel_soft = Image.merge("RGBA", (r, g, b, a))

# Paste Dr. Amsel
canvas.paste(amsel_soft, (paste_x, paste_y), amsel_soft)

output_path = "demo-expert/assets/amsel-hero-seamless-v2.jpg"
canvas.save(output_path, "JPEG", quality=96)
print(f"Generated {output_path} successfully!")
