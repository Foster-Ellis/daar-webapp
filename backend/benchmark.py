import time
import random
import requests
import statistics

API_URL = "http://localhost:8000/api/search"

WORD_BANK = {
    1: ["a", "i"],
    2: ["be", "go", "do", "up", "on", "we", "me", "my", "so", "no",
        "it", "is", "in", "at", "he", "am", "as", "by"],
    3: ["bad", "dog", "cat", "red", "run", "try", "big", "day", "man",
        "sun", "map", "car", "box", "fun",
        "the", "and", "you", "not"],
    4: ["word", "time", "work", "look", "make", "take", "good", "love", "life"],
    5: ["hello", "world", "there", "other", "place", "great", "right", "small"],
    6: ["sample", "people", "little", "should", "before", "system"],
    7: ["another", "without", "thought"],
    8: ["building", "computer", "learning"],
    9: ["something", "including", "education"],
    10: ["generation", "evaluation", "processing"],
}

def run_benchmark():

    lengths = range(1, 11)

    configs = [
        ("keyword", "occurrences", "basic",   "occurrences"),
        ("keyword", "closeness",   "basic",   "closeness"),
        ("regex",   "occurrences", "regex",   "occurrences"),
        ("regex",   "closeness",   "regex",   "closeness"),
    ]

    for label, rank_label, type_, rank in configs:
        print(f"\n--- BENCHMARK: {label} ({type_}) ranked by {rank_label} ---")

        times = []

        for L in lengths:
            word_list = WORD_BANK[L]
            runs = []

            print(f"→ Query length {L}")

            for _ in range(6):

                query = random.choice(word_list)

                try:
                    start = time.time()

                    r = requests.post(API_URL, json={
                        "query": query,
                        "type": type_,
                        "ranking": rank
                    })

                    elapsed = time.time() - start

                    # Check errors but do not crash
                    if r.status_code != 200:
                        print(f"    → Query='{query}' FAILED  status={r.status_code}")
                        runs.append(None)
                    else:
                        runs.append(elapsed)
                        print(f"    → Query='{query}'  {elapsed:.4f}s  status=200")

                except Exception as e:
                    print(f"    → ERROR for query='{query}': {e}")
                    runs.append(None)


            times.append(runs)

        # Print table
        print("\nlength,\t" + "\t".join(str(L) for L in lengths))
        for i, row in enumerate(zip(*times), start=1):
            fmt = lambda x: f"{x:.6f}" if isinstance(x, (int, float)) else "ERR"
            print(f"time {i},\t" + "\t".join(fmt(t) for t in row))

        # Compute mean/std only for valid runs
        clean_cols = [[t for t in col if isinstance(t, float)] for col in times]

        averages = [statistics.mean(col) if col else float('nan') for col in clean_cols]
        stds     = [statistics.stdev(col) if len(col) > 1 else float('nan') for col in clean_cols]

        print("average,\t"  + "\t".join(f"{a:.6f}" for a in averages))
        print("std,\t\t"    + "\t".join(f"{s:.6f}" for s in stds))
        print("mean+std,\t" + "\t".join(f"{a+s:.6f}" for a, s in zip(averages, stds)))
        print("mean-std,\t" + "\t".join(f"{a-s:.6f}" for a, s in zip(averages, stds)))



if __name__ == "__main__":
    run_benchmark()
