#UI and Util
import pyforms
from pyforms.basewidget import BaseWidget
from pyforms.controls   import ControlFile
from pyforms.controls   import *
from pyforms.controls   import ControlSlider
from pyforms.controls   import ControlPlayer
from pyforms.controls   import ControlButton
import sys,os
from PIL import Image, ImageFilter
from shutil import copyfile

try:
    from keras_contrib.layers.normalization import InstanceNormalization
except ImportError:
    os.system('pip install git+https://www.github.com/keras-team/keras-contrib.git')

## Keras
import scipy
import matplotlib.pyplot as plt
from keras.preprocessing.image import ImageDataGenerator, load_img, img_to_array
from keras.models import Sequential, load_model
import scipy
from PIL import Image
import numpy as np
from keras_contrib.layers.normalization import InstanceNormalization
import tensorflow as tf
import cv2

# Detection
import YOLO
from keras import backend as K


#mongoDB
import mongo


global model
model = load_model('./models/gen_model2.h5')
model.load_weights('./models/gen_weights2.h5')
global graph
graph = tf.get_default_graph()

TEMP = "./temp/"
_filename=""
path=""

#Batch
import glob

class Pixie(BaseWidget):


    def __init__(self, *args, **kwargs):
        super().__init__('Pixie')
        tempath=""

        #mainMenu
        self.mainmenu = [
            { 'File': [
                    {'Open': self.__openEvent},
                    '-',
                    {'Save': self.__saveEvent}
                ]
            }
        ]
        #definition
        toolsBox = ToolsBox()
        toolsBox.parent = self

        self._dockleft = ControlDockWidget()
        self._dockleft.value =  toolsBox



        self._imglabel = ControlLabel()
        self._ControlImage  = ControlPlayer('canvas')

        self._ToolsBox__updateImage("")
        self._detail = ControlLabel('Detail')


    def __openEvent(self):
        self.__image_file_selection_event()
    def __saveEvent(self):
        if self.path !="":
            try:
                copyfile(self.tempath+"-current.jpg",self.path)
                self.success(msg="Save to "+self.path+" Completed")
            except: pass
        pass

    def __image_file_selection_event(self):

        open = ControlFile('image')
        open.click()
        fname = open.value.split("/")

        _filename = fname[len(fname)-1]
        ## check blank path
        if  open.value =="":
            return
        ## is image
        try :
            img= cv2.imread(open.value)
            height, width,alp = img.shape
        except:
            self.alert(msg="File is not a image")
        #check for file type

        self.tempath=""
        self.path = open.value

        self.title = "Open file "+path
        self._imglabel.value  =  _filename
        self.tempath = TEMP+_filename
        copyfile(self.path, self.tempath)

        self._ToolsBox__updateImage(self.tempath)





    def _ToolsBox__updateImage(self,path):

        try :
            self._ControlImage.value  = path
            self._ControlImage.videoPlay_clicked()
        except: pass ## case no vid load
    def _ToolsBox__updatedetail(self,txt):
        self._detail.value = str(txt)

class ToolsBox(BaseWidget):

    color = ""
    def read_classes(self,classes_path):
        with open(classes_path) as f:
            class_names = f.readlines()
        class_names = [c.strip() for c in class_names]
        return class_names

    def appliedAlph_event(self):

        try:
            ''' 
            im = Image.open(self.parent.tempath)
            im2 = im.filter(ImageFilter.MinFilter(int(self._sld_blur.value)))
            im2.save(self.parent.tempath+"-current","png")
            Pixie.__updateImage(self.parent,self.parent.tempath+"-current")
            '''
            img= cv2.imread(self.parent.tempath)
            color= cv2.imread(self.parent.tempath+"-colorlayer.jpg")
            newImage = 1.0 * img +  (self._sld_blur.value*.01) * color

            scipy.misc.imsave(self.parent.tempath+"-merg.jpg",   newImage)
            Pixie.__updateImage(self.parent,self.parent.tempath+"-merg.jpg"   )
        except:
            pass
    def _detections_event(self):

        batchCount = BatchCount()
        batchCount.parent = self.parent
        batchCount.show()

    def _detection_event(self):

        classtype = self.read_classes("./model_data/coco_classes.txt")
        try:
            output, out_boxes, out_classes , path = YOLO.predict(K.get_session(), self.parent.tempath.replace('temp/',""))
        except:
            Pixie.alert(self.parent,msg="File shape error")
            return


        classDict = {}
        item=[]
        for j in out_classes:
            item.append(classtype[j])

        for c in item:
            classDict[c] = classDict.get(c, 0) + 1
        #print(sorted(classDict.items(), key = lambda x: x[1], reverse = True))
        output += " "+ str(sorted(classDict.items(), key = lambda x: x[1], reverse = True))
        Pixie.__updateImage(self.parent,path)
        Pixie.__updatedetail(self.parent,output)



    def __init__(self):

        BaseWidget.__init__(self,'window')

        #Definition of the forms fields
        self._sld_blur    = ControlSlider("Alpha",min=0)
        self._sld_blur.max = 100

        self.colorize   = ControlButton("Colorize By AI")
        self.classify  = ControlButton("Image Detection")
        self.b_classify  = ControlButton("Object Detection batch")

        #Define the controller action
        self.classify.value = self._detection_event
        self.colorize.value = self.__colorizeAction
        self._sld_blur.changed_event = self.appliedAlph_event
        self.b_classify.value = self._detections_event

    def imread(self,path):
            return scipy.misc.imread(path, mode='RGB').astype(np.float)

    def imprep(self,path) :
            c = self.imread(path)
            c = scipy.misc.imresize(c, (128, 128))
            c = np.array(c)/125.5 - 1.#edges
            c = np.expand_dims(c, axis=0)
            return  c
    def __colorizeAction(self):
        print(self.parent.tempath)
        try:
            img= cv2.imread(self.parent.tempath)
            height, width,alp = img.shape

            im =self.imprep(self.parent.tempath)

            with graph.as_default():
                    colorize = model.predict(im)

                    color =scipy.misc.imresize( np.concatenate(colorize),(height,width))
                    scipy.misc.imsave(self.parent.tempath+"-colorlayer.jpg",   color)
                    newImage = 1.0 * img + 0.9 * color
                    #print(color.shape)
                    scipy.misc.imsave(self.parent.tempath+"-current.jpg",   newImage)
                    Pixie.__updateImage(self.parent,self.parent.tempath+"-current.jpg"   )
        except: self.alert(msg="Shape ERROR")



class BatchCount(BaseWidget):

    def read_classes(self,classes_path):
        with open(classes_path) as f:
            class_names = f.readlines()
        class_names = [c.strip() for c in class_names]
        return class_names

    def __init__(self):
        BaseWidget.__init__(self,'Batch Object Detection')


        self.batchFolder =""
        self.batchFile =""

        self._dir   = ControlFile()
        self.Canvas = ControlPlayer('Canvas')
        self._label1 = ControlLabel("")
        self._start = ControlButton("Count")
        self._clr = ControlButton("Clear count")
        self._Progress = ControlProgress(label="0/0")
        self._Progress.min = 0



        self._clr.value = self.clr_mongo
        self.Canvas.value = "./batchDetect/test.jpg"
        self._dir.changed_event = self.folderpath_event
        self._start.value = self._startCount

    def clr_mongo(self):
        mongo.createDatabase()
        self.success(msg="All record is cleared")
    def _startCount(self):
        if self.question(title="Begin Counting Object",msg="It would take Lot of time And replace the image with output, Are you Sure?",buttons=["No","Yes"])=="yes":
            file = []
            for filename in glob.glob(self.batchFolder+"/*.*"):
                file.append(filename)
            files_number = len(file)
            self._Progress.max = files_number


            self._label1.value = ""
            classDict = {}
            i = 1
            classtype = self.read_classes("./model_data/coco_classes.txt")
            for t in file :
                try:

                    output, out_boxes, out_classes , path = YOLO.predict(K.get_session(), t,specificPath=True)
                except:
                    self.alert(self.parent,msg="File shape error")
                    return
                self._label1.value = "{0} out of {1} files".format(i,files_number)
                i= i+1
                self._Progress.value = i
                try :

                    item=[]
                    for j in out_classes:
                        item.append(classtype[j])

                    for c in item:
                        classDict[c] = classDict.get(c, 0) + 1
                except:
                    self.alert(self,msg="error")
                print(classDict)
                self._refresh_canvas(file=t)
            #add data to  to mongo

            collec = mongo.conDB()
            for _type in classDict:
                for j in range(classDict.get(_type,0)):
                    mongo.increment(collec,_type)

            try:
                self._refresh_canvas(file=file[0])

                plt = mongo.result(collec)

                self.success(msg="Succes")
                plt.show()
            except:
                pass

        else : return
    def folderpath_event(self):
        print (os.path.dirname( self._dir.value))
        self.batchFile =self._dir.value
        self.batchFolder = os.path.dirname(self.batchFile)
        if self.batchFolder !="":
            self._label1.value ="*Every file in "+self.batchFolder+" Will be Count "
        self._refresh_canvas(file=self._dir.value)

    def _refresh_canvas(self,file="./batchDetect/test.jpg"):
        try :
            self.Canvas.value = file
            self.Canvas.videoPlay_clicked()
        except:
            pass
            # no path refresh error

if __name__ == '__main__':

    from pyforms import start_app
    start_app(Pixie)
