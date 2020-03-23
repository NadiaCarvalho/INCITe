from music21 import stream


class Event:
    def __init__(self, id, offset):
        self.id = id
        self.offset_time = offset
        self.viewpoints = {}

    def addViewpoint(self, viewpoint):
        self.viewpoints[viewpoint.getName()] = viewpoint

    def getViewpoint(self, name):
        if name in self.viewpoints:
            return self.viewpoints[name]

    def getOffset(self):
        return self.offset_time

    def isRest(self):
        return self.viewpoints['is_rest'].getInfo()

    def isGraceNote(self):
        return self.viewpoints['is_grace'].getInfo()

    def toString(self):
        to_return = 'Event {} at offset {}: \n'.format(
            self.id, self.offset_time)
        for key, viewpoint in self.viewpoints.items():
            to_return += viewpoint.toString()
        return to_return
