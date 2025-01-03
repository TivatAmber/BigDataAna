from .functions import *
from .utility import *


class ContentRecommend:
    def __init__(self, anime: pd.DataFrame, train_set: pd.DataFrame) -> None:
        self.anime = anime
        self.train_set = train_set
        self.anime_id_name = {}
        self.handle_anime()
        self.min_hash: bool = False
        self.calc_dic = {}

    def handle_anime(self) -> None:
        temp_df: pd.DataFrame = self.anime[['Anime_id', 'Name']]
        self.anime_id_name = {anime_id: name for anime_id, name in temp_df.values}
        self.anime = self.anime[['Anime_id', 'Genres']]
        item_dummies: pd.DataFrame = self.anime['Genres'].str.get_dummies(sep=', ')
        count_ones = item_dummies.apply(lambda x: (x == 1).sum())
        item_dummies = item_dummies.loc[:, count_ones > 1]
        self.anime = pd.concat([self.anime, item_dummies], axis=1)
        self.anime = self.anime.drop(labels=['Genres', 'Unknown'], axis=1)
        # print(count_ones)

    def get_predict_rating(self, scored_anime: list[tuple[int, int]], target_anime: int) -> float:
        upper = 0
        lower = 0
        for anime_id, score in scored_anime:
            x, y = self.calc_dic[anime_id], self.calc_dic[target_anime]
            sim = minhash_sim(x, y) if self.min_hash else get_anime_anime_sim(x, y)
            upper += score * sim
            lower += sim
        return upper / lower if lower != 0 else 0

    def fit(self, *, min_hash: bool = False,
            min_hash_col: int = 100) -> None:
        self.min_hash = min_hash
        anime_traits = self.anime.iloc[:, 1:]

        sum_anime = len(anime_traits)  # the number of anime
        count_ones = anime_traits.apply(lambda x: (x == 1).sum())
        int_to_trait = {index: column for index, column in enumerate(anime_traits.columns)}
        trait_to_int = {value: key for key, value in int_to_trait.items()}

        anime_traits = anime_traits.values
        anime_dic: dict[int, AnimeWithTraits] = {}
        for index, anime_trait in zip(self.anime.iloc[:, 0], anime_traits):
            anime_dic[index] = AnimeWithTraits(index, list(np.squeeze(np.argwhere(anime_trait == 1), axis=1)))

        # print(count_ones)
        # print(anime_dic[4103].traits)

        calc_dic: dict[int, list[float]]
        if not min_hash:
            tf_dic = {
                index: anime_trait / len(anime_dic[index].traits) if len(anime_dic[index].traits) != 0 else [0] * len(
                    anime_trait) for index, anime_trait in zip(self.anime.iloc[:, 0], anime_traits)}
            idf = np.log2((sum_anime + 1) / (count_ones + 1))
            calc_dic = {key: np.multiply(value, idf.values) for key, value in tf_dic.items()}
        else:
            minhash_module = MinHash(min_hash_col)
            calc_dic = {
                now_anime_index: minhash_module.compute_minhash(now_anime.traits)
                for now_anime_index, now_anime in anime_dic.items()}
        # print(calc_dic)
        self.calc_dic = calc_dic

    def predict(self, test_set: pd.DataFrame):
        test_set = test_set.values
        train_set = self.train_set.values
        SSE: float = 0
        ret = []
        for item in test_set:
            scored_anime = [(train_item[1], train_item[2]) for train_item in train_set if item[0] == train_item[0]]
            ret.append((item[0], item[1],
                        predict_rating := self.get_predict_rating(scored_anime, item[1])))
            SSE += (item[2] - predict_rating) ** 2
        return ret, SSE

    def recommend(self, *, user_id, max_k: int = 10, remove_seen: bool = True) -> list[tuple[int, float]]:
        all_anime: set[int] = set(self.anime_id_name.keys())
        scored_anime = [(train_item[1], train_item[2]) for train_item in self.train_set.values if
                        user_id == train_item[0]]
        if remove_seen:
            all_anime = all_anime - {anime_id for anime_id, _ in scored_anime}
        ret = []
        for anime in all_anime:
            predict_rating = (anime, self.get_predict_rating(scored_anime, anime))
            ret.append(predict_rating)
        ret = sorted(ret, key=lambda x: x[1], reverse=True)
        return ret[:min(len(ret), max_k)]
