
import json
import re

input_path = "data/raw/grammar/lang-8-20111007-2.0/lang-8-20111007-L1-v2.dat"
output_path = "data/processed/grammar/lang8_slovak_simple.json"

# Heuristics
SLOVAK_CHARS = set("áäčďéíĺľňóôŕšťúýžÁÄČĎÉÍĹĽŇÓÔŔŠŤÚÝŽ")
CZECH_CHARS = set("řůěŘŮĚ")
ENGLISH_WORDS = {"the", "is", "are", "i", "you", "he", "she", "it", "we", "they", "to", "and", "of", "in", "for", "on", "my", "your", "hello", "hi"}
SLOVAK_WORDS = {"je", "sú", "som", "si", "sme", "ste", "sa", "v", "na", "z", "zo", "k", "ku", "o", "pre", "pri", "ako", "kde", "kto", "čo", "alebo", "iba", "len", "áno", "nie"}

def is_likely_english(text):
    words = set(re.findall(r'\b[a-z]+\b', text.lower()))
    intersection = words.intersection(ENGLISH_WORDS)
    if len(intersection) >= 2: # At least 2 common English words
        return True
    return False

def is_likely_slovak(text):
    # Check for diacritics
    if any(c in SLOVAK_CHARS for c in text):
        return True
    
    # Check for common words if no diacritics (short sentences)
    words = set(re.findall(r'\b[a-z]+\b', text.lower()))
    if words.intersection(SLOVAK_WORDS):
        return True
        
    return False

def clean_text(text):
    text = re.sub(r'\[/?f-[a-z]+\]', '', text)
    text = re.sub(r'\[sline\].*?\[/sline\]', '', text)
    text = re.sub(r'\[/?sline\]', '', text) # Just in case some leftover tags
    return text.strip()

simple_pairs = []
seen_pairs = set()

print(f"Reading from {input_path}...")

try:
    with open(input_path, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                data = json.loads(line)
                # [journal_id, sentence_id, learning_lang, native_lang, sentences, corrections]
                if len(data) > 2 and data[2] == "Slovak":
                    
                    sentences = data[4]
                    corrections_list = data[5]
                    
                    for i, original_sent in enumerate(sentences):
                        if len(original_sent) < 3:
                            continue

                        if i < len(corrections_list):
                            corrs = corrections_list[i]
                            if not corrs:
                                continue
                                
                            raw_correction = corrs[0]
                            cleaned_correction = clean_text(raw_correction)
                            original_clean = original_sent.strip()
                            
                            if not cleaned_correction or original_clean == cleaned_correction:
                                continue
                            
                            # Language Filtering
                            # 1. Reject if Original is English
                            if is_likely_english(original_clean):
                                continue
                            
                            # 2. Reject if Correction is English
                            if is_likely_english(cleaned_correction):
                                continue

                            # 3. Require at least one to look Slovak?
                            # Actually, if Original doesn't look English, and we are in "Slovak" section...
                            # But we saw "Hello" -> "Dobrý deň". "Hello" is English.
                            # So my is_likely_english check should handle that.
                            
                            # Let's enforce that Correction MUST look Slovak (it's the target)
                            if not is_likely_slovak(cleaned_correction):
                                # If it's short and has no common slovak words, it might be questionable.
                                # But if it has NO slovak chars and NO common words, it's likely garbage/other language.
                                continue

                            pair_tuple = (original_clean, cleaned_correction)
                            if pair_tuple in seen_pairs:
                                continue
                            seen_pairs.add(pair_tuple)

                            pair = {
                                "original": original_clean,
                                "corrected": cleaned_correction
                            }
                            simple_pairs.append(pair)
                    
            except json.JSONDecodeError:
                continue

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(simple_pairs, f, ensure_ascii=False, indent=2)

    print(f"Extracted {len(simple_pairs)} filtered pairs to {output_path}")
    
    # Print sample
    for p in simple_pairs[:10]:
        print(f"O: {p['original']}")
        print(f"C: {p['corrected']}")
        print("-")

except FileNotFoundError:
    print(f"File not found: {input_path}")
