import time

import Algorithm


def fit(system, *, max_k: int = 150, min_hash: bool = False, min_hash_col: int = 3) -> None:
    print(min_hash, min_hash_col)
    if isinstance(system, Algorithm.UserUserRecommend):
        system.fit(max_k=max_k, min_hash=min_hash, min_hash_col=min_hash_col)
    elif isinstance(system, Algorithm.ContentRecommend):
        system.fit(min_hash=min_hash, min_hash_col=min_hash_col)

    pred, SSE = system.predict(test_set)
    for user_id, anime_id, value in pred:
        print(f"{user_id} - {anime_id}, {value:.2f}")
    print(f"SSE: {SSE:.2f}")


def warn(msg: str):
    def outer(func):
        def wrapper(*args, **kwargs):
            try:
                func(*args, **kwargs)
            except:
                print(msg)

        return wrapper

    return outer


def get_time(name: str):
    def outer(func):
        def wrapper(*args, **kwargs):
            now = time.time()
            func(*args, **kwargs)
            print(f"{name} Time: {time.time() - now:.2f}")

        return wrapper

    return outer


# @warn("Invalid Input")
def get_pred_list(user_id: int, *, max_k: int, remove_seen: bool):
    anime_list = system.recommend(user_id=user_id, max_k=max_k, remove_seen=remove_seen)
    for anime_id, score in anime_list:
        print(f"Anime Name: {anime_id}, scored:{score:.2f}")


# @warn("Out of Range")
@get_time("Pred")
def get_pred(inp: str, *, max_k: int = 150, remove_seen: bool = True):
    user_id = int(inp)
    get_pred_list(user_id, max_k=max_k, remove_seen=remove_seen)


if __name__ == '__main__':
    anime, train_set = Algorithm.read_train_data('data/anime.csv', 'data/train_set.csv')
    test_set = Algorithm.read_test_data('data/test_set.csv')
    anime = anime.drop(anime.columns[-3:], axis=1)

    system = Algorithm.ContentRecommend(anime, train_set)
    fit(system, min_hash=False, min_hash_col=10)

    while True:
        print("Input:")
        inp = input()
        if inp == 'Q':
            break
        else:
            get_pred(inp, max_k=20, remove_seen=False)

    print("End")
