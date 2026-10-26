# -*- coding: utf-8 -*-
import re
with open(r"E:\502\maoxuan.txt", encoding="utf-8") as f:
    lines = f.read().splitlines()

Z = "〇○◯ＯOo0０零"
NUM = Z + "一二三四五六七八九"
bare_date_re = re.compile(rf"^[{NUM}]{{4}}年[{NUM}]{{1,2}}月[{NUM}]{{0,2}}日")
tests = ["一九七五年四月十七日于北京", "一九七五年四月三十日于北京", "一九四九年十月二十六日",
         "一九五九年九月九日", "一九六六年八月三十日维也纳", "一九四六年解放区工作的方针*"]
for t in tests:
    print(repr(t), "->", bool(bare_date_re.match(t)))
print("full repr of L31405:", repr(lines[31405]))
print("full repr of L31441:", repr(lines[31441]))
print("ord check:", [hex(ord(c)) for c in lines[31405][:6]])
# 愚公移山 full region
print("=== lines 9762-9794 full ===")
for i in range(9762, 9794):
    print(i, repr(lines[i]))
