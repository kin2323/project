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
from ui import UI



name = "MainState"

SKILL_MAXNUM = 6
MON_MAXNUM = 1
RIGHT,LEFT,UP,DOWN,Z,X,EMPTY = range(7)
STATE_IDLE, STATE_MOVE, STATE_SKILL1, STATE_SKILL2,STATE_SKILL3,STATE_ATTACKED = range(6)
MON_STATE_IDLE,MON_STATE_MOVE,MON_STATE_ATTACK,MON_STATE_ATTACKED, MON_STATE_DIE = range(5)
InputKey = False

boy = None
skill = None
grass = None
InputSys = None
monster = None
ui = None

def collision(a,b):
    left_a, bottom_a, right_a, top_a = a.get_hb()
    left_b, bottom_b, right_b, top_b = b.get_bb()

    """if (right_a < left_b) or (left_a > right_b)  or (bottom_a < top_b) or (top_a > bottom_b):
        return False
    else:
        return True"""

    if left_a > right_b: return False
    if right_a < left_b : return False
    if top_a < bottom_b : return False
    if bottom_a > top_b : return  False

    return  True

#사실 스킬아니고 캐릭터의 key 클래스
class Skill:
    def __init__(self):
        self.name = None
        self.number = None
        self.skillNum = None
        self.frames = None
        self.key = None
        self.size = 0
        self.height = 0
        self.width = 0
        self.time = [-1,-1]
        self.tick = [-1,-1]
        self.hitCount = 1
        self.hp = 100

        self.hbPosX = 50
        self.hbPosY= 0
        self.hbHeight = 100
        self.hbWidth = 200
        self.move = 0
        #def get_bb(self,x,y):
            #return x - self.width/2, y - self.height/2,x+self.width/2,y+self.height/2

#맵
class Grass:
    def __init__(self):
        self.image = load_image('map.png')
        self.bgm = load_music('bgm.mp3')
        self.bgm.set_volume(64)
        #self.bgm.repeat_play()

    def draw(self):
        self.image.draw(400,300)
#몬스터
class Monster:
    image = None
    def __init__(self):
        global InputSys
        if self.image == None:
            self.image = [
                load_image('mon1_walk_right.png'),
                load_image('mon1_attack_right.png'),
                load_image('mon1_walk_left.png'),
                load_image('mon1_attack_left.png'),
                load_image('mon1_getHit_right.png'),
                load_image('mon1_getHit_left.png')
            ]

        self.frame = 0
        self.state = MON_STATE_IDLE
        self.x = random.randint(100,700)
        self.y = 90
        self.dir = 0
        self.time = 0
        self.width = 124
        self.height = 108
        self.damage = 0
        self.hp = 10

        self.attackTime = -1
        self.hbWidth = 0
        self.hbHeight = 0
        self.hbPosX = 2000
        self.hbPosY = 2000

        self.jumpHeight=10;
        self.gravity = 200;

        self.skillNum = 0

        self.monBgm = load_music('get_hit.wav')
        self.monBgm.set_volume(32)


    def draw(self):
        if self.state == MON_STATE_IDLE or self.state == MON_STATE_MOVE :
            if self.dir == 1:
                self.image[0].clip_draw(self.frame*124,0,124,108,self.x, self.y)
            else:
                self.image[2].clip_draw(self.frame*124,0,124,108,self.x, self.y)
        elif self.state == MON_STATE_ATTACK:
            if self.dir == 1:
                self.image[1].clip_draw(self.frame*124,0,124,108,self.x, self.y)
            else :
                self.image[3] .clip_draw(self.frame*124,0,124,108,self.x, self.y)
        elif self.state == MON_STATE_ATTACKED:
            self.damageDraw()
            if self.dir == 1:
                self.image[4].clip_draw(self.frame*124,0,124,108,self.x, self.y)
            else :
                self.image[5] .clip_draw(self.frame*124,0,124,108,self.x, self.y)
        elif self.state == MON_STATE_DIE:
            if self.dir == 1:
                self.image[4].clip_draw(self.frame*124,0,124,108,self.x, self.y)
            else :
                self.image[5] .clip_draw(self.frame*124,0,124,108,self.x, self.y)

    def damageDraw(self):
        ui.draw(self.x ,self.y + 100, self.damage)
        ui.update()
    def update(self):
        self.ChangeState()
        self.set_hb()
        self.time = (self.time+1)%15
        if self.state == MON_STATE_IDLE:
            #print("IDLE")
            if self.time == 0:
                self.dir = random.randint(-1,1)
            self.frame = (self.frame+1)%6
            self.x = min(750,self.x+3*self.dir)
            self.x = max(0,self.x+3*self.dir)
        elif self.state == MON_STATE_MOVE:
            #print("MOVE")
            self.frame = (self.frame+1)%6
            self.x = min(750,self.x+3*self.dir)
            self.x = max(0,self.x+3*self.dir)
        elif self.state == MON_STATE_ATTACK:
            #print("ATTACK")
            if self.frame == 0:
                self.attackTime = time.time()
            self.frame = (self.frame+1)%4
            #self.y += (self.gravity / self.jumpHeight)
            #self.gravity -= 20
        elif self.state == MON_STATE_ATTACKED:
            #print("attacked22")
            #print(InputSys.skillNumber)
            if self.state != MON_STATE_DIE:
                if self.skillNum ==  STATE_SKILL1 or self.skillNum ==  STATE_SKILL3 :
                    self.x -= 3*self.dir
                    print("get attacked")
                    print(self.x)
                    if self.y > 90:
                        self.y += (self.gravity / self.jumpHeight)
                        self.gravity -= 20
                        if self.gravity / self.jumpHeight >0:
                            self.frame = 1
                        else:
                            if self.frame != 4 :
                             self.frame = (self.frame+1)%5
                    else:
                        self.y = 90
                        self.gravity = 200
                        self.frame += 1
                        self.state = MON_STATE_IDLE
                elif self.skillNum ==  STATE_SKILL2:
                    self.y += (self.gravity / self.jumpHeight)
                    if self.y > 90:
                        self.gravity -= 20
                        if self.gravity / self.jumpHeight >0:
                            self.frame = 1
                        else:
                            if self.frame != 4 :
                             self.frame = (self.frame+1)%5
                    else:
                        self.y = 90
                        self.gravity = 200
                        self.frame += 1
                        self.state = MON_STATE_IDLE

        elif self.state == MON_STATE_DIE:
            self.y += (self.gravity / self.jumpHeight)
            if self.y > 90:
                self.gravity -= 20
                if self.gravity / self.jumpHeight >0:
                    self.frame = 1
                else:
                    if self.frame != 4 :
                     self.frame = (self.frame+1)%5
            else:
                self.y = 90
                self.frame = 5
                del(self)

    def ChangeState(self):
        #print(math.sqrt((boy.x - self.x)*(boy.x - self.x)))
        if self.state != MON_STATE_DIE:
            if self.state != MON_STATE_ATTACKED:
                if math.sqrt((boy.x - self.x)*(boy.x - self.x)) <= 30:
                    if self.time == 0:
                        self.state = MON_STATE_ATTACK
                        #print("attack",self.time)
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

    def getHit(self):
        if self.state != MON_STATE_DIE:
            if self.hp <= 0:
                self.state = MON_STATE_DIE
            else:
                self.state = MON_STATE_ATTACKED
            self.frame = 0
            if self.skillNum != STATE_SKILL1:
                self.gravity = 200
            self.monBgm.play()
            self.skillNum = InputSys.skillNumber
            #print(self.skillNum)
            self.damage = random.randint(0,10);
            self.hp -= self.damage

    def get_bb(self):
        return self.x - self.width/3, self.y - self.height/3, self.x+self.width/3,self.y +self.height/3
    def get_hb(self):
        return (self.x +self.hbPosX)- self.hbWidth/2, (self.y +self.hbPosY) - self.hbHeight/2, (self.x +self.hbPosX)+self.hbWidth/2,(self.y +self.hbPosY) +self.hbHeight/2
    def set_hb(self):
        if self.state != MON_STATE_DIE:
            if self.attackTime <= time.time() and self.attackTime+ 0.1 >= time.time():
                self.hbWidth = 50
                self.hbHeight = 50
                self.hbPosX = 50*self.dir
                self.hbPosY = 0
            else:
                self.hbWidth = 0
                self.hbHeight = 0
                self.hbPosX = 2000
                self.hbPosY = 2000
    def draw_bb(self):
        draw_rectangle(*self.get_bb())
    def draw_hb(self):
        draw_rectangle(*self.get_hb())
#플레이어
class Boy:
    def __init__(self):
        global skill
        self.x, self.y = 300,90
        self.frame = random.randint(0,7)
        self.image = load_image('skill2_right.png')
        self.image1 = load_image('skill3_right.png')
        self.image2 = load_image('skill1_right.png')
        self.image3 = load_image('walk_right.png')

        self.image4 = load_image('skill2_left.png')
        self.image5 = load_image('skill3_left.png')
        self.image6 = load_image('skill1_left.png')
        self.image7 = load_image('walk_left.png')

        self.image8 = load_image('effect.png')
        self.image9 = load_image('effect1.jpg')
        self.image10 = load_image('effect2.jpg')

        self.image11 = load_image('attacked_right.png')
        self.image12 = load_image('attacked_left.png')

        self.image13 = load_image('effect3_right.png')
        self.image14 = load_image('effect3_left.png')

        self.image15 = load_image('hpbar.jpg')
        self.image16 = load_image('hpbar_frame.jpg')

        self.dir = 1
        self.KeyNum = 0
        self.State = STATE_IDLE
        self.accel = random.randint(3,7)
        self.width = 100
        self.height = 133
        self.hbWidth = 0
        self.hbHeight = 0
        self.hbPosX = 0
        self.hbPosY = 0
        self.hp = 800
        self.inSkill = True
        self.skImage = None

    def update(self):
        #self.ChangePos()
        if self.State == STATE_IDLE:
            self.frame = 0
        elif self.State == STATE_MOVE:
            self.x = min(750,self.x+8*self.dir)
            self.x = max(0,self.x+8*self.dir)
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
        elif self.State == STATE_ATTACKED:
            self.frame = 0
            self.State = STATE_IDLE
            self.x = min(750,self.x-8*self.dir)
            self.x = max(0,self.x-8*self.dir)
    def draw(self):
        self.image15.clip_draw(0,0,self.hp,46,self.hp/2,574)
        self.image16.clip_draw(0,0,800,50,400,574)
        if self.State == STATE_IDLE:
            #dir == right/left일때로 이미지 드로우 변경
            if self.dir == 1:
                self.image3.clip_draw(100,0,100,133,self.x, 90)
                if boy.inSkill:
                    self.skImage.clip_draw(0,0,790,392,((self.x-100) +self.hbPosX)- self.hbWidth/2, 90)
            elif self.dir == -1:
                self.image7.clip_draw(100,0,100,133,self.x, 90)
                if boy.inSkill:
                    self.skImage.clip_draw(0,0,790,392,((self.x+100)+self.hbPosX)- self.hbWidth/2, 90)
        elif self.State == STATE_MOVE:
            #self.image1.clip_draw(self.frame*320,0,320,218,self.x, self.y)
            if self.dir == 1:
                self.image3.clip_draw(self.frame*100,0,100,133,self.x, 90)
                if boy.inSkill:
                    self.skImage.clip_draw(0,0,790,392,((self.x-100) +self.hbPosX)- self.hbWidth/2, 90)
            elif self.dir == -1:
                self.image7.clip_draw(self.frame*100,0,100,133,self.x, 90)
                if boy.inSkill:
                    self.skImage.clip_draw(0,0,790,392,((self.x+100) +self.hbPosX)- self.hbWidth/2, 90)
        elif self.State == STATE_SKILL1:
            #print("state attack")
            if self.dir == 1:
                self.image.clip_draw(self.frame*280,0,280,105,self.x, 90)
                self.skImage = self.image13
                self.image13.clip_draw(0,0,790,392,((self.x-100) +self.hbPosX)- self.hbWidth/2, 90)
            elif self.dir == -1:
                self.image4.clip_draw(self.frame*280,0,280,105,self.x, 90)
                self.skImage = self.image14
                self.image14.clip_draw(0,0,790,392,((self.x+100) +self.hbPosX)- self.hbWidth/2, 90)
            self.image10.clip_draw(self.frame*140,0,140,80,self.x, 80)
        elif self.State == STATE_SKILL2:
            if self.dir == 1:
                self.image2.clip_draw(self.frame*300,0,300,204,self.x, 120)
            elif self.dir == -1:
                self.image6.clip_draw(self.frame*300,0,300,204,self.x, 120)
            self.image8.clip_draw(self.frame*118,0,118,146,self.x-15, 90)
        elif self.State == STATE_SKILL3:
            if self.dir == 1:
                self.image1.clip_draw(self.frame*320,0,320,218,self.x, 150)
            elif self.dir == -1:
                self.image5.clip_draw(self.frame*320,0,320,218,self.x, 150)
            self.image9.clip_draw(self.frame*128,0,128,128,self.x, 80)
        elif self.State == STATE_ATTACKED:
            if self.dir == 1:
                self.image11.clip_draw(self.frame*100,0,100,133,self.x, 90)
            elif self.dir == -1:
                self.image12.clip_draw(self.frame*100,0,100,133,self.x, 90)
    def ChangePos(self):
        if self.State == STATE_IDLE:
            self.y = 90
        elif self.State == STATE_SKILL1:
            self.y = 90
        elif self.State == STATE_SKILL2:
            self.y = 120
        elif self.State == STATE_SKILL3:
            self.y = 120
    def getHit(self):
        self.State = STATE_ATTACKED
        if self.hp > 0:
            self.hp -= 100
        #else:
            #game_framework.change_state(title_state)
    #바운딩 박스 구하기
    def get_bb(self):
        return self.x - self.width/2, self.y - self.height/2, self.x+self.width/2,self.y +self.height/2
    #히트 박스 구하기
    def get_hb(self):
        #return (self.x +self.hbPosX)- self.hbWidth/2, (self.y +self.hbPosY) - self.hbHeight/2, (self.x +self.hbPosX)+self.hbWidth/2,(self.y +self.hbPosY) +self.hbHeight/2
        if self.dir == 1:
            return (self.x +self.hbPosX)- self.hbWidth/2, (self.y +self.hbPosY) - self.hbHeight/2, (self.x +self.hbPosX)+self.hbWidth/2,(self.y +self.hbPosY) +self.hbHeight/2
        else:
            return (self.x +self.hbPosX)+ self.hbWidth/2, (self.y +self.hbPosY) + self.hbHeight/2, (self.x +self.hbPosX)-self.hbWidth/2,(self.y +self.hbPosY) -self.hbHeight/2
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
        self.skillNumber = -1

    #원래는 클래스 생성자에서 하면됩니다만 생성자를 여러개 만들기 귀찮아서 그냥 이렇게 썼습니다 죄송합니다
    def InitSkill(self):
        for i in range(SKILL_MAXNUM):
            #skillname = state_skill 즉 스테이트가 된다
            skill[i].skillNum = 0
        skill[0].frames = 8
        skill[0].key = [RIGHT]
        skill[0].size = 1
        skill[0].name = STATE_MOVE
        skill[1].frames = 8
        skill[1].key = [LEFT]
        skill[1].size = 1
        skill[1].name = STATE_MOVE
        skill[2].frames = 10
        skill[2].key = [UP, UP, X]
        skill[2].size = 3
        skill[2].time[0] = 0.2
        skill[2].tick[0] = 3.0
        skill[2].move = 2
        skill[2].name = STATE_SKILL1
        skill[3].frames = 8
        skill[3].key = [DOWN,Z]
        skill[3].size = 2
        skill[3].time[0] = 0.1
        skill[3].tick[0] = 0.1
        skill[3].name = STATE_SKILL2
        skill[4].frames = 16
        skill[4].key = [DOWN, UP,Z]
        skill[4].size = 3
        skill[4].name = STATE_SKILL3
        skill[4].hitCount = 2
        skill[4].time[0] = 0.2
        skill[4].tick[0] = 0.2
        skill[4].time[1] = 0.8
        skill[4].tick[1] = 0.2
        skill[5].frames = 0
        skill[5].key = [EMPTY]
        skill[5].size = 1
        skill[5].name = STATE_IDLE

#키 버퍼에 들어가는 시간 체크
    def CheckTime(self):
        if self.InputTime + 0.2 <= time.time() :
            self.InTime = False
        else:
            self.InTime = True
#키 버퍼에 들어간 키를 커맨드 키와 대조, 만약 같다면 스테이트를 바꿔줍니다
    def CheckSkill(self):
        if len(self.KeyBuffer) != 0:
            self.it = iter(self.KeyBuffer)
            for i in range(SKILL_MAXNUM):
                for j in range(len(self.KeyBuffer)):
                    if len(self.KeyBuffer) == skill[i].size:
                        if next(self.it) == skill[i].key[j]:
                            #print("correct")
                            #print(skill[i].key[j])
                            skill[i].skillNum += 1
                            #print(skill[i].skillNum)
                self.it = iter(self.KeyBuffer)
            for i in range(SKILL_MAXNUM):
                if(skill[i].size == skill[i].skillNum):
                    #print("all correct")
                    #print(self.SkillTime)
                    boy.frame = 0
                    if boy.State == STATE_IDLE or boy.State == STATE_MOVE:
                        boy.State = skill[i].name
                        self.SkillTime = time.time()
                        self.skillNumber = i
                    if i == 0:
                        boy.dir = 1
                    elif i == 1:
                        boy.dir = -1

            self.ClearBuffer()

    def SetHitbox(self):
        #self.i = 0
        if self.SkillTime + skill[self.skillNumber].time[0] <= time.time() and self.SkillTime +skill[self.skillNumber].time[0]+skill[self.skillNumber].tick[0] >= time.time():
            boy.inSkill = True
            if self.SkillTime + skill[self.skillNumber].time[0] + 0.1 >= time.time():
                boy.hbPosX = skill[self.skillNumber].hbPosX*boy.dir
                boy.hbPosY= skill[self.skillNumber].hbPosY*boy.dir
                boy.hbHeight = (skill[self.skillNumber].hbHeight*boy.dir)
                boy.hbWidth = (skill[self.skillNumber].hbWidth*boy.dir)
            else:
                boy.hbPosX += skill[self.skillNumber].move*boy.dir
        elif self.SkillTime + skill[self.skillNumber].time[1] <= time.time() and self.SkillTime +skill[self.skillNumber].time[1]+skill[self.skillNumber].tick[1] >= time.time():
            #print("true")
            boy.hbPosX = (100*boy.dir)
            boy.hbPosY= 0*boy.dir
            boy.hbHeight = (50*boy.dir)
            boy.hbWidth = (100*boy.dir)
        else:
            #print("false")
            boy.hbPosX = 2000
            boy.hbPosY = 2000
            boy.hbHeight = 1000
            boy.hbWidth = 1000
            boy.inSkill = False

#버퍼 초기화
    def ClearBuffer(self):
        for i in range(SKILL_MAXNUM):
            skill[i].skillNum = 0
        self.KeyBuffer.clear()
        #self.SkillTime = 0



def enter():
    global  boy, grass,skill,InputSys,monster, ui
    skill = [Skill() for i in range(SKILL_MAXNUM)]
    boy = Boy()
    grass = Grass()
    InputSys = InputSystem()
    ui = UI()
    monster = [Monster() for i in range(MON_MAXNUM)]



def exit():
    global boy, grass,skill,InputSys,monster,ui
    del(boy)
    del(grass)
    for i in skill:
        del(i)
    del(InputSys)
    for i in monster:
        del(i)
    del(ui)


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
        if event.type == SDL_KEYDOWN:
            #print("down")
            #print("down")
            InputSys.InputTime = time.time()
            if event.key == SDLK_ESCAPE:
                game_framework.change_state(title_state)
            if event.key == SDLK_RIGHT:
                InputSys.key = RIGHT
                if InputSys.InputTime:
                    #print("right")
                    InputSys.KeyBuffer.append(RIGHT)
            if event.key == SDLK_LEFT:
                InputSys.key = LEFT
                if InputSys.InputTime:
                    #print("left")
                    InputSys.KeyBuffer.append(LEFT)
            if event.key == SDLK_UP:
                InputSys.key = UP
                if InputSys.InputTime:
                    #print("up")
                    InputSys.KeyBuffer.append(UP)
            if event.key == SDLK_DOWN:
                InputSys.key = DOWN
                if InputSys.InputTime:
                    #print("down")
                    InputSys.KeyBuffer.append(DOWN)
            if event.key == SDLK_z:
                InputSys.key = Z
                if InputSys.InputTime:
                    #print("z")
                    InputSys.KeyBuffer.append(Z)
            if event.key == SDLK_x:
                InputSys.key = X
                if InputSys.InputTime:
                    #print("x")
                    InputSys.KeyBuffer.append(X)
        if event.type == SDL_KEYUP:
            if event.key == SDLK_RIGHT:
                InputSys.KeyBuffer.append(EMPTY)
                #print("up")
            if event.key == SDLK_LEFT:
                InputSys.KeyBuffer.append(EMPTY)
                #print("up")





def update():
    InputSys.CheckTime()
    if InputSys.InTime == False:
        InputSys.CheckSkill()
    InputSys.SetHitbox()
    for i in monster:
        i.update()
    boy.update()
    for i in monster:
        if collision(i,boy):
            boy.getHit()
        if collision(boy,i):
            if i.state != MON_STATE_DIE:
                i.getHit()

def draw():
    clear_canvas()
    grass.draw()
    boy.draw()
    #boy.draw_bb()
    #boy.draw_hb()
    for i in monster:
        i.draw()
    #monster.draw_bb()
    #monster.draw_hb()
    update_canvas()
    delay(0.07)

