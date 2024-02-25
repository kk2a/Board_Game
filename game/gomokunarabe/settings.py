import settings as st 

title = "Gomokunarabe Settings"
win_w = 300
win_h = 100
disp_w = 1000
disp_h = 600
args = ((0, "display width", disp_w, 100, 9999),
        (0, "display height", disp_h, 100, 9999))


def GameSettings(x: int, y: int):
    return st.settings(title, x, y, win_w, win_h, args)
