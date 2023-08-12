import faiss
import numpy as np

from .faiss_index_factory import FaissIndexFactory


class SearchEngine:
    def __init__(self, indices, features, index=None):
        super().__init__()
        self.indices = indices
        if index is None:
            self.index = FaissIndexFactory.create_index(features, "hnsw_32_32_128")
            self.index.add(features)
        else:
            self.index = index

    def run(self, query, k=1):
        _, I = self.index.search(query.unsqueeze(0).cpu().detach().numpy(), k)
        return [self.indices[i] for i in I[0] if i >= 0]

    def save(search_engine, dir, name):
        indices_path = dir / (name + ".npy")
        np.save(str(indices_path), search_engine.indices)
        index_path = dir / (name + ".index")
        faiss.write_index(search_engine.index, str(index_path))

    def load(dir, name):
        indices_path = dir / (name + ".npy")
        index_path = dir / (name + ".index")
        indices = np.load(str(indices_path))
        return SearchEngine(indices, None, faiss.read_index(str(index_path)))

    def can_load(dir, name):
        indices_path = dir / (name + ".npy")
        index_path = dir / (name + ".index")
        return indices_path.exists() and index_path.exists()
