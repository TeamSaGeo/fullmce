class InputData:
    def __init__(self, name, inputLayer, ready, type):
        self.name = name
        self.ready = ready
        self.type = type
        self.inputLayer = inputLayer

    def __setattr__(self, name, value):
        self.__dict__[name] = value

    def setname(self, name):
        self.name = name

    def setready(self, ready):
        self.ready = ready

    def setinputLayer(self,inputLayer):
        self.inputLayer.remove_element(self)
        self.inputLayer = inputLayer
        inputLayer.add_element(self)

    def setfield_idx (self, field_idx):
        self.field_idx = field_idx
        field = self.inputLayer.vlayer.fields().at(self.field_idx)
        self.field_name = field.name()
        self.field_type = field.typeName()

    def getfield_values(self):
        return list(filter(None,self.inputLayer.vlayer.uniqueValues(self.field_idx,-1)))


    def __getattr__(self, item):
        return 'inputData does not have `{}` attribute.'.format(str(item))
