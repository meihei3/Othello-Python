class Point:
    """
    石の位置を指定する座標系クラス．

    Attributes:
        x (int): x座標．
        y (int): y座標．
    """

    def __init__(self, x:int=0, y:int=0):
    self.__x, self.__y = x, y

    @property
    def x(self):
        return self.__x

    @property
    def y(self):
        return self.__y



if __name__ == "__main__":
    p0 = Point()
    print(p0.x, p0.y)
    p1 = Point(1, 1)
    print(p1.x, p1.y)
    p1.x = 10
    print(p1.x, p1.y)
