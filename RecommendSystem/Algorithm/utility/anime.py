class UserRatedAnime:
    def __init__(self, anime_id: int, rating: int):
        self.id = anime_id
        self.rating = rating


class AnimeWithTraits:
    def __init__(self, anime_id: int, traits: list[int] = None):
        self.id = anime_id
        self.traits = traits
