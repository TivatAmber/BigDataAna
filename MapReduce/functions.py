import multiprocessing
import os.path
import queue
import re


def get_words() -> set[str]:
    now_set = set()
    with open("words.txt", 'r') as fp:
        while now_str := fp.readline():
            now_str = now_str.strip()
            now_set.add(now_str)
    return now_set


def get_folder_path(number: int) -> str:
    folder_path = "source_data/folder_"
    folder_path += str(number)
    return folder_path


def get_file(file_path: str) -> str:
    with open(file_path, 'r') as fp:
        return fp.read()


def needed_char(x: str) -> bool:
    if x.isalpha(): return True
    if x == '_': return True
    return False


def hash_str(x: str) -> int:
    return sum([ord(char) for char in x])

def get_file_alnum_as_list(file_path: str) -> list[str]:
    now_file = get_file(file_path).lower()
    now_file = re.findall(r'\w+', now_file)
    return now_file
    # now_file = list(map(lambda x: x.lower() if needed_char(x) else ' ', list(now_file)))
    # return list(filter(None, ''.join(now_file).split(' ')))


# def get_result(folder_index: int) -> dict[tuple[str, str], int]:
#     now_path = get_folder_path(folder_index)
#     dic = {}
#     for now_file_path in os.listdir(now_path):
#         print(folder_index)
#         now_title = now_file_path.split('.')[0]
#         list_words = get_file_alnum_as_list(os.path.join(now_path, now_file_path))
#         for now_words in list_words:
#             if now_words not in key_words: continue
#             pair = (now_title, now_words)
#             if dic.get(pair):
#                 dic[pair] += 1
#             else:
#                 dic[(now_title, now_words)] = 1
#     return dic
#
# def test_module(now_folder: int) -> None:
#     # mapper = Mapper(now_folder)
#     # dic = mapper.get_result()
#     dic = (now_folder)
#     # with open(mapper.save_path, 'w') as fp:
#     with open(f'map_folder/ans{now_folder}.txt', 'w') as fp:
#         fp.write(repr(dic))


key_words = get_words()
