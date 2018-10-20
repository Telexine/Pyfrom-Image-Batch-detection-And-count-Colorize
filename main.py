import pyforms
from pyforms.basewidget import BaseWidget
from pyforms.controls   import ControlFile
from pyforms.controls   import *
from pyforms.controls   import ControlSlider
from pyforms.controls   import ControlPlayer
from pyforms.controls   import ControlButton
import os
from PIL import Image, ImageFilter
from shutil import copyfile

PYFORMS_STYLESHEET = 'style.css'
TEMP = "./temp/"
_filename=""
path="/Users/lexine/Desktop/final-result.png"
tempath=TEMP+"final-result.png"




class Pixie(BaseWidget):


    def __init__(self, *args, **kwargs):
        super().__init__('Pixie')

        #mainMenu
        self.mainmenu = [
            { 'File': [
                    {'Open': self.__openEvent},
                    '-',
                    {'Save': self.__saveEvent},
                    {'Save as': self.__saveAsEvent}
                ]
            }
        ]
        #definition



        print(os.curdir)

        #self._imgfile = ControlFile('image')

        toolsBox = ToolsBox()
        toolsBox.parent = self

        self._dockleft = ControlDockWidget()

        self._dockleft.value =  toolsBox



        self._imglabel = ControlLabel()
        self._ControlImage  = ControlPlayer('canvas')

        self._ControlImage.value  = path
        self._ControlImage.videoPlay_clicked()
        self._outputfile = ControlText('path')
        self.cc = ControlText('cc')
        self.dd = ControlText('dd')



        #define
       # self._imgfile.changed_event = self.__image_file_selection_event


        #self._imgfile

        #Definition of the forms fields
        '''
        self._videofile  = ControlFile('Video')
        self._outputfile = ControlText('Results output file')
        self._threshold  = ControlSlider('Threshold', default=114, minimum=0, maximum=255)
        self._blobsize   = ControlSlider('Minimum blob size', default=110, minimum=100, maximum=2000)
        self._player     = ControlPlayer('Player')
        self._runbutton  = ControlButton('Run')
       
        #Define the function that will be called when a file is selected
        self._videofile.changed_event = self.__video_file_selection_event
        #Define the event that will be called when the run button is processed
        self._runbutton.value = self.run_event
        #Define the event called before showing the image in the player
        self._player.process_frame_event = self.__process_frame
        
        #Define the organization of the Form Controls
        self._formset = [
            ('_videofile', '_outputfile'),
            '_threshold',
            ('_blobsize', '_runbutton'),
            '_player'
        ]
         '''

    def __openEvent(self):
        """
        When the videofile is selected instanciate the video in the player
        """
        self.__image_file_selection_event()
    def __saveEvent(self):
        1+1
    def __saveAsEvent(self):
        1+1

    def __image_file_selection_event(self):
        open = ControlFile('image')
        open.click()
        fname = open.value.split("/")
        print(fname)
        _filename = fname[len(fname)-1]


        #check for file type
        if(True ):
            self.path = open.value
            self.title = "Open file "+path
            self._imglabel.value  =  _filename
            self.tempath = TEMP+_filename
            copyfile(path, tempath)
            self._ControlImage.value = tempath
            self._ControlImage.videoPlay_clicked()

        else :
            #not an image
            self.alert(_filename+" is not an image")

        print(open.value)

    def _ToolsBox__updateImage(self,path):
        print(path)
        self._ControlImage.value  = path
        self._ControlImage.videoPlay_clicked()


class ToolsBox(BaseWidget):

    def appliedBlur_event(self):

        #filter =  copyfile(TEMP,TEMP+"-current")
        try:
            im = Image.open(tempath)
            im2 = im.filter(ImageFilter.MinFilter(int(self._sld_blur.value)))
            im2.save(tempath+"-current","png")
            Pixie.__updateImage(self.parent,tempath+"-current")
        except:
            1+1



    def __init__(self):

        BaseWidget.__init__(self,'Person window')

        #Definition of the forms fields
        self._sld_blur    = ControlSlider("Blur",min=0.0)
        self._sld_blur.max = 8


        self.colorize    = ControlButton("data")


        #Define the controller action
        self.colorize.value = self.__buttonAction
        self._sld_blur.changed_event = self.appliedBlur_event

    def __buttonAction(self):
        1+1

        #In case the window has a parent



if __name__ == '__main__':

    from pyforms import start_app
    start_app(Pixie)
