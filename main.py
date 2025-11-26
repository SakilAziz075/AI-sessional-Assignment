from AI_phase1 import generate_schedules, write_to_csv
from genetic_algorithm import genetically_enhance
from p2_timetable import P2TimeTable

schedules = generate_schedules()
p2_tts = [P2TimeTable(k, 4, 5, 7) for k in schedules]
final = genetically_enhance(p2_tts)
write_to_csv([final.batch_wise_slots])