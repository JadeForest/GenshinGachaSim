"""
Core of the gacha system.
---
Items, Banners, BannerPullers
"""
import random

from data import C4, W4S, C5S, W5S, DataList
from util import _STAR, UNPATHED, WP


def get(prob: float) -> bool:
    "probability of getting an item"
    assert 0 <= prob <= 1, "Invalid probability."
    rand = random.random()
    return True if rand <= 1 * prob else False


class Item:
    rank = 0

    def __init__(self, pull_count) -> None:
        self.name = None
        self.type = None
        self.prob = self.__class__._get_prob(pull_count)

    def __bool__(self):
        return True

    def __str__(self) -> str:
        return self.name + "({}星{})".format(self.rank, self.type)

    @property
    def rank_display(self):
        return _STAR * self.rank

    @staticmethod
    def _get_prob(pull_count):
        pass

    def pull(self):
        if get(self.prob):
            return self
        return False


class RateUpItem(Item):
    def __init__(self, pull_count, pity, *args, **kwargs) -> None:
        super().__init__(pull_count, *args, **kwargs)
        self.isup = self._is_upitem(pity)

    def _is_upitem(self, pity):
        if pity > 0:
            return True
        if get(0.5):
            return True
        return False


class Star3Item(Item):
    rank = 3

    def __init__(self) -> None:
        self.name = None
        self.type = None

    def pull(self):
        return self


class Star4Item(Item):
    rank = 4

    @staticmethod
    def _get_prob(pull_count):
        if pull_count <= 8:
            return 0.051
        if pull_count >= 10:
            return 1
        return 0.561


class Star5Item(Item):
    rank = 5

    @staticmethod
    def _get_prob(pull_count):
        if pull_count <= 73:
            return 0.006
        if pull_count >= 90:
            return 1
        return 0.006 + (pull_count - 73) * 0.06


class CustomItem(Item):
    custom_prob = 0.01

    def __init__(self, pull_count, *args, **kwargs) -> None:
        super().__init__(pull_count, *args, **kwargs)
        self.prob = self.custom_prob

    @classmethod
    def set_custom_prob(cls, prob):
        cls.custom_prob = prob


class Star5ItemCustom(Star5Item, CustomItem):
    pass


class UPStar4Item(Star4Item, RateUpItem):
    pass


class UPStar5Item(Star5Item, RateUpItem):
    pass


class UPStar5ItemCustom(Star5ItemCustom, RateUpItem):
    pass


class UPStar4Weapon(UPStar4Item):
    @staticmethod
    def _get_prob(pull_count):
        if pull_count <= 7:
            return 0.06
        if pull_count >= 9:
            return 1
        return 0.66


class UPStar5Weapon(UPStar5Item):
    @staticmethod
    def _get_prob(pull_count):
        if pull_count <= 62:
            return 0.007
        if pull_count >= 77:
            return 1
        return 0.007 + (pull_count - 62) * 0.07


class Banner:
    def __init__(self, *args, **kwargs) -> None:
        self.pool = {3: [("-", WP)]}

    def pick_item(self, rank, item):
        item.name, item.type = random.choice(self.pool[rank])
        return item


class StandardBanner(Banner):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.pool.update(DataList(C4, W4S, W5S, C5S).data)


class RateUpBanner(Banner):
    def __init__(self, rateups, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._rateups = rateups

    @property
    def rateups(self) -> dict[int, list[tuple[str, str]]]:
        return self._rateups

    def pick_rateup(self, rank, item: RateUpItem):
        if item.isup:
            item.name, item.type = random.choice(self._rateups[rank])
        else:
            pick = random.choice(self.pool[rank])
            if pick in self._rateups[rank]:
                item.isup = True
            item.name, item.type = pick
        return item


class CharacterBanner(RateUpBanner):
    def __init__(self, rateups, *args, **kwargs) -> None:
        super().__init__(rateups, *args, **kwargs)
        self.pool.update(DataList(C4, W4S, C5S).data)


class WeaponBanner(RateUpBanner):
    def __init__(self, rateups, *args, **kwargs) -> None:
        super().__init__(rateups, *args, **kwargs)
        self.pool.update(DataList(C4, W4S, W5S).data)
        # Epitome Path
        self.reset_path()
        if 'path' in kwargs:
            self.set_path(kwargs['path'])

    def get_path(self) -> str:
        return self._path, self._path_value

    def set_path(self, value: str):
        assert value in [UNPATHED] + [
            e[0] for e in self._rateups[5]
        ], "Not a valid Epitome Path!"
        self._path = value
        self._path_value = 0

    def reset_path(self):
        self._path = None
        self._path_value = 0

    def pick_rateup(self, rank, item: RateUpItem):
        item = super().pick_rateup(rank, item)
        if rank == 5:
            if self._path_value >= 2:
                item.name = self._path
                item.isup = True
                self._path_value = 0
            elif self._path:
                self._path_value = (
                    0 if self._path == item.name else self._path_value + 1
                )
        return item


class Puller:
    items = {5: Star5Item, 4: Star4Item, 3: Star3Item}
    required_banner_type = Banner

    def __init__(self, banner=None, count=1, star4count=1, star5count=1) -> None:
        self._banner = banner
        self.counts = {5: star5count, 4: star4count, 0: count}

    @property
    def banner(self) -> Banner:
        return self._banner

    def set_banner(self, banner: Banner):
        assert isinstance(
            banner, (self.required_banner_type, None)
        ), "Not a valid banner!"
        self._banner = banner

    def info(self) -> tuple:
        return self.counts[0], self.counts[4], self.counts[5]

    def _pull_item(self):
        pass

    def _pull_3star(self) -> Star3Item:
        star3 = self.items[3]().pull()
        star3 = self._banner.pick_item(3, star3)
        return star3

    def pull(self) -> Item:
        for k in self.counts.keys():
            self.counts[k] += 1

        for rank in (5, 4):
            item = self._pull_item(rank)
            if item:
                return item
        return self._pull_3star()

    def multiple_pull(self, count=1):
        for _ in range(count):
            yield self.info(), self.pull()


class StandardBannerPuller(Puller):
    required_banner_type = StandardBanner

    def _pull_item(self, rank):
        item: Item = self.items[rank](self.counts[rank] - 1).pull()
        if item:
            item = self._banner.pick_item(rank, item)
            self.counts[rank] = 1
        return item


class RateUpPuller(Puller):
    required_banner_type = RateUpBanner
    items = {5: UPStar5Item, 4: UPStar4Item, 3: Star3Item}

    def __init__(self, banner=None, star4pity=0, star5pity=0, *args, **kwargs) -> None:
        super().__init__(banner, *args, **kwargs)
        self.pitys = {5: star5pity, 4: star4pity}

    def info(self) -> tuple:
        return (
            self.counts[0],
            self.counts[4],
            self.pitys[4],
            self.counts[5],
            self.pitys[5],
        )

    def _pull_item(self, rank) -> RateUpItem:
        item: Item = self.items[rank](self.counts[rank] - 1, self.pitys[rank]).pull()
        if item:
            item = self._banner.pick_rateup(rank, item)
            self.counts[rank] = 1
            self.pitys[rank] = 0 if item.isup else self.pitys[rank] + 1
        return item


class CharacterBannerPuller(RateUpPuller):
    required_banner_type = CharacterBanner


class WeaponBannerPuller(RateUpPuller):
    required_banner_type = WeaponBanner
    items = {5: UPStar5Weapon, 4: UPStar4Weapon, 3: Star3Item}

    def info(self) -> tuple:
        return (
            self.counts[0],
            self.counts[4],
            self.pitys[4],
            self.counts[5],
            self.pitys[5],
            self._banner.get_path()[1],
        )

###=======================testrun========================###
if __name__ == "__main__":
    puller = StandardBannerPuller()
    banner1 = StandardBanner()
    Star5ItemCustom.set_custom_prob(0.1)
    puller.items[5] = Star5ItemCustom
    puller.set_banner(banner1)
    for i in puller.multiple_pull(100):
        if i[1].rank != "***":
            print(i[0][0], "\t", i[1])
