import random


class MelodyGenerator:
    def __init__(self, root_note="C", octave=4, scale_type="major"):
        self.root_note = root_note
        self.base_octave = octave
        self.scale_type = scale_type

        # Semitone intervals from the root for common scales
        self.scale_intervals = {
            "major": [0, 2, 4, 5, 7, 9, 11],
            "natural_minor": [0, 2, 3, 5, 7, 8, 10],
            "blues": [0, 3, 5, 6, 7, 10],  # Packed with chromatic accidental flavor!
        }

        self.note_names = [
            "C",
            "C#",
            "D",
            "D#",
            "E",
            "F",
            "F#",
            "G",
            "G#",
            "A",
            "A#",
            "B",
        ]
        self.scale_pool = self._build_scale_pool()

    def _build_scale_pool(self):
        """Builds a pool of valid notes across a couple of octaves based on music theory."""
        root_idx = self.note_names.index(self.root_note)
        intervals = self.scale_intervals.get(
            self.scale_type, self.scale_intervals["major"]
        )

        pool = []
        # Generate across 2 octaves (e.g., octave 4 and 5)
        for oct_offset in [0, 1]:
            for interval in intervals:
                total_semitones = root_idx + interval + (oct_offset * 12)
                note_idx = total_semitones % 12
                octave = self.base_octave + (total_semitones // 12)
                pool.append(f"{self.note_names[note_idx]}{octave}")
        return pool

    def generate_progression(self, length=8):
        """Generates a pleasant melodic progression using stepwise motion theory."""
        if not self.scale_pool:
            return ["C4", "D4", "E4", "F4", "G4"]

        progression = []
        # Start on the root note
        current_idx = 0
        progression.append(self.scale_pool[current_idx])

        for _ in range(length - 1):
            # Music theory rule: Prefer moving by small steps (scale degrees -1, 0, +1, +2)
            # rather than jumping wildly, which mimics vocal/instrumental phrasing.
            step = random.choice([-2, -1, -1, 1, 1, 2, 3])
            current_idx = max(0, min(len(self.scale_pool) - 1, current_idx + step))
            progression.append(self.scale_pool[current_idx])

        # Ensure the final note resolves nicely back to the root or fifth
        progression[-1] = self.scale_pool[0]
        return progression
