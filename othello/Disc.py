from Point import Point


class disc_meta(type):
    """
    石の色を表す定数のメタクラス．

    Attributes:
        BLACK (int): 黒石
        EMPTY (int): 空状態
        WHITE (int): 白石
        WALL (int): 壁
    """

    def __init__(cls, *args, **kwargs):
        cls.__black: int = 1
        cls.__empty: int = 0
        cls.__white: int = -1
        cls.__wall: int = 2

    @property
    def BLACK(cls) -> int:
        return cls.__black

    @property
    def EMPTY(cls) -> int:
        return cls.__empty

    @property
    def WHITE(cls) -> int:
        return cls.__white

    @property
    def WALL(cls) -> int:
        return cls.__wall


class Disc(Point, metaclass=disc_meta):
    """
    石の表すクラス．

    Attributes:
        x (int): x座標．
        y (int): y座標．
        color (int): 色．
    """

    def __init__(self, x:int=0, y:int=0, color:int=disc_meta.EMPTY):
        super().__init__(x, y)
        self.color = color


if __name__ == "__main__":
    d0 = Disc()
    print(d0.x, d0.y, d0.color)
    d1 = Disc(10, 20, Disc.WHITE)
    print(d1.x, d1.y, d1.color)
