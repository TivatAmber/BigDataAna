from .functions import *
import os


@log_time("Apriori")
def apriori(raw_data: dict[str, set[str]], support_threshold: float, confidence_threshold: float, *,
            save_folder: str = "Apriori_Result", save_file_name: str = "result",
            max_k: int = -1) -> (list[frozenset[int]], list[tuple[set[str], set[str], float]]):
    assert max_k == -1 or max_k > 0
    delete_result(save_folder)
    now_dict, reverse_dict, now_sets = pre_handle(raw_data)
    single_item = [frozenset({num}) for num in now_dict.values()]
    frequent_pair = get_frequent_items(single_item, now_sets, support_threshold)
    now_items, _ = zip(*frequent_pair)
    now_items = list(now_items)
    all_frequent_items = now_items.copy()
    save_result(save_folder, save_file_name, frequent_pair, reverse_dict, 1)
    if max_k == 1: return all_frequent_items, {}

    all_frequent_items = iterate(now_sets, now_items, support_threshold, save_folder, save_file_name,
                                 reverse_dict, all_frequent_items=all_frequent_items, start_k=1, max_k=max_k)
    rules = get_and_save_rules(now_sets, confidence_threshold, save_folder, save_file_name,
                               reverse_dict, all_frequent_items=all_frequent_items)

    return all_frequent_items, rules
