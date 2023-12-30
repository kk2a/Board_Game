import pygame as pg
import numpy as np
import copy

RED = 1
YELLOW = -1
NONE = 0

BOARDSIZE_W = 7
BOARDSIZE_H = 6


class Board:
    def __init__(self):
        h = BOARDSIZE_H
        w = BOARDSIZE_W
        self.stone = np.zeros((w, h))
        self.nowturn = RED
        self.hist = []

        # 0: normal
        # RED: red win
        # YELLOW: yellow win
        # 2: draw
        self.status = 0

    def __valid(self, i):
        w = BOARDSIZE_W
        if not (0 <= i < w):
            return 0
        if self.stone[i][0]:
            return 0
        if self.status:
            return 0
        return 1

    def valid(self, i):
        i = int(i)
        h = BOARDSIZE_H
        if not self.__valid(i):
            return
        self.snapshot()
        j = -1
        for ii in reversed(range(h)):
            if not self.stone[i][ii]:
                self.stone[i][ii] = self.nowturn
                j = ii
                break
        self.next(i, j)

    def next(self, i, j):
        h = BOARDSIZE_H
        w = BOARDSIZE_W
        di = [0, 1, 1, 1]
        dj = [-1, -1, 0, 1]

        for k in range(4):
            for ii in range(4):
                ni = i + ii * di[k]
                nj = j + ii * dj[k]
                nii = i + (ii - 3) * di[k]
                njj = j + (ii - 3) * dj[k]
                if not (0 <= ni < w and 0 <= nj < h):
                    continue
                if not (0 <= nii < w and 0 <= njj < h):
                    continue
                tmp = -self.nowturn * 4
                for _ in range(4):
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
        h = BOARDSIZE_H
        w = BOARDSIZE_W
        if not len(self.hist):
            return
        tmp = self.hist.pop()
        self.nowturn = tmp[1]
        self.status = tmp[2]
        self.stone = copy.deepcopy(tmp[0])


class Game:
    def __init__(self, w, h):
        pg.init()
        self.board = Board()
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
                self.board.valid(i)
        pg.display.update()

    def __convert(self, p):
        i, j = p
        sp = self.init_space
        n_h = BOARDSIZE_H
        h = self.disp_h
        interval = (h - 2 * sp) / n_h
        i -= sp
        i //= interval
        j -= sp
        j //= interval
        return (i, j)

    def draw(self):
        sp = self.init_space
        n_h = BOARDSIZE_H
        n_w = BOARDSIZE_W
        w = self.disp_w
        h = self.disp_h
        interval = (h - 2 * sp) / n_h

        back = "#e2e2e2"
        self.screen.fill(back)
        pg.draw.rect(self.screen, "#0981cb", (sp, sp, interval * n_w, interval * n_h))
        for i in range(n_w + 1):
            pg.draw.line(self.screen, '#000000',
                         (sp + i * interval, sp),
                         (sp + i * interval, h - sp))
        for i in range(n_h + 1):
            pg.draw.line(self.screen, '#000000',
                         (sp, sp + i * interval),
                         (h - sp + interval, sp + i * interval))

        for i in range(n_w):
            for j in range(n_h):
                pg.draw.circle(self.screen, back,
                               (sp + interval * (i + 0.5),
                                sp + interval * (j + 0.5)),
                               interval / 2 * 0.85)

        color = {RED: "#e60000", YELLOW: "#e6e645"}
        for i in range(n_w):
            for j in range(n_h):
                if self.board.stone[i, j]:
                    pg.draw.circle(self.screen, color[self.board.stone[i][j]],
                                   (sp + interval * (i + 0.5),
                                    sp + interval * (j + 0.5)),
                                   interval / 2 * 0.85)

        self.draw_explanation()
        if self.board.status:
            self.draw_finish()
            return

        row = 5
        color[RED] = "赤"
        color[YELLOW] = "黄"
        st = f"現在のターンは{color[self.board.nowturn]}です"
        txt = self.font.render(st, True, "#000000")
        self.screen.blit(txt, txt.get_rect(
            center=((w + h + interval) / 2, h / 2 - row * self.font_size)))

    def draw_finish(self):
        w = self.disp_w
        h = self.disp_h
        n_h = BOARDSIZE_H
        sp = self.init_space
        interval = (h - 2 * sp) / n_h

        color = {RED: "赤", YELLOW: "黄"}
        st = ["しゅうりょうーーー"]

        if self.board.status == 2:
            st.append("引き分け！！すげー")
        else:
            st.append(f"{color[self.board.status]}の勝ち！！")

        for i, s in enumerate(st):
            txt = self.font.render(s, True, "#000000")
            self.screen.blit(txt, txt.get_rect(
                center=((w + h + interval) / 2,
                        h / 2 - (5 - i) * self.font_size)))

    def draw_explanation(self):
        w = self.disp_w
        h = self.disp_h
        n_h = BOARDSIZE_H
        sp = self.init_space
        interval = (h - 2 * sp) / n_h
        st = ["Q → ゲームをやめる", "Z → 一つもどる"]
        for i, s in enumerate(st):
            txt = self.font.render(s, True, "#000000")
            self.screen.blit(txt, txt.get_rect(
                center=((w + h + interval) / 2,
                        h / 2 + (5 - i) * self.font_size)))


if __name__ == "__main__":
    DISPLAY_W = 1000
    DISPLAY_H = 600
    Game(DISPLAY_W, DISPLAY_H)
