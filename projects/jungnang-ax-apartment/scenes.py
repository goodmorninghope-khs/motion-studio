#!/usr/bin/env python3
"""중랑 AX 파트너즈 — 아파트 입주자 모집 (9:16 · 약 24초 · 나레이션 없음)

콘셉트: 분양 광고인 줄 알고 멈췄는데, 들어가 보면 사람과 전문성이 모여 사는 동네.
킥: 매치 컷 — 장면 2 회의 테이블의 미니어처 아파트로 빨려 들어가면 장면 3 동네 지도가 된다.

작업 폴더에서:  python3 scenes.py --sheet  ·  --check  →  python3 scenes.py --bake
"""
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

SC = [('Main.dc.html', 3.6), ('Scene02.dc.html', 3.6), ('Scene03.dc.html', 5.2),
      ('Scene04.dc.html', 4.2), ('Scene05.dc.html', 4.4), ('Scene06.dc.html', 3.0)]
DURS = [d for _, d in SC]
STARTS = [sum(DURS[:i]) for i in range(len(DURS))]
SCENES = [(s, s + d) for s, d in zip(STARTS, DURS)]
DUR = SCENES[-1][1]
B = [canvas.read_board(BOARD(n)) for n, _ in SC]
KIT = '팝'
K = kit.load(KIT)
CORAL, NAVY, BLUE = (242, 85, 63), (11, 47, 99), (31, 111, 178)


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


# ── 장면 1 · 훅: «아파트»에 붙어 있다 빠지며 공개 → 딱지 쾅 → 입주자 모집 ──
def s1(lt, root, els):
    mountain, leaf_l, leaf_r, top, apt, pill, recruit, bar = els
    img = static('s1-bg', root, [mountain])
    motion.put(img, leaf_l, off=motion.float_(lt, 8, 3.0), rot=motion.float_(lt, 1.5, 3.4)[1])
    motion.put(img, leaf_r, off=motion.float_(lt, 8, 3.0, 0.5), rot=-motion.float_(lt, 1.5, 3.6)[1])
    motion.put(img, apt)                                                   # 제목은 처음부터 — 움직이는 건 카메라
    appear.put(img, top, seg(lt, 0.85, 1.25), 'down', dist=40)
    k = seg(lt, 1.1, 1.38)                                                 # 딱지 — 크게 왔다 줄며 쾅
    if k > 0: motion.put(img, pill, s=1 + 1.3 * (1 - eo(k)), alpha=min(1, k * 3))
    appear.put(img, recruit, seg(lt, 1.45, 1.9), 'up', dist=120)
    appear.put(img, bar, seg(lt, 1.9, 2.3), 'wipe', dir='left')
    c = camera.keys(lt, [(0, camera.on(apt, img, fill=1.75, dy=0.02)),
                         (0.25, camera.on(apt, img, fill=1.6, dy=0.02)),
                         (1.05, camera.full(img), '부드럽게')])
    c = camera.drift(c, max(0, lt - 1.05), DURS[0] - 1.05)
    if 1.38 <= lt < 1.6:                                                   # 쾅 — 짧게 흔들림
        a = (1.6 - lt) / 0.22 * 14; c = camera.Cam(c.cx + a * ((-1) ** int(lt * 60)), c.cy + a * 0.6, c.z, c.rot)
    return camera.shoot(img, c, (W, H))


# ── 장면 2: 줄마다 튀어나옴 → 회의 그림이 올라옴 → 미니어처 아파트로 밀고 들어감 ──
MINI = (450, 1200, 480, 200)        # 회의 그림 속 미니어처 도시 (아트보드 좌표)


def s2(lt, root, els):
    axbg, leaf, l1, l2, river, meet, flower = els
    img = static('s2-bg', root, [river, flower])
    appear.put(img, axbg, seg(lt, 0.0, 0.6), 'fade')
    motion.put(img, leaf, off=motion.float_(lt, 8, 3.0))
    appear.put(img, l1, seg(lt, 0.15, 0.55), 'pop')
    appear.put(img, l2, seg(lt, 0.4, 0.8), 'pop')
    appear.put(img, meet, seg(lt, 0.8, 1.35), 'up', dist=320)
    c = camera.keys(lt, [(0, camera.full(img)), (1.7, camera.full(img)),
                         (3.6, camera.on(MINI, img, fill=0.95), '부드럽게')])
    return camera.shoot(img, c, (W, H))


# ── 장면 3: 동네 지도 — 길이 그려지고 카메라가 길을 따라 훑는다 → 핀 · 그림 차례로 → 한 마디 ──
def s3(lt, root, els):
    road, dash, shop, cap, office, p1, p2, p3, mountain, t1, t2, t3, bar = els
    img = static('s3-bg', root, [mountain])
    kr = seg(lt, 0.0, 3.4)
    motion.draw_on(img, road, kr); motion.draw_on(img, dash, seg(lt, 0.3, 3.6))
    for pic, pin, t0, how in ((shop, p1, 0.15, 'pop'), (cap, p2, 1.25, 'right'), (office, p3, 2.25, 'up')):
        if how == 'pop': appear.put(img, pic, seg(lt, t0, t0 + 0.45), 'pop')
        else: appear.put(img, pic, seg(lt, t0, t0 + 0.45), how, dist=200)
        appear.put(img, pin, seg(lt, t0 + 0.3, t0 + 0.6), 'down', dist=120, ease=lambda x: motion_bounce(x))
    appear.put(img, t1, seg(lt, 3.0, 3.4), 'up', dist=60)
    appear.put(img, t2, seg(lt, 3.25, 3.65), 'up', dist=60)
    appear.put(img, t3, seg(lt, 3.5, 3.85), 'pop')
    appear.put(img, bar, seg(lt, 3.9, 4.3), 'wipe', dir='left')
    end = camera.on((0, 1080, 1080, 1920), img, fill=1.0)
    c = camera.keys(lt, [(0, camera.at(560, 620, 1.22)), (1.15, camera.at(560, 760, 1.15)),
                         (2.2, camera.at(620, 1300, 1.12)), (3.1, camera.at(540, 1840, 1.06)),
                         (3.9, end, '부드럽게')])
    return camera.shoot(img, camera.drift(c, max(0, lt - 3.9), DURS[2] - 3.9), (W, H))


def motion_bounce(x):
    """핀이 떨어져 한 번 튀고 앉는다"""
    if x < 0.7: return (x / 0.7) ** 2 * 1.06
    u = (x - 0.7) / 0.3
    return 1.06 - 0.06 * (1 - (1 - u) ** 2) if u < 1 else 1.0


# ── 장면 4: 제목에서 칩으로 시선 옮기기 → 칩 차례로 → «전문성 연결» 두근 → 빠지며 전체 ──
def s4(lt, root, els):
    leaf, flower, leaf2, h1, h2, h3, c1, d1, c2, d2, c3 = els
    img = static('s4-bg', root, [leaf, flower, leaf2])
    motion.blur_in(img, h1, seg(lt, 0.0, 0.45))
    motion.blur_in(img, h2, seg(lt, 0.2, 0.65))
    motion.blur_in(img, h3, seg(lt, 0.4, 0.85))
    appear.put(img, c1, seg(lt, 1.15, 1.5), 'pop')
    appear.put(img, d1, seg(lt, 1.45, 1.6), 'fade')
    k2 = seg(lt, 1.55, 1.9)
    if k2 >= 1: motion.put(img, c2, s=motion.pulse(lt, 2.55, 0.12, 0.4))
    else: appear.put(img, c2, k2, 'pop')
    appear.put(img, d2, seg(lt, 1.85, 2.0), 'fade')
    appear.put(img, c3, seg(lt, 1.95, 2.3), 'pop')
    heads, chips = (0, 320, 1080, 520), (150, 900, 780, 560)
    c = camera.keys(lt, [(0, camera.on(heads, img, fill=0.9)), (0.95, camera.on(heads, img, fill=0.88)),
                         (1.45, camera.at(540, 1010, 1.12), '부드럽게'),
                         (2.9, camera.at(540, 1000, 1.1)), (3.7, camera.full(img), '부드럽게')])
    return camera.shoot(img, c, (W, H))


# ── 장면 5: 두 줄이 양쪽에서 미끄러져 들어옴 → 빠지며 강변 · 주최 공개 ──
def s5(lt, root, els):
    river, flower, leaf, l1, l2, sub, credit = els
    img = static('s5-bg', root, [river, flower])
    motion.put(img, leaf, off=motion.float_(lt, 8, 3.0))
    appear.put(img, l1, seg(lt, 0.1, 0.6), 'left', dist=360)
    appear.put(img, l2, seg(lt, 0.45, 0.95), 'right', dist=360)
    appear.put(img, sub, seg(lt, 1.35, 1.75), 'fade')
    appear.put(img, credit, seg(lt, 1.7, 2.1), 'up', dist=60)
    c = camera.keys(lt, [(0, camera.at(540, 900, 1.13, -4)),
                         (1.2, camera.at(540, 900, 1.12, -3)),
                         (2.8, camera.full(img), '부드럽게')])
    return camera.shoot(img, camera.drift(c, max(0, lt - 2.8), DURS[4] - 2.8), (W, H))


# ── 장면 6: 쾅 착지로 포스터 → 빛 한 줄 → 천천히 다가감 ──
def s6(lt, root, els):
    title, poster = els
    img = static('s6', root, els)
    sweep(img, (poster['x'], poster['y'], poster['w'], poster['h']), seg(lt, 0.7, 1.6))
    c = camera.keys(lt, [(0, camera.full(img)), (DURS[5], camera.on(poster, img, fill=1.0), '선형')])
    return camera.shoot(img, c, (W, H))


SCENE_FN = [s1, s2, s3, s4, s5, s6]
SIGNATURE = []
PLAN = [
    {'level': 3, 'camera': ['빠지며 공개', '천천히 흐르기'], 'enter': ['down', 'zoom', 'up'], 'emph': [], 'kick': None,
     'borrow': '딱지 «쾅»은 내려앉기(zoom) — 훅 = 봉우리'},
    {'level': 2, 'camera': ['밀고 들어가기'], 'enter': ['pop', 'up'], 'emph': [], 'kick': None,
     'borrow': '나가는 편집 zoom_cut — 미니어처 아파트 속으로 빨려 들어가는 매치 컷 킥'},
    {'level': 2, 'camera': ['훑기'], 'enter': ['draw_on', 'pop', 'right', 'up'], 'emph': ['underline'], 'kick': '매치 컷',
     'borrow': '길 그려지기(draw_on) — 포스터의 분홍 길 · 들어오는 편집 zoom_cut = 매치 컷 킥'},
    {'level': 1, 'camera': ['시선 옮기기', '빠지며 공개'], 'enter': ['blur_in', 'pop'], 'emph': ['pulse'], 'kick': None,
     'borrow': '제목은 흐림→또렷 — 앞뒤 장면과 등장 리듬을 바꾸려고'},
    {'level': 2, 'camera': ['기울기', '빠지며 공개', '천천히 흐르기'], 'enter': ['left', 'right', 'fade'], 'emph': [], 'kick': None,
     'borrow': '들어오는 편집 cover(up) — 캔버스 노트 «덮이며 바뀜»'},
    {'level': 3, 'camera': ['밀고 들어가기'], 'enter': [], 'emph': ['shine'], 'kick': None},
]
NAMES = ['훅', '연결', '동네지도', '세단계', '넓어진다', '포스터']
EDIT = K.cuts([p['level'] for p in PLAN[1:]], names=NAMES)
EDIT[1] = ('cube', 0.5, {'dir': 'left'})                 # 캔버스 노트: 정육면체가 돌듯
EDIT[2] = ('zoom_cut', 0.5, {'focus': (W / 2, H / 2)})   # 킥: 미니어처 아파트 속으로 → 동네 지도
EDIT[3] = ('push', 0.45, {'dir': 'left'})
EDIT[4] = ('cover', 0.45, {'dir': 'up'})                 # 캔버스 노트: 덮이며 바뀜
EDIT[5] = ('impact', 0.5, {})                            # 캔버스 노트: 쾅 착지


def render(k, t, xf=0.0):
    root, els = B[k]; lt = t - STARTS[k] + (xf / 2 if k > 0 else 0)
    return SCENE_FN[k](lt, root, els)


def frame(t):
    k = max(i for i, s in enumerate(STARTS) if s <= t + 1e-9)
    for j in (k, k + 1):
        if j in EDIT:
            name, xf, opt = EDIT[j]
            if abs(t - STARTS[j]) < xf / 2:
                a = render(j - 1, STARTS[j] - xf / 2, EDIT.get(j - 1, ('', 0))[1]); b_ = render(j, t, xf)
                return K.finish(K.edit(name, a, b_, (t - (STARTS[j] - xf / 2)) / xf, **opt), t)
    return K.finish(render(k, t, EDIT.get(k, ('', 0, {}))[1]), t)


def build_audio(path):
    """배경음 «경쾌 팝» + 효과음 묶음 «경쾌 팝» — 컷마다 휙 · 등장 톡 · 딱지 · 포스터 착지 쾅"""
    from core import sfx as SFX
    S = SFX.Kit(K.sounds); trk = audio.new_track(DUR)
    for j, (name, xf, _) in EDIT.items():
        if name == 'impact': S.put(trk, 'impact', STARTS[j], 0.75)
        elif name != 'cut': S.put(trk, 'cut', STARTS[j] - min(0.3, xf / 2), 0.45)
    S.put(trk, 'impact', 1.12, 0.6)                                       # 딱지 쾅
    S.put(trk, 'enter', 1.45, 0.35)
    for t0 in (0.15, 1.25, 2.25): S.put(trk, 'enter', STARTS[2] + t0 + 0.45, 0.35)   # 핀 톡
    for t0 in (1.15, 1.55, 1.95): S.put(trk, 'tick', STARTS[3] + t0, 0.4)            # 칩
    S.put(trk, 'emph', STARTS[3] + 2.55, 0.4)
    S.put(trk, 'emph', STARTS[5] + 0.7, 0.4)                                         # 빛
    S.put(trk, 'done', DUR - 1.2, 0.5)
    try:
        bg = audio.bgm([(0, 1.1, 'sting', {}), (1.1, STARTS[2], 'groove', {}), (STARTS[2], STARTS[4], 'main', {}),
                        (STARTS[4], STARTS[5], 'build', {}), (STARTS[5], DUR, 'outro', {'hit': STARTS[5]})], DUR, style=K.music)
    except SystemExit as e:
        print(e); bg = None
    return audio.mixdown(DUR, path, bg, trk, [])


if __name__ == '__main__':
    bake.cli(sys.modules[__name__], out=os.path.join(HERE, 'out', '중랑AX_아파트입주자모집.mp4'), audio=build_audio)
    if canvas.missing: print('⚠ 못 찾음:', ' · '.join(sorted(canvas.missing)))
