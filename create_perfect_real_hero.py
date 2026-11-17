import math
from PIL import Image

# Canvas size matching modern high-res hero
CANVAS_W = 1600
CANVAS_H = 820
BG_COLOR = (247, 247, 245) # #f7f7f5

canvas = Image.new("RGB", (CANVAS_W, CANVAS_H), BG_COLOR)

# Load real photo of Dr. Amsel (800x1200)
orig = Image.open("demo-expert/assets/dr-amsel.jpg")
orig_w, orig_h = orig.size

# We want the photo to fill the full height of the hero section (CANVAS_H = 820)
# Height = 820
# Preserving aspect ratio:
aspect = orig_w / orig_h # 800 / 1200 = 0.6667
target_h = CANVAS_H
target_w = int(target_h * aspect) # ~547px
amsel_res = orig.resize((target_w, target_h), Image.Resampling.LANCZOS)

# Create an ultra-smooth, silky transition mask on the left
# In the previous version, fade_left was 300 with power 1.8 and fade_top was 100.
# That caused:
# 1) The top 100px white line above head
# 2) A steep, murky dark-gray transition zone
#
# NEW MASK:
# - ZERO top fade (fade_top = 0)! So the photo naturally reaches the top edge without any white bar!
# - Wide, silky-smooth Hermite smoothstep fade on the left:
#   fade_width = 380px (almost 70% of the photo width!)
#   smoothstep formula: t = x/fade_width; factor = t * t * (3 - 2 * t)
#   This has zero derivative at x=0 and zero derivative at x=fade_width,
#   meaning there is ZERO visible boundary or harsh cloud edge!
mask = Image.new("L", (target_w, target_h), 255)
mask_pixels = mask.load()

fade_w = 380

for y in range(target_h):
    for x in range(target_w):
        if x < fade_w:
            t = x / float(fade_w)
            # Smooth Hermite curve with gentle ease-in
            factor = t * t * (3.0 - 2.0 * t)
            # Extra gentle curve to avoid middle darkness
            factor = math.pow(factor, 1.25)
            alpha = int(255 * factor)
        else:
            alpha = 255
        mask_pixels[x, y] = alpha

# Paste onto canvas aligned to the right edge (paste_x = CANVAS_W - target_w, paste_y = 0)
paste_x = CANVAS_W - target_w
paste_y = 0

canvas.paste(amsel_res, (paste_x, paste_y), mask)

output_path = "demo-expert/assets/amsel-perfect-blend.jpg"
canvas.save(output_path, quality=96)
print(f"Generated {output_path} successfully!")
