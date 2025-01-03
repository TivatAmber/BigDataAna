import numpy as np
import pandas as pd
from .utility import *


def read_train_data(anime_path: str, train_set: str) -> (pd.DataFrame, pd.DataFrame):
    anime = pd.read_csv(anime_path)
    train_set = pd.read_csv(train_set)
    return anime, train_set


def read_test_data(test_path: str) -> pd.DataFrame:
    test_set = pd.read_csv(test_path)
    return test_set


def jaccard_sim(x: set, y: set):
    return len(x.intersection(y)) / len(x.union(y))


def minhash_sim(x: list, y: list):
    assert len(x) == len(y)
    return (val := sum([1 if x[i] == y[i] else 0 for i in range(len(x))])) / len(x)


def get_anime_anime_sim(a: list[float], b: list[float]) -> float:
    a = np.asarray(a)
    b = np.asarray(b)
    upper = np.sum(np.multiply(a, b))
    lower = np.sqrt(np.sum(a ** 2)) * np.sqrt(np.sum(b ** 2))
    return upper / lower if lower != 0 else 0


def get_user_user_sim(a: User, b: User) -> (int, float):
    upper: float = 0
    a_mean = np.mean(a_val := np.asarray([value.rating for value in a.rating_list.values()]))
    b_mean = np.mean(b_val := np.asarray([value.rating for value in b.rating_list.values()]))
    a_sum = np.sqrt(np.sum((a_val - a_mean) ** 2))
    b_sum = np.sqrt(np.sum((b_val - b_mean) ** 2))
    for item, value in a.rating_list.items():
        if item in b.rating_list:
            upper += (b.rating_list[item].rating - b_mean) * (value.rating - a_mean)
    lower = a_sum * b_sum
    return b.id, upper / lower if lower != 0 else 0


def create_list_with_one(len: int, pos: list[int] = None) -> list[int]:
    ret = [0] * len
    if pos is not None:
        for index in pos:
            assert index < len
            ret[index] = 1
    return ret
