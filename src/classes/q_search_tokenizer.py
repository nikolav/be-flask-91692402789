
import re
from typing import List

SKIP_WORDS_ = (
    'a',
    # add skip words
)

class QSearchTokenizer:
    def __init__(self, lowercase: bool = True, remove_stopwords: bool = True):
        self.lowercase        = lowercase
        self.remove_stopwords = remove_stopwords

        # skip stopwords
        self.stopwords = set(SKIP_WORDS_)

    def tokenize(self, text: str) -> List[str]:
        # Convert to lowercase if required
        if self.lowercase:
            text = text.lower()
        
        # Remove punctuation and split on whitespace
        tokens = re.findall(r'\b\w+\b', text)
        
        # Remove stopwords if required
        if self.remove_stopwords:
            tokens = [token for token in tokens if token not in self.stopwords]
        
        return tokens
