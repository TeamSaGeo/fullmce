from itertools import count
from qgis.core import QgsVectorLayer

class Contrainte:
    _ids = count(0)

    def __init__(self, name, source_path, ready):
        self.name = name
        self.source_path = source_path
        self.ready = ready
        self.id = next(self._ids)

    def __setattr__(self, name, value):
        self.__dict__[name] = value

    def setname(self, name):
        self.name = name

    def setready(self, ready):
        self.ready = ready

    def setvlayer(self,vlayer):
        self.vlayer = vlayer

    def setreclass_output(self,output_path):
        self.reclass_output = output_path

    def source_path_isvalid(self, filename):
        vlayer = QgsVectorLayer(filename,self.name, "ogr")
        if not vlayer.isValid():
            return False
        else:
            self.source_path = filename
            self.vlayer = vlayer
            return True

    def setfield(self, name, type):
        self.field_name = name
        self.field_type = type
        self.field_idx = self.vlayer.fields().indexOf(name)
        self.field_values = list(filter(None,self.vlayer.uniqueValues(self.field_idx,-1)))

    def __getattr__(self, item):
        # return super(Contrainte, self).__setattr__(item, 'orphan')
        return 'Contrainte does not have `{}` attribute.'.format(str(item))
