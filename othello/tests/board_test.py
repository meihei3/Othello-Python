import sys
sys.path.append('..')

from Board import Board
from Disc import Point, COLOR


OFFSET_ASCII_A = ord("a")


def parse_point(c: str):
    if len(c) < 2:
        raise ValueError(c)
    return Point(ord(c[0])-OFFSET_ASCII_A+1, int(c[1]))


def print_board(board: Board):
    print("   a b c d e f g h ")
    print(" +-----------------+")
    for y in range(1, 9):
        print(y, end="| ")
        for x in range(1, 9):
            c = board.get_color(Point(x, y))
            print("X" if c==COLOR.BLACK else \
                  "O" if c==COLOR.WHITE else \
                  " ", end=" ")
        print("|")
    print(" +-----------------+")


def main():
    board = Board()

    while True:
        print_board(board)
        print("黒石:", board.count_disc(COLOR.BLACK),
              "白石:", board.count_disc(COLOR.WHITE),
              "空マス:", board.count_disc(COLOR.EMPTY), end='\n\n')
        inp = input("手を入力してください: ")

        if inp == 'p':
            if not board.pass_turn():
                print("パス出来ません！")
            continue

        if inp == 'u':
            board.undo()
            continue

        try:
            p = parse_point(inp)
        except:
            print("リバーシ形式の手を入力してください！")
            continue

        if not board.move(p):
            print("そこには置けません！")

        if board.is_game_over():
            print("--------------- ゲーム終了 ---------------")
            break


if __name__ == "__main__":
    main()
    # parse_point("a1")