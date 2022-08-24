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

    def settype(self, type):
        self.type = type

    def setnew_field_name (self, field_name):
        self.new_field_name = field_name

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
        return list(filter(lambda x: x,self.inputLayer.vlayer.uniqueValues(self.field_idx,-1)))

    def get_mimimum_value(self):
        result = self.inputLayer.vlayer.minimumValue(self.field_idx)
        if not result:
            result = min(self.getfield_values())
        return result

    def get_maximum_value(self):
        return self.inputLayer.vlayer.maximumValue(self.field_idx)

    def __getattr__(self, item):
        return 'inputData does not have `{}` attribute.'.format(str(item))
