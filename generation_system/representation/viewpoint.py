from music21 import stream


class Viewpoint:  # τ
    def __init__(self, name, info):
        self.name = name
        self.info = info

    def getName(self):
        return self.name

    def getInfo(self):
        return self.info

    def partialFunction(self, event):  # Ψ[τ](event)
        return self

    def coversionSurfaceString(self, event):  # Φ[τ](event)
        return self

    def toString(self):
        return 'Viewpoint {}: {} \n'.format(self.name, self.info)
