import ntpath
from qgis.core import QgsVectorLayer

class InputLayer:
    def __init__(self, path):
        self.path = path
        self.elements = []

    def __setattr__(self, name, value):
        self.__dict__[name] = value

    def setpath(self,path):
        self.path = path

    def setvlayer(self,vlayer):
        self.vlayer = vlayer

    def isValid(self):
        filename = ntpath.basename(self.path)
        self.name = filename.split('.')[0]
        vlayer = QgsVectorLayer(self.path,self.name,"ogr")
        if not vlayer.isValid():
            return False
        else:
            self.vlayer = vlayer
            return True

    def add_element (self,element):
        self.elements.append(element)

    def remove_element (self,element):
        self.elements.remove(element)

    def setreclass_output(self,output_path):
        self.reclass_output = output_path

    def __getattr__(self, item):
        # return super(Contrainte, self).__setattr__(item, 'orphan')
        return 'Source path does not have `{}` attribute.'.format(str(item))
