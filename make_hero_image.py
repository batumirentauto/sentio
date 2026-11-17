import math
from PIL import Image, ImageFilter

# 1. Target canvas size for high-DPI desktop hero
# Width 1600, Height 900 (or height matching the hero section)
# In the hero section, desktop height will be ~720px
CANVAS_W = 1600
CANVAS_H = 900
BG_COLOR = (247, 247, 245) # #f7f7f5

# Create base canvas with the exact page background color #f7f7f5
canvas = Image.new("RGB", (CANVAS_W, CANVAS_H), BG_COLOR)

# Load isolated Dr. Amsel
amsel_rgba = Image.open("demo-expert/assets/dr-amsel-isolated.png")
orig_w, orig_h = amsel_rgba.size

# We want Dr. Amsel to be framed naturally on the right:
# - Head should start ~45px from the top edge so there is natural, elegant headroom.
# - The bottom of his torso should reach the bottom of the canvas (or slightly beyond).
# If canvas height is 900, and headroom is ~45px, his head-to-bottom span is ~855px.
# In original image, bounding box was (0, 52, 800, 1200), so person height is 1148px.
# Scaling factor: 855 / 1148 ≈ 0.745
target_h = int(CANVAS_H * 0.98) # ~882px
scale = target_h / orig_h
target_w = int(orig_w * scale)
amsel_scaled = amsel_rgba.resize((target_w, target_h), Image.Resampling.LANCZOS)

# Position on canvas:
# Right-aligned with a subtle offset from right edge (e.g. right: 40px)
paste_x = CANVAS_W - target_w - 40
paste_y = CANVAS_H - target_h # sits at the bottom, head has ~45px headroom!

# Now let's create a subtle, high-end studio ambient backdrop behind Dr. Amsel:
# In the original Sentio, there is a very soft, warm greige/studio light behind the subject,
# which fades with an ultra-smooth, multi-stop diffusion into #f7f7f5.
# Let's create this studio lighting on a separate layer:
studio_light = Image.new("RGBA", (CANVAS_W, CANVAS_H), (0, 0, 0, 0))
studio_pixels = studio_light.load()

# Center of soft studio light is around Dr. Amsel's head/upper torso
center_x = paste_x + target_w * 0.55
center_y = paste_y + target_h * 0.45
rx = target_w * 1.1 # wide horizontal spread
ry = target_h * 0.85 # vertical spread

# Subtle studio tint: slightly deeper warm neutral greige (RGB: 228, 226, 221)
# It only has an alpha of ~0.35 at peak, fading to 0 smoothly at distance > 1.0
tint_r, tint_g, tint_b = (226, 224, 219)

for y in range(CANVAS_H):
    for x in range(CANVAS_W):
        # Normalized elliptical distance
        dx = (x - center_x) / rx
        dy = (y - center_y) / ry
        dist = math.sqrt(dx*dx + dy*dy)
        if dist < 1.0:
            # Smooth cosine falloff
            falloff = 0.5 * (1.0 + math.cos(math.pi * dist))
            # Subtle peak intensity: max alpha ~ 95 out of 255 (very soft, warm tone)
            alpha = int(95 * (falloff ** 1.6))
            studio_pixels[x, y] = (tint_r, tint_g, tint_b, alpha)

# Composite studio light onto canvas
canvas.paste(studio_light, (0, 0), studio_light)

# For Dr. Amsel himself, let's create a very soft transition on the far left edge of his torso
# so that where his left shoulder/arm touches the text area, it melts into the background
# with zero hard cuts, but his face and head remain 100% crisp!
r, g, b, a = amsel_scaled.split()
a_pixels = a.load()

# Soft edge on left: only for x in [0..140] of the scaled image, and only lower down (torso)
for y in range(target_h):
    for x in range(target_w):
        curr_a = a_pixels[x, y]
        if curr_a > 0:
            # If on the left edge of torso
            if x < 120 and y > target_h * 0.4:
                factor = (x / 120.0) ** 1.4
                a_pixels[x, y] = int(curr_a * factor)

amsel_soft = Image.merge("RGBA", (r, g, b, a))

# Composite Dr. Amsel onto the canvas!
canvas.paste(amsel_soft, (paste_x, paste_y), amsel_soft)

# Save high-quality output
output_path = "demo-expert/assets/amsel-hero-seamless-v2.jpg"
canvas.save(output_path, "JPEG", quality=96)
print(f"Generated {output_path} successfully!")
