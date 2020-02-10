import sys
from abc import abstractmethod
from dataclasses import dataclass
from typing import List

from Disc import Point
from Board import Board


INT_MAX = sys.maxsize


@dataclass
class AI:
    """
    AIの探索アルゴリズムを実装するための抽象クラス．

    Attributes:
        presearch_depth (int): alpha-beta法やNegaScout法において，事前に調べて探索順序を決めるための先読み手数．
        normal_depth (int): 序盤・中盤の探索における先読み手数．
        wld_depth (int): 終盤において，必勝読みを始める残り手数．
        perfect_depth (int): 終盤において，完全読みを始める残り手数．
    """
    presearch_depth: int = 3
    normal_depth: int = 5
    wld_depth: int = 15
    perfect_depth: int = 13

    @abstractmethod
    def move(self):
        pass


class AlphaBetaAI(AI):
    """
    Alpha-Beta法を実装したAIクラス．
    """

    @dataclass(frozen=True)
    class Move(Point):
        """
        Pointに評価値を付け加えたデータクラス．

        Attributes:
            x (int): x座標．
            y (int): y座標．
            evaluated (int): 評価値．
        """
        evaluated: int = 0

    def move(self, board: Board):
        """
        Alpha-Beta法を用いて，Boardを一手動かす．

        Args:
            board (Board): 対戦板
        """
        movables: List[Point] = board.get_mvoable_pos()

        if not movables:
            # 打てる箇所がなければパスする
            board.pass_turn()
            return

        if len(movables) == 1:
            # 打てる箇所が一箇所だけなら探索は行わず、即座に打って返る
            board.move(movables[0])
            return

        limit: int = INT_MAX if (Board.INFO.MAX_TURNS - board.get_turns) <= self.wld_depth else self.normal_depth
        eval_max: int = -INT_MAX
        q: Point = None
        for p in movables:
            board.move(p)
            _eval: int = self.__alphabeta(board, limit-1, -INT_MAX, INT_MAX)
            board.undo()
            if _eval > eval_max:
                eval_max = _eval
                q = p  # イミュータブルなオブジェクトだからコピーは大丈夫なはず
        board.move(q)

    def __alphabeta(self, board: Board, limit: int, alpha: int, beta: int) -> int:
        """
        Alpha-Beta法．

        Args:
            board (Board): 対戦板．
            limit (int): 上限値．
            alpha (int): alpha．
            beta (int): beta．

        Return:
            (int) 評価値．
        """
        if board.is_game_over() or limit == 0:
            # 深さの上限に達したら評価値を返す．
            return self.__evaluate(board)

        pos: List[Point] = board.get_mvoable_pos()

        if not pos:
            # パスの時
            board.pass_turn()
            _eval: int = -self.__alphabeta(board, limit, -beta, -alpha)
            board.undo()
            return _eval

        for p in pos:
            board.move(p)
            _eval: int = -self.__alphabeta(board, limit-1, -beta, -alpha)
            board.undo()

            alpha = alpha if alpha >= _eval else _eval

            if alpha >= beta:
                # ベータ刈り
                return alpha
        return alpha

    def __evaluate(self, board: Board) -> int:
        return 0

    def __sort(self, board: Board, movables: List[Point], limit: int) -> List[Point]:
        """
        事前に浅い先読みを行って評価値の高い順に手を並べ替える．

        Args:
            board (Board): 対戦板．
            movables (List[Point]): 移動可能（移動予定順になっている）Pointのリスト．
            limit (int): 上限．

        Return:
            (List[Point]) 浅い先読みでソートされたリスト．
        """
        moves: List[AlphaBetaAI.Move] = []

        for p in movables:
            board.move(p)
            _eval: int = -self.__alphabeta(board, limit-1, -INT_MAX, INT_MAX)
            board.undo()
            moves.append(AlphaBetaAI.Move(p.x, p.y, _eval))

        # 評価値の大きい順にソート
        moves.sort(reverse=True, key=lambda x: x.evaluated)

        # 結果の書き直し
        return moves


if __name__ == "__main__":
    ai = AlphaBetaAI()
    print(ai.__dir__())
