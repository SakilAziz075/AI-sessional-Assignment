import copy
import random
import collections
import pandas

class P2TimeTable:
    def __init__(self, phase1_timetable, morning_classes, working_days, slots_per_day):
        self.working_days = working_days
        self.slots_per_day = slots_per_day
        self.morning_classes = morning_classes
        self.num_batches = len(phase1_timetable) 
        self.num_slots = len(phase1_timetable[0]) - 1 
        self.batch_wise_slots = phase1_timetable
        self.score = self.calculateScore()

    def mutate(self, num_tries = 1000):
        conflicting = True
        while conflicting and num_tries > 0:
            num_tries -= 1
            conflicting = False

            batch1 = random.randint(0, self.num_batches - 1)
            batch2 = random.randint(0, self.num_batches - 1)
            slot1, slot2 = 0, 0
            while slot1 == slot2:
                slot1 = random.randint(0, self.num_slots - 1)
                slot2 = random.randint(0, self.num_slots - 1)
            
            # checking for batch clashes
            if batch1 != batch2:
                if self.batch_wise_slots[batch2][slot1 + 1][1] is not None or self.batch_wise_slots[batch1][slot2 + 1][1] is not None:
                    conflicting = True
                    continue

            # checking for instructor clashes
            b1_s1_ins_details = self.batch_wise_slots[batch1][slot1 + 1][1]
            if b1_s1_ins_details is not None:
                b1_s1_ins = b1_s1_ins_details[1]
                for batch in self.batch_wise_slots:
                    s2_ins_details = batch[slot2 + 1][1]
                    if s2_ins_details is not None:
                        if s2_ins_details[1] == b1_s1_ins:
                            conflicting = True
                            continue

            b2_s2_ins_details = self.batch_wise_slots[batch2][slot2 + 1][1]
            if b2_s2_ins_details is not None:
                b2_s2_ins = b2_s2_ins_details[1]
                for batch in self.batch_wise_slots:
                    s1_ins_details = batch[slot1 + 1][1]
                    if s1_ins_details is not None:
                        if s1_ins_details[1] == b2_s2_ins:
                            conflicting = True
                            continue

        if not conflicting:
            temp_tt = copy.deepcopy(self.batch_wise_slots)
            temp = temp_tt[batch1][slot1 + 1][1]
            temp_tt[batch1][slot1 + 1][1] = None
            temp_tt[batch2][slot1 + 1][1] = temp_tt[batch2][slot2 + 1][1]
            temp_tt[batch2][slot2 + 1][1] = None
            temp_tt[batch1][slot2 + 1][1] = temp
            return P2TimeTable(temp_tt, self.morning_classes, self.working_days, self.slots_per_day)
        else:
            return self     
        
    def calculateScore(self):
        # gaps between classes
        gaps = 0
        for batch in self.batch_wise_slots:
            for day_no in range(self.working_days):
                last_class_slot = -1
                for slot_no in range(self.morning_classes):
                    if batch[day_no * self.slots_per_day + slot_no + 1][1] is not None:
                        if last_class_slot != -1:
                            gaps += slot_no - last_class_slot - 1
                        last_class_slot = slot_no
                last_class_slot = -1
                for slot_no in range(self.morning_classes, self.slots_per_day):
                    if batch[day_no * self.slots_per_day + slot_no + 1][1] is not None:
                        if last_class_slot != -1:
                            gaps += slot_no - last_class_slot - 1
                        last_class_slot = slot_no

        single_class_penalty = 0
        for batch in self.batch_wise_slots:
            for day_no in range(self.working_days):
                num_classes = 0
                for slot_no in range(self.morning_classes):
                    if batch[day_no * self.slots_per_day + slot_no + 1][1] is not None:
                        num_classes += 1
                if num_classes == 1:
                    single_class_penalty += 1
                num_classes = 0
                for slot_no in range(self.morning_classes, self.slots_per_day):
                    if batch[day_no * self.slots_per_day + slot_no + 1][1] is not None:
                        num_classes += 1
                if num_classes == 1:
                    single_class_penalty += 2
        
        early_morning_penalty = 0
        for batch in self.batch_wise_slots:
            for day_no in range(self.working_days):
                if batch[day_no * self.slots_per_day + 1][1] is not None:
                    early_morning_penalty += 1
                
        class_repeat_penalty = 0
        for batch in self.batch_wise_slots:
            for day_no in range(self.working_days):
                course_list = [k[1] for k in batch[day_no * self.slots_per_day + 1: min((day_no + 1) * self.slots_per_day + 1, len(batch))] if k is not None]
                cntr = collections.Counter(course_list)
                for _, count in cntr.items():
                    if count > 1:
                        class_repeat_penalty += count

        return (1 + gaps) * (1 + single_class_penalty) * (1 + early_morning_penalty) * (1 + class_repeat_penalty)

    def getScore(self):
        return self.score
    
    def __lt__(self, other):
        return self.score < other.getScore()

    def getDataFrame(self):
        result = []
        for day_no in range(self.working_days):
            for batch in self.batch_wise_slots:
                prep_dict = {
                    "Day": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"][day_no],
                    "Batch": str(batch[0]),
                }
                for slot_no in range(self.morning_classes):
                    prep_dict[f"Slot {slot_no+1}"] = "" if batch[slot_no + 1][1] is None else f"{batch[slot_no + 1][1][0]} ({batch[slot_no + 1][1][1]})"
                prep_dict["Break"] = "Break"
                for slot_no in range(self.morning_classes, self.slots_per_day):
                    prep_dict[f"Slot {slot_no+1}"] = "" if batch[slot_no + 1][1] is None else f"{batch[slot_no + 1][1][0]} ({batch[slot_no + 1][1][1]})"
                result.append(prep_dict)
        return pandas.DataFrame(result)
