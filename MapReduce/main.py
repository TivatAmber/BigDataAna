import collections
import multiprocessing.pool
import os
import time
from process import Mapper, Reducer, Shuffler

folder_start_index = 1
folder_num = 9
processes_num = 10
mapper_num = shuffler_num = 9
reducer_num = 3
result_path = "result.txt"
sorted_result_path = "sorted_result.txt"
relative_result_path = "relative_result.txt"
sorted_relative_result_path = "sorted_relative_result.txt"
map_folder_path = "map_folder"
reducer_folder_path = "reducer_folder"


def map_combine_process() -> list[list[tuple[tuple[str, str], int]]]:
    mappers = []
    mappers_pool: multiprocessing.pool.Pool = multiprocessing.Pool(processes=processes_num)
    mappers_result = []
    mapper_len = ((max_len := folder_num) + mapper_num - 1) // mapper_num
    for now_folder_index in range(folder_start_index, max_len + folder_start_index, mapper_len):
        mappers.append(Mapper(
            (now_folder_index - folder_start_index) // mapper_len + 1,
            list(range(now_folder_index, min(now_folder_index + mapper_len, max_len + folder_start_index))),
            map_folder_path
        ))
    for mapper in mappers:
        mappers_result.append(mappers_pool.apply_async(mapper.save_result))
    mappers_pool.close()
    mappers_pool.join()
    mappers_result = [mapper_result.get() for mapper_result in mappers_result]
    return mappers_result


def shuffler_process(mappers_result: list[list[tuple[tuple[str, str], int]]]) -> list[
    dict[str, int], dict[str, set[str]]]:
    shufflers = []
    shuffler_pool: multiprocessing.pool.Pool = multiprocessing.Pool(processes=processes_num)
    shufflers_result = []
    # shuffler_len = ((max_len := len(mappers_result)) + shuffler_num - 1) // shuffler_num
    for index, now_result in enumerate(mappers_result):
        shufflers.append(Shuffler(
            index + 1,
            now_result,
            reducer_num
        ))
    for shuffler in shufflers:
        shufflers_result.append(shuffler_pool.apply_async(shuffler.get_result))
    shuffler_pool.close()
    shuffler_pool.join()
    shufflers_result = [shuffler_result.get() for shuffler_result in shufflers_result]
    return shufflers_result


def reduce_process(shufflers_result: list[list[tuple[str, list[int]]]]) -> list[dict[str, int]]:
    reducers = []
    reducer_pool: multiprocessing.pool.Pool = multiprocessing.Pool(processes=processes_num)
    reducers_result = []
    shufflers_result = list(zip(*shufflers_result))
    for index, now_result_index in enumerate(shufflers_result):
        reducers.append(Reducer(
            index + 1,
            shufflers_result[index],
            reducer_folder_path
        ))
    for reducer in reducers:
        reducers_result.append(reducer_pool.apply_async(reducer.save_result))
    reducer_pool.close()
    reducer_pool.join()
    reducers_result = [reducer_result.get() for reducer_result in reducers_result]
    return reducers_result


def save_result(count_result: list[dict[str, int]], relative_result: dict[str, set[str]]) -> None:
    result = collections.defaultdict(int)
    for now_dict in count_result:
        now_dict: dict[str, int]
        for key, value in now_dict.items():
            result[key] += value

    with open(result_path, 'w') as fp:
        fp.write(repr(result))
    with open(relative_result_path, 'w') as fp:
        fp.write(repr(relative_result))

    result = list(result.items())
    result = {item[0]: item[1] for item in sorted(result, key=lambda x: x[1], reverse=True)[:1000]}

    new_relative_result = {}
    for key, value in relative_result.items():
        value: set[str]
        new_value = set()
        if result.get(key):
            for target in value:
                if result.get(target):
                    new_value.add(target)
            new_relative_result[key] = new_value

    new_relative_result = {item[0]: item[1] for item in sorted(list(new_relative_result.items()))}

    with open(sorted_relative_result_path, 'w') as fp:
        fp.write(repr(new_relative_result))
    with open(sorted_result_path, 'w') as fp:
        fp.write(repr(result))


def multi_processing_work():
    now = time.time()
    start_time = time.time()
    mappers_result = map_combine_process()
    print(f"Mapper Time:{time.time() - now}, Overall Time: {time.time() - start_time}")

    now = time.time()
    shufflers_result = shuffler_process(mappers_result=mappers_result)
    print(f"Shuffle Time:{time.time() - now}, Overall Time: {time.time() - start_time}")

    now = time.time()

    relative_result = {}
    for shuffler_result in shufflers_result:
        relative_result.update(shuffler_result[1])
    shufflers_result = [shuffler_result[0] for shuffler_result in shufflers_result]

    reducers_result = reduce_process(shufflers_result=shufflers_result)
    print(f"Reduce Time:{time.time() - now}, Overall Time: {time.time() - start_time}")

    now = time.time()
    save_result(count_result=reducers_result, relative_result=relative_result)
    print(f"Save Result Time:{time.time() - now}, Overall Time: {time.time() - start_time}")


if __name__ == '__main__':
    if not os.path.exists(map_folder_path):
        os.mkdir(map_folder_path)
    if not os.path.exists(reducer_folder_path):
        os.mkdir(reducer_folder_path)

    multi_processing_work()
