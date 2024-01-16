import pygame as pg
import random
import copy


class Dices:
    def __init__(self):
        self.hands = [-1] * 5

    def roll(self, p=[]):
        for i in range(5):
            if i not in p:
                self.hands[i] = random.randint(1, 6)

    def next(self):
        self.hands = [-1] * 5


TABLE = {
    "Ones": -1,
    "Twos": -1,
    "Threes": -1,
    "Fours": -1,
    "Fives": -1,
    "Sixes": -1,
    "Fullhouse": -1,
    "Four of a kind": -1,
    "Four straight": -1,
    "Five straight": -1,
    "Yacht": -1,
    "Choices": -1,
}


class Paper:
    def __init__(self):
        self.table = copy.deepcopy(TABLE)

    def score_sum(self):
        bonus = self.bonus_sum()
        res = 0
        for k, v in self.table.items():
            res += v if v != -1 else 0
        if bonus >= 63:
            res += 35
        return res

    def bonus_sum(self):
        bonus_factor = [
            "Ones", "Twos", "Threes",
            "Fours", "Fives", "Sixes"
        ]
        res = 0
        for k in bonus_factor:
            res += self.table[k] if self.table[k] != -1 else 0
        return res

    def __valid(self, k, dices):
        assert list(TABLE.keys()).count(k)
        d = [0] * 7
        for i in dices.hands:
            d[i] += 1
        only = {
            "Ones": 1, "Twos": 2, "Threes": 3,
            "Fours": 4, "Fives": 5, "Sixes": 6
        }
        straight = {
            "Four straight": (3, 4, 15),
            "Five straight": (2, 5, 30)
        }

        res = 0
        if list(only.keys()).count(k):
            res = only[k] * d[only[k]]
        if k == "Choices":
            for i in range(1, 6 + 1):
                res += i * d[i]
        if k == "Fullhouse":
            if d.count(5) or (d.count(3) and d.count(2)):
                for i in range(1, 6 + 1):
                    res += i * d[i]
        if k == "Four of a kind":
            if d.count(4) or d.count(5):
                for i in range(1, 6 + 1):
                    res += i * d[i]
        if list(straight.keys()).count(k):
            n, m, s = straight[k]
            flag = False
            for i in range(1, n + 1):
                flag1 = True
                for ii in range(m):
                    if not d[i + ii]:
                        flag1 = False
                if flag1:
                    flag = True
            if flag:
                res = s
        if k == "Yacht":
            if d.count(5):
                res = 50
        return res

    def valid_table(self, dices):
        res = copy.deepcopy(self.table)
        for k in TABLE.keys():
            if res[k] != -1:
                res[k] = -1
                continue
            res[k] = self.__valid(k, dices)
        return res

    def check(self, k, dices):
        assert list(TABLE.keys()).count(k)
        if self.table[k] != -1:
            return False
        self.table[k] = self.__valid(k, dices)
        return True


class Game:
    def __init__(self, w, h):
        pg.init()
        pg.display.set_caption("yacht")
        self.p1 = Paper()
        self.p2 = Paper()
        self.d1 = Dices()
        self.d2 = Dices()

        self.now = 0
        self.status = 0
        self.select = []
        self.dcount = 0
        self.roll_count = 0

        self.disp_w = w
        self.disp_h = h
        self.screen = pg.display.set_mode((w, h))
        self.init_space = 10

        self.font_size = 15
        self.font = pg.font.Font("../Mplus1-Black.ttf", self.font_size)

        self.paper_w = w / 3
        self.paper_h = h - 2 * self.init_space
        self.cell = self.paper_h / 20
        self.dsz = 40
        self.csz = self.dsz / 3.5 / 2
        self.dsp = 10
        clock = pg.time.Clock()

        self.d1.roll()
        self.exit_flag = False
        while not self.exit_flag:
            self.update()
            self.draw()
        pg.quit()

    def update(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.exit_flag = True
            if self.status == 1:
                continue
            if event.type == pg.MOUSEBUTTONDOWN:
                if self.roll_count:
                    continue
                self.mouse_click()
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_q:
                    self.exit_flag = True
                if event.key == pg.K_SPACE:
                    if self.dcount == 2:
                        continue
                    if self.roll_count:
                        continue
                    self.roll_count = 30
                    self.dcount += 1
                for i, k in enumerate((pg.K_1, pg.K_2,
                                       pg.K_3, pg.K_4, pg.K_5)):
                    if event.key == k:
                        if i not in self.select:
                            self.select.append(i)
                        else:
                            self.select.remove(i)

        if self.roll_count:
            self.roll_count -= 1
            if not self.roll_count % 3:
                (self.d2 if self.now & 1 else self.d1).roll(self.select)

        pg.display.update()

    def mouse_click(self):
        i, _, k, _ = self.__mouse_guide()
        if i == -1:
            return
        if i != self.now & 1:
            return
        if (
            self.p2 if self.now & 1 else self.p1).check(
            k, self.d2 if self.now & 1 else self.d1
        ):
            self.now += 1
            if self.now == 24:
                self.status = 1
                self.now -= 1
                return
            (self.d1 if self.now & 1 else self.d2).next()
            (self.d2 if self.now & 1 else self.d1).roll()
            self.select.clear()
            self.dcount = 0

    def draw(self):
        back = "#0981cb"
        self.screen.fill(back)
        self.draw_paper()
        self.draw_pre_score()
        self.draw_dices()
        self.draw_select_dices()
        self.draw_mouse_guide()
        self.draw_explanation()
        if self.status == 1:
            self.draw_finish()
        # self.__select_dice(dsz, dsp, 4)
        # self.__draw_dice(1, 500, 100)

    def draw_paper(self):
        sp = self.init_space
        h = self.disp_h
        paper_w = self.paper_w
        paper_h = self.paper_h
        cell = self.cell
        good = (cell - self.font_size) / 2

        pg.draw.rect(self.screen, "#ffffff", (sp, sp, paper_w, paper_h))
        # vertical line
        for i in range(2):
            pg.draw.line(self.screen, "#000000", (sp + i * paper_w, sp),
                         (sp + i * paper_w, sp + paper_h))
        for i in range(2, 2 + 2):
            pg.draw.line(self.screen, "#000000", (sp + i * paper_w / 4, sp),
                         (sp + i * paper_w / 4, sp + 12 * cell))
            pg.draw.line(self.screen, "#000000",
                         (sp + i * paper_w / 4, sp + 12.5 * cell),
                         (sp + i * paper_w / 4, sp + paper_h))

        # horizontal line
        for i in range(2):
            pg.draw.line(self.screen, "#000000", (sp, sp + i * paper_h),
                         (sp + paper_w, sp + i * paper_h))
        for i in range(4, 9 + 4):
            pg.draw.line(self.screen, "#000000", (sp, sp + cell * i),
                         (sp + paper_w, sp + cell * i))
        for i in range(13, 7 + 13):
            pg.draw.line(self.screen, "#000000", (sp, sp + cell * (i - 0.5)),
                         (sp + paper_w, sp + cell * (i - 0.5)))
        pg.draw.line(self.screen, "#000000", (sp, sp + cell * 3),
                     (sp + paper_w / 2, sp + cell * 3))

        s = f"{self.now + 1} / 24"
        txt = self.font.render(s, True, "#000000")
        self.screen.blit(txt, (sp + good, sp + cell * 2 + good))

        s = "Category"
        txt = self.font.render(s, True, "#000000")
        self.screen.blit(txt, (sp + good, sp + cell * 3 + good))
        adj = 4
        for i, k in enumerate(TABLE.keys()):
            txt = self.font.render(k, True, "#000000")
            self.screen.blit(txt, (sp + good, sp + cell * (adj + i) + good))
            if k == "Sixes":
                adj += 2.5

        self.screen.blit(self.font.render("Subtotal", True, "#000000"),
                         (sp + good, sp + cell * 10 + good))
        self.screen.blit(self.font.render("Bonus", True, "#000000"),
                         (sp + good, sp + cell * 11 + good))
        self.screen.blit(self.font.render("Total", True, "#000000"),
                         (sp + good, h - sp - good - self.font_size))

        for i, p in enumerate((self.p1, self.p2)):
            adj = 4.5
            for ii, k in enumerate(p.table.values()):
                s = f"{k}" if k != -1 else ""
                txt = self.font.render(s, True, "#000000")
                self.screen.blit(txt, txt.get_rect(
                    center=(sp + paper_w / 4 * (i + 2.5),
                            sp + cell * (adj + ii))))
                if ii == 5:
                    adj += 2.5

            txt = self.font.render(f"{p.bonus_sum()}/63", True, "#000000")
            self.screen.blit(txt, txt.get_rect(
                center=(sp + paper_w / 4 * (i + 2.5), sp + cell * 10.5)))
            txt = self.font.render(("35" if p.bonus_sum() >= 63 else "0"),
                                   True, "#000000")
            self.screen.blit(txt, txt.get_rect(
                center=(sp + paper_w / 4 * (i + 2.5), sp + cell * 11.5)))
            txt = self.font.render((f"{p.score_sum()}"),
                                   True, "#000000")
            self.screen.blit(txt, txt.get_rect(
                centerx=sp + paper_w / 4 * (i + 2.5),
                top=h - sp - good - self.font_size))

    def draw_pre_score(self):
        sp = self.init_space
        paper_w = self.paper_w
        cell = self.cell

        i = self.now & 1
        p, d = (self.p2, self.d2) if i else (self.p1, self.d1)
        adj = 4.5
        for ii, k in enumerate(p.valid_table(d).values()):
            s = f"{k}" if k != -1 else ""
            txt = self.font.render(s, True, "#7f7f7f")
            self.screen.blit(txt, txt.get_rect(
                center=(sp + paper_w / 4 * (i + 2.5),
                        sp + cell * (adj + ii))))
            if ii == 5:
                adj += 2.5

    def __dice_cicrle(self, h, w, x, y):
        dsz = self.dsz
        csz = self.csz
        sp = 3

        pg.draw.circle(self.screen, "#000000",
                       (x + sp + (dsz - 2 * sp) / 6 * (2 * w + 1),
                        y + sp + (dsz - 2 * sp) / 6 * (2 * h + 1)), csz)

    def __draw_dice(self, n, x, y):
        dsz = self.dsz

        pg.draw.rect(self.screen, "#ffffff", (x, y, dsz, dsz))
        if n == 1:
            self.__dice_cicrle(1, 1, x, y)
        elif n == 2:
            self.__dice_cicrle(0, 0, x, y)
            self.__dice_cicrle(2, 2, x, y)
        elif n == 3:
            self.__dice_cicrle(0, 0, x, y)
            self.__dice_cicrle(1, 1, x, y)
            self.__dice_cicrle(2, 2, x, y)
        elif n == 4:
            self.__dice_cicrle(0, 0, x, y)
            self.__dice_cicrle(0, 2, x, y)
            self.__dice_cicrle(2, 0, x, y)
            self.__dice_cicrle(2, 2, x, y)
        elif n == 5:
            self.__dice_cicrle(0, 0, x, y)
            self.__dice_cicrle(0, 2, x, y)
            self.__dice_cicrle(1, 1, x, y)
            self.__dice_cicrle(2, 0, x, y)
            self.__dice_cicrle(2, 2, x, y)
        elif n == 6:
            self.__dice_cicrle(0, 0, x, y)
            self.__dice_cicrle(0, 2, x, y)
            self.__dice_cicrle(1, 0, x, y)
            self.__dice_cicrle(1, 2, x, y)
            self.__dice_cicrle(2, 0, x, y)
            self.__dice_cicrle(2, 2, x, y)

    def draw_dices(self):
        h = self.disp_h
        w = self.disp_w
        dsz = self.dsz
        dsp = self.dsp
        d = self.d2 if self.now & 1 else self.d1

        for i, n in enumerate(d.hands):
            self.__draw_dice(n, w / 2 + (dsp + dsz) * i, h / 4)
        s = f"あと{2 - self.dcount}回"
        txt = self.font.render(s, True, "#000000")
        self.screen.blit(txt, (w / 2 + (dsp + dsz) * 4, h / 4 - dsz))

    def __draw_select_dice(self, n):
        h = self.disp_h
        w = self.disp_w
        dsz = self.dsz
        dsp = self.dsp
        sp = 3

        pg.draw.rect(self.screen, "#f5f531",
                     (w / 2 - sp + (dsz + dsp) * n, h / 4 - sp,
                      dsz + 2 * sp, dsz + 2 * sp), 2)

    def draw_select_dices(self):
        for n in self.select:
            self.__draw_select_dice(n)

    def __mouse_guide(self):
        sp = self.init_space
        paper_w = self.paper_w
        cell = self.cell

        x, y = pg.mouse.get_pos()
        for i in range(2):
            adj = 4
            for ii, k in enumerate(TABLE.keys()):
                if (
                    sp + paper_w / 4 * (i + 2) <= x <=
                    sp + paper_w / 4 * (i + 3) and
                    sp + cell * (adj + ii) <= y <=
                    sp + cell * (adj + ii + 1)
                ):
                    return i, ii, k, adj
                if ii == 5:
                    adj += 2.5
        return -1, -1, -1, -1

    def draw_mouse_guide(self):
        sp = self.init_space
        paper_w = self.paper_w
        cell = self.cell

        i, ii, _, adj = self.__mouse_guide()
        if i == -1:
            return
        pg.draw.circle(self.screen, "#ff0000",
                       (sp + paper_w / 4 * (i + 3) - cell / 2,
                        sp + cell * (adj + 0.5 + ii)), cell / 4)

    def draw_finish(self):
        h = self.disp_h
        w = self.disp_w
        dsz = self.dsz
        dsp = self.dsp
        fisum = self.p1.score_sum()
        sesum = self.p2.score_sum()
        st = ["しゅうりょうーーー"]
        if fisum == sesum:
            st.append("引き分けじゃん！！すげー！！")
        elif fisum > sesum:
            st.append("先行の勝ち！！")
        elif fisum < sesum:
            st.append("後攻の勝ち！！")
        for i, s in enumerate(st):
            txt = pg.font.Font(
                "../Mplus1-Black.ttf", 20
            ).render(s, True, "#000000")
            self.screen.blit(txt, txt.get_rect(
                top=h / 3 + (5 + i) * 20,
                centerx=w / 2 + dsz * 2.5 + dsp * 2))

    def draw_explanation(self):
        w = self.disp_w
        h = self.disp_h
        dsz = self.dsz
        dsp = self.dsp
        st = ["Q: ゲームをやめる", "SPACE: サイコロを振る",
              "1,2,3,4,5: サイコロを選択", "CLICK: 役を選択"]
        for i, s in enumerate(st):
            txt = pg.font.Font(
                "../Mplus1-Black.ttf", 20
            ).render(s, True, "#000000")
            self.screen.blit(txt, txt.get_rect(
                top=h / 3 + (8 + i) * 20,
                centerx=w / 2 + dsz * 2.5 + dsp * 2))


if __name__ == "__main__":
    DISPLAY_W = 800
    DISPLAY_H = 600
    Game(DISPLAY_W, DISPLAY_H)
