from collections import namedtuple
from typing import List

from Disc import Point, Disc, COLOR


_BoardInfo = namedtuple("_BoardInfo", "BOARD_SIZE MAX_TURNS")
_DirBitmask = namedtuple("_DirBitmask", "NONE UPPER UPPER_LEFT LEFT LOWER_LEFT LOWER LOWER_RIGHT RIGHT UPPER_RIGHT")


class ColorStorage:
    """
    石数を保存するクラス．
    """
    def __init__(self):
        self.__data: List[int] = [0] * 3

    def __getitem__(self, key: int):
        if not isinstance(key, int) or key not in (-1, 0, 1):
            raise KeyError(key)
        return self.__data[key + 1]

    def __setitem__(self, key: int, value: int):
        if not isinstance(key, int) or key not in (-1, 0, 1):
            raise KeyError(key)
        if not isinstance(value, int):
            raise ValueError(value)
        self.__data[key + 1] = value


class Board:
    INFO = _BoardInfo(8, 60)
    DIRECTION = _DirBitmask(0, 1, 2, 4, 8, 16, 32, 64, 128)

    def __init__(self):
        self.__raw_board: List[List[int]] = [[0]*(Board.INFO.BOARD_SIZE+2) for _ in range(Board.INFO.BOARD_SIZE+2)]
        self.__turns: int = 0

        self.__current_color: int = 0
        self.__update_log: List[List[Disc]] = []
        self.__movable_pos: List[List[Point]] = [[] for _ in range(Board.INFO.BOARD_SIZE+1)]
        self.__movable_dir: List[List[List[int]]] = [
            [[0]*(Board.INFO.BOARD_SIZE+2) for _ in range(Board.INFO.BOARD_SIZE+2)]
            for _ in range(Board.INFO.MAX_TURNS+1)]
        self.__discs: ColorStorage = ColorStorage()

    def move(self, point: Point) -> bool:
        """
        pointで指定された位置に石を打つ．処理が成功したらTrue，失敗したらFalseが返る．

        Args:
            point (Point): 指定位置．

        Return:
            (bool) 処理が成功したかどうか．
        """
        if point.x < 0 or Board.INFO.BOARD_SIZE <= point.x:
            return False
        if point.y < 0 or Board.INFO.BOARD_SIZE <= point.y:
            return False
        if self.__movable_dir[self.__turns][point.x][point.y] == Board.DIRECTION.NONE:
            return False

        self.__flip_discs(point)

        self.__turns += 1
        self.__current_color *= -1

        self.__init_movable()

        return True

    def Pass(self):
        pass

    def undo(self):
        pass

    def is_game_over(self):
        pass

    def __init_movable(self):
        """
        MovablePos[Turns]とMovableDir[Turns]を再計算．
        """
        self.__movable_pos[self.__turns].clear()
        for y in range(Board.INFO.BOARD_SIZE):
            for x in range(Board.INFO.BOARD_SIZE):
                _disc = Disc(x, y, self.__current_color)
                _dir = self.__check_mobility(_disc)
                if _dir != Board.DIRECTION.NONE:
                    self.__movable_pos[self.__turns].append(_disc)
                self.__movable_dir[self.__turns][x][y] = _dir

    def __check_mobility(self, disc: Disc) -> Disc:
        """
        discで指定された座標に，disc.colorの色の石を打てるかどうか，また，どの方向に石を裏返せるかを判定する．
        石を裏返せる方向にフラグが立った整数値が返る．

        Args:
            disc (Disc): 石の位置．

        Return:
            Disc: その位置に置いた場合石を裏返す事ができる方向．
        """
        # すでに石が置いてあったら置けない
        if self.__raw_board[disc.x][disc.y] != COLOR.EMPTY:
            return Board.INFO.NONE

        _dir = Board.INFO.NONE

        # 上
        if self.__raw_board[disc.x][disc.y-1] == -disc.color:
            _x, _y = disc.x, disc.y-2
            while self.__raw_board[_x][_y] == -disc.color:
                _y -= 1
            if self.__raw_board[_x][_y] == disc.color:
                _dir |= Board.DIRECTION.UPPER

        # 下
        if self.__raw_board[disc.x][disc.y+1] == -disc.color:
            _x, _y = disc.x, disc.y+2
            while self.__raw_board[_x][_y] == -disc.color:
                _y += 1
            if self.__raw_board[_x][_y] == disc.color:
                _dir |= Board.DIRECTION.LOWER

        # 左
        if self.__raw_board[disc.x-1][disc.y] == -disc.color:
            _x, _y = disc.x-2, disc.y
            while self.__raw_board[_x][_y] == -disc.color:
                _x -= 1
            if self.__raw_board[_x][_y] == disc.color:
                _dir |= Board.DIRECTION.LEFT

        # 右
        if self.__raw_board[disc.x+1][disc.y] == -disc.color:
            _x, _y = disc.x+2, disc.y
            while self.__raw_board[_x][_y] == -disc.color:
                _x += 1
            if self.__raw_board[_x][_y] == disc.color:
                _dir |= Board.DIRECTION.RIGHT

        # 右上
        if self.__raw_board[disc.x+1][disc.y-1] == -disc.color:
            _x, _y = disc.x+2, disc.y-2
            while self.__raw_board[_x][_y] == -disc.color:
                _x += 1
                _y -= 1
            if self.__raw_board[_x][_y] == disc.color:
                _dir |= Board.DIRECTION.UPPER_RIGHT

        # 左上
        if self.__raw_board[disc.x-1][disc.y-1] == -disc.color:
            _x, _y = disc.x-2, disc.y-2
            while self.__raw_board[_x][_y] == -disc.color:
                _x -= 1
                _y -= 1
            if self.__raw_board[_x][_y] == disc.color:
                _dir |= Board.DIRECTION.UPPER_LEFT

        # 左下
        if self.__raw_board[disc.x-1][disc.y+1] == -disc.color:
            _x, _y = disc.x-2, disc.y+2
            while self.__raw_board[_x][_y] == -disc.color:
                _x -= 1
                _y += 1
            if self.__raw_board[_x][_y] == disc.color:
                _dir |= Board.DIRECTION.LOWER_LEFT

        # 右下
        if self.__raw_board[disc.x+1][disc.y+1] == -disc.color:
            _x, _y = disc.x+2, disc.y+2
            while self.__raw_board[_x][_y] == -disc.color:
                _x += 1
                _y += 1
            if self.__raw_board[_x][_y] == disc.color:
                _dir |= Board.DIRECTION.LOWER_RIGHT

        return _dir

    def __flip_discs(self, point: Point):
        """
        pointで指定された位置に石を打ち，挟み込めるすべての石を裏返す．
        「打った石」と「裏返した石」をUpdateLogに挿入する．

        Args:
            point (Point): point
        """
        _dir = self.__movable_dir[self.__turns][point.x][point.y]
        update = []
        self.__raw_board[point.x][point.y] = self.__current_color
        update.append(Disc(point.x, point.y, self.__current_color))

        # 上
        if (_dir & Board.DIRECTION.UPPER) != Board.DIRECTION.NONE:
            _y = point.y - 1
            while self.__raw_board[point.x][_y] != self.__current_color:
                self.__raw_board[point.x][_y] = self.__current_color
                update.append(Disc(point.x, _y, self.__current_color))
                _y -= 1

        # 下
        if (_dir & Board.DIRECTION.LOWER) != Board.DIRECTION.NONE:
            _y = point.y + 1
            while self.__raw_board[point.x][_y] != self.__current_color:
                self.__raw_board[point.x][_y] = self.__current_color
                update.append(Disc(point.x, _y, self.__current_color))
                _y += 1

        # 左
        if (_dir & Board.DIRECTION.LEFT) != Board.DIRECTION.NONE:
            _x = point.x - 1
            while self.__raw_board[_x][point.y] != self.__current_color:
                self.__raw_board[_x][point.y] = self.__current_color
                update.append(Disc(_x, point.y, self.__current_color))
                _x -= 1

        # 右
        if (_dir & Board.DIRECTION.RIGHT) != Board.DIRECTION.NONE:
            _x = point.x + 1
            while self.__raw_board[_x][point.y] != self.__current_color:
                self.__raw_board[_x][point.y] = self.__current_color
                update.append(Disc(_x, point.y, self.__current_color))
                _x += 1

        # 右上
        if (_dir & Board.DIRECTION.UPPER_RIGHT) != Board.DIRECTION.NONE:
            _x, _y = point.x + 1, point.y - 1
            while self.__raw_board[_x][_y] != self.__current_color:
                self.__raw_board[_x][_y] = self.__current_color
                update.append(Disc(_x, _y, self.__current_color))
                _x, _y = _x + 1, _y - 1

        # 左上
        if (_dir & Board.DIRECTION.UPPER_LEFT) != Board.DIRECTION.NONE:
            _x, _y = point.x - 1, point.y - 1
            while self.__raw_board[_x][_y] != self.__current_color:
                self.__raw_board[_x][_y] = self.__current_color
                update.append(Disc(_x, _y, self.__current_color))
                _x, _y = _x - 1, _y - 1

        # 左下
        if (_dir & Board.DIRECTION.LOWER_LEFT) != Board.DIRECTION.NONE:
            _x, _y = point.x - 1, point.y + 1
            while self.__raw_board[_x][_y] != self.__current_color:
                self.__raw_board[_x][_y] = self.__current_color
                update.append(Disc(_x, _y, self.__current_color))
                _x, _y = _x - 1, _y + 1

        # 右下
        if (_dir & Board.DIRECTION.LOWER_RIGHT) != Board.DIRECTION.NONE:
            _x, _y = point.x + 1, point.y + 1
            while self.__raw_board[_x][_y] != self.__current_color:
                self.__raw_board[_x][_y] = self.__current_color
                update.append(Disc(_x, _y, self.__current_color))
                _x, _y = _x + 1, _y + 1

        disc_diff = len(update)

        self.__discs[self.__current_color] += disc_diff
        self.__discs[self.__current_color*-1] -= disc_diff
        self.__discs[COLOR.EMPTY] -= 1

        self.__update_log.append(update)


if __name__ == "__main__":
    # board = Board()
    # print(board.INFO, Board.INFO)
    c = ColorStorage()
    print(c[COLOR.BLACK], c[COLOR.WHITE])
