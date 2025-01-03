import numpy as np

from .anime import UserRatedAnime


class User:
    def __init__(self, user_id: int, rating_list: dict[int, UserRatedAnime] = None):
        self.id = user_id
        if rating_list is None:
            self.rating_list: dict[int, UserRatedAnime] = {}
        self.sim_user = []
        self.mean_rating = 0

    def append(self, rated_anime: UserRatedAnime):
        self.rating_list[rated_anime.id] = rated_anime
        self.mean_rating = np.mean([value.rating for value in self.rating_list.values()])

    def set_sim_user(self, sim_user: list):
        self.sim_user = sim_user
