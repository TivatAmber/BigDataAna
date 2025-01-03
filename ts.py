import random


class DGIM:
    def __init__(self, window_size, r_size: int = 3):
        assert r_size >= 3
        self.window_size = window_size
        self.r_size = r_size
        self.buckets = []

    def add_bit(self, bit, timestamp):
        # 忽略0
        if bit == 0:
            return

        # 添加一个新的大小为1的位桶
        self.buckets.append((timestamp, 1))

        # 合并相同大小的位桶
        print(self.buckets)
        self.buckets = self._merge_buckets(self.buckets)
        print(self.buckets)

    def _merge_buckets(self, now_buckets):
        if len(now_buckets) < self.r_size: return now_buckets
        new_buckets = now_buckets.copy()
        while True:
            if len(new_buckets) < self.r_size: break
            piece = new_buckets[-self.r_size:]
            now_num = piece[-1][1]
            flag = True
            for pic in piece:
                if pic[1] != now_num: flag = False
            if flag:
                for i in range(self.r_size):
                    new_buckets.pop()
                new_buckets.append((piece[-2][0], now_num * (self.r_size - 1)))
                new_buckets = self._merge_buckets(new_buckets)
                new_buckets.append(piece[-1])
            else: break

        return new_buckets

    def count_ones(self, current_timestamp):
        total = 0
        last_size = 0

        for timestamp, size in self.buckets:
            if current_timestamp - timestamp >= self.window_size:
                continue

            if last_size == 0:
                last_size = size
            total += size

        if last_size > 0 and len(self.buckets) > 0:
            total -= last_size // 2

        return total

# 示例使用
dgim = DGIM(10, 3)  # 滑动窗口大小为10

# data_stream = [random.choice([0, 1]) for _ in range(1000)]
data_stream = [0, 1, 1, 0, 1, 0, 1, 1, 0, 0, 0, 1, 1, 0, 0, 1, 0, 1, 0, 0, 0, 1, 1, 1, 0, 0, 1]
for timestamp, bit in enumerate(data_stream):
    dgim.add_bit(bit, timestamp)

# 计算滑动窗口中1的个数
print("滑动窗口中1的个数:", dgim.count_ones(len(data_stream)))
