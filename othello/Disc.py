from dataclasses import dataclass
from collections import namedtuple


@dataclass(frozen=True)
class Point:
    """
    石の位置を指定する座標系クラス．

    Attributes:
        x (int): x座標．
        y (int): y座標．
    """
    x: int = 0
    y: int = 0


@dataclass(frozen=True)
class Disc(Point):
    """
    石の表すクラス．

    Attributes:
        x (int): x座標．
        y (int): y座標．
        color (int): 色．
    """
    color: int = 0


DISC_META = namedtuple("__DiscMeta", "BLACK EMPTY WHITE WALL")(1, 0, -1, 2)


if __name__ == "__main__":
    d0 = Disc()
    print(d0.x, d0.y, d0.color)
    d1 = Disc(10, 20, DISC_META.WHITE)
    print(d1.x, d1.y, d1.color)
