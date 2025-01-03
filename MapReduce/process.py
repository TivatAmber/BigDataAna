import collections
from functions import hash_str

import functions
import os


class Mapper:
    def __init__(self, mapper_index:int, folder_indexes: list[int], save_path_folder) -> None:
        self.mapper_index = mapper_index
        self.folder_paths = [functions.get_folder_path(folder_index) for folder_index in folder_indexes]
        self.save_path = os.path.join(save_path_folder, f"ans{mapper_index}.txt")

    def get_result(self) -> list[tuple[tuple[str, str], int]]:
        not_combine_ret = []
        for now_path in self.folder_paths:
            for now_file_path in os.listdir(now_path):
                now_title = now_file_path.split('.')[0]
                list_words = functions.get_file_alnum_as_list(os.path.join(now_path, now_file_path))
                for now_words in list_words:
                    if now_words not in functions.key_words: continue
                    pair = (now_title, now_words)
                    not_combine_ret.append((pair, 1))
        return not_combine_ret

    def combine_ret(self, list_words: list[tuple[tuple[str, str], int]]) -> list[tuple[tuple[str, str], int]]:
        ret: dict[tuple[str, str], int] = collections.defaultdict(int)
        for pair, value in list_words:
            ret[pair] += value
        return list(ret.items())

    def save_result(self) -> list[tuple[tuple[str, str], int]]:
        not_combine_ret = self.get_result()
        with open(self.save_path, 'w') as fp:
            fp.write(repr(not_combine_ret))
        ret: list[tuple[tuple[str, str], int]] = self.combine_ret(not_combine_ret)
        return ret


class Reducer:
    def __init__(self, reducer_index: int, data: list[list[tuple[str, list[int]]]], save_path_folder: str) -> None:
        self.reducer_index = reducer_index
        self.data = data
        self.save_path = os.path.join(save_path_folder, f"ans{reducer_index}.txt")

    def get_result(self) -> dict[str, int]:
        ret = collections.defaultdict(int)
        for dic in self.data:
            for key, values in dic:
                ret[key] += sum(values)
        # ret = {key: sum(values) for key, values in self.data}
        return ret

    def save_result(self) -> dict[str, int]:
        ret = self.get_result()
        with open(self.save_path, 'w') as fp:
            fp.write(repr(ret))
        return ret


class Shuffler:
    def __init__(self, shuffler_index: int, data: list[tuple[tuple[str, str], int]], target_num: int):
        self.shuffler_index = shuffler_index
        self.data = data
        self.target_num = target_num

    def get_result(self) -> (list[list[tuple[str, list[int]]]], dict[str, set[str]]):
        shuffled_data = [collections.defaultdict(list) for _ in range(self.target_num)]
        relative_result = collections.defaultdict(set)
        for key, value in self.data:
            shuffled_data[hash_str(key[1]) % self.target_num][key[1]].append(value)
            relative_result[key[0]].add(key[1])
        sorted_shuffled_data = [list(data.items()) for data in shuffled_data]
        return sorted_shuffled_data, relative_result
