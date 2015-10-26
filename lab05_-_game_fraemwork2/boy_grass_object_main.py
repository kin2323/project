from pico2d import *


class Grass:
    def __init__(self):
        self.image = load_image('grass.png')

    def draw(self):
        self.image.draw(400, 30)


class Boy:
    def __init__(self):
        self.x, self.y = 0, 90
        self.frame = 0
        self.image = load_image('run_animation.png')
        self.dir = 1

    def update(self):
        self.frame = (self.frame + 1) % 8
        self.x += self.dir
        if self.x >= 800:
            self.dir = -1
        elif self.x <= 0:
            self.dir = 1

    def draw(self):
        self.image.clip_draw(self.frame * 100, 0, 100, 100, self.x, self.y)


def handle_events():
    global running
    events = get_events()
    for event in events:
        if event.type == SDL_QUIT:
            running = False
        elif event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
            running = False


# fill here for boy, grass
running = True
boy = None
grass = None

def enter():
    global boy, grass
    open_canvas()
    boy = Boy()
    grass = Grass()


def exit():
    global boy, grass
    del(boy)
    del(grass)
    close_canvas()


def update():
    boy.update()


def draw():
    clear_canvas()
    grass.draw()
    boy.draw()
    update_canvas()


def main():
    enter()
    while running:
        handle_events()
        update()
        draw()
    exit()

if __name__ == '__main__':
    main()

# fill here


