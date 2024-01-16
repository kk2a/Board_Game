import pygame as pg
import numpy as np
import copy

RED = 1
BLUE = -1
NONE = 0


class Board:
    def __init__(self, dot):
        self._w, self._h = dot
        assert self._w > 1 and self._h > 1

        # (odd, even) or (even, odd) -> edge
        # (odd, odd) -> cell
        # (even, even) -> dot
        self.board = np.zeros((2 * self._w - 1, 2 * self._h - 1), int)

        self.now = RED
        self.hist = []

        # 0: normal
        # 1: again
        # 2: end
        self.status = 0

    def valid_line(self, i, j):
        w = self._w
        h = self._h

        if not (i + j) & 1:
            return False
        if not (0 <= i < 2 * w - 1 and 0 <= j < 2 * h - 1):
            return False
        if self.board[i, j]:
            return False
        return True

    def write(self, i, j):
        if not self.valid_line(i, j):
            return
        self.snapshot()
        self.board[i, j] = self.now
        self.next(i, j)

    def next(self, i, j):
        h = self._h
        w = self._w
        di = (1, 0, -1, 0)
        dj = (0, 1, 0, -1)

        self.status = 0
        for d in range(4):
            ni = i + di[d]
            nj = j + dj[d]
            if not (0 <= ni < 2 * w - 1 and 0 <= nj < 2 * h - 1):
                continue
            if not (ni & 1 and nj & 1):
                continue
            flag = True
            for dd in range(4):
                if not self.board[ni + di[dd], nj + dj[dd]]:
                    flag = False
                    break
            if flag:
                self.board[ni, nj] = self.now
                self.status = 1
        self.is_end()
        self.now *= -1 if not self.status else 1

    def is_end(self):
        h = self._h
        w = self._w
        for i in range(2 * w - 1):
            for j in range(2 * h - 1):
                if (i + j) & 1 and not self.board[i, j]:
                    return
        self.status = 2

    def snapshot(self):
        self.hist.append((copy.deepcopy(self.board),
                          self.now, self.status))

    def undo(self):
        if not len(self.hist):
            return
        tmp = self.hist.pop()
        self.board, self.now, self.status = tmp


class Game:
    def __init__(self, disp, dot):
        pg.init()
        pg.display.set_caption("dot and box")
        self.disp_w, self.disp_h = disp
        if dot[0] > dot[1]:
            # 描画のことを考えてswapしておく
            dot = (dot[1], dot[0])
        self.dot_w, self.dot_h = dot
        self.board = Board(dot)
        self.init_space = 50
        self.interval = (self.disp_h - 2 *
                         self.init_space) / (self.dot_h - 1)
        self.screen = pg.display.set_mode((self.disp_w, self.disp_h))
        self.dot_r = 4
        self.color = {RED: "#ff0000", BLUE: "#0000ff"}

        self.font_size = 20
        self.font = pg.font.Font("../Mplus1-Black.ttf", self.font_size)

        self.exit_flag = False

        while not self.exit_flag:
            self.update()
            self.draw()
        pg.quit()

    def update(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.exit_flag = True
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_q:
                    self.exit_flag = True
                if event.key == pg.K_z:
                    self.board.undo()
            if event.type == pg.MOUSEBUTTONDOWN:
                i, j = self.mouse_pos_con()
                self.board.write(i, j)
        pg.display.update()

    def draw(self):
        self.screen.fill("#ffffff")
        self.draw_dot()
        self.draw_line_guide()
        self.draw_lines()
        self.draw_cells()
        self.draw_explanation()
        if self.board.status == 2:
            self.draw_finish()
            return
        self.draw_turn()

    def mouse_pos_con(self):
        sp = self.init_space
        interval = self.interval

        tmp = 2 ** (-0.5)
        rot = np.array([[tmp, tmp], [-tmp, tmp]])

        pos = np.array(pg.mouse.get_pos(), float)
        pos -= sp
        pos = rot @ pos
        pos //= interval * tmp
        return (int(pos[0] - pos[1]), int(pos[0] + pos[1] + 1))

    def draw_dot(self):
        sp = self.init_space
        h = self.dot_h
        w = self.dot_w
        r = self.dot_r
        interval = self.interval

        for i in range(w):
            for j in range(h):
                pg.draw.circle(self.screen, "#000000",
                               (sp + interval * i + 1,
                                sp + interval * j + 1), r)

    def __draw_line(self, pos, color, f=False):
        h = self.dot_h
        sp = self.init_space
        interval = self.interval
        width = 1 if f else 2
        i, j = pos

        assert (i + j) & 1
        d = ((1, 0), (-1, 0)) if i & 1 else ((0, 1), (0, -1))
        start = (sp + interval * (i + d[0][0]) / 2,
                 sp + interval * (j + d[0][1]) / 2)
        end = (sp + interval * (i + d[1][0]) / 2,
               sp + interval * (j + d[1][1]) / 2)
        pg.draw.line(self.screen, color, start, end, width)

    def draw_lines(self):
        h = self.dot_h
        w = self.dot_w
        c = self.color

        for i in range(2 * w - 1):
            for j in range(2 * h - 1):
                if not (i + j) & 1:
                    continue
                if not self.board.board[i, j]:
                    continue
                color = c[self.board.board[i, j]]
                self.__draw_line((i, j), color)

    def draw_cells(self):
        h = self.dot_h
        w = self.dot_w
        sp = self.init_space
        interval = self.interval
        c = self.color
        s = {RED: "RED", BLUE: "BLUE"}

        for i in range(2 * w - 1):
            for j in range(2 * h - 1):
                if not (i & 1 and j & 1):
                    continue
                if not self.board.board[i, j]:
                    continue
                value = self.board.board[i, j]
                txt = self.font.render(s[value], True, c[value])
                self.screen.blit(txt, txt.get_rect(
                    center=(sp + interval * (i / 2),
                            sp + interval * (j / 2))
                ))

    def draw_line_guide(self):
        w = self.dot_w
        h = self.dot_h
        pos = self.mouse_pos_con()
        if not (0 <= pos[0] < 2 * w - 1 and 0 <= pos[1] < 2 * h - 1):
            return
        # 点線とかにしたいけど、検索してもいい感じのものが見つからなかった
        # ので、1px細くした
        self.__draw_line(pos, self.color[self.board.now], True)

    def draw_turn(self):
        w = self.disp_w
        h = self.disp_h
        iv = self.interval
        sp = self.init_space
        dw = self.dot_w
        color = {RED: "赤", BLUE: "青"}

        row = 5
        st = f"現在のターンは{color[self.board.now]}です"
        txt = self.font.render(st, True, "#000000")
        self.screen.blit(txt, txt.get_rect(
            center=((sp + iv * (dw - 1) + w) / 2,
                    h / 2 - row * self.font_size)))
        if self.board.status == 1:
            row -= 1
            self.draw_again(row)

    def draw_again(self, row):
        w = self.disp_w
        h = self.disp_h
        iv = self.interval
        sp = self.init_space
        dw = self.dot_w
        color = {RED: "赤", BLUE: "青"}
        st = [f"四角ができました", f"もう一度{color[self.board.now]}のターンです"]
        for s in st:
            txt = self.font.render(s, True, "#000000")
            self.screen.blit(txt, txt.get_rect(
                center=((sp + iv * (dw - 1) + w) / 2,
                        h / 2 - row * self.font_size)))
            row -= 1

    def draw_explanation(self):
        w = self.disp_w
        h = self.disp_h
        iv = self.interval
        sp = self.init_space
        dw = self.dot_w
        st = ["Q: ゲームをやめる", "Z: 一つもどる", "CLICK: 線を書く"]
        for i, s in enumerate(st):
            txt = self.font.render(s, True, "#000000")
            self.screen.blit(txt, txt.get_rect(
                center=((sp + iv * (dw - 1) + w) / 2,
                        h / 2 + (5 + i) * self.font_size)))

    def draw_finish(self):
        w = self.disp_w
        h = self.disp_h
        iv = self.interval
        sp = self.init_space
        dw = self.dot_w
        dh = self.dot_h
        sum = {RED: 0, BLUE: 0}
        for i in range(2 * dw - 1):
            for j in range(2 * dh - 1):
                if not (i & 1 and j & 1):
                    continue
                sum[self.board.board[i, j]] += 1

        st = ["しゅうりょうーーー", f"赤:{sum[RED]}こ", f"青:{sum[BLUE]}こ"]
        if sum[RED] == sum[BLUE]:
            st.append("引き分けじゃん！！いい勝負！！")
        elif sum[RED] > sum[BLUE]:
            st.append("赤の勝ち！！！")
        else:
            st.append("青の勝ち！！！")

        for i, s in enumerate(st):
            txt = self.font.render(s, True, "#000000")
            self.screen.blit(txt, txt.get_rect(
                center=((sp + iv * (dw - 1) + w) / 2,
                        h / 2 - (5 - i) * self.font_size)))

if __name__ == "__main__":
    dot = (5, 7)
    disp = (1000, 600)
    Game(disp, dot)
