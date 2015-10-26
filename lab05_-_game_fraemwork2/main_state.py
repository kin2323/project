import random
import json
import os
import random
import queue
import time
from pico2d import *

import game_framework
import title_state



name = "MainState"

SKILL_MAXNUM = 4
RIGHT,LEFT,UP,DOWN = range(4)
STATE_IDLE, STATE_MOVE, STATE_SKILL1, STATE_SKILL2,STATE_SKILL3 = range(SKILL_MAXNUM+1)
InputKey = False

boy = None
skill = None
grass = None
InputSys = None

class Skill:
    def __init__(self):
        self.name = None
        self.number = None
        self.skillNum = None
        self.frames = None
        self.key = None

class Grass:
    def __init__(self):
        self.image = load_image('map.png')
    def draw(self):
        self.image.draw(400,300)
class Boy:
    def __init__(self):
        self.x, self.y = 300,90
        self.frame = random.randint(0,7)
        self.image = load_image('평타.jpg')
        self.image1 = load_image('2.png')
        self.image2 = load_image('1.png')
        self.image3 = load_image('0.png')
        #self.dir = 1
        self.KeyNum = 0
        self.State = STATE_IDLE
        self.accel = random.randint(3,7)

    def update(self):
        #self.ChangePos()
        if self.State == STATE_IDLE:
            self.frame = 0
        elif self.State == STATE_MOVE:
            self.x += 5
            self.frame = (self.frame+1)%8
        elif self.State == STATE_SKILL1:
            self.frame = (self.frame+1)%10
            if self.frame == 0:
                self.State = STATE_IDLE
        elif self.State == STATE_SKILL2:
            self.frame = (self.frame+1)%8
            if self.frame == 0:
                self.State = STATE_IDLE
        elif self.State == STATE_SKILL3:
            self.frame = (self.frame+1)%16
            if self.frame == 0:
                self.State = STATE_IDLE
    def draw(self):
        if self.State == STATE_IDLE:
            #self.image1.clip_draw(self.frame*320,0,320,218,self.x, self.y)
            self.image3.clip_draw(100,0,100,133,self.x, 90)
        elif self.State == STATE_MOVE:
            #self.image1.clip_draw(self.frame*320,0,320,218,self.x, self.y)
            self.image3.clip_draw(self.frame*100,0,100,133,self.x, 90)
        elif self.State == STATE_SKILL1:
            #print("state attack")
            self.image.clip_draw(self.frame*180,0,180,113,self.x, 90)
        elif self.State == STATE_SKILL2:
            self.image2.clip_draw(self.frame*300,0,300,204,self.x, 120)
        elif self.State == STATE_SKILL3:
            self.image1.clip_draw(self.frame*320,0,320,218,self.x, 120)
    def ChangePos(self):
        if self.State == STATE_IDLE:
            self.y = 90
        elif self.State == STATE_SKILL1:
            self.y = 90
        elif self.State == STATE_SKILL2:
            self.y = 120
        elif self.State == STATE_SKILL3:
            self.y = 120

class InputSystem:
    def __init__(self):
        #self.t1,self.t2 = 0,0
        global boy
        global skill
        self.key = -1
        self.InputTime = 0
        self.InTime = False
        self.skillNum = 0
        #self.KeyBuffer = queue.Queue()
        self.KeyBuffer = list()
        self.InitSkill()
    def InitSkill(self):
        for i in range(SKILL_MAXNUM):
            #skillname = state_skill 즉 스테이트가 된다
            skill[i].name = i+1
            skill[i].skillNum = 0
        skill[0].frames = 8
        skill[0].key = [RIGHT,RIGHT,RIGHT]
        skill[1].frames = 10
        skill[1].key = [RIGHT, RIGHT, UP]
        skill[2].frames = 8
        skill[2].key = [RIGHT, DOWN, RIGHT]
        skill[3].frames = 16
        skill[3].key = [LEFT, DOWN, RIGHT]

    def CheckTime(self):
        if self.InputTime + 0.2 <= time.time() :
            self.InTime = False
        else:
            self.InTime = True
    def CheckSkill(self):
        #self.size = self.KeyBuffer.qsize()
        self.size = 3
        if len(self.KeyBuffer) != 0:
            self.it = iter(self.KeyBuffer)
            for i in range(SKILL_MAXNUM):
                for j in range(len(self.KeyBuffer)):
                    if next(self.it) == skill[i].key[j]:
                        print("correct")
                        #print(skill[i].key[j])
                        skill[i].skillNum += 1
                        #print(skill[i].skillNum)
                self.it = iter(self.KeyBuffer)
            for i in range(SKILL_MAXNUM):
                if(self.size == skill[i].skillNum):
                    print("all correct")
                    boy.frame = 0
                    boy.State = skill[i].name
            self.ClearBuffer()
    def ClearBuffer(self):
        #print("clear")
        self.KeyNum = 0
        for i in range(SKILL_MAXNUM):
            skill[i].skillNum = 0
        self.KeyBuffer.clear()



def enter():
    global  boy, grass,skill,InputSys
    skill = [Skill() for i in range(SKILL_MAXNUM)]
    boy = Boy()
    grass = Grass()
    InputSys = InputSystem()


def exit():
    global boy, grass,skill,InputSys
    del(boy)
    del(grass)
    for i in skill:
        del(i)
    del(InputSys)


def pause():
    pass


def resume():
    pass


def handle_events():
    global running
    global InputSys
    global boy
    events = get_events()
    for event in events:
        if event.type == SDL_QUIT:
             game_framework.change_state(title_state)
        elif event.type == SDL_KEYDOWN:
            InputSys.InputTime = time.time()
            if event.key == SDLK_ESCAPE:
                running = False
            elif event.key == SDLK_RIGHT:
                InputSys.key = RIGHT
                if InputSys.InputTime:
                    print("right")
                    InputSys.KeyBuffer.append(RIGHT)
            elif event.key == SDLK_LEFT:
                InputSys.key = LEFT
                if InputSys.InputTime:
                    print("left")
                    InputSys.KeyBuffer.append(LEFT)
            elif event.key == SDLK_UP:
                InputSys.key = UP
                if InputSys.InputTime:
                    print("up")
                    InputSys.KeyBuffer.append(UP)
            elif event.key == SDLK_DOWN:
                InputSys.key = DOWN
                if InputSys.InputTime:
                    print("down")
                    InputSys.KeyBuffer.append(DOWN)
                #keyup일 때, checktime이 트루일때 큐에 넣어야 될듯
        """elif event.type == SDL_KEYUP:
            if event.key == SDLK_RIGHT:
                if InputSys.CheckTime():0
                    print(InputSys.key)
            elif event.key == SDLK_LEFT:
                if InputSys.CheckTime():
                    print(InputSys.key)
            elif event.key == SDLK_UP:
                if InputSys.CheckTime():
                    print(InputSys.key)
            elif event.key == SDLK_DOWN:
                if InputSys.CheckTime():
                    print(InputSys.key)"""





def update():
    boy.update()
    InputSys.CheckTime()
    if InputSys.InTime == False:
        InputSys.CheckSkill()

def draw():
    clear_canvas()
    grass.draw()
    boy.draw()
    update_canvas()
    delay(0.05)





