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


@dataclass(frozen=True)
class Color:
    """
    石の色を表すクラス．

    Attributes:
        BLACK (int): 黒石．
        EMPTY (int): 空状態．
        WHITE (int): 白石．
        WALL (int): 壁．
    """
    BLACK: int = 1
    EMPTY: int = 0
    WHITE: int = -1
    WALL: int = 2


COLOR = Color()


if __name__ == "__main__":
    d0 = Disc()
    print(d0.x, d0.y, d0.color)
    d1 = Disc(10, 20, COLOR.WHITE)
    print(d1.x, d1.y, d1.color)
