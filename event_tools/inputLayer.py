import ntpath
from qgis.core import QgsVectorLayer
from qgis.PyQt.QtCore import QVariant
from qgis.core import QgsField

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

    def add_new_field(self,new_field_name):
        # vlayer = contrainte.inputLayer.vlayer

        # Create new field
        vlayer_provider = self.vlayer.dataProvider()
        # new_field_name = contrainte.field_name[:-2] + "Bl"
        new_field_idx = self.vlayer.fields().indexOf(new_field_name)
        if new_field_idx == -1:
            vlayer_provider.addAttributes([QgsField(new_field_name,QVariant.Double,"double",10,2)])
            self.vlayer.updateFields()
            new_field_idx = self.vlayer.fields().indexOf(new_field_name)
        return new_field_idx

    def delete_new_field(self,field_name):
        # vlayer = contrainte.inputLayer.vlayer
        new_field_idx = self.vlayer.fields().indexOf(field_name)
        self.vlayer.dataProvider().deleteAttributes([new_field_idx])
        self.vlayer.updateFields()

    def __getattr__(self, item):
        return 'Source path does not have `{}` attribute.'.format(str(item))
