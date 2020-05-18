"""
Printing Utilities
"""


def show_sequence_of_viewpoint_with_offset(events, viewpoint):
    """
    Returns a string of a specific viewpoint for all events and offset of event
    """
    viewpoint_events = [offset_info(
        event, viewpoint) for event in events if event.check_viewpoint(viewpoint)]
    to_print = 'Viewpoint ' + viewpoint + ' : '
    to_print += ''.join(viewpoint_events)
    return to_print


def show_sequence_of_viewpoint_without_offset(events, viewpoint):
    """
    Returns a string of a specific viewpoint for all events with no offset
    """
    to_print = 'Viewpoint ' + viewpoint + ': '
    to_print += ''.join([(str(event.get_viewpoint(viewpoint)) + ' ')
                         for event in events])
    return to_print


def show_part_viewpoint(viewpoint, part, offset=False):
    """
    Shows only a viewpoint for a specific part
    """
    if offset:
        print(show_sequence_of_viewpoint_with_offset(part, viewpoint))
    else:
        print(show_sequence_of_viewpoint_without_offset(part, viewpoint))

