#!/usr/bin/env python3
"""중랑 AX2030 — 3가지 방법 통합본의 표지 장면들 (여는 장면 · 장 표지 3 · 맺음)

이 파일은 표지 장면만 굽는다 → join.py 가 잘라 세 영상 사이에 끼워 통합본을 만든다.
킥: 맺음 — 포스터 세 장이 화면 밖에서 돌며 날아와 한자리에 모인다.

작업 폴더에서:  python3 scenes.py --sheet  ·  --check  →  python3 scenes.py --bake
"""
import math
import os
import sys

SKILL = os.environ.get('MOTION_SKILL') or os.path.expanduser('~/.claude/skills/motion-studio')
sys.path.insert(0, os.path.join(SKILL, 'scripts'))

from PIL import Image, ImageDraw, ImageFilter                       # noqa: E402
from core import appear, audio, bake, camera, canvas, kit, motion    # noqa: E402
from core.ease import seg, eo, eio                                   # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__)); os.chdir(HERE)
BOARD = lambda n: os.path.join(HERE, 'canvas', '확정', n)
W, H, FPS = 1080, 1920, 30

SC = [('Main.dc.html', 3.4), ('Ch1.dc.html', 2.4), ('Ch2.dc.html', 2.4), ('Ch3.dc.html', 2.4), ('Outro.dc.html', 5.0)]
DURS = [d for _, d in SC]
STARTS = [sum(DURS[:i]) for i in range(len(DURS))]
SCENES = [(s, s + d) for s, d in zip(STARTS, DURS)]
DUR = SCENES[-1][1]
B = [canvas.read_board(BOARD(n)) for n, _ in SC]
KIT = '팝'
K = kit.load(KIT)


_shoot = camera.shoot


def _inside(img, c, out=None, **kw):
    """카메라가 아트보드 밖을 보지 않게 (가장자리 색이 띠로 비치지 않게) — 기울기 없는 카메라만"""
    w, h = img.size; hw, hh = W / (2 * c.z), H / (2 * c.z)
    if not c.rot and hw <= w / 2 and hh <= h / 2:
        c = camera.Cam(min(max(c.cx, hw), w - hw), min(max(c.cy, hh), h - hh), c.z, c.rot)
    return _shoot(img, c, out, **kw)


camera.shoot = _inside


def static(key, root, els):
    """다 나온 뒤 안 바뀌는 바탕 층은 한 번만 그린다 (굽기 속도)"""
    def mk():
        img = canvas.background(root)
        for e in els: appear.put(img, e, 1, 'none')
        return img
    return bake.memo(key, mk).copy()


def sweep(img, box, k, width=160, a=120):
    """빛 한 줄이 대각선으로 쓸고 지나간다 (상자 안만)"""
    if not 0 < k < 1: return img
    bx, by, bw, bh = [int(v) for v in box]
    m = Image.new('L', (bw, bh), 0); d = ImageDraw.Draw(m)
    x = -bh * 0.6 + (bw + bh * 1.2) * eio(k)
    d.polygon([(x, 0), (x + width, 0), (x + width - bh * 0.6, bh), (x - bh * 0.6, bh)], fill=a)
    m = m.filter(ImageFilter.GaussianBlur(24))
    reg = img.crop((bx, by, bx + bw, by + bh)); reg.paste((255, 252, 236), (0, 0), m); img.paste(reg, (bx, by))
    return img


def bounce(x):
    """핀이 떨어져 한 번 튀고 앉는다"""
    if x < 0.7: return (x / 0.7) ** 2 * 1.06
    u = (x - 0.7) / 0.3
    return 1.06 - 0.06 * (1 - (1 - u) ** 2) if u < 1 else 1.0


def box_of(e): return (e['x'], e['y'], e['w'], e['h'])


# ── 여는 장면: «중랑» → AX 쾅 · 2030 → 포스터 세 장이 차례로 톡톡 ──
def s_intro(lt, root, els):
    mountain, leaf_l, leaf_r, top, jr, ax, y2030, pa, pb, pc = els
    img = static('intro-bg', root, [mountain])
    motion.put(img, leaf_l, off=motion.float_(lt, 8, 3.0), rot=motion.float_(lt, 1.5, 3.4)[1])
    motion.put(img, leaf_r, off=motion.float_(lt, 8, 3.0, 0.5), rot=-motion.float_(lt, 1.5, 3.6)[1])
    appear.put(img, top, seg(lt, 0.0, 0.35), 'down', dist=40)
    appear.put(img, jr, seg(lt, 0.2, 0.55), 'pop')
    k = seg(lt, 0.6, 0.88)
    if k > 0: motion.put(img, ax, s=1 + 1.4 * (1 - eo(k)), alpha=min(1, k * 3))
    appear.put(img, y2030, seg(lt, 0.85, 1.2), 'right', dist=360)
    for i, p in enumerate((pa, pb, pc)): appear.put(img, p, seg(lt, 1.35 + i * 0.22, 1.75 + i * 0.22), 'up', dist=420)
    c = camera.keys(lt, [(0, camera.at(540, 800, 1.2)), (0.7, camera.at(540, 810, 1.18)), (1.5, camera.full(img), '부드럽게')])
    c = camera.drift(c, max(0, lt - 1.5), DURS[0] - 1.5)
    if 0.88 <= lt < 1.1:
        a = (1.1 - lt) / 0.22 * 12; c = camera.Cam(c.cx + a * ((-1) ** int(lt * 60)), c.cy + a * 0.6, c.z, c.rot)
    return camera.shoot(img, c, (W, H))


# ── 장 표지: 숫자 쾅 → 이름 · 한 줄 → 포스터 올라옴 → 포스터 쪽으로 다가감 ──
def s_chapter(lt, root, els, n):
    leaf, flower, label, num, name, sub, poster = els
    img = static(f'ch{n}-bg', root, [flower])
    motion.put(img, leaf, off=motion.float_(lt, 8, 3.0))
    appear.put(img, label, seg(lt, 0.0, 0.25), 'fade')
    k = seg(lt, 0.05, 0.33)
    if k > 0: motion.put(img, num, s=1 + 1.5 * (1 - eo(k)), alpha=min(1, k * 3))
    appear.put(img, name, seg(lt, 0.4, 0.75), 'up', dist=80)
    appear.put(img, sub, seg(lt, 0.6, 0.95), 'fade')
    appear.put(img, poster, seg(lt, 0.7, 1.15), 'up', dist=400)
    c = camera.keys(lt, [(0, camera.full(img)), (1.2, camera.full(img)), (DURS[1], camera.at(540, 1180, 1.3), '부드럽게')])
    if 0.33 <= lt < 0.52:
        a = (0.52 - lt) / 0.19 * 10; c = camera.Cam(c.cx + a * ((-1) ** int(lt * 60)), c.cy + a * 0.6, c.z, c.rot)
    return camera.shoot(img, c, (W, H))


# ── 맺음 (킥): 포스터 세 장이 화면 밖에서 돌며 날아와 모임 → 3가지 방법론 → 빛 한 줄 ──
def s_outro(lt, root, els):
    t1, t2, pa, pb, pc, labels, credit = els
    img = canvas.background(root)
    for p, t0, (dx, dy), spin in ((pa, 0.1, (-900, 500), -40), (pb, 0.3, (900, 500), 40), (pc, 0.55, (0, 1300), 0)):
        k = seg(lt, t0, t0 + 0.7)
        if k <= 0: continue
        u = eo(k); motion.put(img, p, off=(dx * (1 - u), dy * (1 - u)), rot=spin * (1 - u), alpha=min(1, k * 2.5))
    appear.put(img, t1, seg(lt, 1.2, 1.5), 'fade')
    appear.put(img, t2, seg(lt, 1.35, 1.75), 'pop')
    appear.put(img, labels, seg(lt, 1.9, 2.3), 'fade')
    appear.put(img, credit, seg(lt, 2.2, 2.6), 'fade')
    sweep(img, box_of(pc), seg(lt, 2.6, 3.4))
    c = camera.keys(lt, [(0, camera.full(img)), (1.3, camera.full(img)), (DURS[4], camera.at(540, 960, 1.12), '선형')])
    return camera.shoot(img, c, (W, H))


SCENE_FN = [s_intro, lambda lt, r, e: s_chapter(lt, r, e, 1), lambda lt, r, e: s_chapter(lt, r, e, 2),
            lambda lt, r, e: s_chapter(lt, r, e, 3), s_outro]
PLAN = [
    {'level': 3, 'camera': ['밀고 들어가기'], 'enter': ['down', 'pop', 'zoom', 'right', 'up'], 'emph': [], 'kick': None,
     'borrow': '«AX» 쾅 — 세 편과 같은 문법'},
    {'level': 2, 'camera': ['밀고 들어가기'], 'enter': ['fade', 'zoom', 'up'], 'emph': [], 'kick': None, 'borrow': '숫자 쾅 — 장 표지'},
    {'level': 2, 'camera': ['밀고 들어가기'], 'enter': ['fade', 'zoom', 'up'], 'emph': [], 'kick': None, 'borrow': '숫자 쾅 — 장 표지'},
    {'level': 2, 'camera': ['밀고 들어가기'], 'enter': ['fade', 'zoom', 'up'], 'emph': [], 'kick': None, 'borrow': '숫자 쾅 — 장 표지'},
    {'level': 3, 'camera': ['밀고 들어가기'], 'enter': ['spin_in', 'fade', 'pop'], 'emph': ['shine'], 'kick': '포스터 모으기'},
]
NAMES = ['여는장면', '표지1', '표지2', '표지3', '맺음']
EDIT = {}                    # 표지 사이에는 세 영상이 들어간다 — 이 파일 안에서는 편집 없이 잘라 쓴다


def render(k, t, xf=0.0):
    root, els = B[k]; lt = t - STARTS[k]
    return SCENE_FN[k](lt, root, els)


def frame(t):
    k = max(i for i, s in enumerate(STARTS) if s <= t + 1e-9)
    return K.finish(render(k, t), t)


def build_audio(path):
    """표지마다 효과음 — 배경음은 표지마다 짧게 (영상들은 각자 배경음이 있다)"""
    from core import sfx as SFX
    S = SFX.Kit(K.sounds); trk = audio.new_track(DUR)
    S.put(trk, 'impact', 0.6, 0.6); S.put(trk, 'cut', 0.8, 0.35)
    for i in range(3): S.put(trk, 'enter', 1.35 + i * 0.22, 0.3)
    for j in (1, 2, 3):
        S.put(trk, 'cut', STARTS[j] + 0.0, 0.4); S.put(trk, 'impact', STARTS[j] + 0.05, 0.55); S.put(trk, 'enter', STARTS[j] + 0.7, 0.3)
    for t0 in (0.1, 0.3, 0.55): S.put(trk, 'cut', STARTS[4] + t0, 0.35)
    S.put(trk, 'impact', STARTS[4] + 0.95, 0.6); S.put(trk, 'emph', STARTS[4] + 2.6, 0.4); S.put(trk, 'done', DUR - 1.4, 0.55)
    try:
        bg = audio.bgm([(0, STARTS[1], 'sting', {}), (STARTS[1], STARTS[4], 'groove', {}),
                        (STARTS[4], DUR, 'outro', {'hit': STARTS[4] + 0.95})], DUR, style=K.music)
    except SystemExit as e:
        print(e); bg = None
    return audio.mixdown(DUR, path, bg, trk, [])


if __name__ == '__main__':
    bake.cli(sys.modules[__name__], out=os.path.join(HERE, 'out', '표지들.mp4'), audio=build_audio)
    if canvas.missing: print('⚠ 못 찾음:', ' · '.join(sorted(canvas.missing)))
