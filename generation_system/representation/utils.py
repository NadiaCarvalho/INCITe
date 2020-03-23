from music21 import *


def sign(x): return x and (1, -1)[x < 0]


def seqInt(midi_viewpoint_1, midi_viewpoint_2):
    return (midi_viewpoint_1.getInfo() - midi_viewpoint_2.getInfo())


def contour(midi_viewpoint_1, midi_viewpoint_2):
    return sign(midi_viewpoint_1.getInfo() - midi_viewpoint_2.getInfo())


# defined in (Mullensiefen and Frieler, 2004a)
def contourHD(midi_viewpoint_1, midi_viewpoint_2):
    result = midi_viewpoint_1.getInfo() - midi_viewpoint_2.getInfo()

    if abs(result) < 1:
        return 0
    elif abs(result) < 3:
        return sign(result)*1
    elif abs(result) < 5:
        return sign(result)*2
    elif abs(result) < 8:
        return sign(result)*3
    else:
        return sign(result)*4


def getLastEventThatIsNoteBeforeIndex(events, actual_index=None):
    if len(events) < 2:
        return None

    if actual_index is None:
        actual_index = len(events) - 1

    events_process = events[:actual_index]
    for i in range(len(events_process)):
        index = len(events_process) - (i + 1)
        if not events_process[index].isRest():
            return index

    return None


def showSequenceOfViewpointWithOffset(events, viewpoint):
    toPrint = 'Viewpoint ' + viewpoint + ' : '
    for event in events:
        if event.getViewpoint(viewpoint) is not None:
            toPrint += 'Off ' + str(event.getOffset()) + ': ' + \
                str(event.getViewpoint(viewpoint).getInfo()) + ', '
    return toPrint


def showSequenceOfViewpointWithoutOffset(events, viewpoint):
    toPrint = 'Viewpoint ' + viewpoint + ': '
    for event in events:
        if event.getViewpoint(viewpoint) is not None:
            toPrint += str(event.getViewpoint(viewpoint).getInfo()) + ' '
        else:
            toPrint += 'None '
    return toPrint


def getEventsAtOffset(events, offset):
    return [event for event in events if event.getOffset() == offset]


def getEventBetweenOffsetsIncluding(events, offset1, offset2=None):
    if offset2 is None:
        offset2 = events[-1].getOffset()
    return [event for event in events if offset1 <= event.getOffset() <= offset2]


def getRests(events):
    return [event for event in events if event.isRest()]


def getGraceNotes(events):
    return [event for event in events if event.isGraceNote()]
