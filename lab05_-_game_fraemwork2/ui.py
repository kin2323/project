from pico2d import *

class UI:
    def __init__(self):
        self.font = load_font('font5.ttf',30)
        self.score = 0
        self.time = 0
        self.x, self.y = 0,0
    """def update(self,frame_time):
        self.time += frame_time"""

    def update(self):
        self.time = get_time()
        self.y += 5
    def draw(self,x,y,damage):
        self.x = x
        self.y = y
        self.font.draw(self.x, self.y," %d" % (damage))

def test_ui():
    open_canvas()
    ui = UI()
    ui.draw()
    ui.update()
    update_canvas()
    delay(2.0)
    close_canvas()


if __name__ == "__main__":
    test_ui()

