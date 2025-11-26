import heapq
from p2_timetable import P2TimeTable

def genetically_enhance(tt_list: list, max_patience=1000) -> P2TimeTable:
    patience = max_patience
    num_tts = len(tt_list)

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
            last_best_penalty = tt_heap[0].getScore()
            print(f"Best Penalty: {last_best_penalty}")
            patience = max_patience
        patience -= 1
    
    return heapq.heappop(tt_heap)
            