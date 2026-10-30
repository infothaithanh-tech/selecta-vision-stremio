"""Dịch toàn bộ mốc thời gian của file .srt.

Dùng:  python shift_subs.py <thư_mục_srt> <giây>
  giây âm  = sub hiện SỚM hơn (vd -1.0)
  giây dương = sub hiện TRỄ hơn
Ghi đè tại chỗ, giữ nguyên BOM và kiểu xuống dòng.
"""
import re, sys, glob, os

TS = re.compile(r"(\d{2}):(\d{2}):(\d{2}),(\d{3}) --> (\d{2}):(\d{2}):(\d{2}),(\d{3})")

def to_ms(h, m, s, ms): return ((int(h) * 60 + int(m)) * 60 + int(s)) * 1000 + int(ms)

def fmt(ms):
    ms = max(0, ms)
    return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"

def shift_text(text, delta_ms):
    def sub(m):
        a = to_ms(*m.groups()[:4]) + delta_ms
        b = to_ms(*m.groups()[4:]) + delta_ms
        return f"{fmt(a)} --> {fmt(b)}"
    return TS.sub(sub, text)

if __name__ == "__main__":
    folder, secs = sys.argv[1], float(sys.argv[2])
    delta = round(secs * 1000)
    for p in sorted(glob.glob(os.path.join(folder, "*.srt"))):
        raw = open(p, "rb").read().decode("utf-8")  # giữ nguyên BOM (﻿) và \r\n
        out = shift_text(raw, delta)
        with open(p, "wb") as f: f.write(out.encode("utf-8"))
    print("done")
