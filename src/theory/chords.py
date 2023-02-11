from src.theory import *
from src.theory.note_sequence import NoteSequence
from src.theory.notes import Note, NoteGeneric
from src.theory.constants import ChordFormulas, ChordSymbols, ChordType
from src.theory.scales import Scale, ScaleFactory, find_scale_factory_for_mode
from src.utils.utils import cycle_n_times


class Chord(NoteSequence):
    """
    Class for chord objects, built from a root note, and
    a scale to pull intervals from. Allows for inversions and
    chord extensions to be utilized
    """

    def __init__(
        self,
        root: Union[NoteGeneric, Note],
        type: ChordType,
        slash_value: Note = None,
        inversion: int = 0,
        extensions: List[str] = None,
        altered_notes: List[dict] = None,
        *args,
        **kwargs
    ) -> None:
        """Initialize a Chord.

        Args:
            root (Union[NoteGeneric, Note]): Note for root of chord.
            type (ChordType): Enum of ChordType
            slash_value (Note, optional): Altered root note for the chord. Defaults to None.
            inversion (int, optional): Inversion value for chord. Defaults to 0.
            extensions (List[str], optional): Chord extensions, built off chord_type scale. Defaults to None.
            altered_notes (List[dict], optional): In format [{"degree": int, "fn": flatten/sharpen}, ...]. Defaults to None.

        Raises:
            NotImplementedError: Altered notes needs to be implemented for chords
        """

        self.root = root
        self.type = type
        self.inversion = (
            inversion
            if inversion in inversion_values
            else ValueError("Inversion value invalid")
        )
        self.slash_value = slash_value
        self.extensions = extensions
        self.altered_notes = altered_notes

        if not self.slash_value is None and self.inversion > 0:
            raise ValueError("Cannot invert a slash chord.")

        self.formula = ChordFormulas.get(self.type, None)
        notes = self._set_notes()
        super(Chord, self).__init__(name=self.type.name, notes=notes, *args, **kwargs)

        if self.altered_notes:
            raise NotImplementedError("altered_notes for chord")
            self.set_altered_notes(notes)

    def __str__(self, alt_symbol:bool=False) -> str:
        symb =  ChordSymbols[self.type][0] if not alt_symbol else ChordSymbols[self.type][1]
        s = f"{self.root}{symb}"
        if self.slash_value:
            s += " / " + self.slash_value
        elif self.inversion > 0:
            s += f" / {self.notes[0]}"
        return s

    def _set_notes(self) -> None:
        notes = []

        # Get relative scale
        base_scale_type = self.formula["scale"]
        sf = find_scale_factory_for_mode(base_scale_type)
        scale = sf.generate_scale(self.root)

        # Select appropriate notes, considering extensions
        notes = [scale.get_notes()[idx - 1] for idx in self.formula["intervals"]]
        if self.extensions:
            # TODO: Add in option for flat and sharp extensions

            # Add in the notes by mod the length of the scale // 9 is the 2, 11 is the 4..

            # NOTE: The octave is IN the scale. So add 9, the 8th index (9-1) is root note again
            # this messes with using mod to circulate through it
            # Dealt with in scale.get_interval

            notes.extend([scale.get_interval(val) for val in self.extensions])

        # Check for inversion
        if self.inversion:
            notes = cycle_n_times(self.inversion)

        # Check for altered root
        if self.slash_value:
            notes = [self.slash_value] + notes

        return notes

    def is_diatonic(self, scale: Scale) -> bool:
        """Checks if this chord is diatonic in the given scale"""
        return all([note in scale for note in self.notes])
