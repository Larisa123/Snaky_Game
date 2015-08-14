import kivy
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.core.window import Window
from kivy.core.image import Image
from kivy.graphics import Color, Rectangle
from kivy.uix.popup import Popup
from kivy.properties import NumericProperty, ReferenceListProperty, ObjectProperty, BooleanProperty, StringProperty
from kivy.vector import Vector
from kivy.uix.textinput import TextInput
from kivy.clock import Clock
from kivy.lang import Builder
from random import randint
from functools import partial
import os, sys
from kivy.animation import Animation
from kivy.core.audio import SoundLoader
import math

def get_text(file, mode):
    os.path.dirname(sys.argv[0])
    path = os.path.join(os.path.dirname(sys.argv[0]), file)
    if mode == "w": return path
    else: 
        with open(path, mode) as textfile:
            text = ""
            for line in textfile:
                text += line
            return text

def save_record(score, player):
    path = get_text("records.txt", "w")
    records = []
    with open(str(path), "r") as file:
        for line in file:
            info = line.split(",")
            info = [l for l in info if l != ""]
            for i in info:
                i2 = i.split(":")
                i2 = [i for i in i2 if i != ""]
                i2[0], i2[1] = int(i2[0]), i2[1]
                records.append(i2)
    records = sorted(records, key=lambda x: x[0], reverse=True)

    if player == "": player = "No name"
    new = [score, player]
    
    if records != [] and score > 0:
        if score > int(records[-1][0]):
            records.remove(records[-1])
            records.append(new)
        elif len(records) < 4:
            records.append(new)
    elif records == [] and score > 0:
        records.append(new)

    records = sorted(records, key=lambda x: x[0], reverse=True)

    with open(str(path), "w") as file:
        for record in records:
            file.write("{}:{},".format(record[0],record[1]))

def get_progress():
    game_list = []
    games = get_text("saved_games.txt", "r").split(",")
    for game in games:
        if game != "": game_list.append(game)
    return game_list

class Snake(Widget):
    velocity_x = NumericProperty(0)
    velocity_y = NumericProperty(0)
    velocity = ReferenceListProperty(velocity_x, velocity_y)
    
    def move(self):
        self.pos = Vector(*self.velocity) + self.pos

class EvilSnake(Snake):
    pass

class Fruit(Widget):
    def __init__(self, imagename, size, **kwargs): 
        super(Fruit, self).__init__(**kwargs)
        with self.canvas:
            self.size = size
            self.x = self.center_x
            self.y = self.center_y
            self.pos = (self.x, self.y)
            self.rect_bg = Rectangle(source=imagename,
                                     pos=self.pos,
                                     size=self.size,
                                     keep_data=True)
            self.bind(pos=self.update_bg_pos)
            self.rect_bg.pos = self.pos
            
    def update_bg_pos(self, instance, value):
        self.rect_bg.pos = value

class LevelLabel(Label):
    def __init__(self, pos, **kwargs): 
        super(LevelLabel, self).__init__(**kwargs)
        self.pos = pos
        self.font_size = 70, 70
        self.text = self.text

class TNT(Fruit):
    pass

class PlusPoint(Fruit):
    pass

class MinusPoint(Fruit):
    pass

global sound_on
sound_on = True

class SnakeGame(Widget):
    score = NumericProperty(0)
    is_on_pause = BooleanProperty(False)
    gameover = BooleanProperty(False)
    level = NumericProperty(1)
    beginning = BooleanProperty(True)
    text_input = StringProperty("")
    imagename = StringProperty("")
    filename = StringProperty(".txt")
    sound = BooleanProperty(True)
    language_slo = BooleanProperty(False)
    updated = BooleanProperty(False)
    load_game = BooleanProperty(False)
    game = ""
    player = StringProperty("")
    selected_game = StringProperty("")
    snaky_png = StringProperty("snaky_vzhod.png")

    evil_snaky = ObjectProperty(None)
    snaky = ObjectProperty(None)
    # Lists for saving, loading:
    saved_games = get_progress()
    filename_list = []
    # Lists containing widgets: 
    fruit_list = []
    tnt_list = []
    point_list = []
    minus_point_list = []
    update_list = []
    

    def __init__(self, *args, **kwargs):
        super(SnakeGame, self).__init__(*args, **kwargs)
        self.My_Clock = Clock
        self.My_Clock.schedule_interval(self.update, 1/60.)

    def on_touch_down(self, touch):
        y = (touch.y - self.snaky.pos[1])
        x = (touch.x - self.snaky.pos[0])
        angle = math.degrees(math.atan2(y, x))
        velx = self.snaky.velocity[0]
        vely = self.snaky.velocity[1]
        self.snaky.move()

        # snaky movement:
        if vely == 0 and velx > 0:
            if angle > 45 and angle < 135:
                velx, vely = vely, velx
                self.snaky_png = "snaky_sever.png"
            elif angle < -45 and angle > -135:
                velx, vely = - Vector(vely, velx)
                self.snaky_png = "snaky_jug.png"
        elif velx == 0 and vely > 0:
            if angle > 135 or angle < -135:
                velx, vely = - Vector(vely, velx)
                self.snaky_png = "snaky_zahod.png"
            elif angle < 45 or angle > -45:
                velx, vely = vely, velx
                self.snaky_png = "snaky_vzhod.png"
        elif velx == 0 and vely < 0:
            if angle > 135 or angle < -135:
                velx, vely = vely, velx
                self.snaky_png = "snaky_zahod.png"
            elif angle < 45 or angle > -45:
                velx, vely = - Vector(vely, velx)
                self.snaky_png = "snaky_vzhod.png"
        elif vely == 0 and  velx < 0:
            if angle > 45 and angle < 135:
                velx, vely = - Vector(vely, velx)
                self.snaky_png = "snaky_sever.png"
            elif angle < -45 and angle > -135:
                velx, vely = vely, velx
                self.snaky_png = "snaky_jug.png"
        else: pass
        self.snaky.velocity[0] = velx
        self.snaky.velocity[1] = vely
        return super(SnakeGame, self).on_touch_down(touch)
    
    
    def begin(self, *args):
        vel = (self.width*0.0014,0)
        self.snaky.velocity = vel
        self.snaky.center = self.center
        if not self.beginning or self.gameover or self.is_on_pause:
            vel = (self.width*0.0014,0)
            self.snaky_png = "snaky_vzhod.png"
            self.score = 0
            self.level = 1
            for fruit in self.fruit_list:
                self.remove_fruit(fruit)
            for tnt in self.tnt_list:
                self.remove_tnt(tnt)
            for label in self.update_list:
                self.remove_update(label)
            self.gameover = False

        if self.fruit_list != [] or self.tnt_list != []:
        # ce se vedno ni prazno (zgornjo ne zadostuje, ne vem zakaj ne)
            for fruit in self.fruit_list:
                self.remove_fruit(fruit)
            for tnt in self.tnt_list:
                self.remove_tnt(tnt)
            
        self.beginning = False

        self.evil_snaky.velocity = Vector(vel[0], -0.3*vel[0])
        self.snaky.center = self.center
        
        if self.is_on_pause == True:
            self.is_on_pause = False
            self.My_Clock.schedule_interval(self.update, 1/60.)
            
            
    def update(self, dt, *args):
        # level and score updates:
        if self.score < 0 or self.score == 10 or self.score == 25 or self.score == 40:
            self.level_update()

        self.snaky.move()
        
        if self.snaky.y  < self.y or self.snaky.top + self.height*0.078 > self.top or self.snaky.x + self.snaky.size[0] > self.width or self.snaky.x < self.x:
            self.game_over() # wall collision
        
        #evil snake update:
        self.evil_snaky.x += self.evil_snaky.velocity[0]
        self.evil_snaky.y += self.evil_snaky.velocity[1]
        
        if self.evil_snaky.x < 0 or (self.evil_snaky.x + self.evil_snaky.size[0]) > self.width:
            self.evil_snaky.velocity[0] *= -1
            self.play_sound("ball_bounce.wav")

        if self.evil_snaky.y < 0 or (self.evil_snaky.y + self.evil_snaky.size[1] + self.height*0.078) > self.height:
            self.evil_snaky.velocity[1] *= -1
            self.play_sound("ball_bounce.wav")

        # if snakes collide:
        if self.widget_collision(self.snaky, self.evil_snaky):
            self.game_over()

        # randomly add fruit:
        randomint = randint(1, 1300)
        if not self.beginning and not self.gameover:
            if randomint % 200 == 0: self.add_fruit()
        # widget removal:
        for fruit in self.fruit_list:
            if self.widget_collision(self.snaky, fruit):
                self.score += 1 # snaky eats a fruit
                self.play_sound("bite.wav")
                self.remove_fruit(fruit)
                self.add_point(fruit.x, fruit.y)
            if self.widget_collision(self.evil_snaky, fruit):
                self.score -= 1 # evil_snaky eats it
                self.play_sound("bite.wav")
                self.remove_fruit(fruit)
                self.add_minus_point(fruit.x, fruit.y)
                
        for tnt in self.tnt_list:
            if self.widget_collision(self.snaky, tnt):
                self.pause()
                self.play_sound("bomb.wav")
                self.remove_tnt(tnt)
                self.My_Clock.schedule_once(self.game_over,2)
            if self.widget_collision(self.evil_snaky, tnt):
                self.play_sound("bomb.wav")
                self.evil_snaky.velocity = Vector(self.evil_snaky.velocity)*1.1
                self.add_tnt()
                self.add_tnt()
                self.remove_tnt(tnt)
            
        # randomly add tnt:
        ranint = randint(1,4000)
        if not self.beginning and not self.gameover:
            if ranint == 525: self.add_tnt()
        # point removal:
        for point in self.point_list:
            if randomint % 68 == 0: self.remove_point(point)
        for point in self.minus_point_list:
            if randomint % 70 == 0: self.remove_minus_point(point)
        # upgrade level removal:
        if self.level > 1 and randomint%30 == 0:
            for label in self.update_list:
                self.remove_update(label)

    def level_update(self, *args):
        pos = self.width*0.5, self.height*0.7
        l = LevelLabel(pos)
        if self.score < 0: self.game_over()
        elif self.score < 10:
            self.level = 1
        elif self.score >= 10:
            self.level = 2
            l.text = "Level 2!"
            self.snaky.velocity = 1.002*Vector(self.snaky.velocity)
            self.evil_snaky.velocity = 1.002*Vector(self.evil_snaky.velocity)
        elif self.score >= 25:
            self.level = 3
            l.text = "Level 3!"
            self.snaky.velocity = 1.002*Vector(self.snaky.velocity)
            self.evil_snaky.velocity = 1.002*Vector(self.evil_snaky.velocity)
        elif self.score >= 40:
            self.level = 3
            l.text = "Level 4!"
            self.snaky.velocity = 1.002*Vector(self.snaky.velocity)
            self.evil_snaky.velocity = 1.002*Vector(self.evil_snaky.velocity)
        if self.level > 1:
            self.add_widget(l)
            self.update_list.append(l)
        self.updated = True
        
    def remove_update(self, obejct, *args):
        self.remove_widget(obejct)
        self.update_list.remove(obejct)

    def play_sound(self, file, *args):
        if self.sound and not self.beginning:
            sound = SoundLoader.load(file)
            if sound:
                sound.play()

    def change_sound(self, *args):
        self.sound = not self.sound
        sound_on = self.sound # sound_on is a global variable

        #if self.sound:
        #    sound = SoundLoader.load("pure_blood-bg_music.mp3")
        #    sound.volume = 0.1
        #    sound.play()
        #elif not self.sound:
        #    SoundLoader.unload("pure_blood-bg_music.mp3")

    def widget_collision(self, object1, object2, *args):
        if object1 == self.snaky and object2 == self.evil_snaky:
            snake_distance = Vector(object1.center).distance(object2.center)
            if snake_distance < (object1.size[0]/2.1 + object2.size[0]/2.1):
                return True
            else: return False
        else:
            snake_distance = Vector(object1.center).distance(object2.pos)
            if snake_distance < (object1.size[0]/2.1 + object2.size[0]/2.1):
                return True
            else: return False       
            

    def pause(self, *args):
        self.My_Clock.unschedule(self.update)
        self.is_on_pause = True

    def show_gameover_popup(self, *args):
        content = GridLayout(rows=6)
        score_label = Label(text="Your score:     {}".format(self.score),
                            text_font=self.parent.height*0.19, size_hint_y=0.2)
        play_button = Button(background_normal="play_again.png", size_hint_y=0.27)
        insert_label = Label(text="Your name:", text_font=self.parent.height*0.19, size_hint_y=0.2)
        
        name_input = TextInput(multiline=False, size_hint_y=0.25)
        name_input.bind(text=self.setter("player"))
        self.player = name_input.text

        empty_label1 = Label(text="", size_hint_y=0.1)
        empty_label2 = Label(text="", size_hint_y=0.2)

        for widget in [score_label, empty_label1, insert_label, name_input, empty_label2, play_button]:
            content.add_widget(widget)
        
        p = GameOverPopup(content=content, on_dismiss=self.save_players_score)
        play_button.bind(on_press=p.dismiss)
        p.open()

    def game_over(self, *args):
        self.pause()
        self.gameover = True
        for i in [1,2]:
            file = "game_end{}.wav".format(i)
            self.play_sound(file)
        self.show_gameover_popup()
        
    def save_players_score(self, *args):
        save_record(self.score, self.player)

    def change_difficulty(self, level, *args):
        self.level = level

    # widget adding, removing:
    def remove_fruit(self, object1, *args):
        if object1 in self.fruit_list:
            self.fruit_list.remove(object1)
            self.remove_widget(object1)

    def add_fruit(self, *args):
        imagename = "fruit{}.png".format(randint(1,6))
        tmpFruit = Fruit(imagename=imagename, size=(self.parent.height*0.067, self.parent.height*0.067))
        tmpFruit.x = randint(1, self.width-40)
        tmpFruit.y = randint(1, self.height-140)

        self.fruit_list.append(tmpFruit)
        self.add_widget(tmpFruit)

    def add_specific_fruit(self, imagename, x, y, *args):
        tmpFruit = Fruit(imagename=imagename, size=(self.parent.height*0.067, self.parent.height*0.067))
        tmpFruit.x = x
        tmpFruit.y = y
        self.fruit_list.append(tmpFruit)
        self.add_widget(tmpFruit)
        
    def add_tnt(self, *args):
        tmpTnt = TNT("tnt.png", (self.parent.height*0.067, self.parent.height*0.067))
        tmpTnt.x = randint(1, self.width-40)
        tmpTnt.y = randint(1, self.height-140)

        self.tnt_list.append(tmpTnt)
        self.add_widget(tmpTnt)

    def add_specific_tnt(self, x, y, *args):
        tmpTnt = TNT("tnt.png", size=(self.parent.height*0.067, self.parent.height*0.067))
        tmpTnt.x = x
        tmpTnt.y = y
        self.tnt_list.append(tmpTnt)
        self.add_widget(tmpTnt)

    def remove_tnt(self, object1, *args):
        if object1 in self.tnt_list:
            self.tnt_list.remove(object1)
            self.remove_widget(object1)
        
    def add_point(self, x, y, *args):
        tmpPoint = PlusPoint("plus.png", (self.parent.height*0.035, self.parent.height*0.035))
        tmpPoint.x = x
        tmpPoint.y = y + 5

        self.point_list.append(tmpPoint)
        self.add_widget(tmpPoint)

    def add_minus_point(self, x, y, *args):
        tmpPoint = PlusPoint("minus.png", (self.parent.height*0.035, self.parent.height*0.035))
        tmpPoint.x = x
        tmpPoint.y = y + 5

        self.minus_point_list.append(tmpPoint)
        self.add_widget(tmpPoint)

    def remove_point(self, object1, *args):
        self.point_list.remove(object1)
        self.remove_widget(object1)

    def remove_minus_point(self, object1, *args):
        self.minus_point_list.remove(object1)
        self.remove_widget(object1)

    def save(self, *args):
        self.pause()
        b = GridLayout(rows=4)
        save_button = Button(background_normal="save_game.png", size_hint=(0.4,0.25))
        text_input = TextInput(text="Insert filename",font_size=self.parent.height*0.027, multiline=False,
                               size_hint_y=0.3, valign="middle")
        text_input.bind(text=self.setter("filename"))
        empty_label1 = Label(text="", size_hint_y=0.12)
        empty_label2 = Label(text="", size_hint_y=0.2)
        self.saved_games.append(text_input.text)

        b.add_widget(empty_label1)
        b.add_widget(text_input)
        b.add_widget(empty_label2)
        b.add_widget(save_button)
        popup = GameSavingPopup(content=b)
        save_button.bind(on_realese=popup.dismiss)
        save_button.bind(on_press=self.save_as_filename)
        popup.open()
        
    def save_as_filename(self, *args):
        loc = get_text("saved_games.txt", "w")
        with open(str(loc), "a") as f:
            f.write("{},".format(self.filename))

        try:
            path = get_text("{}.txt".format(self.filename), "w")
            with open(str(path), "w") as file:
                file.write("{}\n".format(self.score))
                for fruit in self.fruit_list:
                    file.write("F,{},{},{}\n".format(fruit.rect_bg.source,fruit.x,fruit.y))
                for tnt in self.tnt_list:
                    file.write("T,{},{}\n".format(tnt.x,tnt.y))
            text = "Game saved!"
        except: text = "Failed to save the game."
        b = BoxLayout()
        l = Label(text=text, font_size=self.parent.height*0.027)
        b.add_widget(l)
        p = GameSavedPopup(content=b)
        p.open()

        self.saved_games = get_progress()

    def load_info(self, game, *args):
        print("Loading info..")
        try:
            print("Game loaded.")
            file="{}.txt".format(game)
            path = get_text(str(file), "w")
            with open(path,"r") as file:
                i = 0
                for line in file:
                    line = line.strip("\n")
                    if i == 0: self.score = int(line)
                    elif i > 0:
                        info = line.split(",")
                        if info[0] == "F":
                            self.add_specific_fruit(info[1],int(float(info[2])),int(float(info[3])))
                        elif info[0] == "T":
                            self.add_specific_tnt(int(float(info[1])),int(float(info[2])))
                    i += 1
        except: print("Failed to load the game.")

    def open_load_popup(self, *args):
        def change_load_game_status(game, arg):
            self.load_game = True
            self.beginning = True
            self.selected_game = game
        main = BoxLayout(orientation="vertical")
        grid = GridLayout(rows=10)
        main.add_widget(grid)
        p = SelectLoadPopup(content=main, on_dismiss=self.begin)
        for game in reversed(self.saved_games):
            btn = Button(text=str(game),size_hint_y=self.parent.height*0.025, background_color=(0, 0.298, 0.6,.15))
            btn.bind(on_press=p.dismiss)
            btn.bind(on_release=partial(self.load_info, game))
            grid.add_widget(btn)
        for i in range(len(self.saved_games), 10):
            grid.add_widget(Button(text="", size_hint_y=self.parent.height*0.025, background_color=(0, 0.298, 0.6, .15)))
        p.open()

class GameScreen(Screen):
    pass
        


class RootScreen(ScreenManager):
    pass

    
class MenuScreen(Screen):

    def play(self, file, *args):
        sound = SoundLoader.load(file)
        if sound:
            sound.play()

    def show_popup_inst(self, *args):
        b = BoxLayout()
        l = Label(text=get_text("game_instructions.txt", "r"), font_size=self.parent.height*0.025)
        b.add_widget(l)
        p = InstructionsPopup(content=b)
        p.open()

    def show_popup_about(self, *args):
        b = BoxLayout()
        l = Label(text=get_text("about.txt", "r"), font_size=self.parent.height*0.028)
        b.add_widget(l)
        p = AboutPopup(content=b)
        p.open()

    def records_for_display(self):
        text = get_text("records.txt", "r")
        text = [t for t in text.split(",") if t!=""]
        for_display = ""
        for i,t in enumerate(text):
            info = t.split(":")
            if int(info[0]) > 0: for_display += "{}.    {}  -  {} {} \n".format(i+1, info[1], info[0],"fruit" if int(info[0])==1 else "fruits")
        return for_display
    
    def show_popup_records(self, *args):
        b = BoxLayout()
        if self.records_for_display == None: text = "High Scores weren't saved yet."
        else: text = self.records_for_display()
        l = Label(text=text, font_size=self.parent.height*0.028, halign="left", valign="top")
        b.add_widget(l)
        p = RecordsPopup(content=b)
        p.open()
    

class InstructionsPopup(Popup):
    pass

class RecordsPopup(Popup):
    pass

class AboutPopup(Popup):
    pass

class GameOverPopup(Popup):
    pass

class GameSavedPopup(Popup):
    pass

class GameSavingPopup(Popup):
    pass

class SelectLoadPopup(Popup):
    pass



class SnakyGameApp(App):
    def build(self):
        self.load_kv("snaky_kv.kv")

        if sound_on:
            sound = SoundLoader.load("pure_blood-bg_music.mp3")
            sound.volume=0.1
            sound.play()

        return RootScreen()
        

if __name__ == "__main__":
    SnakyGameApp().run()
