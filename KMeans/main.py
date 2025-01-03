import collections

import matplotlib.pyplot as plt
import numpy
import pandas as pd
import numpy as np

cluster_num = 3
# sample_num = 200 // cluster_num
sample_num = 1000
max_iter = 200


# random = True
# def initialize_centroids(X, k):
#     m, n = X.shape
#     centroids = np.zeros((k, n))
#     if random:
#         for i in range(k):
#             index = np.random.randint(0, m)
#             centroids[i, :] = X[index, :]
#     else:
#         for i in range(m):
#             centroids[int(X[i][0]), :] = X[i, :]
#     return centroids


def swap(x, y):
    return y, x


def initialize_centroids(X: np.ndarray, k: int) -> np.ndarray:
    m, n = X.shape
    centroids = np.zeros((k, n))
    centroids[0] = X[np.random.randint(0, m)]

    for i in range(1, k):
        dist_sq = np.min([np.sum((X - centroid) ** 2, axis=1) for centroid in centroids[:i]], axis=0)
        probs = dist_sq / np.sum(dist_sq)
        cumulative_probs = np.cumsum(probs)
        r = np.random.rand()
        for j, p in enumerate(cumulative_probs):
            if r < p:
                centroids[i] = X[j]
                break

    return centroids


def find_closest_centroids(X: np.ndarray, centroids: np.ndarray) -> np.ndarray:
    m = X.shape[0]
    k = centroids.shape[0]
    idx = np.zeros(m)
    for i in range(m):
        min_dist = float('inf')
        for j in range(k):
            dist = np.sum((X[i, :] - centroids[j, :]) ** 2)
            if dist < min_dist:
                min_dist = dist
                idx[i] = j
    return idx


def compute_centroids(X: np.ndarray, idx: np.ndarray, k: int):
    m, n = X.shape
    centroids = np.zeros((k, n))
    for i in range(k):
        points = X[idx == i]
        centroids[i, :] = np.mean(points, axis=0)
    return centroids


def kmeans(X: np.ndarray, k: int, max_iters: int = 100) -> (np.ndarray, np.ndarray):
    centroids = initialize_centroids(X, k)
    for i in range(max_iters):
        idx = find_closest_centroids(X, centroids)
        centroids = compute_centroids(X, idx, k)
    return centroids, idx


def pre_handle(raw_data: pd.DataFrame) -> pd.DataFrame:
    raw_data = raw_data.drop(raw_data.columns[-3:], axis=1)
    raw_data = raw_data.drop(raw_data.columns[:3], axis=1)
    raw_data['Popularity'] = pd.to_numeric(raw_data['Popularity'], errors='coerce')
    raw_data['Ranked'] = pd.to_numeric(raw_data['Ranked'], errors='coerce')
    raw_data['Popularity'] = raw_data['Popularity'].fillna(0).astype(int)
    raw_data['Ranked'] = raw_data['Ranked'].fillna(0).astype(int)
    numeric_columns = raw_data.columns[-9:]

    for column in numeric_columns:
        raw_data[column] = pd.to_numeric(raw_data[column], errors='coerce')

    raw_data = raw_data.dropna(how='any')

    raw_data = raw_data.sort_values(by=['Popularity', 'Ranked'], ascending=[False, True])
    raw_data_numeric = raw_data.select_dtypes(include=[np.number]).columns
    raw_data_numeric = raw_data[raw_data_numeric[-10:]]
    # print(raw_data_numeric.columns)
    raw_data_numeric = raw_data_numeric.fillna(raw_data_numeric.mean())

    raw_data_numeric = (raw_data_numeric - raw_data_numeric.min()) / (raw_data_numeric.max() - raw_data_numeric.min())
    # log_val = np.log(raw_data_numeric)
    # log_val= (log_val - log_val.min()) / (log_val.max() - log_val.min())
    # raw_data_numeric = log_val
    # raw_data_numeric = (raw_data_numeric - raw_data_numeric.mean()) / raw_data_numeric.std()
    # raw_data_numeric = raw_data_numeric / raw_data_numeric.max()
    # print(raw_data_numeric.max())
    # print(raw_data_numeric.min())

    raw_data[raw_data_numeric.columns] = raw_data_numeric
    raw_data.to_csv('sorted_by_popularity.csv', index=False)
    return raw_data


def split_data(data: pd.DataFrame, cluster: int, *, shuffle: bool = False, max_len: int = -1) -> list[pd.DataFrame]:
    data_len = (len(data) + cluster - 1) // cluster
    ret_data: list[pd.DataFrame] = []
    for index in range(cluster):
        dat: pd.DataFrame = data.iloc[index * data_len: min((index + 1) * data_len, len(data)), :]
        if shuffle:
            dat = dat.sample(frac=1).reset_index(drop=True)
        dat = dat.drop(['Ranked'], axis=1).reset_index(drop=True)
        dat.insert(0, 'cluster', index)
        if max_len != -1:
            ret_data.append(dat[:max_len])
        else:
            ret_data.append(dat)
    return ret_data


if __name__ == "__main__":
    # raw_data = pd.read_csv('anime.csv')
    # data = pre_handle(raw_data)
    # data = split_data(data, cluster_num, max_len=-1, shuffle=True)
    # for index, dat in enumerate(data):
    #     dat: pd.DataFrame
    #     dat.to_csv(f"saved_file{index}.csv", index=False)
    #
    # test_X = []
    # new_data = []
    # for dat in data:
    #     test_X.append(dat.sample(n=sample_num, random_state=42))
    #     new_data.append(dat.drop(test_X[-1].index).sample(frac=1))
    #     print(new_data[-1].head(2))
    # data = new_data
    #
    # test_X = pd.concat(data, axis=0).values
    # X = pd.concat(data, axis=0).values
    # X, test_X = swap(X, test_X)
    # np.random.shuffle(test_X)

    X = pd.read_csv('kmeans.csv').values

    test_X = X.copy()
    centroids, idx = kmeans(X[:, 1:], cluster_num, max_iter)
    # print(centroids.shape)
    print(centroids.shape)

    print("Distance")
    dis = []
    for index in range(centroids.shape[0]):
        now = []
        for index2 in range(centroids.shape[0]):
            now.append(np.sqrt(np.sum((centroids[index] - centroids[index2])** 2)))
        dis.append(now)
    dis = np.asarray(dis)
    print(dis)
    # for index in range(centroids.shape[0] - 1):
    #     print(np.sum((centroids[index] - centroids[index + 1]) ** 2))
    # print(np.sum((centroids[centroids.shape[0] - 1] - centroids[0]) ** 2)})

    # print(np.sum((centroids[0] - centroids[1]) ** 2))
    # print(np.sum((centroids[1] - centroids[2]) ** 2))
    # print(np.sum((centroids[2] - centroids[0]) ** 2))

    label = collections.defaultdict(int)
    kinds = find_closest_centroids(X[:, 1:], centroids)
    kinds = np.asarray(kinds).astype(np.int32)
    # if index not in label:
    #     label[index] = x[0]
    SSE = 0
    bucket = np.zeros(shape=(cluster_num, cluster_num), dtype=np.int32)
    for index, kind in enumerate(kinds):
        bucket[kind][int(X[index][0] - 1)] += 1
        SSE += np.sum((X[index, 1:] - centroids[kind]) ** 2)
    # print(bucket)
    for index, row in enumerate(bucket):
        label[index] = np.argmax(row)
    # MSE /= X.shape[0]
    # print(label)
    # print(f"SSE: {SSE}")

    # test_X = pd.read_csv('kmeans.csv', header=None).values
    # print(test_X[:, 0])
    test_y = find_closest_centroids(test_X[:, 1:], centroids)
    # print(test_y)
    kind = np.asarray([label[index] + 1 for index in test_y])
    # print(kind)
    # print(kind == test_X[:, 0])
    acc = np.sum(kind == test_X[:, 0]) / test_X.shape[0]
    print(f"acc: {acc}")

    # centroids = np.asarray(centroids)
    # test_y = np.asarray(test_y).astype(np.int32)
    # kind = centroids[test_y][:, 0]
    # print(np.sum(test_X[:, 0] == kind) / test_X.shape[0])

    plt.scatter(X[:, 2], X[:, -1], s=10, c=idx, cmap='rainbow')
    plt.scatter(centroids[:, 2], centroids[:, -1], s=100, c='black', marker='x')
    plt.title(f"K-means Clustering: SSE: {SSE:.2f}, Acc: {acc:.2f}")
    plt.xlabel("Feature Score 10")
    plt.ylabel("Feature Score 2")
    plt.show()
