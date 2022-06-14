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

    def set_reclass_output(self,vlayer,output_path):
        self.vlayer = vlayer
        self.output_path = output_path

    def __getattr__(self, item):
        # return super(Contrainte, self).__setattr__(item, 'orphan')
        return 'Contrainte does not have `{}` attribute.'.format(str(name))
