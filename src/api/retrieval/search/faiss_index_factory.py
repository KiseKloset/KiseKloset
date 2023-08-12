import faiss


class FaissIndexFactory:
    def create_index(features, method):
        n = features.shape[0]
        d = features.shape[-1]

        if method == "flat":
            index = faiss.IndexFlatL2(d)

        elif method.startswith("lsh"):
            params = method.split("_")
            nbits = int(params[-1])  # num hyperplanes

            index = faiss.IndexLSH(d, nbits)

        elif method.startswith("ivfpq"):
            quantizer = faiss.IndexFlatL2(d)

            params = method.split("_")
            nlist = int(params[-3])  # num clusters
            nprobe = int(params[-2])  # nearby clusters to search
            m = int(params[-1])  # num subvectors
            assert d % m == 0
            nbits = 8  # when using IVF+PQ, higher nbits values are not supported

            index = faiss.IndexIVFPQ(quantizer, d, nlist, m, nbits, faiss.METRIC_L2)
            index.nprobe = nprobe

        elif method.startswith("ivf"):
            quantizer = faiss.IndexFlatL2(d)

            params = method.split("_")
            nlist = int(params[-2])  # num clusters
            nprobe = int(params[-1])  # nearby clusters to search

            index = faiss.IndexIVFFlat(quantizer, d, nlist, faiss.METRIC_L2)
            index.nprobe = nprobe

        elif method.startswith("hnsw"):
            params = method.split("_")

            nearby = int(params[-3])
            efConstruction = int(params[-2])
            efSearch = int(params[-1])

            index = faiss.IndexHNSWFlat(d, nearby, faiss.METRIC_L2)
            index.hnsw.efConstruction = efConstruction
            index.hnsw.efSearch = efSearch

        else:
            index = faiss.IndexFlatL2(d)

        if not index.is_trained:
            index.train(features)

        return index
