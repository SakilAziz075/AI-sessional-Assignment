import csv
import random
import os
import io

DEFAULT_SEED = 42

# Data Structures
BATCH_COURSES = {}     # {BatchID: [CourseCode1, ...]}
COURSE_INFO = {}       # {CourseCode: {'hours': int, 'instructor': InstructorID}}
CLASS_REQUIREMENTS = {} # {BatchID_CourseCode: RequiredHours}
CLASSES_TO_SCHEDULE = [] #list oftuples: [(BatchID, CourseCode), ...]


TOTAL_DAYS = 0
CLASSES_PER_DAY = 0
CLASSES_BEFORE_RECESS = 0
CLASSES_AFTER_RECESS = 0
TOTAL_SLOTS = 0

#utility Functions

def parse_input_file(file, required_cols):
    #Parses a CSV file and returns its content as a list of lists.
    # if not os.path.exists(filename):
    #     raise FileNotFoundError(f"Error: File not found at {filename}")

    # with open(filename, 'r', newline='') as f:

    reader = csv.reader(io.TextIOWrapper(file, encoding='utf-8'))
    header = next(reader) # Skip header
    data = [row for row in reader]

    if required_cols and len(data[0]) < required_cols:
         raise ValueError(f"Error: CSV file must have at least {required_cols} columns.")

    return data

def load_data(batch_file, course_file):
    #loads data
    global BATCH_COURSES, COURSE_INFO, CLASS_REQUIREMENTS, CLASSES_TO_SCHEDULE, TOTAL_SLOTS

    #load batch-course
    batch_data = parse_input_file(batch_file, 2)
    for row in batch_data:
        batch_id = row[0].strip()
        # Assumes courses are space-separated in the second column
        courses = [c.strip() for c in row[1].split(' ') if c.strip()]
        BATCH_COURSES[batch_id] = courses

    #load course details
    course_data = parse_input_file(course_file, 3)
    for row in course_data:
        course_code = row[0].strip()
        try:
            hours = int(row[1].strip())
        except ValueError:
            raise ValueError(f"Invalid hours value for course {course_code}: {row[1]}")

        instructor = row[2].strip()
        COURSE_INFO[course_code] = {'hours': hours, 'instructor': instructor}


    TOTAL_SLOTS = TOTAL_DAYS * CLASSES_PER_DAY

    for batch_id, courses in BATCH_COURSES.items():
        for course_code in courses:
            if course_code in COURSE_INFO:
                hours = COURSE_INFO[course_code]['hours']
                key = (batch_id, course_code)
                CLASS_REQUIREMENTS[key] = hours

                # Create the flat list of classes to schedule
                CLASSES_TO_SCHEDULE.extend([key] * hours)

    if not CLASSES_TO_SCHEDULE:
        raise ValueError("No classes scheduled. Check input files and required hours.")



def check_constraints(schedule, new_batch, new_slot, new_course):
   # check if placing (new_batch, new_course) at new_slot is valid against the currently built schedule.
  #  Schedule structure: schedule[BatchID][SlotIndex] = (CourseCode, InstructorID)
    new_instructor = COURSE_INFO.get(new_course, {}).get('instructor')

    if not new_instructor:
        print(f"Warning: Instructor not found for {new_course}. Skipping slot check.")
        return True

    #Check if the new batch already has a class at this slot, just redundancy check
    if new_batch in schedule and new_slot < len(schedule[new_batch]) and schedule[new_batch][new_slot] is not None:
        return False

    #instructor conflict
    for batch_id, slots in schedule.items():
        if batch_id == new_batch:
            continue

        if new_slot < len(slots) and slots[new_slot] is not None:
            prev_course, prev_instructor = slots[new_slot]
            if prev_instructor == new_instructor:
                return False ##conflict

    return True

def solve_backtracking(classes_to_schedule, current_schedule):
   ##recursive backtracking solver

    if not classes_to_schedule:
        print(f"Viable schedule found.")
        return format_schedule_output(current_schedule)

    index_to_schedule = random.randint(0, len(classes_to_schedule)-1)     #item(Batch, Course) to schedule
    current_batch, current_course = classes_to_schedule[index_to_schedule]  #class at the random index
    remaining_classes = classes_to_schedule[:index_to_schedule]+classes_to_schedule[index_to_schedule+1:]
#    print(f"Depth {len(classes_to_schedule)}: Selected class index: {index_to_schedule}")
    current_instructor = COURSE_INFO[current_course]['instructor']
    available_slots = list(range(TOTAL_SLOTS))

    #random slot order to find different solutions
    random.shuffle(available_slots)

    for slot_index in available_slots:

        #check for conflict
        if current_schedule[current_batch][slot_index] is not None:
            continue
        # check iinstructor conflict
        if check_constraints(current_schedule, current_batch, slot_index, current_course):
            #update the schedule
            current_schedule[current_batch][slot_index] = (current_course, current_instructor)

            #recursive step
            result = solve_backtracking(remaining_classes, current_schedule)

            if result is not None:
                return result
            #Backtrack
            current_schedule[current_batch][slot_index] = None

    return False #failed

#Output Formatting

def initialize_schedule():
    """Initializes the 3-D internal schedule structure."""
    schedule = {}
    for batch_id in BATCH_COURSES.keys():
        #slots for each batch to None
        schedule[batch_id] = [None] * TOTAL_SLOTS
    return schedule

def format_schedule_output(schedule):
    """converts the internal schedule to the required 3-D list output."""
    output = []

    #dim1: BatchID
    for batch_id, slots in schedule.items():
        batch_output = [batch_id]

        #dim2:slot (0 to TOTAL_SLOTS-1)
        for slot_index, class_info in enumerate(slots):
            #dim3: <Course code-instructor> pairs
            if class_info:
                course_code, instructor_id = class_info

                slot_data = [slot_index, (course_code, instructor_id)]
            else:
                #empty slot
                slot_data = [slot_index, None]

            batch_output.append(slot_data)
        output.append(batch_output)

    return output

def write_to_csv(schedules, filename="timetables_output.csv"):
    """Writes the list of schedules to a single CSV file."""
    with open(filename, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["Schedule_ID", "BatchID", "SlotIndex", "CourseCode", "Instructor"])

        for i, schedule_list in enumerate(schedules):
            schedule_id = i + 1

            for batch_data in schedule_list:
                batch_id = batch_data[0]

                # batch_data[1:] contains the slot data
                for slot_data in batch_data[1:]:
                    slot_index, course_instructor = slot_data

                    if course_instructor is not None:
                        writer.writerow([
                            schedule_id,
                            batch_id,
                            slot_index,
                            course_instructor[0],
                            course_instructor[1]
                        ])
    print(f"\nAll schedules saved to '{filename}'")


def get_user_input(prompt, type_func=str, default=None):
    """get input from the user with basic validation."""
    while True:
        try:
            # Display default if available
            default_str = f" [{default}]" if default is not None else ""
            user_input = input(f"{prompt}{default_str}: ").strip()

            if not user_input and default is not None:
                return default

            # Attempt to convert to the required type
            return type_func(user_input)
        except ValueError:
            print("Invalid input. Please try again.")

def generate_schedules(
    batch_file=None,
    course_file=None,
    classes_per_day=None,
    total_days=None,
    num_schedules=None,
    random_seed=DEFAULT_SEED,
    classes_before_recess=None,
    classes_after_recess=None
):
    """
    coordinating function for scheduling process.
    """
    global CLASSES_PER_DAY, TOTAL_DAYS, NUM_SCHEDULES_TO_OUTPUT
    global CLASSES_BEFORE_RECESS, CLASSES_AFTER_RECESS

    print("Timetable Scheduler Setup")


    batch_file = batch_file or get_user_input("Enter Batch-Course CSV file name", default="batches.csv")
    course_file = course_file or get_user_input("Enter Course-Hours-Instructor CSV file name", default="courses.csv")

    TOTAL_DAYS = total_days or get_user_input("Enter number of working days per week", int,default=5)
    CLASSES_PER_DAY = classes_per_day or get_user_input("Enter total number of class slots per day", int,default=7)


    CLASSES_BEFORE_RECESS = classes_before_recess or get_user_input("Enter number of classes before recess", int, default=4)
    CLASSES_AFTER_RECESS = CLASSES_PER_DAY-CLASSES_BEFORE_RECESS

    # Final Config
    random_seed = random_seed or get_user_input("Enter random seed (or leave blank for default 42)", int, default=DEFAULT_SEED)
    NUM_SCHEDULES_TO_OUTPUT = num_schedules or get_user_input("Enter number of viable schedules to output", int, default=100)

    #Validate recess configuration
    if CLASSES_BEFORE_RECESS + CLASSES_AFTER_RECESS != CLASSES_PER_DAY:
        print(f"\nWarning: Recess configuration ({CLASSES_BEFORE_RECESS} + {CLASSES_AFTER_RECESS}) does not equal total slots per day ({CLASSES_PER_DAY}). Using total slots for scheduling.")

    #Set up random seed
 #   random.seed(random_seed)

    try:
        print("\nLoading and preprocessing data...")
        load_data(batch_file, course_file)
        initial_schedule = initialize_schedule()
        timetables_found = []

        print(f"Total classes to schedule: {len(CLASSES_TO_SCHEDULE)}")
        print(f"Total slots available: {TOTAL_SLOTS}")
        print("Starting backtracking solver...")

        while len(timetables_found) < NUM_SCHEDULES_TO_OUTPUT:

            shuffled_classes = CLASSES_TO_SCHEDULE[:]
            random.shuffle(shuffled_classes)

            initial_schedule = initialize_schedule()
            attempt_count = len(timetables_found) + 1
            print(f"Attempting to find schedule #{attempt_count}...")

            #solverreturns a single schedule or None
            # The control is here: we try to find one solution per iteration.
            new_schedule = solve_backtracking(shuffled_classes,initial_schedule)

            if new_schedule is not None:
                #append the returned 3D list to the output list
                timetables_found.append(new_schedule)
            else:
                # If a solution is not found, print a message and continue
                print("Failed to find a schedule on this randomization path. Retrying.")

        if timetables_found:
            print(f"\nOutputting {len(timetables_found)} Viable Schedules")
#
 #           print("\n## Python List Output (3-Dimensional List)")
  #          for i, tt in enumerate(timetables_found):
   #             print(f"Schedule {i+1} Structure:")
    #            print(tt)

            #to csv file
            #write_to_csv(timetables_found)

        else:
            print("\nNo viable schedules found with the given constraints.")


        #return all found schedulesCod
        return timetables_found
    except (FileNotFoundError, ValueError) as e:
        print(f"\n Fatal Error: {e}")

#Example Usage

if __name__ == '__main__':


    #pass all parameters directly to avoid interactive input:
    # generate_schedules(
    #     batch_file="batches.csv",
    #     course_file="courses.csv",
    #     classes_per_day=5,
    #     total_days=5,
    #     num_schedules=5,
    #     random_seed=123
    # )

    generate_schedules()
