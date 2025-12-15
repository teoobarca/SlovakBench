
import json
import sys

filename = "data/raw/grammar/lang-8-20111007-2.0/lang-8-20111007-L1-v2.dat"

total_slovak = 0
slovak_with_corrections = 0
samples = []

print(f"Analyzing {filename}...")

try:
    with open(filename, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f):
            try:
                data = json.loads(line)
                # Structure: [journal_id, sentence_id, learning_lang, native_lang, sentences, corrections]
                if len(data) > 2 and data[2] == "Slovak":
                    total_slovak += 1
                    
                    sentences = data[4]
                    corrections = data[5]
                    
                    has_correction = False
                    for corr_list in corrections:
                        if corr_list: # If there is at least one correction for a sentence
                            has_correction = True
                            break
                    
                    if has_correction:
                        slovak_with_corrections += 1
                        if len(samples) < 5:
                            samples.append(data)
            except json.JSONDecodeError:
                print(f"Error decoding line {i}")
                continue

    print(f"Total Slovak entries: {total_slovak}")
    print(f"Slovak entries with corrections: {slovak_with_corrections}")
    print("\n--- Samples with corrections ---")
    for s in samples:
        print(json.dumps(s, ensure_ascii=False, indent=2))

except FileNotFoundError:
    print(f"File not found: {filename}")
