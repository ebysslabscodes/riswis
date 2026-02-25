# src/retrieval/embedder.py

"""
RISWIS – Phase 2 Retrieval Layer
--------------------------------

Local embedding component responsible for converting raw text
into dense vector representations.

This module belongs strictly to the retrieval layer.

It does NOT:
    - Apply tier multipliers
    - Perform ranking
    - Enforce top-K
    - Execute governance logic
    - Modify audit state

It provides a pure transformation:

    text  →  embedding vector (float32, shape: N x dim)

Downstream similarity and ranking layers consume these vectors.
"""

from typing import Union, List
import numpy as np
from sentence_transformers import SentenceTransformer


class LocalEmbedder:
    """
    Local sentence-transformers embedder.

    Parameters
    ----------
    model_name : str
        HuggingFace model identifier. Default is
        'all-MiniLM-L6-v2' (384-dimensional embeddings).

    Notes
    -----
    - Embedding dimension is determined by the model architecture.
    - Output vectors are returned as float32 numpy arrays.
    - If `normalize=True`, vectors are unit length,
      enabling cosine similarity via dot product.

    Determinism Considerations
    --------------------------
    Embedding outputs depend on:
        - Model weights
        - sentence-transformers version
        - torch version

    Changing any of the above may change vector values.
    """

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model_name = model_name
        self.model = SentenceTransformer(model_name)
        self.dim = int(self.model.get_sentence_embedding_dimension())

    def embed(
        self,
        texts: Union[str, List[str]],
        normalize: bool = True,
    ) -> np.ndarray:
        """
        Generate embeddings for input text(s).

        Parameters
        ----------
        texts : str or List[str]
            Single string or list of strings to embed.
        normalize : bool
            If True, returns unit-length vectors.

        Returns
        -------
        np.ndarray
            Shape (N, dim) float32 array.
        """
        if isinstance(texts, str):
            texts = [texts]

        vectors = self.model.encode(
            texts,
            convert_to_numpy=True,
            normalize_embeddings=normalize,
            show_progress_bar=False,
        )

        return np.asarray(vectors, dtype=np.float32)


if __name__ == "__main__":
    # Development smoke test only.
    emb = LocalEmbedder()
    print("Model:", emb.model_name)
    print("Dim:", emb.dim)

    vec = emb.embed("RISWIS Phase 2 retrieval layer.")
    print("Shape:", vec.shape)
    print("First 5 values:", vec[0][:5])
