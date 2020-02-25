from music21 import stream

class Event: 
    def __init__(self, id, offset):
        self.id = id
        self.offset_time = offset
        self.viewpoints = []

    def addViewpoint(self, viewpoint):
        self.viewpoints.append(viewpoint)

    def toString(self):
        return 'Event {} at offset {}'.format(self.id, self.offset_time)