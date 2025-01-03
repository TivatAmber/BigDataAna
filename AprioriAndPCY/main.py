import encodings.utf_8
import hashlib
import time

import Algorithm

relative_path = '../MapReduce/sorted_relative_result.txt'
support_threshold = 0.15
confidence_threshold = 0.30
pcy_bucket_size = 100003


def new_hash_func(item: set[int], bucket_size: int) -> int:
    ret = 1
    for x in item:
        ret = (ret * x) % bucket_size
    return ret % bucket_size


def new_hash_func2(item: set[int], bucket_size: int) -> int:
    item = list(sorted(item))
    ret = int(hashlib.md5(str(item).encode()).hexdigest(), 16) % bucket_size
    return ret


if __name__ == '__main__':
    with open(relative_path, 'r') as fp:
        raw_data: dict[str, set[str]] = dict(sorted(list(eval(fp.read()).items())))

    print("Apriori:")
    Algorithm.apriori(raw_data.copy(), support_threshold, confidence_threshold, max_k=4)

    # print(new_hash_func2({123, 234}, 100))
    # print(new_hash_func2({123, 234}, 100))

    print("PCY:")
    Algorithm.pcy(raw_data.copy(), support_threshold, confidence_threshold, pcy_bucket_size, hash_func=new_hash_func,
                  max_k=4)
