'''
Gacha Items Data
'''
import json

from collections import namedtuple

from consts import CH, WP

_Code = namedtuple('Code',['file','rank','type'])
C4 = _Code('4StarCharacters.txt', 4, CH)
C5L = _Code('5StarCharacters_Lmt.txt', 5, CH)
C5S = _Code('5StarCharacters_Std.txt', 5, CH)
W4L = _Code('4StarWeapons_Lmt.txt', 4, WP)
W4S = _Code('4StarWeapons_Std.txt', 4, WP)
W5L = _Code('5StarWeapons_Lmt.txt', 5, WP)
W5S = _Code('5StarWeapons_Std.txt', 5, WP)


class DataList():
    def __init__(self, *args) -> None:
        self.lists = {4:[],5:[]}
        for code in args:
            assert isinstance(code,_Code), f'Variable {code} is not a valid code!'
            with open('data\\'+code.file,'r',encoding='utf-8') as file:
                lt = list(map(lambda s:[s.rstrip('\n'), code.type], file.readlines()))
                self.lists[code.rank].extend(lt)

    @property
    def data(self):
        return self.lists
    
    @property
    def names(self):
        return self.flatData(self.lists)
    
    @staticmethod
    def flatData(data):
        if isinstance(data, list):
            return [t[0] for t in data]
        if isinstance(data, dict):
            return {k:[t[0] for t in v] for k,v in data.items()}
        return False


class SavedPool():
    def __init__(self, rank:int) -> None:
        self.rank = rank

    def get(self):
        with open(r'config\defaultPools.json','r',encoding='utf-8') as js:
            return json.load(js, object_hook=lambda d:{int(k):v for k,v in d.items()})[self.rank]
        
    def save(self, d:dict):
        with open(r'config\defaultPools.json','r',encoding='utf-8') as js:
            data = json.load(js, object_hook=lambda d:{int(k):v for k,v in d.items()})
            data[self.rank] = d

        with open(r'config\defaultPools.json','w',encoding='utf-8') as js:    
            json.dump(data, js, ensure_ascii=False)


# if __name__ == '__main__':
#     SavedPool(0).save({
#                 5: [('枫原万叶','角色')],
#                 4: [('瑶瑶','角色'),('香菱','角色'),('鹿野院平藏','角色')]
#             })
#     SavedPool(1).save({
#         5: [('苍古自由之誓','武器'),('裁叶翠光','武器')],
#         4: [('曚云之月','武器'),('断浪长鳍','武器'),('西风剑','武器'),('祭礼大剑','武器'),('西风秘典','武器')]
#     })