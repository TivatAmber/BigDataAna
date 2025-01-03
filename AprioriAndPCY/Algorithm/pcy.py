import collections
import itertools
from functools import partial

from .functions import *


def get_hash(item: set[int], bucket_size: int) -> int:
    return sum(item) % bucket_size


def save_bitmap(folder: str, file_name: str, bitmap: list[int]) -> None:
    bitmap: str = ''.join([str(x) for x in bitmap])
    with open(os.path.join(folder, f"{file_name}_bitmap"), 'w') as fp:
        fp.write(bitmap)


@log_time("PCY")
def pcy(raw_data: dict[str, set[str]], support_threshold: float, confidence_threshold: float, bucket_size: int,
        hash_func=get_hash, *, save_folder: str = "PCY_Result", save_file_name: str = "result",
        max_k: int = -1) -> (list[frozenset[int]], list[tuple[set[str], set[str], float]]):
    assert max_k == -1 or max_k > 0
    delete_result(save_folder)
    now_dict, reverse_dict, now_sets = pre_handle(raw_data)
    hash_func = partial(hash_func, bucket_size=bucket_size)

    single_item_count = collections.defaultdict(int)
    buckets = collections.defaultdict(int)
    for now_set in now_sets:
        for item in now_set:
            single_item_count[item] += 1
        for item in itertools.combinations(now_set, 2):
            bucket = hash_func(item)
            buckets[bucket] += 1

    # print(buckets[76045])

    frequent_single = [(frozenset({key}), support) for key, value in single_item_count.items() if
                       (support := value / len(now_sets)) >= support_threshold]
    all_frequent_items = [x[0] for x in frequent_single].copy()
    if max_k == 1: return all_frequent_items, {}

    temp_frequent_single = list(chain(*[x[0] for x in frequent_single]))
    save_result(save_folder, save_file_name, frequent_single, reverse_dict, 1)
    frequent_buckets = {key for key, value in buckets.items() if value / len(now_sets) >= support_threshold}
    bitmap = [1 if x in frequent_buckets else 0 for x in range(bucket_size)]
    save_bitmap(save_folder, save_file_name, bitmap)

    candidate_pair_count = collections.defaultdict(int)
    for now_set in now_sets:
        now_set = frozenset({item for item in now_set if item in temp_frequent_single})
        for pair in combinations(now_set, 2):
            pair = frozenset(sorted(pair))  # 注意顺序
            bucket = hash_func(pair)
            if bucket in frequent_buckets:
                candidate_pair_count[pair] += 1

    # print("1", candidate_pair_count[(13, 42)])
    # print("2", candidate_pair_count[(42, 13)]) # 注意顺序！

    frequent_pairs = [(frozenset(key), support) for key, value in candidate_pair_count.items() if
                      (support := value / len(now_sets)) >= support_threshold]
    # print(len(frequent_pairs))
    # print(frequent_pairs)
    save_result(save_folder, save_file_name, frequent_pairs, reverse_dict, 2)
    frequent_pairs, _ = zip(*frequent_pairs)
    frequent_pairs = list(frequent_pairs)
    all_frequent_items.extend(frequent_pairs)

    all_frequent_items = iterate(now_sets, frequent_pairs, support_threshold, save_folder, save_file_name,
                                 reverse_dict, all_frequent_items=all_frequent_items, start_k=2, max_k=max_k)
    rules = get_and_save_rules(now_sets, confidence_threshold, save_folder, save_file_name,
                               reverse_dict, all_frequent_items=all_frequent_items)
    return all_frequent_items, rules
