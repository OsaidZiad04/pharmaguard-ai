import hashlib


class MockEmbedder:
    """Deterministic placeholder embedder.

    TODO: Replace with a validated local or approved embedding model.
    """

    dimensions = 12

    def embed(self, text: str) -> list[float]:
        digest = hashlib.sha256(text.encode("utf-8")).digest()
        return [round(byte / 255, 4) for byte in digest[: self.dimensions]]

    def embed_many(self, texts: list[str]) -> list[list[float]]:
        return [self.embed(text) for text in texts]
