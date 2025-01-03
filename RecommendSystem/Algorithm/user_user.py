from .functions import *
import numpy as np


class UserUserRecommend:
    def __init__(self, anime: pd.DataFrame, train_set: pd.DataFrame) -> None:
        self.anime = anime
        self.train_set = train_set
        self.user_list: dict[int, User] = {}
        temp_df: pd.DataFrame = self.anime[['Anime_id', 'Name']]
        self.anime_id_name = {anime_id: name for anime_id, name in temp_df.values}

    def get_predict_rating(self, user: User, anime_id: int) -> float:
        upper: float = 0
        lower: float = 0
        for other_user in user.sim_user:
            if anime_id in self.user_list[other_user[0]].rating_list:
                now_anime_rating = self.user_list[other_user[0]].rating_list[anime_id].rating
            else:
                now_anime_rating = self.user_list[other_user[0]].mean_rating
            sim = other_user[1]
            upper += now_anime_rating * sim
            lower += sim
        return upper / lower if lower != 0 else 0

    def fit(self, *, max_k: int = 200,
            min_hash: bool = False, min_hash_col: int = 100) -> None:
        user_ids = np.unique(self.train_set['user_id'].values)
        self.user_list: dict[int, User] = {user_id: User(user_id) for user_id in user_ids}
        for item in self.train_set.values:
            self.user_list[item[0]].append(UserRatedAnime(item[1], item[2]))

        if not min_hash:
            for now_user in self.user_list.values():
                sim_list = []
                for other_user in self.user_list.values():
                    if now_user == other_user: continue
                    sim_pair = get_user_user_sim(now_user, other_user)
                    if sim_pair[1] < 0: continue
                    sim_list.append(sim_pair)
                sim_list.sort(key=lambda x: x[1], reverse=True)
                sim_list = sim_list[:min(max_k, len(sim_list))]
                now_user.set_sim_user(sim_list)
        else:
            minhash_module = MinHash(min_hash_col)
            # for now_user in user_list.values():
            #     for now_anime in now_user.rating_list.values():
            #         now_anime.rating = 1 if now_anime.rating >= 5 else 0
            minhash_dic: dict[int, list] = {
                now_user_index: minhash_module.compute_minhash(
                    [x.id for x in now_user.rating_list.values() if x.rating >= 5])
                for now_user_index, now_user in self.user_list.items()}

            for now_user_index in self.user_list.keys():
                sim_list = []
                for other_user_index in self.user_list.keys():
                    if now_user_index == other_user_index: continue
                    sim_pair = other_user_index, minhash_sim(minhash_dic[now_user_index], minhash_dic[other_user_index])
                    if sim_pair[1] < 0: continue
                    sim_list.append(sim_pair)
                sim_list.sort(key=lambda x: x[1], reverse=True)
                sim_list = sim_list[:min(max_k, len(sim_list))]
                self.user_list[now_user_index].set_sim_user(sim_list)

    def predict(self, test_set: pd.DataFrame) -> (list[tuple[int, float]], float):
        test_users = test_set.values
        ret = []
        SSE = 0
        for user in test_users:
            predict_rating = self.get_predict_rating(self.user_list[user[0]], user[1])
            ret.append((user[0], user[1], predict_rating))
            SSE += (predict_rating - user[2]) ** 2
        return ret, SSE

    def recommend(self, *, user_id, max_k: int = 10, remove_seen: bool = False) -> list[tuple[int, float]]:
        all_anime: set[int] = set(self.anime_id_name.keys())
        scored_anime = {train_item[1] for train_item in self.train_set.values if
                        user_id == train_item[0]}
        if remove_seen:
            all_anime = all_anime - scored_anime
        ret = []
        for anime in all_anime:
            predict_rating = (anime, self.get_predict_rating(self.user_list[user_id], anime))
            ret.append(predict_rating)
        ret = sorted(ret, key=lambda x: x[1], reverse=True)
        # ret = [(self.anime_id_name[anime_id], value) for anime_id, value in ret]
        return ret[:min(len(ret), max_k)]
