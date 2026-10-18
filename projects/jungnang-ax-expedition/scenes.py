#!/usr/bin/env python3
"""중랑 AX 원정대 — 현장학습 프로젝트 (9:16 · 약 27초 · 나레이션 없음)

콘셉트: 질문을 들고 떠나는 원정 — 큰 «?»로 출발해 걷는 원정대를 따라 분홍 길 위 현장 세 곳을 지나 «바꾸다»에 닿는다.
킥: 휩 팬 — 원정대가 가리키는 오른쪽으로 화면이 휙 넘어가 동네 길로 이어진다.
같은 시리즈: 아파트 입주자 모집 영상과 같은 톤 · 글꼴 · 키트(팝) · 소리 묶음.

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

SC = [('Main.dc.html', 3.4), ('Scene02.dc.html', 3.8), ('Scene03.dc.html', 3.6), ('Scene04.dc.html', 5.2),
      ('Scene05.dc.html', 4.0), ('Scene06.dc.html', 4.2), ('Scene07.dc.html', 3.0)]
DURS = [d for _, d in SC]
STARTS = [sum(DURS[:i]) for i in range(len(DURS))]
SCENES = [(s, s + d) for s, d in zip(STARTS, DURS)]
DUR = SCENES[-1][1]
B = [canvas.read_board(BOARD(n)) for n, _ in SC]
KIT = '팝'
K = kit.load(KIT)


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


# ── 장면 1 · 훅: «중랑»에 붙어 있다 빠지며 공개 → 가운데 «AX» 쾅 → 원정대 ──
def s1(lt, root, els):
    mountain, leaf_l, leaf_r, top, jr, ax, team, bar = els
    img = static('s1-bg', root, [mountain])
    motion.put(img, leaf_l, off=motion.float_(lt, 8, 3.0), rot=motion.float_(lt, 1.5, 3.4)[1])
    motion.put(img, leaf_r, off=motion.float_(lt, 8, 3.0, 0.5), rot=-motion.float_(lt, 1.5, 3.6)[1])
    motion.put(img, jr)
    appear.put(img, top, seg(lt, 0.85, 1.2), 'down', dist=40)
    k = seg(lt, 1.05, 1.33)
    if k > 0: motion.put(img, ax, s=1 + 1.4 * (1 - eo(k)), alpha=min(1, k * 3))
    appear.put(img, team, seg(lt, 1.4, 1.85), 'up', dist=120)
    appear.put(img, bar, seg(lt, 1.85, 2.25), 'wipe', dir='left')
    c = camera.keys(lt, [(0, camera.on(jr, img, fill=1.6)), (0.25, camera.on(jr, img, fill=1.48)),
                         (1.0, camera.full(img), '부드럽게')])
    c = camera.drift(c, max(0, lt - 1.0), DURS[0] - 1.0)
    if 1.33 <= lt < 1.55:
        a = (1.55 - lt) / 0.22 * 14; c = camera.Cam(c.cx + a * ((-1) ** int(lt * 60)), c.cy + a * 0.6, c.z, c.rot)
    return camera.shoot(img, c, (W, H))


# ── 장면 2: 질문이 한 자씩 → 큰 «?»가 튀어나와 흔들흔들 · 카메라는 질문 쪽으로 다가감 ──
def s2(lt, root, els):
    leaf, flower, q, h1, l1, l2 = els
    img = static('s2-bg', root, [flower])
    motion.put(img, leaf, off=motion.float_(lt, 8, 3.0))
    appear.type_text(img, h1, seg(lt, 0.15, 1.0))
    appear.put(img, l1, seg(lt, 1.0, 1.4), 'up', dist=60)
    appear.put(img, l2, seg(lt, 1.25, 1.65), 'up', dist=60)
    kq = seg(lt, 1.7, 2.1)
    if kq >= 1: motion.put(img, q, rot=5 * math.sin((lt - 2.1) * 4.5) * math.exp(-(lt - 2.1) * 0.8))
    else: appear.put(img, q, kq, 'pop')
    c = camera.keys(lt, [(0, camera.full(img)), (2.3, camera.full(img)), (DURS[1], camera.at(660, 1150, 1.3), '부드럽게')])   # 다 읽힌 뒤 «?»로 다가간다
    return camera.shoot(img, c, (W, H))


# ── 장면 3: 원정대가 올라오고 · 카메라가 걷는 사람들을 따라 오른쪽으로 → 휙(다음 장면) ──
def s3(lt, root, els):
    leaf, h1, h2, walk, flower = els
    img = static('s3-bg', root, [])
    motion.put(img, leaf, off=motion.float_(lt, 8, 3.0))
    appear.put(img, walk, seg(lt, 0.05, 0.55), 'left', dist=300)   # 걷는 방향 그대로 왼쪽에서
    appear.put(img, h1, seg(lt, 0.4, 0.8), 'down', dist=80)
    appear.put(img, h2, seg(lt, 0.65, 1.05), 'down', dist=80)
    motion.put(img, flower, off=motion.float_(lt, 6, 3.2, 1.0))
    c = camera.keys(lt, [(0, camera.full(img)), (1.4, camera.full(img)),
                         (DURS[2], camera.at(660, 1200, 1.3), '부드럽게')])   # 가리키는 오른쪽으로 — 휩 팬으로 이어진다
    return camera.shoot(img, c, (W, H))


# ── 장면 4: 동네 길 — 길이 그려지고 카메라가 길을 따라 훑는다 → 핀 · 현장 셋 → 바꾸다 ──
def s4(lt, root, els):
    road, dash, office, elder, workshop, p1, p2, p3, mountain, t1, t2, bar = els
    img = static('s4-bg', root, [mountain])
    motion.draw_on(img, road, seg(lt, 0.0, 3.4)); motion.draw_on(img, dash, seg(lt, 0.3, 3.6))
    for pic, pin, t0, how in ((office, p1, 0.15, 'pop'), (elder, p2, 1.25, 'left'), (workshop, p3, 2.25, 'up')):
        if how == 'pop': appear.put(img, pic, seg(lt, t0, t0 + 0.45), 'pop')
        else: appear.put(img, pic, seg(lt, t0, t0 + 0.45), how, dist=200)
        appear.put(img, pin, seg(lt, t0 + 0.3, t0 + 0.6), 'down', dist=120, ease=bounce)
    appear.put(img, t1, seg(lt, 3.0, 3.4), 'up', dist=60)
    appear.put(img, t2, seg(lt, 3.3, 3.7), 'pop')
    appear.put(img, bar, seg(lt, 3.85, 4.25), 'wipe', dir='left')
    end = camera.on((0, 1080, 1080, 1920), img, fill=1.0)
    c = camera.keys(lt, [(0, camera.at(640, 560, 1.2)), (1.15, camera.at(640, 640, 1.15)),
                         (2.2, camera.at(520, 1150, 1.12)), (3.1, camera.at(540, 1720, 1.07)),
                         (3.9, end, '부드럽게')])
    return camera.shoot(img, camera.drift(c, max(0, lt - 3.9), DURS[3] - 3.9), (W, H))


# ── 장면 5: 칩마다 끊어 다가가기 · 칩은 양옆에서 미끄러져 → 빠지며 셋을 함께 · «작은 실험» 반짝 ──
def s5(lt, root, els):
    leaf, flower, leaf2, top, c1, d1, c2, d2, c3 = els
    img = static('s5-bg', root, [leaf, flower, leaf2])
    appear.put(img, top, seg(lt, 0.0, 0.3), 'fade')
    appear.put(img, c1, seg(lt, 0.25, 0.6), 'left', dist=300)
    appear.put(img, d1, seg(lt, 0.75, 0.9), 'fade')
    appear.put(img, c2, seg(lt, 0.85, 1.2), 'right', dist=300)
    appear.put(img, d2, seg(lt, 1.35, 1.5), 'fade')
    appear.put(img, c3, seg(lt, 1.45, 1.8), 'left', dist=300)
    if lt > 2.6: sweep(img, box_of(c3), seg(lt, 2.7, 3.4), width=140, a=150)
    on = lambda e: camera.on(e, img, fill=0.92)
    c = camera.keys(lt, [(0, camera.full(img)), (0.25, camera.full(img)), (0.25, on(c1)),
                         (0.85, on(c1)), (0.85, on(c2)), (1.45, on(c2)), (1.45, on(c3)),
                         (2.2, on(c3)), (2.9, camera.full(img), '부드럽게')])
    return camera.shoot(img, c, (W, H))


# ── 장면 6: 흐림→또렷 · 내려앉기 → 기운 화면이 바로 서며 빠져 강변 · 주최 ──
def s6(lt, root, els):
    river, flower, leaf, l1, l2, sub, credit = els
    img = static('s6-bg', root, [river, flower])
    motion.put(img, leaf, off=motion.float_(lt, 8, 3.0))
    motion.blur_in(img, l1, seg(lt, 0.1, 0.6))
    appear.put(img, l2, seg(lt, 0.55, 0.95), 'right', dist=300)
    appear.put(img, sub, seg(lt, 1.4, 1.8), 'fade')
    appear.put(img, credit, seg(lt, 1.75, 2.15), 'fade')
    c = camera.keys(lt, [(0, camera.full(img)), (2.3, camera.full(img)),
                         (DURS[5], camera.at(540, 1180, 1.3), '부드럽게')])   # 강변 풍경으로 밀고 들어간다
    return camera.shoot(img, c, (W, H))


# ── 장면 7: 쾅 착지로 포스터 → 빛 한 줄 → 천천히 다가감 ──
def s7(lt, root, els):
    title, poster = els
    img = static('s7', root, els)
    sweep(img, box_of(poster), seg(lt, 0.7, 1.6))
    c = camera.keys(lt, [(0, camera.full(img)), (DURS[6], camera.on(poster, img, fill=1.0), '선형')])
    return camera.shoot(img, c, (W, H))


SCENE_FN = [s1, s2, s3, s4, s5, s6, s7]
PLAN = [
    {'level': 3, 'camera': ['빠지며 공개', '천천히 흐르기'], 'enter': ['down', 'zoom', 'up'], 'emph': [], 'kick': None,
     'borrow': '«AX» 쾅은 내려앉기(zoom) — 훅 = 봉우리 · 아파트 편과 같은 문법'},
    {'level': 2, 'camera': ['시선 옮기기', '밀고 들어가기'], 'enter': ['type_text', 'up', 'pop'], 'emph': [], 'kick': None,
     'borrow': '질문은 한 자씩(type_text) — 묻는 말투'},
    {'level': 1, 'camera': ['밀고 들어가기', '훑기'], 'enter': ['left', 'down'], 'emph': [], 'kick': None,
     'borrow': '나가는 편집 whip — 가리키는 쪽으로 휙 넘어가는 킥'},
    {'level': 2, 'camera': ['훑기'], 'enter': ['draw_on', 'pop', 'left', 'up'], 'emph': ['underline'], 'kick': '휩 팬',
     'borrow': '길 그려지기(draw_on) — 포스터의 분홍 길'},
    {'level': 1, 'camera': ['끊어 다가가기', '빠지며 공개'], 'enter': ['left', 'right', 'fade'], 'emph': ['shine'], 'kick': None},
    {'level': 2, 'camera': ['밀고 들어가기'], 'enter': ['blur_in', 'right', 'fade'], 'emph': [], 'kick': None,
     'borrow': '흐림→또렷 — 마무리 한 마디'},
    {'level': 3, 'camera': ['밀고 들어가기'], 'enter': [], 'emph': ['shine'], 'kick': None},
]
NAMES = ['훅', '질문', '원정대', '동네길', '세걸음', '변화로', '포스터']
EDIT = K.cuts([p['level'] for p in PLAN[1:]], names=NAMES)
EDIT[1] = ('push', 0.45, {'dir': 'left'})       # 캔버스 노트: 밀어내듯
EDIT[2] = ('stretch', 0.45, {'dir': 'left'})
EDIT[3] = ('whip', 0.5, {})                      # 킥: 가리키는 쪽으로 휙
EDIT[4] = ('tiles', 0.5, {})                     # 캔버스 노트: 타일이 뒤집히듯
EDIT[5] = ('cover', 0.45, {'dir': 'up'})         # 캔버스 노트: 덮이며
EDIT[6] = ('impact', 0.5, {})                    # 캔버스 노트: 쾅 착지


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
    """배경음 «경쾌 팝» + 효과음 묶음 «경쾌 팝» — 아파트 편과 같은 소리 결"""
    from core import sfx as SFX
    S = SFX.Kit(K.sounds); trk = audio.new_track(DUR)
    for j, (name, xf, _) in EDIT.items():
        if name == 'impact': S.put(trk, 'impact', STARTS[j], 0.75)
        elif name != 'cut': S.put(trk, 'cut', STARTS[j] - min(0.3, xf / 2), 0.5 if name == 'whip' else 0.42)
    S.put(trk, 'impact', 1.07, 0.6)                                         # AX 쾅
    S.put(trk, 'enter', 1.4, 0.35)
    for i in range(6): S.put(trk, 'tick', STARTS[1] + 0.15 + i * 0.14, 0.18)  # 한 자씩
    S.put(trk, 'emph', STARTS[1] + 1.7, 0.45)                                 # ? 튀어나옴
    for t0 in (0.15, 1.25, 2.25): S.put(trk, 'enter', STARTS[3] + t0 + 0.45, 0.35)
    for t0 in (0.25, 0.85, 1.45): S.put(trk, 'tick', STARTS[4] + t0, 0.4)
    S.put(trk, 'emph', STARTS[4] + 2.7, 0.4)
    S.put(trk, 'emph', STARTS[6] + 0.7, 0.4)
    S.put(trk, 'done', DUR - 1.2, 0.5)
    try:
        bg = audio.bgm([(0, 1.0, 'sting', {}), (1.0, STARTS[3], 'groove', {}), (STARTS[3], STARTS[5], 'main', {}),
                        (STARTS[5], STARTS[6], 'build', {}), (STARTS[6], DUR, 'outro', {'hit': STARTS[6]})], DUR, style=K.music)
    except SystemExit as e:
        print(e); bg = None
    return audio.mixdown(DUR, path, bg, trk, [])


if __name__ == '__main__':
    bake.cli(sys.modules[__name__], out=os.path.join(HERE, 'out', '중랑AX원정대_현장학습.mp4'), audio=build_audio)
    if canvas.missing: print('⚠ 못 찾음:', ' · '.join(sorted(canvas.missing)))
