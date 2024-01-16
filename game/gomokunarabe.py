import pygame as pg
import numpy as np
import copy

BLACK = 1
WHITE = -1
NONE = 0
BOARD_SIZE = 14


class Board:
    def __init__(self):
        n = BOARD_SIZE
        self.stone = np.zeros((n + 1, n + 1))

        self.nowturn = BLACK
        self.hist = []

        # 0: normal
        # BLACK: black win
        # WHITE: white win
        # 2: draw
        self.status = 0

    def __valid(self, i, j):
        n = BOARD_SIZE
        if not (0 <= i < n + 1 and 0 <= j < n + 1):
            return 0
        if self.stone[i, j]:
            return 0
        if self.status:
            return 0
        return 1

    def valid(self, i, j):
        i = int(i)
        j = int(j)
        if not self.__valid(i, j):
            return
        self.snapshot()
        self.stone[i, j] = self.nowturn
        self.next(i, j)

    def next(self, i, j):
        n = BOARD_SIZE
        di = [0, 1, 1, 1]
        dj = [-1, -1, 0, 1]

        for k in range(4):
            for ii in range(5):
                ni = i + ii * di[k]
                nj = j + ii * dj[k]
                nii = i + (ii - 4) * di[k]
                njj = j + (ii - 4) * dj[k]
                if not (0 <= ni < n + 1 and 0 <= nj < n + 1):
                    continue
                if not (0 <= nii < n + 1 and 0 <= njj < n + 1):
                    continue
                tmp = -self.nowturn * 5
                for _ in range(5):
                    tmp += self.stone[ni, nj]
                    ni -= di[k]
                    nj -= dj[k]

                if not tmp:
                    self.status = self.nowturn
                    return
        if not np.sum(self.stone == NONE):
            self.status = 2
            return
        self.nowturn = -self.nowturn

    def snapshot(self):
        self.hist.append((copy.deepcopy(self.stone),
                          self.nowturn, self.status))

    def rollback(self):
        n = BOARD_SIZE
        if not len(self.hist):
            return
        tmp = self.hist.pop()
        self.nowturn = tmp[1]
        self.status = tmp[2]
        self.stone = copy.deepcopy(tmp[0])


class Game:
    def __init__(self, w, h):
        pg.init()
        pg.display.set_caption("五目並べ")   
        self.board = Board()
        self.exit_flag = False

        self.disp_w = w
        self.disp_h = h
        self.screen = pg.display.set_mode((w, h))
        self.init_space = 20

        self.font_size = 20
        self.font = pg.font.Font("../Mplus1-Black.ttf", self.font_size)

        while not self.exit_flag:
            self.update()
            self.draw()
        pg.quit()

    def update(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:  # ウィンドウ[X]の押下
                self.exit_flag = True
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_z:
                    self.board.rollback()
                if event.key == pg.K_q:
                    self.exit_flag = True
            if event.type == pg.MOUSEBUTTONDOWN:
                i, j = self.__convert(pg.mouse.get_pos())
                self.board.valid(i, j)
        pg.display.update()

    def __convert(self, p):
        i, j = p
        sp = self.init_space
        n = BOARD_SIZE
        h = self.disp_h
        interval = (h - 2 * sp) / n
        i -= sp - interval / 2
        i //= interval
        j -= sp - interval / 2
        j //= interval
        return (i, j)

    def draw(self):
        sp = self.init_space
        n = BOARD_SIZE
        w = self.disp_w
        h = self.disp_h
        interval = (h - 2 * sp) / n

        self.screen.fill('#c18a39')
        for i in range(n + 1):
            pg.draw.line(self.screen, '#000000',
                         (sp + i * interval, sp),
                         (sp + i * interval, h - sp))
            pg.draw.line(self.screen, '#000000',
                         (sp, sp + i * interval),
                         (h - sp, sp + i * interval))

        chobo = ((3, 3), (3, n - 3), (n - 3, 3), (n - 3, n - 3))
        for i, j in chobo:
            pg.draw.circle(self.screen, '#000000',
                           (sp + i * interval, sp + j * interval), 3)

        color = {BLACK: "#000000", WHITE: "#ffffff"}
        for i in range(n + 1):
            for j in range(n + 1):
                if self.board.stone[i, j]:
                    pg.draw.circle(self.screen, color[self.board.stone[i][j]],
                                   (sp + interval * i,
                                    sp + interval * j),
                                   interval / 2 * 0.9)

        self.draw_explanation()
        if self.board.status:
            self.draw_finish()
            return

        row = 5
        color[BLACK] = "黒"
        color[WHITE] = "白"
        st = f"現在のターンは{color[self.board.nowturn]}です"
        txt = self.font.render(st, True, "#000000")
        self.screen.blit(txt, txt.get_rect(
            center=((w + h) / 2, h / 2 - row * self.font_size)))

    def draw_finish(self):
        w = self.disp_w
        h = self.disp_h
        color = {BLACK: "黒", WHITE: "白"}
        bl = np.sum(self.board.stone == BLACK)
        wh = np.sum(self.board.stone == WHITE)
        st = ["しゅうりょうーーー"]

        if self.board.status == 2:
            st.append("引き分け！！すげー")
        else:
            st.append(f"{color[self.board.status]}の勝ち！！")

        for i, s in enumerate(st):
            txt = self.font.render(s, True, "#000000")
            self.screen.blit(txt, txt.get_rect(
                center=((w + h) / 2, h / 2 - (5 - i) * self.font_size)))

    def draw_explanation(self):
        w = self.disp_w
        h = self.disp_h
        st = ["Q: ゲームをやめる", "Z: 一つもどる", "CLICK: 石を置く"]
        for i, s in enumerate(st):
            txt = self.font.render(s, True, "#000000")
            self.screen.blit(txt, txt.get_rect(
                center=((w + h) / 2, h / 2 + (5 + i) * self.font_size)))


if __name__ == '__main__':
    DISPLAY_W = 1000
    DISPLAY_H = 600
    Game(DISPLAY_W, DISPLAY_H)
