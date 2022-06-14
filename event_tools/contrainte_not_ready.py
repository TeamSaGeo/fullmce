from .contrainte import Contrainte

class Contrainte_not_ready:
    def __init__(self, name, source_path, ready, field):
        self.field = field

        # invoking the __init__ of the parent class
        Contrainte.__init__(self, name, source_path, ready)
