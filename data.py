"""
Gacha Items Data
"""

import json
from dataclasses import dataclass

from util import CH, WP


@dataclass
class _Code:
    file: str
    rank: int
    type: str


C4 = _Code("4StarCharacters.txt", 4, CH)
C5L = _Code("5StarCharacters_Lmt.txt", 5, CH)
C5S = _Code("5StarCharacters_Std.txt", 5, CH)
W4L = _Code("4StarWeapons_Lmt.txt", 4, WP)
W4S = _Code("4StarWeapons_Std.txt", 4, WP)
W5L = _Code("5StarWeapons_Lmt.txt", 5, WP)
W5S = _Code("5StarWeapons_Std.txt", 5, WP)


class DataList:
    def __init__(self, *args) -> None:
        self.dict = None
        for code in args:
            assert isinstance(code, _Code), f"{code} is not valid!"
        self.codes: tuple[_Code] = args

    def _load(self):
        self.dict = {4: [], 5: []}
        for code in self.codes:
            with open("data\\" + code.file, "r", encoding="utf-8") as file:
                lt = list(map(lambda s: (s.rstrip("\n"), code.type), file.readlines()))
                self.dict[code.rank].extend(lt)

    @property
    def data(self):
        self._load() if self.dict is None else None
        return self.dict

    @property
    def names(self):
        self._load() if self.dict is None else None
        return self.flatData(self.dict)

    @staticmethod
    def exclude(data: dict[int, list], exclude: dict[int, list]) -> dict[int, list]:
        assert (
            exclude.keys() <= data.keys()
        ), "Exclude keys must be a subset of data keys."
        updated = {k: list(set(data[k]) - set(ex)) for k, ex in exclude.items()}
        return data.update(updated)

    @staticmethod
    def flatData(data):
        if isinstance(data, list):
            return [t[0] for t in data]
        if isinstance(data, dict):
            return {k: [t[0] for t in v] for k, v in data.items()}
        raise TypeError("Input is not a list or dict.")


class SavedPool:
    pool_file = r"config\defaultPools.json"

    def __init__(self, pool_id: int) -> None:
        self.pool_id = pool_id

    def get(self):
        with open(self.pool_file, "r", encoding="utf-8") as js:
            return json.load(
                js,
                object_hook=lambda d: {
                    int(k): [tuple(t) for t in v] if type(v) == list else v
                    for k, v in d.items()
                },
            )[self.pool_id]

    def save(self, d: dict):
        with open(self.pool_file, "r", encoding="utf-8") as js:
            data = json.load(
                js, object_hook=lambda d: {int(k): v for k, v in d.items()}
            )
            data[self.pool_id] = d

        with open(self.pool_file, "w", encoding="utf-8") as js:
            json.dump(data, js, ensure_ascii=False)


class SavedChroniclePool:
    pool_file = r"config\chroniclePool.json"

    @classmethod
    def get(cls):
        with open(cls.pool_file, "r", encoding="utf-8") as js:
            return json.load(
                js, object_hook=lambda d: {int(k): v for k, v in d.items()}
            )

    @classmethod
    def save(cls, d: dict):
        with open(cls.pool_file, "w", encoding="utf-8") as js:
            json.dump(d, js, ensure_ascii=False)


if __name__ == "__main__":
    d = {0: {}, 1: {}}

    SavedChroniclePool.save()
