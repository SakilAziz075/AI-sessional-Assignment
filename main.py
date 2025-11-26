from AI_phase1 import generate_schedules, write_to_csv
from genetic_algorithm import genetically_enhance
from p2_timetable import P2TimeTable
import streamlit as st

my_bar = 0
pat_bar = 0
result_df = None

if 'generated_df' not in st.session_state:
    st.session_state.generated_df = None
if 'penalty_min' not in st.session_state:
    st.session_state.penalty_min = "Never calculated"

def perform_the_jaadu():
    global morning_slots, working_days, slots_per_day, morning_slots, num_tts, patience, course_file, batch_file, my_bar, result_df
    schedules = generate_schedules(batch_file=batch_file, course_file=course_file, classes_per_day=slots_per_day, classes_before_recess=morning_slots, total_days=working_days, num_schedules=num_tts)
    p2_tts = [P2TimeTable(k, morning_classes=morning_slots, working_days=working_days, slots_per_day=slots_per_day) for k in schedules]
    final = genetically_enhance(p2_tts, my_bar, pat_bar, max_patience=patience)
    write_to_csv([final.batch_wise_slots])
    st.session_state.generated_df = final.getDataFrame()
    st.toast("Succesfully generated!")

morning_slots = 4
st.write("# Timetable Scheduler")
st.space()
course_file = st.file_uploader("Please upload CSV file containing course details", type="csv", accept_multiple_files=False)
batch_file = st.file_uploader("Upload CSV file containing batch-course mappings", type="csv", accept_multiple_files=False)
st.divider()
working_days = int(st.number_input("No. class days per week", min_value=1, max_value=7, step=1, value=5))
slots_per_day = int(st.number_input("No. of slots per day", min_value=morning_slots, max_value=24, step=1, value=7))
morning_slots = int(st.number_input("No. of forenoon slots per day", min_value=1, max_value=slots_per_day, step=1, value=4))
num_tts = int(st.number_input("No. of intermediate timetables", min_value=1, max_value=1000, step=1, value=100))
patience = int(st.number_input("Patience for genetic algorithm", min_value=1, max_value=10000, step=1, value=200))

st.space()
if course_file and batch_file:
    st.button("Generate Timetable", type="primary", icon=":material/wand_stars:", on_click=perform_the_jaadu)
else:
    st.warning("Please upload both CSV files to generate the timetable.")
st.divider()

my_bar = st.progress(1.0, text=f"Least penalty acheived: {st.session_state.penalty_min}")
pat_bar = st.progress(100, text=f"Patience: {patience}")
st.divider()

if st.session_state.generated_df is not None:
    st.write("## Generated Timetable")
    st.dataframe(data=st.session_state.generated_df)
    
    # Optional: Add a download button
    csv = st.session_state.generated_df.to_csv(index=False).encode('utf-8')
    st.download_button("Download CSV", data=csv, file_name="timetable.csv", mime="text/csv")