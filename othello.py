import pygame as pg
import numpy as np

BLACK = 1
WHITE = -1
NONE = 0


class Board:
    def __init__(self, n):
        assert not (n & 1)
        self._n = n
        self.stone = np.zeros((n, n))
        tmp = n >> 1
        self.stone[tmp - 1, tmp - 1] = WHITE
        self.stone[tmp, tmp] = WHITE
        self.stone[tmp - 1, tmp] = BLACK
        self.stone[tmp, tmp - 1] = BLACK

        self.nowturn = BLACK
        self.hist = []

        # 0: normal
        # 1: lose a turn
        # 2: end
        self.status = 0

    def __valid(self, i, j, di, dj, nt):
        n = self._n
        if not (0 <= i < n and 0 <= j < n):
            return 0
        if self.stone[i, j]:
            return 0

        ni = i + di
        nj = j + dj
        num = 0

        while True:
            if not (0 <= ni < n and 0 <= nj < n):
                num = 0
                break
            if not self.stone[ni, nj]:  # none
                num = 0
                break
            if self.stone[ni, nj] + nt:
                break
            num += 1
            ni += di
            nj += dj
        return num

    def valid(self, i, j):
        di = [0, 1, 1, 1, 0, -1, -1, -1]
        dj = [-1, -1, 0, 1, 1, 1, 0, -1]
        res = False
        snap = True
        good = np.zeros(8, int)

        for k in range(8):
            num = self.__valid(i, j, di[k], dj[k], self.nowturn)
            good[k] = num

        for k in range(8):
            if good[k]:
                if snap:
                    self.snapshot()
                    snap = False
                res = True
                for L in range(good[k] + 1):
                    self.stone[i + di[k] * L, j + dj[k] * L] = self.nowturn
        return res

    def next(self):
        n = self._n
        di = [0, 1, 1, 1, 0, -1, -1, -1]
        dj = [-1, -1, 0, 1, 1, 1, 0, -1]
        for i in range(n):
            for j in range(n):
                for k in range(8):
                    num = self.__valid(i, j, di[k], dj[k], -self.nowturn)
                    if num > 0:
                        self.status = 0
                        self.nowturn = -self.nowturn
                        return
        for i in range(n):
            for j in range(n):
                for k in range(8):
                    num = self.__valid(i, j, di[k], dj[k], self.nowturn)
                    if num > 0:
                        self.status = 1
                        return
        self.status = 2

    def snapshot(self):
        n = self._n
        tmp = np.zeros((n, n))
        for i in range(n):
            for j in range(n):
                tmp[i, j] = self.stone[i, j]
        self.hist.append((tmp, self.nowturn, self.status))

    def rollback(self):
        n = self._n
        if not len(self.hist):
            return
        tmp = self.hist.pop()
        self.nowturn = tmp[1]
        self.status = tmp[2]
        for i in range(n):
            for j in range(n):
                self.stone[i, j] = tmp[0][i, j]


class Game:
    def __init__(self, n, w, h):
        pg.init()
        self.board = Board(n)
        self._n = n
        self.exit_flag = False

        self.disp_w = w
        self.disp_h = h
        self.screen = pg.display.set_mode((w, h))
        self.init_space = 20

        self.font_size = 20
        self.font = pg.font.Font("ipaexg.ttf", self.font_size)

        while not self.exit_flag:
            self.update()
            self.draw()

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
                if self.board.valid(i, j):
                    self.board.next()
        pg.display.update()

    def __convert(self, p):
        i, j = p
        sp = self.init_space
        n = self._n
        h = self.disp_h
        interval = (h - 2 * sp) / n
        i -= sp
        i //= interval
        j -= sp
        j //= interval
        return (int(i), int(j))

    def draw(self):
        sp = self.init_space
        n = self._n
        w = self.disp_w
        h = self.disp_h
        interval = (h - 2 * sp) / n

        self.screen.fill('#009900')
        for i in range(n + 1):
            pg.draw.line(self.screen, '#000000',
                         (sp + i * interval, sp),
                         (sp + i * interval, h - sp))
            pg.draw.line(self.screen, '#000000',
                         (sp, sp + i * interval),
                         (h - sp, sp + i * interval))

        color = {BLACK: "#000000", WHITE: "#ffffff"}
        for i in range(n):
            for j in range(n):
                if self.board.stone[i, j]:
                    pg.draw.circle(self.screen, color[self.board.stone[i][j]],
                                   (sp + interval * (i + 0.5),
                                    sp + interval * (j + 0.5)),
                                   interval / 2 * 0.9)

        self.draw_explanation()
        if self.board.status == 2:
            self.draw_finish()
            return

        row = 5
        color[BLACK] = "黒"
        color[WHITE] = "白"
        st = f"現在のターンは{color[self.board.nowturn]}です"
        txt = self.font.render(st, True, "#000000")
        self.screen.blit(txt, txt.get_rect(
            center=((w + h) / 2, h / 2 - row * self.font_size)))
        if self.board.status == 1:
            row -= 1
            self.draw_lose_a_turn(row)

    def draw_lose_a_turn(self, r):
        w = self.disp_w
        h = self.disp_h
        color = {BLACK: "黒", WHITE: "白"}
        st = f"置く場所がなかったので{color[-self.board.nowturn]}は休みです"
        txt = self.font.render(st, True, "#000000")
        self.screen.blit(txt, txt.get_rect(
            center=((w + h) / 2, h / 2 - r * self.font_size)))

    def draw_finish(self):
        w = self.disp_w
        h = self.disp_h
        color = {BLACK: "黒", WHITE: "白"}
        bl = np.sum(self.board.stone == BLACK)
        wh = np.sum(self.board.stone == WHITE)

        st = ["しゅうりょうーーー", f"黒:{bl}枚", f"白:{wh}枚"]

        if bl == wh:
            st.append("引き分け！！すげー")
        else:
            st.append(f"{color[(bl - wh) // abs(bl - wh)]}の勝ち！！")

        for i, s in enumerate(st):
            txt = self.font.render(s, True, "#000000")
            self.screen.blit(txt, txt.get_rect(
                center=((w + h) / 2, h / 2 - (5 - i) * self.font_size)))

    def draw_explanation(self):
        w = self.disp_w
        h = self.disp_h
        st = ["Q → ゲームをやめる", "Z → 一つもどる"]
        for i, s in enumerate(st):
            txt = self.font.render(s, True, "#000000")
            self.screen.blit(txt, txt.get_rect(
                center=((w + h) / 2, h / 2 + (5 - i) * self.font_size)))


if __name__ == '__main__':
    DISPLAY_W = 1000
    DISPLAY_H = 600
    n = 6
    Game(n, DISPLAY_W, DISPLAY_H)
    pg.quit()
