from solomon_chronos_planner import ChronosTemporalPlanner
from solomon_hardware.zero_copy_memory import ZeroCopyMemoryMap
import time
import math

def run_100_strengthening_tasks():
    """
    Executes a high-volume loop of 100 tasks through the Chronos retrocausal planner,
    and updates their successful end-states into the Zero-Copy memory graph.
    """
    planner = ChronosTemporalPlanner()
    mem = ZeroCopyMemoryMap(filepath="gabriel_knowledge_base.bin", initial_records=100)

    print("Beginning 100-Task Strengthening Cycle...")
    start_time = time.time()

    total_rewinds = 0
    for task_id in range(100):
        # 1. Run the task through retrocausal planner
        res = planner.execute_task_with_retrocausality(task_id, total_steps=10)
        total_rewinds += res['rewinds_used']

        # 2. Extract final energy and progress state
        final_energy = res['final_state']['energy']
        final_progress = res['final_state']['progress']

        # 3. Quantize the result and store it in True O(1) Zero-Copy memory
        # We'll normalize energy/progress into a simple float space
        weight = final_energy / 100.0
        state = math.sin(final_progress * task_id)

        mem.write_node(task_id, node_id=task_id * 100, weight=weight, state=state)

    end_time = time.time()
    mem.close()

    print(f"Cycle Complete. Total Tasks: 100")
    print(f"Total Temporal Rewinds (Divergence Nodes Patched): {total_rewinds}")
    print(f"Execution Time: {(end_time - start_time)*1000:.2f} ms")

if __name__ == '__main__':
    run_100_strengthening_tasks()