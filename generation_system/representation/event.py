from music21 import stream

class Event: 
    def __init__(self, id, offset):
        self.id = id
        self.offset_time = offset
        self.viewpoints = []

    def addViewpoint(self, viewpoint):
        self.viewpoints.append(viewpoint)

    def toString(self):
        to_return = 'Event {} at offset {}: \n'.format(self.id, self.offset_time)
        for viewpoint in self.viewpoints:
            to_return += viewpoint.toString()
        return to_return