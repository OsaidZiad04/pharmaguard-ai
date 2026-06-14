import math
import re
from collections import Counter
from typing import Any, Protocol


class Embedder(Protocol):
    def fit_transform(self, texts: list[str]) -> Any:
        ...

    def transform(self, texts: list[str]) -> Any:
        ...


class TfidfEmbedder:
    """TF-IDF embedder with a pure-Python fallback.

    Phase 1 uses scikit-learn when available. The fallback keeps tests and local
    demos working in minimal environments, while preserving the same public API.
    TODO: Add a sentence-transformers implementation behind this interface.
    """

    def __init__(self) -> None:
        try:
            from sklearn.feature_extraction.text import TfidfVectorizer

            self._backend = "sklearn"
            self._vectorizer = TfidfVectorizer(
                lowercase=True,
                ngram_range=(1, 2),
                stop_words="english",
                sublinear_tf=True,
                norm="l2",
            )
            self._fallback = None
        except Exception:
            self._backend = "fallback"
            self._vectorizer = None
            self._fallback = SimpleTfidfEmbedder()

    @property
    def backend(self) -> str:
        return self._backend

    def fit_transform(self, texts: list[str]) -> Any:
        if self._vectorizer is not None:
            return self._vectorizer.fit_transform(texts)
        return self._fallback.fit_transform(texts)

    def transform(self, texts: list[str]) -> Any:
        if self._vectorizer is not None:
            return self._vectorizer.transform(texts)
        return self._fallback.transform(texts)


class SimpleTfidfEmbedder:
    """Small local TF-IDF fallback used only if scikit-learn is unavailable."""

    def __init__(self) -> None:
        self._vocabulary: dict[str, int] = {}
        self._idf: dict[str, float] = {}

    def fit_transform(self, texts: list[str]) -> list[list[float]]:
        tokenized = [_tokenize(text) for text in texts]
        vocabulary = sorted({token for tokens in tokenized for token in tokens})
        self._vocabulary = {term: index for index, term in enumerate(vocabulary)}

        document_count = max(len(tokenized), 1)
        document_frequency = Counter(
            term for tokens in tokenized for term in set(tokens)
        )
        self._idf = {
            term: math.log((1 + document_count) / (1 + document_frequency[term])) + 1
            for term in vocabulary
        }
        return [self._vectorize(tokens) for tokens in tokenized]

    def transform(self, texts: list[str]) -> list[list[float]]:
        return [self._vectorize(_tokenize(text)) for text in texts]

    def _vectorize(self, tokens: list[str]) -> list[float]:
        vector = [0.0] * len(self._vocabulary)
        if not tokens:
            return vector

        counts = Counter(tokens)
        for token, count in counts.items():
            index = self._vocabulary.get(token)
            if index is None:
                continue
            vector[index] = (count / len(tokens)) * self._idf.get(token, 0.0)

        norm = math.sqrt(sum(value * value for value in vector))
        if norm == 0:
            return vector
        return [value / norm for value in vector]


def _tokenize(text: str) -> list[str]:
    words = re.findall(r"[a-z0-9]+", text.lower())
    bigrams = [f"{left} {right}" for left, right in zip(words, words[1:])]
    return words + bigrams
