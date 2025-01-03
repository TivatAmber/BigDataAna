import hashlib


class MinHash:
    @staticmethod
    def _hash_factory(seed):
        return lambda x: int(hashlib.sha1((str(seed) + str(x)).encode()).hexdigest(), 16)

    def __init__(self, hash_col: int = 10):
        self.hash_col = hash_col
        self.hash_func = [MinHash._hash_factory(seed) for seed in range(hash_col)]

    def compute_minhash(self, elements):
        min_hash = [float('inf')] * self.hash_col
        for element in elements:
            for i in range(self.hash_col):
                hash_val = self.hash_func[i](element)
                if hash_val < min_hash[i]:
                    min_hash[i] = hash_val
        return min_hash
