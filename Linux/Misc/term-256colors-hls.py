import colorsys


def hsv_8bit(h, s=1.0, l=.3):
    rgb = colorsys.hls_to_rgb(h, l, s)
    r, g, b = map(lambda x: int(x * 5), rgb)
    return 16 + int(round(r * 36 + g * 6 + b))


def make_palette(colors, min_hue=0, max_hue=360):
    step = int((max_hue - min_hue) / colors)
    for hue in range(min_hue, max_hue, step):
        yield hsv_8bit(hue / 360)


min_hue = 0
max_hue = 260
colors = 11


palette = list(make_palette(9 * 6, min_hue=260, max_hue=0))
print(palette)
for idx, c8b in enumerate(palette):
    print('\x1b[48;5;{c8b}m   \x1b[0m {idx} [{c8b}]'.format(idx=idx, c8b=c8b))
