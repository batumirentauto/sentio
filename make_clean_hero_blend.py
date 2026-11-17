import math
from PIL import Image

CANVAS_W = 1600
CANVAS_H = 760
BG_COLOR = (247, 247, 245) # #f7f7f5

canvas = Image.new("RGB", (CANVAS_W, CANVAS_H), BG_COLOR)

# Load real photo of Dr. Amsel
orig = Image.open("demo-expert/assets/dr-amsel.jpg")
orig_w, orig_h = orig.size # 800, 1200

# Scale to fit height 760
scale = CANVAS_H / float(orig_h) # ~0.6333
target_w = int(orig_w * scale)   # ~506px
target_h = CANVAS_H              # 760px
amsel_res = orig.resize((target_w, target_h), Image.Resampling.LANCZOS)

# In this 506x760 scaled image:
# Where does Dr. Amsel actually start?
# At eye level (y=200): in orig, x=139 -> scaled x = 139 * 0.6333 ≈ 88px!
# At mouth level (y=280): in orig, x=156 -> scaled x = 156 * 0.6333 ≈ 99px!
# At neck level (y=380): in orig, x=224 -> scaled x = 224 * 0.6333 ≈ 142px!
# At shoulder/chest (y=500+): in orig, x=72 -> scaled x ≈ 45px!
#
# Therefore, any fade MUST be confined to x < 80-90px!
# If fade_width is ~90px:
# - Dr. Amsel's face (which is at x >= 90) has 100% full opacity (alpha = 255)! ZERO cloud over face!
# - His eyes, nose, mouth, cheek, ear, and suspenders are 100% crisp and clear!
# - The left edge of the photo (x < 90) smoothly dissolves into #f7f7f5 with a soft cubic ease.
# - ZERO top fade: photo touches top edge naturally under navbar.

mask = Image.new("L", (target_w, target_h), 255)
m_pixels = mask.load()

fade_w = 95 # ONLY 95px on the far left edge of the photo!

for y in range(target_h):
    for x in range(target_w):
        if x < fade_w:
            t = x / float(fade_w)
            # Smoothstep curve: 3t^2 - 2t^3
            v = t * t * (3.0 - 2.0 * t)
            m_pixels[x, y] = int(255 * v)
        else:
            m_pixels[x, y] = 255

paste_x = CANVAS_W - target_w
paste_y = 0
canvas.paste(amsel_res, (paste_x, paste_y), mask)

output_path = "demo-expert/assets/amsel-option-real-blend.jpg"
canvas.save(output_path, quality=96)
print(f"Generated clean {output_path} successfully!")
