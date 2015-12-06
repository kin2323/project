from pico2d import *

class UI:
    def __init__(self):
        self.font = load_font('font5.ttf',30)
        self.score = 0
        self.time = 0
    """def update(self,frame_time):
        self.time += frame_time"""

    def update(self):
        self.time = get_time()
    def draw(self,x,y,damage):
        #print("시간 %d :, 점수 : %d" % (self.score,self.time))
        self.font.draw(x,y," %d" % (damage))

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

