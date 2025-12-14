import json
import os
from pathlib import Path

RESULTS_DIR = Path("data/results/exam/2025")

def sort_results():
    if not RESULTS_DIR.exists():
        print(f"Directory not found: {RESULTS_DIR}")
        return

    count = 0
    for f in RESULTS_DIR.glob("*.json"):
        try:
            with open(f, "r", encoding="utf-8") as fp:
                data = json.load(fp)
            
            # Sort results by question_id (numeric sort if possible)
            results = data.get("results", [])
            
            # Helper to extract integer id
            def get_id(r):
                try:
                    return int(r["question_id"])
                except ValueError:
                    return 9999
            
            start_len = len(results)
            # Sort
            results.sort(key=get_id)
            
            # Check if order changed
            is_sorted = all(results[i]["question_id"] == results[i+1]["question_id"] for i in range(len(results)-1)) # logic check invalid
            
            # Just save it
            data["results"] = results
            
            with open(f, "w", encoding="utf-8") as fp:
                json.dump(data, fp, indent=2, ensure_ascii=False)
            
            count += 1
            print(f"Sorted {f.name} ({len(results)} questions)")
            
        except Exception as e:
            print(f"Error processing {f.name}: {e}")

    print(f"✅ Sorted {count} files in {RESULTS_DIR}")

if __name__ == "__main__":
    sort_results()
