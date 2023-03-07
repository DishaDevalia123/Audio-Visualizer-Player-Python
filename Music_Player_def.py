import io
import os
import sys
import time
import librosa
from pydub import AudioSegment
import numpy as np
from Music_Player_UI import Ui_music_player
from PIL import Image
from PyQt5 import QtWidgets
from PyQt5.QtCore import QDirIterator, QElapsedTimer, Qt, QTimer, QUrl
from PyQt5.QtGui import QBrush, QColor, QIcon, QLinearGradient, QPainter, QPalette,QPixmap
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer, QMediaPlaylist
from PyQt5.QtWidgets import QAction, QApplication, QColorDialog, QFileDialog,QStyle
from tinytag import TinyTag


class music_player(QtWidgets.QMainWindow):
    
    def __init__(self):
        super().__init__()   
        self.ui= Ui_music_player()
        self.ui.setupUi(self)
        self.show()         
        self.filename = ''
        self.path= ''
        self.spectrogram = None
        self.time_index_ratio = 0
        self.frequencies_index_ratio = 0
        self.x1= 0
        self.y1= 0
        self.width1 = 0
        self.height1 =0
        self.max_height = 0
        self.bars= []
        self.player= None
        self.deltaTime=0
        self.con=0
        self.proc= None
        self.getTicksLastFrame= 0
        self.t=0
        self.vol= False   #sets the value of this var once
        self.pp= True
        self.song_list= []
        self.mp3_list= []
        self.i= 0
        self.colorf= 0
        self.db=0
        self.col=None
        self.colgrd = 0
                
        self.timer= QElapsedTimer()
        self.player= QMediaPlayer()
        self.playlist= QMediaPlaylist()
        self.pal= QPalette()
        self.timer_play = QTimer(self)
        self.timer_play.setInterval(10)
        self.qi= QIcon('music_icon.ico')
        self.setWindowIcon(self.qi)

        menubar = self.menuBar()
        filemenu = menubar.addMenu('File')
        filemenu2 = menubar.addMenu('Theme')


        fileAct = QAction('Open File', self)
        fileAct.setShortcut('Ctrl+O')
        filemenu.addAction(fileAct)
        fileAct.triggered.connect(self.openFile)
        
        
        folderAct = QAction('Open Folder', self)
        folderAct.setShortcut('Ctrl+D')
        filemenu.addAction(folderAct)
        folderAct.triggered.connect(self.openFolder)
        
        
        change_color= filemenu.addMenu('Color settings')
        color_change = QAction("Change Color", self)
        act_grad = QAction("Activate Gradient", self)
        change_color.addAction(color_change)
        change_color.addAction(act_grad)
        color_change.triggered.connect(self.ok)
        act_grad.triggered.connect(self.grad)
        
        
        close= QAction('Quit', self)
        close.setShortcut('Ctrl+X')
        filemenu.addAction(close)
        close.triggered.connect(self.close)
        
        
        Light = QAction('Light', self)
        Dark = QAction('Dark', self)
        filemenu2.addAction(Light)
        filemenu2.addAction(Dark)
        Light.triggered.connect(lambda: self.change_theme(1))
        Dark.triggered.connect(lambda: self.change_theme(0))
        
        
        self.ui.play_btn.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.ui.back_btn.setIcon(self.style().standardIcon(QStyle.SP_MediaSkipBackward))
        self.ui.next_btn.setIcon(self.style().standardIcon(QStyle.SP_MediaSkipForward))
        self.ui.vol_btn.setIcon(self.style().standardIcon(QStyle.SP_MediaVolume))
        app.setStyle("Fusion")
        self.pal.setColor(QPalette.Window, QColor(30,30,30))
        self.pal.setColor(QPalette.WindowText, Qt.white)
        self.pal.setColor(QPalette.Base, QColor(25, 25, 25))
        self.pal.setColor(QPalette.Text, Qt.white)
        self.pal.setColor(QPalette.ButtonText, Qt.white)
        app.setPalette(self.pal)

        self.connection()
        self.create_bars()

        #self.hbox= QHBoxLayout()
        #self.hbox.setContentsMargins(0,0,0,0)

      #  self.vbox= QVBoxLayout()

       # self.vbox.addWidget(self.ui.play_btn)
       # self.hbox.addWidget(self.ui.back_btn)
     #   self.hbox.addWidget(self.ui.vol_btn)
      #  self.hbox.addWidget(self.ui.next_btn)
       # self.hbox.addWidget(self.ui.vol_slider)
        
    def connection(self):
        self.ui.play_btn.clicked.connect(self.play_func)
        #self.ui.pause_btn.clicked.connect(self.pause_func)
        self.ui.back_btn.clicked.connect(self.back_func)
        self.ui.next_btn.clicked.connect(self.next_func)
        self.ui.vol_btn.clicked.connect(self.vol_func)
        self.ui.vol_slider.valueChanged[int].connect(self.changeVolume)
        self.ui.prog_slider.sliderMoved.connect(self.set_position)
        #self.ui.open_combo.activated.connect(self.opt_sel)  
        self.timer_play.timeout.connect(self.chutiya_while)
        self.playlist.currentIndexChanged.connect(self.indexChanged) #jab index/music khudse change hoga, next pe jaayega tab indexchanged method call hoga   
                                                                        
        self.player.positionChanged.connect(self.pos_changed)
        self.player.durationChanged.connect(self.duration_changed)

        self.ui.vol_slider.show()
        
    def mouseReleaseEvent(self, event):
        if event.button() == 1: # left
            self.drag = False

    def mousePressEvent(self, event):
        if event.button() == 1: # left
            self.drag = True
            # mouse position
            point = event.screenPos()
            # window position
            rect = self.geometry()

            # distance between both
            self.relative_x = point.x() - rect.x()
            self.relative_y = point.y() - rect.y() 


        if event.button() == 4: # middle
            print('middle')

    def mouseMoveEvent(self, event):
        if self.drag:
            # mouse position
            point = event.screenPos()
            # window new position
            new_x = point.x() - self.relative_x
            new_y = point.y() - self.relative_y
            self.move(new_x, new_y)
        
    def vol_func(self):

        if self.vol == False:
            self.ui.vol_btn.setIcon(self.style().standardIcon(QStyle.SP_MediaVolumeMuted))
            self.v= self.player.volume()
            self.player.setVolume(0)
            self.ui.vol_slider.setValue(0)
            self.ui.vol_slider.hide()
            self.vol= True
        else:
            self.ui.vol_btn.setIcon(self.style().standardIcon(QStyle.SP_MediaVolume))
            self.ui.vol_slider.setValue(self.v)
            self.ui.vol_slider.show()
            self.player.setVolume(self.v)
            self.vol= False

    def change_theme(self,theme):
        
        if theme==0:
            self.pal.setColor(QPalette.Window, QColor(30,30,30))
            self.pal.setColor(QPalette.WindowText, Qt.white)
            self.pal.setColor(QPalette.Base, QColor(25, 25, 25))
            self.pal.setColor(QPalette.Text, Qt.white)
            self.pal.setColor(QPalette.ButtonText, Qt.white)
            app.setPalette(self.pal)
            self.setStyleSheet("QMenuBar { background-color: rgb(0,0,0);color: rgb(255,255,255);}")
            self.ui.start_lbl.setStyleSheet("color: rgb(255, 255, 255)")
            self.ui.end_lbl.setStyleSheet("color: rgb(255, 255, 255)")
            self.ui.songname_lbl.setStyleSheet('color: rgb(255, 255, 255)')
            
        elif theme==1:
 
            self.pal.setColor(QPalette.Window, QColor(255,255,255))
            self.pal.setColor(QPalette.WindowText, Qt.white)
            self.pal.setColor(QPalette.Base, QColor(240, 240, 240))
            self.pal.setColor(QPalette.Text, Qt.black)
            self.pal.setColor(QPalette.ButtonText, Qt.black)
            app.setPalette(self.pal)
            self.setStyleSheet("QMenuBar { background-color: rgb(255,255,255);color: rgb(30,30,30);}")
            self.ui.start_lbl.setStyleSheet("color: rgb(30,30,30)")
            self.ui.end_lbl.setStyleSheet("color: rgb(30,30,30)")
            self.ui.songname_lbl.setStyleSheet('color: rgb(30,30,30)')
            
    def openFile(self):
        self.colorf=0
        self.filename = QFileDialog.getOpenFileName(self, "Open Song", "~", "Sound Files (*.mp3 *.wav )")

        
        if self.filename[0].endswith('.mp3'):
            self.pp=True
            self.mp3_list= []
            self.song_list=[]
            self.playlist.clear()
            self.mp3_list.append(self.filename[0])
            self.a= self.filename[0]
            self.b= self.a.replace('.mp3','.wav')
            sound = AudioSegment.from_mp3(self.a)
            sound.export(self.b, format="wav")
            #str= 'ffmpeg -i "{}" -acodec pcm_u8 -ar 44100 -y "{}"'.format(self.a,self.b) # mp3 to wav conversion
            #self.r= call(str,shell= True)
            url = QUrl.fromLocalFile(self.b)
            content = QMediaContent(url)
            self.player.setMedia(content)
            self.playlist.addMedia(QMediaContent(url))
            self.player.setPlaylist(self.playlist)
            self.song_list.append(self.b) 
            #retreival of image and details from mp3_list

            self.a_tag = TinyTag.get(self.mp3_list[0],image=True)
            self.ui.songname_lbl.setText(self.a_tag.title + ' - ' + self.a_tag.albumartist) 
            im = self.a_tag.get_image()
            pi = Image.open(io.BytesIO(im))

# Save as PNG, or JPEG
            pi.save('cover.jpeg')
            pixmap = QPixmap('cover.jpeg')
            self.ui.pic_label.setPixmap(pixmap)
            self.getmusicdata()
            os.remove(self.b)
            os.remove('cover.jpeg')

        elif self.filename[0].endswith('.wav'):
            pixmap2= QPixmap('wav_image.jpeg')
            self.ui.pic_label.setPixmap(pixmap2)
            self.ui.songname_lbl.setText('')
            if self.filename[0] != '':
                url = QUrl.fromLocalFile(self.filename[0])
                self.song_list=[]
                self.song_list.append(self.filename[0]) 
                if self.playlist.mediaCount() == 0:
                    self.playlist.addMedia(QMediaContent(url))
                    self.player.setPlaylist(self.playlist)
                    
                    self.getmusicdata()
                    self.ui.play_btn.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
                    self.pp=True
                else:
                    self.playlist.clear()
                    self.playlist.addMedia(QMediaContent(url))
                    
                    self.getmusicdata()
                    self.ui.play_btn.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
                    self.pp=True

    def openFolder(self):

        if self.playlist.mediaCount() != 0:
            self.folderIterator()
            try:
                self.getmusicdata()
            except Exception:
                pass
        else:
            self.folderIterator()
            self.player.setPlaylist(self.playlist)
            #print(self.playlist)
            self.player.playlist().setCurrentIndex(0)
            self.player.pause()
            try:
                self.getmusicdata()
            except Exception:
                pass
            
    
    def folderIterator(self):
        folderChosen = QFileDialog.getExistingDirectory(self, 'Open Music Folder', '~') #folderchosen is path of the selected folder
        print(folderChosen)
        if folderChosen != '':
            self.song_list=[]
            self.playlist.clear()
            pixmap2= QPixmap('wav_image.jpeg')
            self.ui.pic_label.setPixmap(pixmap2)
            self.ui.songname_lbl.setText('')
            it = QDirIterator(folderChosen)
            self.pp = True
            self.ui.play_btn.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
            #self.play_func()
            it.next()
            while it.hasNext():
                if it.fileInfo().isDir() == False and it.filePath() != '.':
                    fInfo = it.fileInfo()
                    if fInfo.suffix() in ('wav'):
                        self.song_list.append(it.filePath())
                        self.playlist.addMedia(QMediaContent(QUrl.fromLocalFile(it.filePath())))
                        self.pp = True
                        self.ui.play_btn.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
                it.next()
                            
            if it.fileInfo().isDir() == False and it.filePath() != '.':     #for last file
                fInfo = it.fileInfo()
                if fInfo.suffix() in ('wav'):
                    self.song_list.append(it.filePath())
                    self.playlist.addMedia(QMediaContent(QUrl.fromLocalFile(it.filePath())))
                    self.pp = True
                    self.ui.play_btn.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
                    
            if self.playlist.isEmpty():
                self.ui.songname_lbl.setText('No .wav files to play')
            
       
    def changeVolume(self,value):
        self.player.setVolume(value)
    
    def indexChanged(self):
        try:
            self.player.pause()
            self.ui.play_btn.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))    
            self.i= self.playlist.currentIndex()    
            self.getmusicdata() 
            self.player.play()  
            self.ui.play_btn.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))
        except Exception:
            pass    

    def play_func(self):

        if self.pp==True:
            self.ui.play_btn.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))
            self.music()
            self.pp= False
        elif self.pp==False:                                         
            self.timer_play.stop()
            self.ui.play_btn.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
            self.player.pause()
            self.pp=True


    def back_func(self):
        self.colorf=0
        self.db=0
        url = QUrl.fromLocalFile(self.song_list[self.i])
        content = QMediaContent(url)
        self.player.setMedia(content)
        self.music()


    def next_func(self):
        if self.playlist.mediaCount() == 0:
            self.openFile()
        elif self.playlist.mediaCount() != 0: 
            self.player.playlist().next()
           

    def pos_changed(self,pos):
        self.ui.prog_slider.setValue(pos)
        if pos==0:
            self.colorf=0
            
        
        self.ui.start_lbl.setText(time.strftime("%M:%S", time.gmtime(pos/1000)))

    def duration_changed(self,dur):
        self.ui.prog_slider.setRange(0,dur)

    def set_position(self, position):
        self.player.setPosition(position)

    def getmusicdata(self):
            time_series, sample_rate = librosa.load(self.song_list[self.i],res_type="kaiser_fast")  # getting information from the file

            # getting a matrix which contains amplitude values according to frequency and time indexes
            stft = np.abs(librosa.stft(time_series, hop_length=512, n_fft=2048*4)) 

            self.spectrogram = librosa.amplitude_to_db(stft, ref=np.max)  # converting the matrix to decibel matrix #frame wise freq n time matrix

            frequencies = librosa.core.fft_frequencies(n_fft=2048*4)  # getting an array of possible frequencies

            # getting an array of time taken
            times = librosa.core.frames_to_time(np.arange(self.spectrogram.shape[1]), sr=sample_rate, hop_length=512, n_fft=2048*4)
            self.ui.end_lbl.setText(time.strftime("%M:%S", time.gmtime(times[len(times) - 1])))
            #print(time.strftime("%M:%S", time.gmtime(times[len(times) - 1])))

            self.time_index_ratio = len(times)/times[len(times) - 1]
            self.frequencies_index_ratio = len(frequencies)/frequencies[len(frequencies)-1]
      
    def get_decibel(self,target_time, freq): #returns the decibel value of sound for given time and freq

     #print(spectrogram[int(freq * frequencies_index_ratio)][int(target_time * time_index_ratio)])
        return self.spectrogram[int(freq * self.frequencies_index_ratio)][int(target_time * self.time_index_ratio)]


    def paintEvent(self,event):   
        #print('hii')
        painter = QPainter(self)
        try:
            for b in self.bars:
                self.db+=self.get_decibel(self.player.position()/1000.0,b.freq)
            self.db=self.db/len(self.bars)
            #print(self.db)
            if self.get_decibel(self.player.position()/1000.0,self.bars[0].freq)>-20 and self.get_decibel(self.player.position()/1000.0,250)>-35 and self.db>-57:
                if self.colgrd == 0:
                    self.colorf=1
                 
        except Exception:
            pass
        if self.colorf==1:
            grad1 = QLinearGradient(200,0,551,0)
            grad1.setColorAt(0.0, Qt.cyan)
            grad1.setColorAt(0.25, Qt.green)
            grad1.setColorAt(0.35, Qt.yellow)
            grad1.setColorAt(0.60, Qt.red)
            grad1.setColorAt(0.8, Qt.magenta)
            grad1.setColorAt(0.9, Qt.darkMagenta)
            grad1.setColorAt(1.0, Qt.blue)
            painter.setBrush(QBrush(grad1))
            painter.setPen(Qt.black)
        
        else :
            try:
                if self.col.isValid():
                    my_brush= QBrush()
                    c= QColor(self.col.name())
                    my_brush.setStyle(Qt.SolidPattern)
                    my_brush.setColor(c)
                    painter.setBrush(my_brush)   
                    painter.setPen(Qt.black)
            except:
                painter.setBrush(QBrush(Qt.white, Qt.SolidPattern))
                painter.setPen(Qt.black) 

        try:
            for b in self.bars:
                b.updatebar(self.deltaTime, self.get_decibel(self.player.position()/1000.0, b.freq))
                self.x1, self.y1, self.width1, self.height1, self.max_height= b.abc()
                painter.drawRect(self.x1, self.y1 , int( self.width1) , -abs(self.height1))  
        except Exception:
            pass

    def ok(self):      
        self.col= QColorDialog.getColor()
        self.colorf = 0
        self.colgrd = 1
        
    def grad(self):
        self.colgrd=0
        
    def create_bars(self):
        
        self.timer.start()

        screen_w = 351
        
        frequencies = np.arange(100, 8000, 400)

        r = len(frequencies)

        width = screen_w/r

        x = 200

        for c in frequencies:
            self.bars.append(AudioBar(x, 250, c, (0, 0, 0), max_height=200, width=width))
            x += width


        self.t = self.timer.elapsed()
        #print(self.t)
        self.getTicksLastFrame = self.t      #time taken by bars to create

    

    def music(self):
        self.player.play()
        self.timer_play.start() 

        
    # Run until the user asks to quit
    def chutiya_while(self): 
        self.t = self.timer.elapsed()   #combined time taken
        self.deltaTime = (self.t - self.getTicksLastFrame) / 1000.0     #time passed in music
        self.getTicksLastFrame = self.t
        self.repaint()

    
class AudioBar(): 

    def __init__(self, x, y, freq, color, width=50, min_height=0, max_height=100, min_decibel=-80, max_decibel=0):

        self.x, self.y, self.freq = x, y, freq

        self.color = color

        self.width, self.min_height, self.max_height = width, min_height, max_height

        self.height = min_height

        self.min_decibel, self.max_decibel = min_decibel, max_decibel

        self.__decibel_height_ratio = (self.max_height - self.min_height)/(self.max_decibel - self.min_decibel) 

    def abc(self):
        
        return self.x, self.y, self.width, self.height, self.max_height

    def updatebar(self, dt, decibel):

        desired_height = decibel * self.__decibel_height_ratio + self.max_height    

        speed = (desired_height - self.height)/0.1 

        self.height += speed * dt           

        self.height = self.clamp(self.min_height, self.max_height, self.height)      

    
    def clamp(self,min_value, max_value, value):

        if value < min_value:
            return min_value

        if value > max_value:
            return max_value

        return value
            


if __name__ == "__main__":
    import warnings
    warnings.filterwarnings("ignore")
    app = QApplication(sys.argv)
    m_obj= music_player()
    #m_obj.show()
    sys.exit(app.exec_())
