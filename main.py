from random import choice, uniform, randint
import json
import kivy
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.relativelayout import RelativeLayout
from kivy.lang import Builder
from kivy.uix.label import Label
from kivy.uix.button import ButtonBehavior
from kivy.properties import DictProperty, NumericProperty, BooleanProperty, OptionProperty, ObjectProperty, \
    StringProperty
from kivy.clock import Clock
from kivy.gesture import GestureDatabase, Gesture
from kivy.uix.screenmanager import Screen
from kivy.core.audio import SoundLoader
from kivy.uix.popup import Popup

SOUND_BG = SoundLoader.load('bg.ogg')
SOUND_BG.loop = True
SOUND_CLEAR = SoundLoader.load('clear.ogg')
SOUND_MOVE = SoundLoader.load('move.ogg')
SOUND_ROTATE = SoundLoader.load('rotate.ogg')
SOUND_START = SoundLoader.load('start.ogg')

KV = '''
#:import Window kivy.core.window.Window

<MyLabel>:
    color:0,0,0,1
    size_hint:None,None
    font_size:'14sp'
    font_name:'pixel.ttf'

<Block>:
    size_hint:None,None
    size:Window.width/20.0,Window.width/20.0
    pos:self.co_x*(Window.width/20.0+3)+3,self.co_y*(Window.width/20.0+3)+3
    opacity:1 if self.active and self.co_y<20 else 0
    mode:app.mode
    canvas.before:
        PushMatrix
        Scale:
            origin:self.center
            x:self.x_scale
            y:self.y_scale
    canvas:
        Color:
            rgba:0,0,0,1
        Line:
            points:[self.x,self.y,self.right,self.y,self.right,self.top,self.x,self.top]
            width:1
            joint:'bevel'
            close:True
        Color:
            rgba:0,0,0,1
        Rectangle:
            pos:self.x+self.width/8.0,self.y+self.width/8.0
            size:self.size[0]*3/4.0,self.size[1]*3/4.0
    canvas.after:
        PopMatrix


<Board>:
    size_hint:None,None
    size:Window.width/2 + 33, Window.width+63
    canvas:
        Color:
            rgba:0,0,0,1
        Line:
            points:[0,0,self.size[0],0,self.size[0],self.size[1],0,self.size[1]]
            width:1
            joint:'bevel'
            close:True

<NPiece>:

<GameButton>:
    color1:0,0,0,1
    color2:103/255.0,120/255.0,104/255.0,1.0
    size_hint:None,None
    canvas:
        Color:
            rgba:0,0,0,1
        Ellipse:
            angle_start: 0
            angle_end: 360
            pos: self.pos
            size: self.size
        Color:
            rgba:self.color1 if self.state == 'down' else self.color2
        Ellipse:
            angle_start: 0
            angle_end: 360
            pos: self.pos
            size: self.size[0]-2,self.size[1]-2

<UpButton@GameButton>:
<DownButton@GameButton>:
<LeftButton@GameButton>:
<RightButton@GameButton>:
<RotateButton@GameButton>:
<PauseButton@GameButton>:
<RotationButton@GameButton>:

<Game>:
    board:board
    n_piece:n_piece
    canvas:
        Color:
            rgba:103/255.0,120/255.0,104/255.0,1.0
        Rectangle:
            pos:0,0
            size:self.size
    FloatLayout:
        canvas.before:
            PushMatrix
            Scale:
                origin:Window.width/2.0,Window.height
                x:0.7 if app.controls == 'button' else 1
                y:0.7 if app.controls == 'button' else 1
        canvas:
        canvas.after:
            PopMatrix
        Board:
            id:board
            pos_hint:{'x':0.05,'y':0.05}
            canvas.before:
                PushMatrix
                Rotate:
                    origin:self.center
                    angle:root.angle
            canvas:
            canvas.after:
                PopMatrix
        NPiece:
            id:n_piece
            pos_hint:{'x':0.7,'y':0.05}
        MyLabel:
            text:'Hi-Score' if app.language=='EN' else u'\u6700\u9ad8\u5206'
            pos_hint:{'x':0.65,'y':0.8}
        MyLabel:
            text:str(root.high_score)
            pos_hint:{'x':0.65,'y':0.7}
        MyLabel:
            text:'Score' if app.language=='EN' else u'\u5206\u6570'
            pos_hint:{'x':0.65,'y':0.6}
        MyLabel:
            text:str(root.score)
            pos_hint:{'x':0.65,'y':0.5}
        MyLabel:
            text:'Level' if app.language=='EN' else u'\u5173\u5361'
            pos_hint:{'x':0.65,'y':0.4}
        MyLabel:
            text:str(root.level)
            pos_hint:{'x':0.65,'y':0.3}
        MyLabel:
            text:'NEXT' if app.language=='EN' else u'\u4e0b\u4e00\u4e2a'
            pos_hint:{'x':0.65,'y':0.2}
    FloatLayout:
        canvas.before:
            PushMatrix
            Scale:
                origin:Window.width/2.0,0
                x:1 if app.controls == 'button' else 0.01
                y:1 if app.controls == 'button' else 0.01
        canvas:
        canvas.after:
            PopMatrix
        LeftButton:
            size_hint:0.1,0.1
            pos_hint:{'center_x':0.2 if app.hand == 'right' else 0.6,'center_y':0.15}
            on_press:root.piece_move_left()
        UpButton:
            size_hint:0.1,0.1
            pos_hint:{'center_x':0.3 if app.hand == 'right' else 0.7,'center_y':0.22}
            on_press:root.piece_rotate()
        RightButton:
            size_hint:0.1,0.1
            pos_hint:{'center_x':0.4 if app.hand == 'right' else 0.8,'center_y':0.15}
            on_press:root.piece_move_right()
        DownButton:
            size_hint:0.1,0.1
            pos_hint:{'center_x':0.3 if app.hand == 'right' else 0.7,'center_y':0.08}
            on_press:root.hard_drop()
        RotateButton:
            size_hint:0.2,0.2
            pos_hint:{'center_x':0.75 if app.hand == 'right' else 0.25,'center_y':0.15}
            on_press:root.piece_rotate()
        PauseButton:
            size_hint:0.05,0.05
            pos_hint:{'center_x':0.1,'center_y':0.9}
            on_press:root.show_pause()
        RotationButton:
            size_hint:0.05,0.05
            pos_hint:{'center_x':0.1,'center_y':0.8}
            on_press:root.switch_rot()


<TitleButton>:
    size_hint:(0.4,0.08)
    font_size:'21sp'
    font_name:'pixel.ttf'
    color:0,0,0,1
    canvas:
        Color:
            rgba:0,0,0,1
        Line:
            points:[self.x,self.y,self.right,self.y,self.right,self.top,self.x,self.top]
            width:1
            close:True

<Title>:
    canvas:
        Color:
            rgba:103/255.0,120/255.0,104/255.0,1.0
        Rectangle:
            pos:0,0
            size:self.size
    Label:
        size_hint:(None,None)
        pos_hint:{'center_x': 0.5,'center_y':0.7}
        color:(0,0,0,1)
        text: 'IRREGULAR\\n TETRIS' if app.language=='EN' else u'\u4fc4\u7f57\u65af\u677f\u7816'
        font_size:'48sp'
        font_name:'pixel.ttf'
    TitleButton:
        pos_hint:{'center_x': 0.5,'center_y':0.45}
        text:'PLAY' if app.language=='EN' else u'\u5f00\u59cb\u6e38\u620f'
        on_press:app.root.transition.direction = 'down';app.root.current = 'game'
    TitleButton:
        pos_hint:{'center_x': 0.5,'center_y':0.35}
        text:'HELP' if app.language=='EN' else u'\u6e38\u620f\u5e2e\u52a9'
        on_press:app.root.transition.direction = 'right';app.root.current = 'help'
    TitleButton:
        pos_hint:{'center_x': 0.5,'center_y':0.25}
        text:'SETTINGS' if app.language=='EN' else u'\u6e38\u620f\u8bbe\u7f6e'
        on_press:app.root.transition.direction = 'up';app.root.current = 'controls'
    TitleButton:
        pos_hint:{'center_x': 0.5,'center_y':0.15}
        text:'ABOUT' if app.language=='EN' else u'\u5173\u4e8e\u6e38\u620f'
        on_press:app.root.transition.direction = 'left';app.root.current = 'about'
    Label:
        size_hint:None,None
        size:self.texture_size
        text:'ver 1.0'
        pos_hint:{'y':0.01,'right':0.98}
        font_name:'pixel.ttf'
        color:0,0,0,1

<ControlsButton>:
    size_hint:None,None
    size:self.texture_size
    color:0,0,0,1
    font_name:'pixel.ttf'
    font_size:'14sp'

<BackButton@ControlsButton>:
    text:' BACK ' if app.language=='EN' else u' \u8fd4\u56de '
    canvas:
        Color:
            rgba:0,0,0,1
        Line:
            points:[self.x,self.y,self.right,self.y,self.right,self.top,self.x,self.top]
            width:1
            close:True

<Controls>:
    canvas:
        Color:
            rgba:103/255.0,120/255.0,104/255.0,1.0
        Rectangle:
            pos:0,0
            size:self.size
    Label:
        color:0,0,0,1
        font_name:'pixel.ttf'
        font_size:'21sp'
        pos_hint:{'center_x': 0.5,'center_y':0.8}
        text:'SETTINGS' if app.language=='EN' else u'\u6e38\u620f\u8bbe\u7f6e'
    ControlsButton:
        pos_hint:{'center_x': 0.2,'center_y':0.65}
        text:'Music' if app.language=='EN' else u'\u97f3\u4e50'
    Slider:
        size_hint:0.5,0.1
        cursor_size:20,20
        background_horizontal:'bar.png'
        cursor_image:'cursor.png'
        background_width:'5sp'
        pos_hint:{'center_x':0.7,'center_y':0.65}
        value:app.music_volume
        max:1
        min:0
        on_touch_move:app.music_volume = self.value
    Slider:
        size_hint:0.5,0.1
        cursor_size:20,20
        background_horizontal:'bar.png'
        cursor_image:'cursor.png'
        background_width:'5sp'
        pos_hint:{'center_x':0.7,'center_y':0.55}
        value:app.sound_volume
        max:1
        min:0
        on_touch_move:app.sound_volume = self.value
    ControlsButton:
        pos_hint:{'center_x': 0.2,'center_y':0.55}
        text:'Sound' if app.language=='EN' else u'\u97f3\u6548'
    ControlsButton:
        pos_hint:{'center_x': 0.2,'center_y':0.45}
        text:'Language' if app.language=='EN' else u'\u8bed\u8a00'
    ControlsButton:
        pos_hint:{'center_x': 0.2,'center_y':0.35}
        text:'Mode' if app.language=='EN' else u'\u6a21\u5f0f'
    ControlsButton:
        pos_hint:{'center_x': 0.2,'center_y':0.25}
        text:'Controls' if app.language=='EN' else u'\u63a7\u5236'
    ControlsButton:
        opacity:0 if app.controls == 'touch' else 1
        pos_hint:{'center_x': 0.2,'center_y':0.15}
        text:'Button pos' if app.language=='EN' else u'\u952e\u4f4d'
    ControlsButton:
        pos_hint:{'center_x': 0.7,'center_y':0.45}
        text:'<English>' if app.language=='EN' else u'<\u4e2d\u6587>'
        on_press:app.switch_language()
    ControlsButton:
        t1:'<irregular>' if app.language=='EN' else u'<\u677f\u7816>'
        t2:'<normal>' if app.language=='EN' else u'<\u6b63\u5e38>'
        pos_hint:{'center_x': 0.7,'center_y':0.35}
        text:self.t1 if app.mode == 'irregular' else self.t2
        on_press:app.switch_mode()
    ControlsButton:
        t1:'<guesture>' if app.language=='EN' else u'<\u89e6\u6ed1>'
        t2:'<button>' if app.language=='EN' else u'<\u6309\u952e>'
        pos_hint:{'center_x': 0.7,'center_y':0.25}
        text:self.t1 if app.controls == 'touch' else self.t2
        on_press:app.switch_controls()
    ControlsButton:
        opacity:0 if app.controls == 'touch' else 1
        t1:'<right-hand>' if app.language=='EN' else u'<\u53f3\u624b>'
        t2:'<left-hand>' if app.language=='EN' else u'<\u5de6\u624b>'
        pos_hint:{'center_x': 0.7,'center_y':0.15}
        text:self.t1 if app.hand == 'right' else self.t2
        on_press:app.switch_hand()
    BackButton:
        pos_hint:{'center_x': 0.5,'y':0.05}
        on_press:app.root.transition.direction = 'down';app.root.current = 'title'


<MyPopup>:
    canvas:
        Color:
            rgba:0,0,0,1
        Line:
            points:[self.x,self.y,self.right,self.y,self.right,self.top,self.x,self.top]
            width:1
            close:True
    separator_color:0,0,0,1
    background:'pop.png'
    size_hint:0.8,0.3
    pos_hint:{'center_x':0.5,'center_y':0.5}
    title_font:'pixel.ttf'
    title_color:0,0,0,1
    title_align:'center'
    auto_dismiss:False

<Pause>:
    title:'Pause' if app.language=='EN' else u'\u6682\u505c'
    RelativeLayout:
        ControlsButton:
            pos_hint:{'center_x':0.2,'center_y':0.6}
            text:'continue' if app.language=='EN' else u'\u7ee7\u7eed'
            on_press:
                root.dismiss()
                app.root.current_screen.falling()
                app.root.current_screen.rot()
        ControlsButton:
            pos_hint:{'center_x':0.5,'center_y':0.6}
            text:'replay' if app.language=='EN' else u'\u91cd\u73a9'
            on_press:
                root.dismiss()
                app.root.current_screen.on_enter()
        ControlsButton:
            pos_hint:{'center_x':0.8,'center_y':0.6}
            text:'exit' if app.language=='EN' else u'\u9000\u51fa'
            on_press:
                app.root.transition.direction = 'up'
                root.dismiss()
                app.root.current='title'

<GameOver>:
    title:'Game over' if app.language=='EN' else u'\u6e38\u620f\u7ed3\u675f'
    RelativeLayout:
        ControlsButton:
            pos_hint:{'center_x':0.3,'center_y':0.6}
            text:'replay'
            on_press:
                root.dismiss()
                app.root.current_screen.on_enter()
        ControlsButton:
            pos_hint:{'center_x':0.8,'center_y':0.6}
            text:'exit'
            on_press:
                app.root.transition.direction = 'up'
                root.dismiss()
                app.root.current='title'


<Help>:
    canvas:
        Color:
            rgba:103/255.0,120/255.0,104/255.0,1.0
        Rectangle:
            pos:0,0
            size:self.size
    MyLabel:
        text:'guesture' if app.language=='EN' else u'\u89e6\u6ed1'
        pos_hint:{'center_x':0.5,'center_y':0.9}
        font_size:'21sp'
    Image:
        source:'swipe.png'
        size_hint:0.3,0.3
        pos_hint:{'center_x':0.2,'center_y':0.72}
    Image:
        source:'clock.png'
        size_hint:0.1,0.1
        pos_hint:{'center_x':0.5,'center_y':0.75}
    Image:
        source:'cclock.png'
        size_hint:0.1,0.1
        pos_hint:{'center_x':0.5,'center_y':0.65}
    Image:
        source:'finger.png'
        size_hint:0.15,0.15
        pos_hint:{'center_x':0.2,'center_y':0.72}
    Image:
        source:'tripletap.png'
        size_hint:0.15,0.15
        pos_hint:{'center_x':0.8,'center_y':0.72}
    MyLabel:
        text:'move' if app.language=='EN' else u'\u79fb\u52a8'
        pos_hint:{'center_x':0.2,'center_y':0.58}
    MyLabel:
        text:'rotate' if app.language=='EN' else u'\u65cb\u8f6c'
        pos_hint:{'center_x':0.3,'center_y':0.8}
    MyLabel:
        text:'swing' if app.language=='EN' else u'\u6447\u6446'
        pos_hint:{'center_x':0.5,'center_y':0.58}
    MyLabel:
        text:'pause' if app.language=='EN' else u'\u6682\u505c'
        pos_hint:{'center_x':0.8,'center_y':0.58}
    MyLabel:
        text:'button' if app.language=='EN' else u'\u6309\u952e'
        pos_hint:{'center_x':0.5,'center_y':0.5}
        font_size:'21sp'
    LeftButton:
        size_hint:0.08,0.08
        pos_hint:{'center_x':0.2,'center_y':0.15}
    UpButton:
        size_hint:0.08,0.08
        pos_hint:{'center_x':0.3,'center_y':0.22}
    RightButton:
        size_hint:0.08,0.08
        pos_hint:{'center_x':0.4,'center_y':0.15}
    DownButton:
        size_hint:0.08,0.08
        pos_hint:{'center_x':0.3,'center_y':0.08}
    RotateButton:
        size_hint:0.18,0.18
        pos_hint:{'center_x':0.75,'center_y':0.15}
    PauseButton:
        size_hint:0.05,0.05
        pos_hint:{'center_x':0.1,'center_y':0.4}
    RotationButton:
        size_hint:0.05,0.05
        pos_hint:{'center_x':0.1,'center_y':0.32}
    MyLabel:
        text:'pause' if app.language=='EN' else u'\u6682\u505c'
        pos_hint:{'center_x':0.25,'center_y':0.4}
    MyLabel:
        text:'swing' if app.language=='EN' else u'\u6447\u6446'
        pos_hint:{'center_x':0.25,'center_y':0.32}
    MyLabel:
        text:'move' if app.language=='EN' else u'\u79fb\u52a8'
        pos_hint:{'center_x':0.45,'center_y':0.05}
    MyLabel:
        text:'rotate' if app.language=='EN' else u'\u65cb\u8f6c'
        pos_hint:{'center_x':0.85,'center_y':0.05}
    BackButton:
        pos_hint:{'center_x': 0.85,'center_y':0.5}
        on_press:app.root.transition.direction = 'left';app.root.current = 'title'

<About>:
    canvas:
        Color:
            rgba:103/255.0,120/255.0,104/255.0,1.0
        Rectangle:
            pos:0,0
            size:self.size
    Label:
        size:Window.width,self.texture_size[1]
        text_size:Window.width*3/4.0, None
        center:Window.width/2.0,Window.height/10.0
        color:0,0,0,1
        font_size:'14sp'
        font_name:'pixel.ttf'
        text:
            """
            Thanks for playing my game, hope you would enjoy it!

            This game is creat for 'Game Off' 5th annual game jam.

            It is just Tetris, I mode some modification, I think it is still fine :)

            The background music and gesture images are download from opengameart.org,

            licenses are CC0, created by poinl and xelu.

            Special thanks to /u/terminak, who helped me a lot in the past.

            I nealy spend a week on it, but I am sure there are still a lot of bugs,

            I am glad to hear your suggestions and feedback! Thanks!
            """
    BackButton:
        pos_hint:{'center_x': 0.1,'center_y':0.1}
        on_press:app.root.transition.direction = 'right';app.root.current = 'title'

<SM@ScreenManager>:
    Title:
        name:'title'
    Help:
        name:'help'
    Game:
        name:'game'
    About:
        name:'about'
    Controls:
        name:'controls'



SM:
    current:'title'

'''

gesture_strings = {
    'bottom_to_top_line': 'eNq1l81u2zAMx+96kebSgBS/pBforgP6AEM/jDRo0RhJuq1vP4nOnKrLtoNgXwxQ5J+mfhIlr7bP2+/v681wOL7th/Dl9B4hrB5HDLdXh+N+9zwcrsIYw+plpLC6GHHrbmHkGiclbtxtX481TGuY/SXsa/UKY6pRuUS9lwCEcHMNa2FKkpUzxpiALRxur37WYSzDuAaVhIxAyoACNFwjh8P93T/zYPSyKGxOSTglAoZMohYFy8hh05XA60c5J6BonIQSIGrmXnl1eVtK3jlgnuUpopJx1AwgSUA7E0RfVhGXS+CAIy2XwAFHWS6BI45nxFEVEiZDYoFouVffGccz44ggUQnFUmbtlScnTLiUvPOlM18UzgamEIkyWuzVd7wki+k7XTrThZwZJQKrJVIA603geCkvloAdMJ8BQ9OnSxvqTeCImZZL4Iz5xLjo19YpGbQ207KBuXuKHDLbnMDPFlbM9bTp/nwnzHkZdXG8gr/Vfc4N0KbjWHo3sDhdocX0pwvIDBfrqo9i5PtAuzewOFuxxfSdrsx0ve0kjElrI6LUy1edr858Y+nKRprY+7Rot77zVVpM3/nqzNcPxRwpWz0mWXr3rjpftcX0na/OfLneGtiy+D0i594LqDlfw8X0na/NfFkUGUggmWHJ8n/5co0/POyH4XX+QzD2XwQJqxtKti66UeIaPj4UjqNpuGs88sfHqoc1HlxexZgao1wIy42HeViCxpja79HqgY1HnsLiR6PCZKTGiBe0uPGIU5g0RpqM+snYlMPVo5kFlSmsmQXVyZg/Gf/Qys0saPKw3BSuU+G5KdymwjNdMpZap3XwY/t4fCoLIIsfZPUP77h7GfZ3rw9DNat32Go+LcZv4373+PZwrINWFNfK5WZWWrCVHlxOQam+T8N28+QuKdygfeZ9uF//Arrd4HI=',
    'top_to_bottom_line': 'eNqtlktu2zAQQPe8iL2pMf8hL+BuC/gART6GY6SIBctpm9uXHKW2laQfAfJGwGjmgfOGprjcP+6/v6x22/70fNymz6/PDtLyvsO0WfSn4+Fx2y9SR2n5reO0/LBiE2mpk1anta477J9Orcxamf+h7EvLSl1uVaVWvdQChLSGlZIxqucizpazpn6z+NneYnsLqb+9+SsSKTrgtBt4Yi6FyAAMC0nqd/9Nip5QzyTIZtkZTAGNwaewLFg+CyusYfnNYilZlACJMxedQKKYNuEMpLBOZ+tUEAjNMZPV9iahQjvpHKiwTmfrxIQlo5CgZCOZYp3COpU5WBze+ewdndnFkAEYAZWnsMI88yysUM9n9YiiipBZC1YqTGKFe/ZZWOGez+5B1clVBb2oG5QJLAn3grOwwr28uv9US4ChaHGN3YHFcAot7IteaNYYCmJS/40mNgUW+sXngYV/KWcYErgwsIQ90SltagxAcR5YTEAvE2hTNFPjdu5nlSnHhQ4fMZ0HFgPQywDiTAUolL1+h2zKl0jDv5Y5WBb67aKfihOyEbWDFmVSkxb6jeeBhX676Gc1YEdFB/J2I5gCC/3m88DCv138x5kPlrGdasIyBeYxAMd5YDEAvwwgbk1CCHGPwjf+612qvztut0/nW5pLXNM0LddUtGatRag+Tp1burkK4hD0UbCdeFc/axn5OoPLUFZGwRzBDKOgrcr1T1oGvsmIMhoFdQjyKCjv15VllMFDmY6CQ+N51DjDB+vyNxlRNmqcygdLGFmgwUIZWSAfgqPGaWi8jBoneb+uwv/MqBaGffBjf396qBugXvOG3bFZnA7ftsebp7ttC1t8tFv4ded97Y6H++e7U3vpaU0r03r4ZKo3xnrb4Eh92O53D5GR0xp9rKCehf3t6hdWSVuU',
    'left_to_right_line': 'eNq1l0luGzEQRfd9EWsTgTVXXcDZBvABAg+CLSSwG5Kc4fZhF52BQJLmpleCPlm/+flKFHt3/HT88n3/eDhfXk+H6f3b51ym3cMM083V+XJ6+XQ4X00zTrvPM027v1bc5LRp5qVOat38cny+LGW6lNk/yj4ss6bZl6qoVd9rAZTp+l3ZFwoiY2PAUswLT+ebq2/LOOS4IBgFUGFis9DpfHf734cAZiaaHv/9hMc38zfR0UGMEGTdPZPXiSPuqFKgkECoOtu6uaa5jZiTuTuEm5gpGQ4sPbcfYht3zFZCaO7V/OeucnhocPE/3AlQMShCXDx83TyZIm1jnkhRRszRSZk8kCiEkQb2JZmibeSeTDGG3EkLsjMbFg6OVXNKpDSEFNy5iIVBAWbR9WanZEq0kXtCpSGowLX71eqeOFJ4bbZV94RKQ1BLEKhZAVciKTaw9oRKsY07J1UeolpYhF1rLzJTIVrfGU6qvE51GcJiv86gegg5rdsnVpat7JMr24g9h3owlwiyAFk/ZzixcoyYh1Fxdtdl2VHWVy5JVWAb84QqI1DrzzPQhBSp/miV17dF2l1iBCkECqs4udS+r2jXzROo2DbmCVRGgCIXUFEC1ggHWt8WTaA6AhTdzFktikdBH/BOnkqbeCdOHcFZDywu9XKhVny5f6z/3Wni1BGc5FQQzZjQAGXAO2lqbOFtCdNGYNZzVhkcIVjBMAbMk6aN0GRz1OIaooK4XPjubut1+3x/Ohyef13ljfMuL9Puuh4U+2oqUG2ny2w63S5idKKlmN9+i95E6MRoIjYRUvTSROpEaCJ3IjZROpGaqJ3ITbROlCZ6J7ZEEJ3YEmHpxJYIoRNbIuwSRUuEXaJoibBLFC0RdomiJcIuUbRE2CWKlgi7RNESYZco7G9iTdQa4Ovx4fJUyUdM1xmwapeXz4fT7fP9Id/VsrNg0d+a8ON8enl4vb/kaG0u3Gt9YagnGwfVG5rUVqmTnw7Hx6c2B6frdL7b/wBF3Mpg',
    'right_to_left_line': 'eNq1l8+OmzAQh+9+keSyyPb8sf0C2WulPECVJihBu0oQsG337WsP2Qaq7sJl5oI0md/nwBeC2TYvzc/36lz3w1tXm+f7sbVme2qd2W/6obu91P3GtN5sX1sw2/8m9jJmWiw5yrn21lyHEuMSC5/EvpUp08aSSjn1ngPOmp2rQmAgjpDQWk+W6idHpt9vfpcJZ3a2IorwKALT/zh8uYrzclJgzl8tcb7THU8q0DJdTj0T1tCB7KRydJHOQg9KdBHgkg7dy4/JOyW6WPWgRBerfp1V72lG98t40eqDFl68+qSEBxELTgsvZmGN2Sdb2RnfAi3fsiBygfQWEL0Q9BYQwZDUFkBRjE5vAZGMepJRJKOeZBTJqCcZRTKulcyzwuXnIoljcmp8UUwrFfuA6VGRl/HjnoO08KKXghZe5FJSwrO4ZaeFF7WspZZFLa9Ui3ZWsIIvbjmo8UUuJy1+ELvBqfFFb1ipF3G6Z0aWf7a8Ze+PXV1f/74QBJQ3AjLbnedUZTBEnw9DG9gcSjPOmmFs4qwZx6abNZM0Cas0rfCYiPZjYhKLTpqYv8rs8kwm/DjBsxiMTfo8hosTZA7jNfrVnIZLvjj5pth5+PcE8sBwe627w/VYl6FQNlSutO/evrfd7fR2HMqHMRMqTgzxoxKW0UvdnC8ykUrcZjvVH8xWrBo=',
    'clockwise_circle': 'eNqlmMFuGzkMhu/zIvGlhiiSovQC2esCeYBFmhiJ0SIxbHd3+/aroRSN6MYr252DA3wj/SPyJyUhq+237d8/1y+bw/HHfjP9Uf/u3LR63sH0cHc47t+/bQ53085Pq+87nFafznjQYdOO5nmc5+3et2/HeVqYp8mZaX/Oo6ZdnGelPOtnngBuundrQgmQHJVfIpkOD3f/zq9huv/i1i5idIl9+RWJ0+Hr4/9+BLzGhNPL2S+8zOJZ2+Py+BSFx+IaOHATd4u0cJJFHLDxAJEv0Q6qLWNtb95EGUtr5iF9SGPoUiKIi7KYlKShstcK8tCUTdghNmUk6nwAN86HVyN9M9KnXiF/8kOaoI8mTxsqq4u+ueg5davmQIs0X5lpryb6ZiLEc9VH5g3SWFpN9M1EF02FObpdGtVFbC46dzYhV0uri1hdnDs6dQ1NuQd/Q1t9RG7aEJoyRkCIv6GtRqI07bzWTpzy+5vrD9VJTIu2hO5JbtHGeO02QuolQRNH8N0eyrwkHI3NFMbaaiYtZiKdM/PqPYrUTOILtF26di8hdZPkEvHrTwVSPykN1W860FgNZbhEPaejK1LOTg3V1VLGS9R96CspjOuFyz2BLxHP2e4Tc0Fe1FOWYRd9mc9S7pYe09hTVk85Dft/Vieb9aF4UEsDDDeuWbyPShyMxdXR0O244WQDoEWd4UpLg1oaeHRU3KStjgYZnXA3aaufIY0O5lu0Re0UGN0nbnFT1E3BwQXrTBXmy/Thab/ZvLV7upBe1Hla3WPAddZElzM9HXcSpscZsoFSYDAwFhhnmG+JBaYCUw+jUyhgIBToC4wF+gLRQCyQDCQDpUAukA0sEYkYKAaGAktEEg1MBrLCVCNKBoKBVKA3EAtEA32BZCAUyD2MaZ36h+YR4WSEThMDS8pSNDCH3j9hHpHMiJIAcCbYyJWaaCP9qgbOxB6xTsQ+odFXSoZCpdzb1GgNOVgqhrpKY18SkipNffV8UHB99Ums1BRqo76v6UZrbM5S6julUe6aaqF9/y20NuDJymoHnqystqBdgy+xcbK0xMZ2Zb7ExmJpiY3ten2Jje16PRta8+tLbEzGIV9iY7Q0Glo99snQWjtYY/OWgqG1+tAb+lnZIpohtd6xBgqmN5ANlc/kghlSM4RiaM0QxhP6S7sDpn5I3SaAnKE1BQSG1hSQN5QqRUNr1ER9LhplQ2suKPTm1I0WSHrTG42G1qRQ+ozmq+9jOcX+2T4fX+d/C+V7cE5Pfp3h8f37Zv/49rTRF16P9ZnXk/Sv3f79+cfTUd/idC9rD4lTYgoU2edraR77utm+vJYhlJXnuA5f1/8BNQnElw==',
    'counterclockwise_circle': 'eNqlmNtu2zgQhu/1IslNDc6R5AuktwvkARZpYiRBi8Sw3e327ZenSJxGWlmJbwx8Gv7mzD8cEb5+/v78z+/d4/50/nncD1/b98EN1w8HGG6vTufj6/f96Wo44HD940DD9eyK2xI2HDivk7Tu8Pr8cs7LNC/zC8v+ylHDIeRVMa36nRaAG27cjgIri1PwGCiK0nC6vfo3P4b82LEIskYgCQ6F4nD6dve/vwFYUqLhcfEHHrP2lyweMGm6oAzRs8K6eMkb5AJxyJqd+Lq2Fm1/gTaqbtQulYc4agslyXntaIuyqo2lhxBGbUSY9k1BJ21S57dpFzNxNBMlLtWE4sZ6Y/ESRy/TKljQZqSNNSle4uglUO+lqQkL87Z9Fy9x9NKxCwtecpBt9abiJTUv8xERDMJpx+hB028wf0a9uEk0qgMITerJ3E+UnIqdJJO4993WmfwneoWKn+QvEse4zVAqhlIcxZEdLYhvPp1cHOXJ0ao5L+42tiIXQ3kylBwulWXzPORiKE+GEjEs7NyBHYjOr8sXS3mylFRmq57VGX3/EqJ19eIpT55S1NmyJ3WvvlPnVW0plgpcoA3e9a/PC7SLo0IXaKOaqlygXS8NckHFKcSN2sVN8avNkifL1poULyWuHqE8zGGbl1q8VFgdLHncptO1Sbt4qevj1u0ENnqpxUudvHRoa6LhE+LFTB3fnunSMPtm/oh08VLHlyeozL48PyDti5V+vAdhUXyT9vxxI30x0k+3oOgWNj3Xf+k+fbo/7vcv41U97SXf1WW4vsFIu6RJENLX+eB1uMsQDfQVgoGhQmdgLDDEHgZXYTAQKvQGYoVqIFUoBnKFZvNBDPQV1owCGlgzCmBgMFB2sf9wjmjpucWI6P6IyMKx5uqjgWggV1hz9cFANjBl1380R4iJwLpMDYQKa+K+lt3FmQxqFby+RZRl0cBabnDOUN8oGKqNoqHSKBlK77eTZrjZMbWFJmOH72sCzuTvoC30fdlHGgx1jRq73yi4vk1GCh3FGBvFrvkmSoa2akJrabZUuu7H2GoM2h2UifruTGFslYfQHb+J9id1pOi6k46xuYTQDYV0uW205hbZUjK02YU1tyiW1tyiWtpGkLe0zaBgaRtC0dKSW7VmouQqRUuhUpsFYaVi6kBkaKsZcaVqqRjaHCKt1BuPyRvauoRCR8c+o5ab7Wp2hs4dBwYT0tJnNLQlymRoS4nZ0LZ5FkPb5ln/oO8PNvs+BN4yCYZioybruREI4vpyzYdA58nbdAVBQ1sJpPd6dtSDcNc6CyGyHpIqVV/Sv54fzk/5j690i72hnHmC59cf++Pdy/2+PAjlypJ5uyj8fTi+Pvy8P5encbjRnQ+s6X7hlTSG1IUp9mn//PhUQjQ3WE7p9G33Hygz85s='}

gestures = GestureDatabase()
for name, gesture_string in gesture_strings.items():
    gesture = gestures.str_to_gesture(gesture_string)
    gesture.name = name
    gestures.add_gesture(gesture)


class TitleButton(ButtonBehavior, Label):
    pass


class ControlsButton(ButtonBehavior, Label):
    pass


class MyLabel(Label):
    pass


class MyPopup(Popup):
    pass


class Pause(MyPopup):
    pass


class GameOver(MyPopup):
    pass


class Block(Widget):
    co_x = NumericProperty(0)
    co_y = NumericProperty(0)
    x_scale = NumericProperty(1)
    y_scale = NumericProperty(1)
    active = BooleanProperty(False)
    mode = StringProperty('irregular')

    def __init__(self, co_x, co_y, **kwargs):
        super(Block, self).__init__(**kwargs)
        self.co_x = co_x
        self.co_y = co_y
        self.rescale()

    def rescale(self, *args):
        self.x_scale = uniform(0.2, 1.8) if self.mode == 'irregular' else 1
        self.y_scale = uniform(0.2, 1.8) if self.mode == 'irregular' else 1


class Piece(RelativeLayout):
    grids = DictProperty({})
    style = OptionProperty('I', options=('I', 'O', 'T', 'S', 'Z', 'J', 'L'))
    co_x = NumericProperty(0)
    co_y = NumericProperty(0)

    def __init__(self, co_x, co_y, **kwargs):
        super(Piece, self).__init__(**kwargs)
        self.co_x = co_x
        self.co_y = co_y
        self.creat()

    def creat(self, *args):
        self.style = choice(Piece.style.options)
        styles = {'I': [(0, 2), (1, 2), (2, 2), (3, 2)],
                  'O': [(1, 1), (1, 2), (2, 1), (2, 2)],
                  'T': [(0, 1), (1, 1), (2, 1), (1, 2)],
                  'S': [(0, 1), (1, 1), (1, 2), (2, 2)],
                  'Z': [(0, 2), (1, 2), (1, 1), (2, 1)],
                  'J': [(0, 1), (1, 1), (2, 1), (2, 2)],
                  'L': [(0, 2), (0, 1), (1, 1), (2, 1)]}
        for pos in styles[self.style]:
            self.add_widget(Block(self.co_x + pos[0], self.co_y + pos[1], active=True))
        if self.style in ('I', 'O'):
            self.rotation_center = [self.co_x + 1.5, self.co_y + 1.5]
        else:
            self.rotation_center = [self.co_x + 1, self.co_y + 1]

    def rotate(self, *args):
        for child in self.children:
            dest_x = int(self.rotation_center[0] + child.co_y - self.rotation_center[1])
            dest_y = int(self.rotation_center[0] - child.co_x + self.rotation_center[1])
            child.co_x, child.co_y = dest_x, dest_y
            child.rescale()


class Board(RelativeLayout):
    def __init__(self, **kwargs):
        super(Board, self).__init__(**kwargs)
        self.update_grids()

    def update_grids(self, *args):
        self.grids = {}
        for i in range(10):
            for j in range(25):
                self.grids[i, j] = Block(i, j, active=False)
                self.add_widget(self.grids[i, j])

    @property
    def grids_state(self):
        return [[self.grids[i, j].active for i in range(10)] for j in range(25)]

    def clear_blocks(self, *args):
        self.clear_widgets()
        self.update_grids()


class NPiece(RelativeLayout):
    def __init__(self, **kwargs):
        super(NPiece, self).__init__(**kwargs)
        self.update_grids()

    def update_grids(self, *args):
        self.grids = {}
        for i in range(4):
            for j in range(4):
                self.grids[i, j] = Block(i, j, active=False)
                self.add_widget(self.grids[i, j])

    def update(self, new_piece):
        for i in range(4):
            for j in range(4):
                self.grids[i, j].active = False
        for child in new_piece.children:
            i, j = child.co_x, child.co_y
            self.grids[i, j].active = True

    def clear_blocks(self, *args):
        self.clear_widgets()
        self.update_grids()


class GameButton(ButtonBehavior, Widget):
    pass


class Game(Screen):
    board = ObjectProperty(None)
    n_piece = ObjectProperty(None)
    angle = NumericProperty(0)
    level = NumericProperty(1)
    piece = ObjectProperty(None)
    high_score = NumericProperty(0)
    score = NumericProperty(0)
    lines = NumericProperty(0)
    rotation = BooleanProperty(False)

    def __init__(self, **kwargs):
        for name in gesture_strings:
            self.register_event_type('on_{}'.format(name))
        super(Game, self).__init__(**kwargs)

    def on_enter(self, *args):
        SOUND_START.stop()
        SOUND_BG.play()
        with open('record.json', 'r') as f:
            self.high_score = json.load(f)
        self.score = 0
        self.level = 1
        self.lines = 0
        self.rotation = False
        self.pause = Pause()
        self.gameover = GameOver()
        self.n_piece.update_grids()
        self.n_piece.clear_blocks()
        self.board.update_grids()
        self.board.clear_blocks()
        if self.piece:
            self.piece.clear_widgets()
        self.next_piece = Piece(0, 0)
        self.add_piece()
        self.falling = Clock.schedule_interval(self.piece_falling, 1.0 / self.level)
        self.rot = Clock.schedule_interval(self.rotate, 1.0 / self.level)

    def on_leave(self, *args):
        SOUND_BG.stop()
        self.n_piece.clear_blocks()
        self.board.clear_blocks()
        if self.piece:
            self.piece.clear_widgets()

    def rotate(self, *args):
        self.angle = randint(-15, 15) if self.rotation else 0

    def on_level(self, *args):
        self.falling.cancel()
        self.falling = Clock.schedule_interval(self.piece_falling, 1.0 / self.level)
        self.rot.cancel()
        self.rot = Clock.schedule_interval(self.rotate, 1.0 / self.level)

    def on_lines(self, *args):
        self.level = self.lines // 40 + 1

    def piece_move_left(self, *args):
        SOUND_MOVE.play()
        stop = False
        for child in self.piece.children:
            if child.co_x == 0:
                stop = True
            elif self.board.grids[child.co_x - 1, child.co_y].active:
                stop = True
        if stop:
            pass
        else:
            self.piece.co_x -= 1
            self.piece.rotation_center[0] -= 1
            for child in self.piece.children:
                child.co_x -= 1

    def piece_move_right(self, *args):
        SOUND_MOVE.play()
        stop = False
        for child in self.piece.children:
            if child.co_x == 9:
                stop = True
            elif self.board.grids[child.co_x + 1, child.co_y].active:
                stop = True
        if stop:
            pass
        else:
            self.piece.co_x += 1
            self.piece.rotation_center[0] += 1
            for child in self.piece.children:
                child.co_x += 1

    def piece_rotate(self, *args):
        SOUND_ROTATE.play()
        stop = False
        for child in self.piece.children:
            dest_x = int(self.piece.rotation_center[0] + child.co_y - self.piece.rotation_center[1])
            dest_y = int(self.piece.rotation_center[0] - child.co_x + self.piece.rotation_center[1])
            if dest_x < 0 or dest_x > 9:
                stop = True
            elif self.board.grids[dest_x, dest_y].active:
                stop = True
        if stop:
            pass
        else:
            self.piece.rotate()

    def hard_drop(self, *args):
        SOUND_MOVE.play()
        n = [self.get_falling_distance(block) for block in self.piece.children]
        n.sort()
        d = n[0]
        self.piece.co_y -= d
        self.piece.rotation_center[1] -= d
        for child in self.piece.children:
            child.co_y -= d

    def switch_rot(self, *args):
        self.rotation = not self.rotation

    def on_clockwise_circle(self):
        self.rotation = True

    def on_counterclockwise_circle(self):
        self.rotation = False

    def on_left_to_right_line(self):
        self.piece_move_right()

    def on_right_to_left_line(self):
        self.piece_move_left()

    def on_bottom_to_top_line(self):
        self.piece_rotate()

    def on_top_to_bottom_line(self):
        self.hard_drop()

    def get_falling_distance(self, block):
        d = block.co_y
        for j in range(d):
            if self.board.grids[block.co_x, j].active == True:
                d = block.co_y - j - 1
        return d

    def on_touch_down(self, touch):
        app = App.get_running_app()
        if app.controls == 'button':
            for child in self.children[:]:
                if child.dispatch('on_touch_down', touch):
                    return True
        else:
            if touch.is_triple_tap:
                self.show_pause()
            touch.ud['gesture_path'] = [(touch.x, touch.y)]
            super(Game, self).on_touch_down(touch)

    def show_pause(self, *args):
        self.pause.open()
        self.falling.cancel()
        self.rot.cancel()

    def on_touch_move(self, touch):
        app = App.get_running_app()
        if app.controls == 'button':
            pass
        else:
            touch.ud['gesture_path'].append((touch.x, touch.y))
            super(Game, self).on_touch_move(touch)

    def on_touch_up(self, touch):
        app = App.get_running_app()
        if app.controls == 'button':
            pass
        else:
            if 'gesture_path' in touch.ud:
                gesture = Gesture()
                gesture.add_stroke(touch.ud['gesture_path'])
                gesture.normalize()
                match = gestures.find(gesture, minscore=0.60)
                if match:
                    self.dispatch('on_{}'.format(match[1].name))
            super(Game, self).on_touch_up(touch)

    def add_piece(self, *args):
        self.check_failure()
        for child in self.next_piece.children:
            child.co_x += 3
            child.co_y += 19
        self.piece = self.next_piece
        self.piece.rotation_center = [self.piece.rotation_center[0] + 3, self.piece.rotation_center[1] + 19]
        self.board.add_widget(self.piece)
        self.next_piece = Piece(0, 0)
        self.n_piece.update(self.next_piece)

    def check_failure(self, *args):
        if True in self.board.grids_state[:][20]:
            self.falling.cancel()
            self.rot.cancel()
            self.gameover.open()
            with open('record.json', 'w') as f:
                json.dump(self.high_score, f)

    def piece_falling(self, *args):
        self.check_piece_stop()
        self.piece.co_y -= 1
        self.piece.rotation_center[1] -= 1
        for child in self.piece.children:
            child.co_y -= 1

    def check_piece_stop(self, *args):
        stop = False
        for child in self.piece.children:
            if child.co_y == 0:
                stop = True
            elif self.board.grids[child.co_x, child.co_y - 1].active:
                stop = True
        if stop:
            self.add_piece_to_grids()

    def on_score(self, *args):
        if self.score >= self.high_score:
            self.high_score = self.score

    def add_piece_to_grids(self, *args):
        for child in self.piece.children:
            i, j = child.co_x, child.co_y
            self.board.grids[i, j].active = True
        self.clear_line()
        self.board.remove_widget(self.piece)
        self.add_piece()

    def clear_line(self, *args):
        lines = set([block.co_y for block in self.piece.children])
        delete_lines = []
        for line in lines:
            if False not in self.board.grids_state[:][line]:
                delete_lines.append(line)
        delete_lines.sort()
        n = len(delete_lines)
        if n == 1:
            SOUND_CLEAR.play()
            self.lines += 1
            self.score += 40 * self.level
            for j in range(22):
                for i in range(10):
                    if j == delete_lines[0]:
                        self.board.grids[i, j].active = False
                    elif j > delete_lines[0] and self.board.grids[i, j].active == True:
                        self.board.grids[i, j].active = False
                        self.board.grids[i, j - 1].active = True
        elif n == 2:
            SOUND_CLEAR.play()
            self.lines += 2
            self.score += 100 * self.level
            for j in range(22):
                for i in range(10):
                    if j in (delete_lines[0], delete_lines[1]):
                        self.board.grids[i, j].active = False
                    elif delete_lines[0] < j < delete_lines[1] and self.board.grids[i, j].active == True:
                        self.board.grids[i, j].active = False
                        self.board.grids[i, j - 1].active = True
                    elif delete_lines[1] < j and self.board.grids[i, j].active == True:
                        self.board.grids[i, j].active = False
                        self.board.grids[i, j - 2].active = True
        elif n == 3:
            SOUND_CLEAR.play()
            self.lines += 3
            self.score += 300 * self.level
            for j in range(22):
                for i in range(10):
                    if j in (delete_lines[0], delete_lines[1], delete_lines[2]):
                        self.board.grids[i, j].active = False
                    elif delete_lines[0] < j < delete_lines[1] and self.board.grids[i, j].active == True:
                        self.board.grids[i, j].active = False
                        self.board.grids[i, j - 1].active = True
                    elif delete_lines[1] < j < delete_lines[2] and self.board.grids[i, j].active == True:
                        self.board.grids[i, j].active = False
                        self.board.grids[i, j - 2].active = True
                    elif delete_lines[2] < j and self.board.grids[i, j].active == True:
                        self.board.grids[i, j].active = False
                        self.board.grids[i, j - 3].active = True
        elif n == 4:
            SOUND_CLEAR.play()
            self.lines += 4
            self.score += 1200 * self.level
            for j in range(22):
                for i in range(10):
                    if j in (delete_lines[0], delete_lines[1], delete_lines[2], delete_lines[3]):
                        self.board.grids[i, j].active = False
                    elif delete_lines[0] < j < delete_lines[1] and self.board.grids[i, j].active == True:
                        self.board.grids[i, j].active = False
                        self.board.grids[i, j - 1].active = True
                    elif delete_lines[1] < j < delete_lines[2] and self.board.grids[i, j].active == True:
                        self.board.grids[i, j].active = False
                        self.board.grids[i, j - 2].active = True
                    elif delete_lines[2] < j < delete_lines[3] and self.board.grids[i, j].active == True:
                        self.board.grids[i, j].active = False
                        self.board.grids[i, j - 3].active = True
                    elif delete_lines[3] < j and self.board.grids[i, j].active == True:
                        self.board.grids[i, j].active = False
                        self.board.grids[i, j - 4].active = True


class Title(Screen):
    pass


class Help(Screen):
    pass


class About(Screen):
    pass


class Controls(Screen):
    pass


class TetrisApp(App):
    language = OptionProperty('EN', options=('EN', 'CH'))
    controls = OptionProperty('touch', options=('button', 'touch'))
    mode = OptionProperty('irregular', options=('irregular', 'normal'))
    hand = OptionProperty('right', options=('right', 'left'))
    music_volume = NumericProperty(1)
    sound_volume = NumericProperty(1)

    def on_music_volume(self, *args):
        SOUND_BG.volume = self.music_volume

    def on_sound_volume(self, *args):
        SOUND_CLEAR.volume = self.sound_volume
        SOUND_MOVE.volume = self.sound_volume
        SOUND_ROTATE.volume = self.sound_volume
        SOUND_START.volume = self.sound_volume

    def switch_language(self, *args):
        if self.language == 'EN':
            self.language = 'CH'
        elif self.language == 'CH':
            self.language = 'EN'

    def switch_mode(self, *args):
        if self.mode == 'irregular':
            self.mode = 'normal'
        elif self.mode == 'normal':
            self.mode = 'irregular'

    def switch_controls(self, *args):
        if self.controls == 'touch':
            self.controls = 'button'
        elif self.controls == 'button':
            self.controls = 'touch'

    def switch_hand(self, *args):
        if self.hand == 'left':
            self.hand = 'right'
        elif self.hand == 'right':
            self.hand = 'left'

    def build(self):
        SOUND_START.play()
        return Builder.load_string(KV)


if __name__ == '__main__':
    TetrisApp().run()
