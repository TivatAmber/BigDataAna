import collections
import math
import multiprocessing.pool
import os.path
import random


def is_pri(x: int) -> bool:
    for i in range(2, int(math.sqrt(x)) + 1):
        if x % i == 0:
            return False
    return True


def new_hash_func(item: tuple, bucket_size: int) -> int:
    ret = 1
    for x in item:
        ret = (ret * x) % bucket_size
    return ret % bucket_size


def get_dict(pri_range: list[int], data: list[tuple]) -> dict[int, collections.defaultdict[int]]:
    now_dict = {now_pri: collections.defaultdict(int) for now_pri in pri_range}
    # print(f"task: {pri_range[0]} to {pri_range[-1]}, {len(pri_range)}")
    for index, now_pri in enumerate(pri_range):
        # if index % 100 == 0:
            # print(f"task: {pri_range[0]} to {pri_range[-1]}, {len(pri_range)}, now: {index}")
        for i in data:
            now_dict[now_pri][new_hash_func(i, now_pri)] += 1
    return now_dict


reRandom = True
if __name__ == '__main__':
    print('------')
    for file in range(10):
        nums = []
        for i in range(100003 - 200, 100003 + 200):
            nums.append(i)
        now_dict = {now_num: collections.defaultdict(int) for now_num in nums}

        task_len = 10
        pools: multiprocessing.pool.Pool = multiprocessing.Pool(processes=task_len)

        num_len = len(nums)
        task_num_len = num_len // task_len
        ans = []
        if reRandom or not os.path.exists(f'random_{file}'):
            random_list = [(random.randint(1, 1000 * 1000), random.randint(1, 1000 * 1000)) for _ in range(40000)]
        else:
            with open(f'random_{file}', 'r') as fp:
                random_list = eval(fp.read())
        with open(f'random_{file}', 'w') as fp:
            fp.write(repr(random_list))

        for i in range(task_len):
            ans.append(pools.apply_async(func=get_dict,
                                         args=[nums[i * task_num_len:min((i + 1) * task_num_len, num_len)], random_list]))
        pools.close()
        pools.join()

        now_dict = {}
        for x in ans:
            now_dict.update(x.get())

        with open('ans', 'w') as fp:
            for key, dic in now_dict.items():
                fp.write(f"{key} {is_pri(key)}: {len(dic)}\n")

        pri_num = [0, 0, 0]
        other_num = [0, 0, 0]
        for key, dic in now_dict.items():
            td = set()
            if is_pri(key):
                pri_num[0] += 1
                pri_num[1] += len(dic)
                for i in range(1, key):
                    if (i * i) % key in td: break
                    td.add((i * i) % key)
                pri_num[2] += len(td)
            else:
                other_num[0] += 1
                other_num[1] += len(dic)
                for i in range(1, key):
                    if (i * i) % key in td: break
                    td.add((i * i) % key)
                other_num[2] += len(td)

        pri_avg = pri_num[1] / pri_num[0]
        other_avg = other_num[1] / other_num[0]
        pri_avg_len = pri_num[2] / pri_num[0]
        other_avg_len = other_num[2] / other_num[0]

        print(f"{pri_avg:.2f}, {other_avg:.2f}")
        print(f"{((pri_avg / other_avg) - 1) * 100:.2f}%")
        print(f"{pri_avg_len:.2f}, {other_avg_len:.2f}")
        print(f"------")
