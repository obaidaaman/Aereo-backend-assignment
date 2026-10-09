from PIL import Image, ImageDraw, ImageFont
import math

WIDTH, HEIGHT = 3508, 2480
BG = (250, 248, 242)
NAVY = (25, 42, 70)
GOLD = (190, 150, 65)
DARK = (45, 45, 45)
MUTED = (105, 105, 105)

FONT_REGULAR = "Roboto-Regular.ttf"
FONT_BOLD = "Roboto-Bold.ttf"
FONT_SANS = "Roboto-Regular.ttf"
FONT_SANS_BOLD = "Roboto-Bold.ttf"

def F(path, size):
    return ImageFont.truetype(path, size)

def center(draw, xy, text, font, fill):
    draw.text(xy, text, font=font, fill=fill, anchor="mm")

def corner(draw, x, y, sx, sy):
    draw.line((x, y, x + sx, y), fill=GOLD, width=5)
    draw.line((x, y, x, y + sy), fill=GOLD, width=5)

def draw_seal(draw, cx, cy, r):
    draw.ellipse((cx-r, cy-r, cx+r, cy+r), outline=GOLD, width=8)
    draw.ellipse((cx-r+20, cy-r+20, cx+r-20, cy+r-20), outline=GOLD, width=3)

    points = []
    for i in range(16):
        angle = math.radians(i * 22.5 - 90)
        radius = r * (0.62 if i % 2 == 0 else 0.28)
        points.append((cx + radius * math.cos(angle),
                       cy + radius * math.sin(angle)))
    draw.polygon(points, outline=GOLD)

    center(draw, (cx, cy-8), "VERIFIED", F(FONT_SANS_BOLD, 34), NAVY)
    center(draw, (cx, cy+35), "CERTIFICATE", F(FONT_SANS, 24), MUTED)

def generate_certificate(
    name="Aman Obaid",
    achievement="Python Backend Development",
    date="09 October 2026",
    organization="Aereo Private Limited",
    certificate_title="CERTIFICATE OF COMPLETION",
    certificate_id="CERT-2026-0001",
    output_path="certificate.png",
):
    img = Image.new("RGB", (WIDTH, HEIGHT), BG)

    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    cx, cy = WIDTH // 2, HEIGHT // 2
    od.ellipse((cx-430, cy-430, cx+430, cy+430),
               outline=(190, 150, 65, 20), width=18)
    od.ellipse((cx-360, cy-360, cx+360, cy+360),
               outline=(25, 42, 70, 12), width=10)
    img = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")
    draw = ImageDraw.Draw(img)

    margin = 95

    draw.rectangle((margin, margin, WIDTH-margin, HEIGHT-margin),
                   outline=NAVY, width=12)
    draw.rectangle((margin+32, margin+32, WIDTH-margin-32, HEIGHT-margin-32),
                   outline=GOLD, width=5)

    corner(draw, margin+55, margin+55, 150, 150)
    corner(draw, WIDTH-margin-55, margin+55, -150, 150)
    corner(draw, margin+55, HEIGHT-margin-55, 150, -150)
    corner(draw, WIDTH-margin-55, HEIGHT-margin-55, -150, -150)

    center(draw, (WIDTH//2, 370), organization,
           F(FONT_SANS_BOLD, 38), NAVY)
    center(draw, (WIDTH//2, 500), certificate_title,
           F(FONT_SANS_BOLD, 110), NAVY)

    draw.line((WIDTH//2-260, 625, WIDTH//2+260, 625),
              fill=GOLD, width=5)
    draw.ellipse((WIDTH//2-12, 613, WIDTH//2+12, 637), fill=GOLD)

    center(draw, (WIDTH//2, 750),
           "This certificate is proudly presented to",
           F(FONT_SANS, 42), MUTED)

    name_font = F(FONT_BOLD, 150)
    center(draw, (WIDTH//2, 1000), name, name_font, NAVY)

    bbox = draw.textbbox((0, 0), name, font=name_font)
    name_width = bbox[2] - bbox[0]
    underline = min(name_width + 140, 1500)
    draw.line((WIDTH//2-underline//2, 1115,
               WIDTH//2+underline//2, 1115),
              fill=GOLD, width=5)

    center(draw, (WIDTH//2, 1280),
           f"for successfully completing {achievement}",
           F(FONT_REGULAR, 58), DARK)
    center(draw, (WIDTH//2, 1400), f"on {date}",
           F(FONT_SANS, 42), MUTED)

    footer_y = 1900

    draw.line((450, footer_y, 1050, footer_y), fill=NAVY, width=3)
    center(draw, (750, footer_y+55), "Authorized Signatory",
           F(FONT_SANS, 32), DARK)

    draw.line((2458, footer_y, 3058, footer_y), fill=NAVY, width=3)
    center(draw, (2758, footer_y+55), "Program Director",
           F(FONT_SANS, 32), DARK)

    draw_seal(draw, WIDTH//2, footer_y-10, 135)

    center(draw, (WIDTH//2, 2225),
           f"Certificate ID: {certificate_id}",
           F(FONT_SANS_BOLD, 27), MUTED)

    img.save(output_path, quality=95)
    return output_path
