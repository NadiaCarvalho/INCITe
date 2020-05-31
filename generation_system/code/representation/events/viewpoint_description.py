"""
Dictionary of descriptions of viewpoints for
the interface
"""

DESCRIPTION = {
    "parts": {

        "metadata.piece_title": "Title of the piece to which the event belongs",
        "metadata.composer": "Composer of the piece to which the event belongs",
        "metadata.part": "Part of a piece to which the event belongs",
        "metadata.voice": "Voice in a part of the piece to which the event belongs",
        "metadata.instrument": "Instrument of the part of the piece to which the event belongs",

        "basic.chord": "Event is a Chord?",
        "basic.grace": "Event is a Grace Note?",
        "basic.rest": "Event is a Rest?",
        "basic.bioi": "Basic Interval of Offset of the event to penultimate event",

        "duration.length": "Length of the event",
        "duration.type": "Type of event (Quarter Note, Half Note, ...)",
        "duration.dots": "Number of Dots applied to the duration type of the event",
        "duration.slash": "Number of slashes (only applies when event is a grace note)",

        "pitch.cpitch": "Midi Pitch of event; if it has decimals, the event is microtonal.",
        "pitch.dnote": "Note in C, D, E, F, G, A, B notation",
        "pitch.octave": "Octave in which the note is inserted",
        "pitch.accidental": "Accidental applied to dnote",
        "pitch.microtonal": "Microtonality of event in cents",
        "pitch.pitch_class": "Pitch class of note",
        "pitch.chordPitches": "Pitches of event if event is chord.",

        "expressions.articulation": "Articulations of Event",
        "expressions.breath_mark": "Event has a breath mark?",
        "expressions.dynamic": "Dynamics of Event",
        "expressions.fermata": "Event has a fermata?",
        "expressions.expression": "Expressions of Event",
        "expressions.ornamentation": "Ornamentations of Event",
        "expressions.rehearsal": "Event has a rehearsal mark?",
        "expressions.volume": "Volume of the event (according to expressions present)",
        "expressions.notehead.type": "Type of notehead",
        "expressions.notehead.fill": "Fill of notehead",
        "expressions.notehead.parenthesis": "Notehead has surrounding parenthesis?",
        "expressions.tie.type": "Type of tie (if existent) in event",
        "expressions.tie.style": "style of tie (if existent) in event. Can be normal, dotted, etc.",
        "expressions.slur.begin": "Is at the beginning of a slur?",
        "expressions.slur.end": "Is at the end of a slur?",
        "expressions.slur.between": "Is in a slur?",
        "expressions.clef": "Clef of event",

        "key.keysig": "Key Signature (by number of sharps/flats) at the time of Event.",
        "key.measure.key": "Key Analysis at the measure level.",
        "key.measure.scale_degree": "Scale Degree of Event relating to Key Analysed at measure.",
        "key.signatures.key": "Key Analysis at the entire piece level",
        "key.signatures.scale_degree": "Scale Degree of Event relating to Key Analysed at entire piece.",

        "time.timesig": "Time Signature at the time of Event",
        "time.pulses": "",
        "time.barlength": "",
        "time.ref.type": "",
        "time.ref.value": "",
        "time.metro.value": "",
        "time.metro.sound": "",
        "time.metro.text": "",
        "time.barlines.double": "",
        "time.barlines.repeat.exists_before": "",
        "time.barlines.repeat.direction": "",
        "time.barlines.repeat.is_end": "",

        "phrase.boundary": "",
        "phrase.length": "",

        "derived.anacrusis": "Event is in Anacrusis?",
        "derived.seq_int": "",
        "derived.contour": "",
        "derived.contour_hd": "",
        "derived.upwards": "",
        "derived.downwards": "",
        "derived.no_movement": "",
        "derived.closure": "",
        "derived.registral_direction": "",
        "derived.intervallic_difference": "",
        "derived.fib": "",
        "derived.posinbar": "",
        "derived.beat_strength": "",
        "derived.tactus": "",
        "derived.intfib": "",
        "derived.thrbar": "",
        "derived.intphrase": ""
    },

    "vertical": {

        "duration.length": "",
        "duration.type": "",
        "duration.dots": "",

        "tie.type": "",
        "tie.style": "",

        "basic.root": "",
        "basic.pitches": "",
        "basic.cardinality": "",
        "basic.inversion": "",
        "basic.prime_form": "",
        "basic.quality": "",

        "classes.pc_ordered": "",
        "classes.pc_cardinality": "",
        "classes.pitch_class": "",
        "classes.forte_class": "",
        "classes.forte_class_number": "",

        "quality.is_consonant": "",
        "quality.is_major_triad": "",
        "quality.is_incomplete_major_triad": "",
        "quality.is_minor_triad": "",
        "quality.is_incomplete_minor_triad": "",
        "quality.is_augmented_sixth": "",
        "quality.is_french_augmented_sixth": "",
        "quality.is_german_augmented_sixth": "",
        "quality.is_italian_augmented_sixth": "",
        "quality.is_swiss_augmented_sixth": "",
        "quality.is_augmented_triad": "",
        "quality.is_half_diminished_seventh": "",
        "quality.is_diminished_seventh": "",
        "quality.is_dominant_seventh": "",

        "key.keysig": "",
        "key.measure.key": "",
        "key.measure.certainty": "",
        "key.measure.function": "",
        "key.signatures.key": "",
        "key.signatures.certainty": "",
        "key.signatures.function": ""
    }
}