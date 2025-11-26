import heapq
from p2_timetable import P2TimeTable
import math
import streamlit as st

def genetically_enhance(tt_list: list, prg_bar, pat_bar, max_patience=1000) -> P2TimeTable:
    patience = max_patience
    num_tts = len(tt_list)
    largest_stored = False
    largest_penalty = -1

    # populate the heap initially
    tt_heap = []
    for tt in tt_list:
        heapq.heappush(tt_heap, tt)
    last_best_penalty = tt_heap[0].getScore()
    print(f"Length of tt_heap is {len(tt_heap)}")
    while patience > 0:
        temp_heap = []
        for i in range(num_tts):
            curr_tt = heapq.heappop(tt_heap)
            new_tt = curr_tt.mutate()
            heapq.heappush(temp_heap, curr_tt)
            heapq.heappush(temp_heap, new_tt)
        tt_heap.clear()
        tt_heap = temp_heap
        if (tt_heap[0].getScore() < last_best_penalty):
            if not largest_stored:
                largest_penalty = tt_heap[0].getScore()
                largest_stored = True
            last_best_penalty = tt_heap[0].getScore()
            st.session_state.penalty_min = last_best_penalty
            print(f"Best Penalty: {last_best_penalty}")
            patience = max_patience
            prg_bar.progress(math.log(last_best_penalty, largest_penalty), text=f"Least penalty achieved: {last_best_penalty}")
        pat_bar.progress(int(patience * 100 / max_patience), text=f"Patience: {patience}")
        patience -= 1
    
    return heapq.heappop(tt_heap)
            