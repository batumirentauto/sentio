import math
from PIL import Image, ImageFilter, ImageDraw

# Approach 1: Studio Retouch (Sentio Cyclorama)
# Isolated Dr. Amsel placed with right-bleed, bottom-bleed, soft contact shadow,
# and an authentic warm studio cyclorama background (identical to Sentio hero-cube-v2).

CANVAS_W = 1600
CANVAS_H = 800
BG_COLOR = (247, 247, 245) # #f7f7f5

# 1. Base canvas
canvas = Image.new("RGB", (CANVAS_W, CANVAS_H), BG_COLOR)

# Load isolated Dr. Amsel
amsel_rgba = Image.open("demo-expert/assets/dr-amsel-isolated.png")
orig_w, orig_h = amsel_rgba.size # 800x1200

# We want his head to have ~60px headroom from top.
# In original, top of head is y=52.
# So if person height from head to bottom is 1200 - 52 = 1148px.
# In canvas of height 800, if head is at y=60, available height = 740px.
# scale = 740 / 1148 ≈ 0.644
scale = (CANVAS_H - 60) / (orig_h - 52)
target_w = int(orig_w * scale) # ~515px
target_h = int(orig_h * scale) # ~773px

amsel_scaled = amsel_rgba.resize((target_w, target_h), Image.Resampling.LANCZOS)

# Position:
# MUST bleed off the right edge so right shoulder is not cut off!
# paste_x = CANVAS_W - target_w (exact right bleed)
# paste_y = CANVAS_H - target_h (exact bottom bleed)
paste_x = CANVAS_W - target_w
paste_y = CANVAS_H - target_h

# Now, create the authentic Sentio Studio Cyclorama background:
# Look at Sentio: behind the person is a soft, warm neutral studio gradient:
# Right side: RGB (218, 216, 211) -> (232, 230, 226)
# Left side: seamlessly transitions into (247, 247, 245)
studio_bg = Image.new("RGBA", (CANVAS_W, CANVAS_H), (0, 0, 0, 0))
studio_draw = ImageDraw.Draw(studio_bg)

# Horizontal gradient on the right half
for x in range(CANVAS_W):
    if x < 650:
        continue
    # progress from x=650 (0.0) to x=1600 (1.0)
    p = (x - 650) / (CANVAS_W - 650)
    # smooth hermite curve (smoothstep)
    t = p * p * (3 - 2 * p)
    # color transitions from BG_COLOR to soft studio tone (222, 220, 215)
    r = int(247 + (220 - 247) * t)
    g = int(247 + (218 - 247) * t)
    b = int(245 + (213 - 245) * t)
    studio_draw.line([(x, 0), (x, CANVAS_H)], fill=(r, g, b, 255))

canvas.paste(studio_bg, (0, 0), studio_bg)

# Soft studio ambient / contact shadow behind Dr. Amsel so he looks grounded and real
# Extract alpha mask of Dr. Amsel
_, _, _, amsel_a = amsel_scaled.split()
shadow_mask = amsel_a.filter(ImageFilter.GaussianBlur(radius=25))

# Create shadow image: subtle warm gray tone
shadow_layer = Image.new("RGBA", (target_w, target_h), (180, 175, 170, 0))
# apply blurred mask with low opacity (max ~70)
shadow_layer.putalpha(shadow_mask.point(lambda p: int(p * 0.35)))

# Paste shadow behind Dr. Amsel, offset slightly to the left/down
canvas.paste(shadow_layer, (paste_x - 15, paste_y + 10), shadow_layer)

# Paste Dr. Amsel on top
canvas.paste(amsel_scaled, (paste_x, paste_y), amsel_scaled)

canvas.save("demo-expert/assets/amsel-studio-sentio.jpg", quality=96)
print("Generated amsel-studio-sentio.jpg successfully!")
