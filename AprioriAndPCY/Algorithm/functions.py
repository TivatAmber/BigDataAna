import os.path
import time
from itertools import combinations, chain


def log_time(name):
    def decorator(func):
        def wrapper(*args, **kwargs):
            now = time.time()
            func(*args, **kwargs)
            print(f"{name} Total Time: {time.time() - now}")

        return wrapper

    return decorator


def pre_handle(raw_data: dict[str, set[str]]) -> (dict[str, int], dict[int, str], list[set[int]]):
    now_sets = [value.union([key]) for key, value in raw_data.items()]
    str_to_int: dict[str, int] = {}
    reverse_dict: dict[int, str] = {}
    for now_set in sorted(now_sets):
        for word in sorted(now_set):
            if word not in str_to_int:
                str_to_int[word] = len(str_to_int)
                reverse_dict[str_to_int[word]] = word
    now_sets = [sorted({str_to_int[word] for word in now_set}) for now_set in now_sets]
    now_sets = [frozenset(now_set) for now_set in now_sets]
    return str_to_int, reverse_dict, now_sets


def get_frequent_items(now_items: list[frozenset[int]], overall_sets: list[set[int]],
                       support_threshold: float) -> list[tuple[frozenset[int], float]]:
    now_dict = {now_item: 0 for now_item in now_items}
    for now_set in overall_sets:
        for now_item in now_items:
            if now_item.issubset(now_set):
                now_dict[now_item] += 1
    ret_sets = []
    for key, value in now_dict.items():
        if (support := value / len(overall_sets)) >= support_threshold:
            ret_sets.append((frozenset(key), support))
    return ret_sets


def union_items(now_items: list[frozenset[int]], target_k: int) -> list[frozenset[int]]:
    now_k: int = target_k - 1
    ret_sets: list[frozenset[int]] = []
    for first_index in range(len(now_items)):
        for second_index in range(first_index + 1, len(now_items)):
            l1 = sorted(now_items[first_index])[:now_k - 1]
            l2 = sorted(now_items[second_index])[:now_k - 1]
            if l1 == l2 and (candidate := now_items[first_index] | now_items[second_index]) not in ret_sets:
                ret_sets.append(frozenset(candidate))
    return ret_sets


def prune_items(now_items: list[frozenset[int]], lst_frequent_items: list[frozenset[int]],
                target_k: int) -> list[frozenset[int]]:
    now_k = target_k - 1
    ret_sets: list[frozenset[int]] = []
    for now_item in now_items:
        should_ret = True
        for sub_item in combinations(now_item, now_k):
            if frozenset(sub_item) not in lst_frequent_items:
                should_ret = False
        if should_ret:
            ret_sets.append(now_item)
    return ret_sets


def delete_result(folder: str) -> None:
    if not os.path.exists(folder): return
    for file in os.listdir(folder):
        os.remove(os.path.join(folder, file))


def save_result(folder: str, name: str, now_items: list[tuple[frozenset[int], float]], now_dict: dict[int, str],
                now_k: int) -> None:
    if not os.path.exists(folder):
        os.mkdir(folder)
    print(f"k: {now_k}, total: {len(now_items)}")
    with open(os.path.join(folder, f"{name}_{now_k}"), 'w') as fp:
        for now_item, value in sorted(now_items, key=lambda x: x[1], reverse=True):
            now_item = sorted({now_dict[word] for word in now_item})
            fp.write(f"{now_item}, {value:.2f}\n")


def get_rules(frequent_items: list[frozenset[int]], overall_sets: list[set[int]],
              confidence_threshold: float) -> list[tuple[frozenset[int], frozenset[int], float]]:
    ret_rules = []
    now_dict = {frequent_item: 0 for frequent_item in frequent_items}
    for now_item in frequent_items:
        for now_set in overall_sets:
            if now_item.issubset(now_set):
                now_dict[now_item] += 1
    # print(now_dict)

    for item in frequent_items:
        subsets = list(chain(*[combinations(item, i) for i in range(1, len(item))]))
        now_item_support = now_dict[item] / len(overall_sets)
        for subset in subsets:
            subset = frozenset(subset)
            other = item - subset
            subset_support = now_dict[subset] / len(overall_sets)
            # print(now_item_support, subset_support, now_item_support / subset_support)
            if (confidence := now_item_support / subset_support) >= confidence_threshold:
                ret_rules.append((subset, other, confidence))

    return ret_rules


def iterate(now_sets: list[set[int]], now_items: list[frozenset[int]], support_threshold: float, save_folder: str,
            save_file_name: str, reverse_dict: dict[int, str], *, all_frequent_items: list[frozenset[int]],
            start_k: int = 1, max_k: int = -1) -> list[frozenset[int]]:
    if max_k == -1: max_k = len(reverse_dict)
    k = start_k
    while now_items and (k := k + 1) <= max_k:
        candidates = union_items(now_items, k)
        candidates = prune_items(candidates, now_items, k)
        frequent_pair = get_frequent_items(candidates, now_sets, support_threshold)
        if len(frequent_pair) == 0: break
        now_items, _ = zip(*frequent_pair)
        now_items = list(now_items)
        all_frequent_items.extend(now_items)

        save_result(save_folder, save_file_name, frequent_pair, reverse_dict, k)

    return all_frequent_items


def get_and_save_rules(now_sets: list[set[int]], confidence_threshold: float, save_folder: str, save_file_name: str,
                       reverse_dict: dict[int, str], *, all_frequent_items) -> list[tuple[set[str], set[str], float]]:
    rules: list[tuple[frozenset[int], frozenset[int], float]] = get_rules(all_frequent_items, now_sets,
                                                                          confidence_threshold)
    rules: list[tuple[set[str], set[str], float]] = [
        ({reverse_dict[word] for word in antecedent}, {reverse_dict[word] for word in consequent}, value) for
        antecedent, consequent, value in rules]
    # print(len(rules))
    with open(os.path.join(save_folder, f'{save_file_name}_Rules'), 'w') as fp:
        for antecedent, consequent, value in rules:
            fp.write(f"{antecedent} -> {consequent}: {value:.2f}\n")

    return rules


def debug(all_frequent_items: list[frozenset[int]], index: int, bucket_size=2000) -> None:
    from .pcy import get_hash
    print(len(all_frequent_items))
    all_frequent_items = [sorted(item) for item in all_frequent_items]
    with open(f'debug{index}', 'w') as fp:
        for item in sorted(all_frequent_items):
            fp.write(f"{item}: {get_hash(set(item), bucket_size)}\n")
