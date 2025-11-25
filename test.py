class ClassObj:
    def __init__(self, subject, professor, room):
        self.subject = subject
        self.professor = professor
        self.room = room

    def __repr__(self):
        return f"ClassObj({self.subject}, {self.professor}, {self.room})"


class Timetable:
    def __init__(self):
        # main structure
        self.data = {}   # { Batch : { Day : { Slot : ClassObj } } }

    def add_class(self, batch, day, time_slot, subject, professor, room):
        """Add (or update) a class in the timetable."""

        # Create batchs if not exists
        if batch not in self.data:
            self.data[batch] = {}

        # Create days if not exists
        if day not in self.data[batch]:
            self.data[batch][day] = {}

        # Insert or overwrite class in this slot
        self.data[batch][day][time_slot] = ClassObj(subject, professor, room)

    def get_class(self, batch, day, time_slot):
        """Return the class object in a time slot (if exists)."""
        return self.data.get(batch, {}).get(day, {}).get(time_slot)

    def get_batch_timetable(self, batch):
        """Return full timetable of a batch."""
        return self.data.get(batch, {})

    def print_timetable(self):
        """Pretty print the full timetable."""
        for batch, days in self.data.items():
            print(f"\n=== {batch} ===")
            for day, slots in days.items():
                print(f"  {day}:")
                for slot, classobj in slots.items():
                    print(f"    {slot}: {classobj}")
