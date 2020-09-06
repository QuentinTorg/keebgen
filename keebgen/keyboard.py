from abc import abstractmethod
from keebgen.geometry_base import Assembly

class Keyboard(Assembly):
    @abstractmethod
    def __init__(self):
        super().__init__(parts, anchors)


class DactylManuform(Keyboard):
    def __init__(self, rows=4, cols=6):
        super().__init__()

        #TODO: add everything

