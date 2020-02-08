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
        # self.__raw_board: List[List[int]] = None
        self.__turns: int = 0

        self.__current_color: int = 0
        # self.__update_log: List[List[Disc]] = []
        self.__movable_pos: List[List[Point]] = [[] for _ in range(Board.INFO.BOARD_SIZE+1)]
        self.__movable_dir: List[List[List[int]]] = [
            [[0]*(Board.INFO.BOARD_SIZE+2) for _ in range(Board.INFO.BOARD_SIZE+2)]
            for _ in range(Board.INFO.MAX_TURNS+1)]
        self.__discs: ColorStorage = ColorStorage()

        self.init_game()

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
        self.__current_color = -self.__current_color

        self.__init_movable()

        return True

    def pass_turn(self):
        """
        パスをする．成功したらTrueが返る．パス出来ない場合は（打つ手がある場合は）Falseが返る．

        Return:
            (bool) パスが成功したかどうか．
        """
        # 打つ手があるなら，パスは出来ない．
        if len(self.__movable_pos[self.__turns]) != 0:
            return False
        # ゲームが終了しているなら，パスは出来ない．
        if self.is_game_over():
            return False

        self.__current_color = -self.__current_color
        self.__update_log.append([])
        self.__init_movable()

        return True

    def undo(self):
        """
        直前の一手を元に戻す．成功するとTrueが返る．もとに戻せない場合，すなわち
        まだ一手も打っていない場合はFalseが返る．
        """
        if self.__turns == 0:
            return False

        self.__current_color = -self.__current_color

        update: List[Disc] = self.__update_log.pop()

        # 前回がパスかどうかで場合分け
        if not update:
            # 前回はパス
            # MovablePosとMovableDirを再構築
            self.__movable_pos[self.__turns].clear()
            for x in range(1, Board.INFO.MAX_TURNS):
                for y in range(1, Board.INFO.MAX_TURNS):
                    self.__movable_dir[self.__turns][x][y] = Board.DIRECTION.NONE
        else:
            # 前回はパスではない
            self.__turns -= 1

            # 石をもとに戻す
            p = update[0]
            self.__raw_board[p.x][p.y] = COLOR.EMPTY
            for i in range(1, len(update)):
                p = update[i]
                self.__raw_board[p.x][p.y] = -self.__current_color

            # 石の更新
            disc_diff = len(update)
            self.__discs[self.__current_color] -= disc_diff
            self.__discs[-self.__current_color] += disc_diff - 1
            self.__discs[COLOR.EMPTY] += 1

        return True

    def is_game_over(self) -> bool:
        """
        ゲームが終了していればTrueを，終了していなければFalseを返す．

        Return:
            (bool) ゲームが終了しているか．
        """
        # 60手に達していたらゲーム終了
        if self.__turns == Board.INFO.MAX_TURNS:
            return True
        # 打てる手があるならゲーム終了ではない
        if len(self.__movable_pos[self.__turns]) != 0:
            return False

        # 現在の手番と逆の色が打てるかどうかを調べる
        for x in range(1, Board.INFO.MAX_TURNS+1):
            for y in range(1, Board.INFO.MAX_TURNS+1):
                disc = Disc(x, y, -self.__current_color)
                if self.__check_mobility(disc) != Board.DIRECTION.NONE:
                    return False
        return True

    def init_game(self):
        """
        ボードをゲーム開始直後の状態にする．Boardクラスのインスタンスが生成された直後は，
        コンストラクタによって同様の尾初期化処理が呼ばれているので，initを呼ぶ必要はない．
        """
        # 壁と空きマスでボードを埋める
        self.__raw_board: List[List[int]] = [[COLOR.WALL]*(Board.INFO.BOARD_SIZE+2)] + [
            [COLOR.WALL]+[COLOR.EMPTY]*Board.INFO.BOARD_SIZE+[COLOR.WALL]
            for _ in range(Board.INFO.BOARD_SIZE)
            ] + [[COLOR.WALL]*(Board.INFO.BOARD_SIZE+2)]

        # 初期配置
        self.__raw_board[4][4] = COLOR.WHITE
        self.__raw_board[5][5] = COLOR.WHITE
        self.__raw_board[4][5] = COLOR.BLACK
        self.__raw_board[5][4] = COLOR.BLACK

        # 石数の初期設定
        self.__discs[COLOR.BLACK] = 2
        self.__discs[COLOR.WHITE] = 2
        self.__discs[COLOR.EMPTY] = Board.INFO.BOARD_SIZE * Board.INFO.BOARD_SIZE - 4

        self.__turns = 0
        self.__current_color = COLOR.BLACK

        # updateをすべて削除
        self.__update_log: List[List[Disc]]  = []

        self.__init_movable()

    def count_disc(self, color: int):
        """
        colorで指定された色の石の数を数える．色にはBLACK，WHITE，EMPTYを指定可能．

        Args:
            color (int): 指定する石の色．

        Return:
            (int) 指定された色の石の数
        """
        if color not in (COLOR.BLACK, COLOR.WHITE, COLOR.EMPTY):
            raise ValueError(color)
        return self.__discs[color]

    def get_color(self, point: Point):
        """
        pointで指定された位置の色を返す．

        Args:
            point (Point): 指定する位置．

        Return:
            (int) その位置の色．
        """
        return self.__raw_board[point.x][point.y]

    def get_mvoable_pos(self):
        """
        石を打てる座標が並んだlistを返す．

        Return:
            (List[Point]) 現在のターンの石を打てる座標が並んだlist
        """
        return self.__movable_pos[self.__turns]

    def get_update(self):
        """
        直前の手で打った石と裏返した石が並んだlistを返す．

        Return:
            (List[Disc]) 直前の手で打った石と裏返した石が並んだlist
        """
        if not self.__update_log:
            return []
        return self.__update_log[-1]

    def get_current_color(self):
        """
        現在の手番の色を返す．

        Return:
            (int) 現在の手番の色．
        """
        return self.__current_color

    def get_turns(self):
        """
        現在の手数を返す．最初は０から始まる．

        Return:
            (int) 現在の手番の色．
        """
        return self.__turns

    def __init_movable(self):
        """
        MovablePos[Turns]とMovableDir[Turns]を再計算．
        """
        self.__movable_pos[self.__turns].clear()
        for y in range(1, Board.INFO.BOARD_SIZE+1):
            for x in range(1, Board.INFO.BOARD_SIZE+1):
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
            return Board.DIRECTION.NONE

        _dir = Board.DIRECTION.NONE

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
        self.__discs[-self.__current_color] -= disc_diff - 1
        self.__discs[COLOR.EMPTY] -= 1

        self.__update_log.append(update)


if __name__ == "__main__":
    board = Board()
    for line in board._Board__raw_board:
        print("".join([' ' if c == 0 else 'x' if c == 1 else 'o' if c == -1 else '#' for c in line]))
