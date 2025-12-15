
import json
import math

def levenshtein(s1, s2):
    if len(s1) < len(s2):
        return levenshtein(s2, s1)
    if len(s2) == 0:
        return len(s1)
    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    return previous_row[-1]

input_path = "data/processed/grammar/lang8_slovak_simple.json"
output_path = "data/processed/grammar/ranked_candidates.md"

try:
    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    ranked_items = []
    for item in data:
        orig = item['original']
        corr = item['corrected']
        
        dist = levenshtein(orig, corr)
        length = max(len(orig), len(corr))
        
        # Difficulty score heuristic: 
        # We want high distance (lots of errors) but also reasonable length.
        # Too short = likely trivial. Too long with few errors = hard to spot but maybe not "grammatically dense".
        # Let's use distance * log(length)
        if length < 10: # Skip very short
            continue
            
        score = dist * math.log(length)
        
        ranked_items.append({
            'score': score,
            'dist': dist,
            'len': length,
            'original': orig,
            'corrected': corr
        })

    # Sort by score descending
    ranked_items.sort(key=lambda x: x['score'], reverse=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("# Ranked Candidates for Selection\n\n")
        f.write("| ID | Score | Dist | Original | Corrected |\n")
        f.write("|---|---|---|---|---|\n")
        for i, item in enumerate(ranked_items[:100]): # Top 100 to choose from
            orig = item['original'].replace('\n', ' ').replace('|', '')
            corr = item['corrected'].replace('\n', ' ').replace('|', '')
            f.write(f"| {i} | {item['score']:.2f} | {item['dist']} | {orig} | {corr} |\n")

    print(f"Ranked {len(ranked_items)} items. Top 100 written to {output_path}")

except FileNotFoundError:
    print(f"File not found: {input_path}")
