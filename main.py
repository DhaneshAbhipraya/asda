import numpy as np
import pygame as pg
from functools import wraps

def get_non_overlapping_pairs(lst):
    return [(lst[i], lst[j]) for i in range(len(lst)) for j in range(i + 1, len(lst))]


def memoize(expiration, exclude=0b0):
    def decorator(func):
        cache = {}
        func.__dict__['remem'] = lambda: cache.clear()
        call_count = 0

        @wraps(func)
        def wrapper(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count >= expiration and expiration > 0:
                cache.clear()
                call_count = 0
            key = (args, frozenset(kwargs.items()))
            if key in cache:
                return cache[key]
            result = func(*args, **kwargs)
            cache[key] = result
            return result

        return wrapper

    return decorator


def split_list(lst, n):
    return [lst[i:i+n] for i in range(0, len(lst), n)]


@memoize(10) # memoize
def load_image(filename, palette=None):
    print(f"loading image {filename}")
    if palette is None:
        palette = {}
    with open(filename, 'rb') as f:
        if f.read(3).decode() != 'ASD':
            # This is not a valid asset data file, so just return nothing
            return 1
        if f.read(1) != bytes([1]):
            # This is not an image file, so just return nothing
            return 2
        # Flags
        # GRAYSCALE, PALETTE, _, _, _, _, _, _ = reversed([True if int(i)==1 else False for i in bin(int(f.read(1)[0]))[2:].ljust(8, "0")])
        n = int(f.read(1)[0])
        GRAYSCALE = (n >> 0) % 2
        PALETTE = (n >> 1) % 2
        # Get width and height
        width, height = int.from_bytes(f.read(2), "little"), int.from_bytes(f.read(2), "little")
        collected_data = []
        table = f.read()
        colors = split_list(table, 1 if GRAYSCALE or PALETTE else 3)
        result = colors
        if PALETTE:
            result = []
            for i in colors:
                result.append(bytes(dict(palette).get(int.from_bytes(i)%max(dict(palette).keys()))))
        collected_data.extend(result)

        collected_data = collected_data[:width*height]
        collected_data = collected_data + [bytes([0,0,0])] * (width*height - len(collected_data))
        l = split_list([int(i.hex(), 16) for i in collected_data], width)
        image = np.array(l)
        conv = pg.surfarray.array3d(pg.surface.Surface((image.shape[1], image.shape[0])))
        if GRAYSCALE:
            conv[:,:,:] = np.array([image & 0xff]*3).transpose()
        else:
            conv[:,:,0] = (image.transpose() >> 16) & 0xff
            conv[:,:,1] = (image.transpose() >> 8) & 0xff
            conv[:,:,2] = image.transpose() & 0xff
        return conv
        

def load_palette(filename):
    print(f"loading palette {filename}")
    with open(filename, 'rb') as f:
        if f.read(3).decode() != 'ASD':
            # This is not a valid asset data file, so just return nothing
            return 1
        if f.read(1) != bytes([2]):
            # This is not a palette file, so just return nothing
            return 2
        colors = split_list(f.read(), 3)
        d = {}
        for i, v in enumerate(colors):
            d.update({i: v})
        
        class P:
            def __init__(self, org, cache={}):
                self.cache = cache
                self.org = org
            def __call__(self):
                return self.cache
            def reload(self):
                self.cache = load_palette(self.org).cache

        return P(filename, tuple(d.items()))


def main():
    pg.init()

    screen = pg.display.set_mode((800, 600))
    clock = pg.time.Clock()

    # palette = tuple({
    #     0:  (255, 255, 255), 1:  (255, 000, 000), 2:  (000, 255, 000), 3:  (000, 000, 255),
    #     4:  (255, 255, 000), 5:  (000, 255, 255), 6:  (255, 000, 255), 7:  (127, 000, 255),
    #     8:  (127, 127, 127), 9:  (127, 000, 000), 10: (000, 127, 000), 11: (000, 000, 127),
    #     12: (127, 127, 000), 13: (000, 127, 127), 14: (127, 000, 127), 15: (000, 000, 000),
    # }.items())
    palette = load_palette('assets/palettes/p1.asd')

    running = True
    while running:
        for e in pg.event.get():
            if e.type == pg.QUIT:
                running = False
            if e.type == pg.MOUSEBUTTONDOWN:
                palette.reload()
                load_image.remem()

        conv = load_image("assets/images/out.asd", palette())
        screen = pg.display.set_mode([max(100,min(2000, i)) for i in conv.shape[:2]])
        if isinstance(conv, np.ndarray):
            # print(image)
            
            # print(conv)
            conv = pg.surfarray.make_surface(conv)
            conv = pg.transform.scale(conv, (screen.get_width(), screen.get_height()))
            screen.blit(conv, (0,0), pg.Rect(0, 0, screen.get_width(), screen.get_height()))
        else:
            print("error " + str(conv))

        pg.display.flip()

        clock.tick(24)

if __name__ == "__main__":
    main()
    pg.quit()
    exit()