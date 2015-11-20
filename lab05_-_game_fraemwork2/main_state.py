import random
import json
import os
import random
import queue
import time
import math
from pico2d import *

import game_framework
import title_state



name = "MainState"

SKILL_MAXNUM = 4
RIGHT,LEFT,UP,DOWN,Z,X = range(6)
STATE_IDLE, STATE_MOVE, STATE_SKILL1, STATE_SKILL2,STATE_SKILL3 = range(SKILL_MAXNUM+1)
MON_STATE_IDLE,MON_STATE_MOVE,MON_STATE_ATTACK = range(3)
InputKey = False

boy = None
skill = None
grass = None
InputSys = None
monster = None

#사실 스킬아니고 캐릭터의 key 클래스
class Skill:
    def __init__(self):
        self.name = None
        self.number = None
        self.skillNum = None
        self.frames = None
        self.key = None
        self.size = 0
        self.height = 0;
        self.width = 0;
        def get_bb(self,x,y):
            return x - self.width/2, y - self.height/2,x+self.width/2,y+self.height/2

#맵
class Grass:
    def __init__(self):
        self.image = load_image('map.png')
    def draw(self):
        self.image.draw(400,300)
#몬스터
class Monster:
    def __init__(self):
        global boy
        self.image = load_image('mon_walk.png')
        self.image1 = load_image('mon_attack.png')
        self.frame = 0
        self.state = MON_STATE_IDLE
        self.x = 100
        self.dir = 0
        self.time = 0
    def draw(self):
        if self.state == MON_STATE_IDLE:
            self.image.clip_draw(self.frame*115,0,115,122,self.x, 90)
        elif self.state == MON_STATE_MOVE:
            self.image.clip_draw(self.frame*115,0,115,122,self.x, 90)
        elif self.state == MON_STATE_ATTACK:
            self.image1.clip_draw(self.frame*115,0,115,122,self.x, 90)
    def update(self):
        self.ChangeState()
        self.time = (self.time+1)%5
        if self.state == MON_STATE_IDLE:
            print("IDLE")
            if self.time == 0:
                self.dir = random.randint(-1,1)
            self.frame = (self.frame+1)%6
            self.x = min(750,self.x+3*self.dir)
            self.x = max(0,self.x+3*self.dir)
        elif self.state == MON_STATE_MOVE:
            print("MOVE")
            self.frame = (self.frame+1)%6
            self.x = min(750,self.x+3*self.dir)
            self.x = max(0,self.x+3*self.dir)
        elif self.state == MON_STATE_ATTACK:
            print("ATTACK")
            self.frame = (self.frame+1)%4
    def ChangeState(self):
        #print(math.sqrt((boy.x - self.x)*(boy.x - self.x)))
        if math.sqrt((boy.x - self.x)*(boy.x - self.x)) <= 50:
            self.state = MON_STATE_ATTACK
        elif math.sqrt((boy.x - self.x)*(boy.x - self.x)) <= 200:
            self.state = MON_STATE_MOVE
            if self.x < boy.x :
                self.dir = 1
            elif self.x > boy.x:
                self.dir = -1
            elif self.x == boy.x:
                self.dir = 0
        elif math.sqrt((boy.x - self.x)*(boy.x - self.x)) <= 300:
            self.state = MON_STATE_IDLE

        #elif self.state == MON_STATE_MOVE:
            #self.dir = 1

        #print(self.dir)
#플레이어
class Boy:
    def __init__(self):
        self.x, self.y = 300,90
        self.frame = random.randint(0,7)
        self.image = load_image('skill2_right.png')
        self.image1 = load_image('skill3_right.png')
        self.image2 = load_image('skill1_right.png')
        self.image3 = load_image('walk_right.png')
        #self.dir = 1
        self.KeyNum = 0
        self.State = STATE_IDLE
        self.accel = random.randint(3,7)
        self.width = 100
        self.height = 133
        self.hbWidth = 0
        self.hbHeight = 0
        self.hbPosX = 0
        self.hbPosY = 0

    def update(self):
        #self.ChangePos()
        if self.State == STATE_IDLE:
            self.frame = 0
        elif self.State == STATE_MOVE:
            self.x += 10
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
            #dir == right/left일때로 이미지 드로우 변경
            #self.image1.clip_draw(self.frame*320,0,320,218,self.x, self.y)
            self.image3.clip_draw(100,0,100,133,self.x, 90)
        elif self.State == STATE_MOVE:
            #self.image1.clip_draw(self.frame*320,0,320,218,self.x, self.y)
            self.image3.clip_draw(self.frame*100,0,100,133,self.x, 90)
        elif self.State == STATE_SKILL1:
            #print("state attack")
            self.image.clip_draw(self.frame*280,0,280,105,self.x, 90)
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
    #바운딩 박스 구하기
    def get_bb(self):
        return self.x - self.width/2, self.y - self.height/2, self.x+self.width/2,self.y +self.height/2
    #히트 박스 구하기
    def get_hb(self):
        return (self.x +self.hbPosX)- self.hbWidth/2, (self.y +self.hbPosY) - self.hbHeight/2, (self.x +self.hbPosX)+self.hbWidth/2,(self.y +self.hbPosY) +self.hbHeight/2
    def draw_bb(self):
        draw_rectangle(*self.get_bb())
    def draw_hb(self):
        draw_rectangle(*self.get_hb())

#캐릭터에 관한 모든 키입력을 처리하는 클래스
class InputSystem:
    def __init__(self):
        #self.t1,self.t2 = 0,0
        global boy
        global skill
        self.InputTime = 0
        self.InTime = False
        self.KeyBuffer = list()
        self.InitSkill()
        self.SkillTime = time.time()-10

    #원래는 클래스 생성자에서 하면됩니다만 생성자를 여러개 만들기 귀찮아서 그냥 이렇게 썼습니다 죄송합니다
    def InitSkill(self):
        for i in range(SKILL_MAXNUM):
            #skillname = state_skill 즉 스테이트가 된다
            skill[i].name = i+1
            skill[i].skillNum = 0
        skill[0].frames = 8
        skill[0].key = [RIGHT]
        skill[0].size = 1
        skill[1].frames = 10
        skill[1].key = [RIGHT, RIGHT, X]
        skill[1].size = 3
        skill[2].frames = 8
        skill[2].key = [RIGHT, DOWN, RIGHT]
        skill[2].size = 3
        skill[3].frames = 16
        skill[3].key = [DOWN, RIGHT,Z]
        skill[3].size = 3

#키 버퍼에 들어가는 시간 체크
    def CheckTime(self):
        if self.InputTime + 0.2 <= time.time() :
            self.InTime = False
        else:
            self.InTime = True
#키 버퍼에 들어간 키를 커맨드 키와 대조, 만약 같다면 스테이트를 바꿔줍니다
    def CheckSkill(self):
        #self.size = self.KeyBuffer.qsize()
        if len(self.KeyBuffer) != 0:
            self.it = iter(self.KeyBuffer)
            for i in range(SKILL_MAXNUM):
                for j in range(len(self.KeyBuffer)):
                    if len(self.KeyBuffer) == skill[i].size:
                        if next(self.it) == skill[i].key[j]:
                            print("correct")
                            #print(skill[i].key[j])
                            skill[i].skillNum += 1
                            #print(skill[i].skillNum)
                self.it = iter(self.KeyBuffer)
            for i in range(SKILL_MAXNUM):
                if(skill[i].size == skill[i].skillNum):
                    print("all correct")
                    self.SkillTime = time.time()
                    #print(self.SkillTime)
                    boy.frame = 0
                    boy.State = skill[i].name

            self.ClearBuffer()

    def SetHitbox(self):
        if self.SkillTime + 0.2 <= time.time() and self.SkillTime +0.5 >= time.time():
            boy.hbPosX = 100
            boy.hbPosY= 0
            boy.hbHeight = 100
            boy.hbWidth = 100
        else:
            boy.hbPosX = 2000
            boy.hbPosY = 2000
            boy.hbHeight = 1000
            boy.hbWidth = 1000

#버퍼 초기화
    def ClearBuffer(self):
        for i in range(SKILL_MAXNUM):
            skill[i].skillNum = 0
        self.KeyBuffer.clear()
        #self.SkillTime = 0



def enter():
    global  boy, grass,skill,InputSys,monster
    skill = [Skill() for i in range(SKILL_MAXNUM)]
    boy = Boy()
    grass = Grass()
    InputSys = InputSystem()
    monster = Monster()



def exit():
    global boy, grass,skill,InputSys,monster
    del(boy)
    del(grass)
    for i in skill:
        del(i)
    del(InputSys)
    del(monster)


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
            print("down")
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
            elif event.key == SDLK_z:
                InputSys.key = Z
                if InputSys.InputTime:
                    print("z")
                    InputSys.KeyBuffer.append(Z)
            elif event.key == SDLK_x:
                InputSys.key = X
                if InputSys.InputTime:
                    print("x")
                    InputSys.KeyBuffer.append(X)
        elif event.type == SDL_KEYUP:
            print("up")
            if event.key == SDLK_RIGHT:
                if boy.State == STATE_MOVE:
                    boy.State = STATE_IDLE
            elif event.key == SDLK_LEFT:
                if boy.State == STATE_MOVE:
                    boy.State = STATE_IDLE
            """elif event.key == SDLK_UP:
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
    InputSys.SetHitbox()
    monster.update()

def draw():
    clear_canvas()
    grass.draw()
    boy.draw()
    boy.draw_bb()
    boy.draw_hb()
    monster.draw()
    update_canvas()
    delay(0.07)

