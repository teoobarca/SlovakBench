"""CoNLL-U parser and data utilities for UD Slovak SNK dataset."""
from dataclasses import dataclass, field
from typing import List, Optional, Iterator
from pathlib import Path


@dataclass
class Token:
    """Single token from CoNLL-U format."""
    id: str  # Can be range (1-2) or decimal (1.1) for special tokens
    form: str  # Word as appears in text
    lemma: str  # Base form
    upos: str  # Universal POS tag
    xpos: str  # Language-specific POS
    feats: str  # Morphological features
    head: str  # Head token ID
    deprel: str  # Dependency relation
    deps: str  # Enhanced dependencies
    misc: str  # Other annotations
    
    @property
    def is_word(self) -> bool:
        """Check if this is a regular word token (not multiword or empty node)."""
        return self.id.isdigit()
    
    @property
    def head_int(self) -> Optional[int]:
        """Get head as integer (0 = root)."""
        if self.is_word and self.head.isdigit():
            return int(self.head)
        return None


@dataclass
class Sentence:
    """A sentence with tokens and metadata."""
    sent_id: str
    text: str
    tokens: List[Token] = field(default_factory=list)
    
    @property
    def words(self) -> List[Token]:
        """Get only word tokens (exclude multiword tokens and empty nodes)."""
        return [t for t in self.tokens if t.is_word]
    
    def get_pos_sequence(self) -> List[str]:
        """Get sequence of UPOS tags for words."""
        return [t.upos for t in self.words]
    
    def get_lemma_pairs(self) -> List[tuple[str, str]]:
        """Get (form, lemma) pairs for words."""
        return [(t.form, t.lemma) for t in self.words]
    
    def get_dep_triples(self) -> List[tuple[int, str, int]]:
        """Get (token_id, deprel, head_id) triples for words."""
        return [(int(t.id), t.deprel, t.head_int) for t in self.words if t.head_int is not None]


def parse_conllu(path: Path) -> Iterator[Sentence]:
    """Parse CoNLL-U file and yield sentences."""
    current_sentence = None
    
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")
            
            if not line:
                # Blank line = sentence boundary
                if current_sentence and current_sentence.tokens:
                    yield current_sentence
                current_sentence = None
                continue
                
            if line.startswith("# "):
                # Comment line with metadata
                if current_sentence is None:
                    current_sentence = Sentence(sent_id="", text="", tokens=[])
                
                if line.startswith("# sent_id = "):
                    current_sentence.sent_id = line[12:]
                elif line.startswith("# text = "):
                    current_sentence.text = line[9:]
                continue
            
            # Token line - 10 tab-separated fields
            fields = line.split("\t")
            if len(fields) != 10:
                continue
                
            if current_sentence is None:
                current_sentence = Sentence(sent_id="", text="", tokens=[])
            
            token = Token(
                id=fields[0],
                form=fields[1],
                lemma=fields[2],
                upos=fields[3],
                xpos=fields[4],
                feats=fields[5],
                head=fields[6],
                deprel=fields[7],
                deps=fields[8],
                misc=fields[9],
            )
            current_sentence.tokens.append(token)
        
        # Don't forget last sentence
        if current_sentence and current_sentence.tokens:
            yield current_sentence


def load_ud_snk(split: str = "test") -> List[Sentence]:
    """Load UD Slovak SNK dataset.
    
    Args:
        split: One of 'train', 'dev', 'test'
    
    Returns:
        List of sentences
    """
    path = Path(f"data/raw/ud_snk/sk_snk-ud-{split}.conllu")
    if not path.exists():
        raise FileNotFoundError(f"Dataset not found: {path}")
    return list(parse_conllu(path))


def get_dataset_stats(sentences: List[Sentence]) -> dict:
    """Get basic statistics about the dataset."""
    total_tokens = sum(len(s.words) for s in sentences)
    pos_counts = {}
    for s in sentences:
        for tag in s.get_pos_sequence():
            pos_counts[tag] = pos_counts.get(tag, 0) + 1
    
    return {
        "sentences": len(sentences),
        "tokens": total_tokens,
        "avg_length": total_tokens / len(sentences) if sentences else 0,
        "pos_distribution": dict(sorted(pos_counts.items(), key=lambda x: -x[1])),
    }


if __name__ == "__main__":
    # Quick test
    for split in ["train", "dev", "test"]:
        try:
            sentences = load_ud_snk(split)
            stats = get_dataset_stats(sentences)
            print(f"\n{split.upper()}:")
            print(f"  Sentences: {stats['sentences']}")
            print(f"  Tokens: {stats['tokens']}")
            print(f"  Avg length: {stats['avg_length']:.1f}")
            print(f"  Top POS: {list(stats['pos_distribution'].items())[:5]}")
        except FileNotFoundError as e:
            print(f"  {e}")
