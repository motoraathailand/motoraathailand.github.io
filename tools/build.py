#!/usr/bin/env python3
"""Builds index.html, assets/strings.js, assets/fonts.css and font subsets for the MOTOR AA hub."""
import json, os, html, subprocess, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EMAIL = "motoraathailand@gmail.com"
LANGS = [("th", "ไทย"), ("en", "English"), ("ko", "한국어"), ("zh", "中文"), ("hi", "हिन्दी")]

# live = linked intro page (verified HTTP 200 before publishing). soon = no link.
APPS = [
 dict(id="aaai", name="AAAi", icon="icons/aaai.svg", url="https://aaai-iji8.onrender.com/about", live=True,
      c="#5b4ee8", ink="#5b4ee8", soft="#f1effe", d="#8f86ff", dsoft="#25224a"),
 dict(id="nammanthuk", name="น้ำมันถูก", icon="icons/nammanthuk.svg", url="https://motoraathailand.github.io/nammanthuk-site/", live=True,
      c="#0c635c", ink="#0c635c", soft="#e6f4f2", d="#2dd4bf", dsoft="#123532"),
 dict(id="aacalc", name="AA Calc", icon="icons/aacalc.svg", url="https://motoraathailand.github.io/aacalc-site/", live=True,
      c="#1ea869", ink="#0f7a4b", soft="#e3f6ec", d="#3ddc97", dsoft="#14301f"),
 dict(id="moffee", name="Moffee", icon="icons/moffee.svg", url="https://motoraathailand.github.io/moffee-site/", live=True,
      c="#2563eb", ink="#1d4ed8", soft="#e8effd", d="#6ea0ff", dsoft="#172444"),
 dict(id="suayshot", name="SuayShot", icon="icons/suayshot.png", url=None, live=False,
      c="#f59e0b", ink="#b45309", soft="#fff4de", d="#ffbf47", dsoft="#3a2b10"),
 dict(id="scanner", name="AA Scanner Lite", icon="icons/scanner.png", url=None, live=False,
      c="#2160d9", ink="#2160d9", soft="#e8f0fd", d="#7fa8ff", dsoft="#16233f"),
]

S = {  # th, en, ko, zh, hi
 "doc_title": ["MOTOR AA — แอปทั้งหมดของเรา", "MOTOR AA — All our apps", "MOTOR AA — 모든 앱", "MOTOR AA — 我们的全部应用", "MOTOR AA — हमारे सभी ऐप"],
 "kicker": ["MOTOR AA", "MOTOR AA", "MOTOR AA", "MOTOR AA", "MOTOR AA"],
 "h1": ["แอปทั้งหมดของเรา|อยู่ที่เดียว", "All our apps,|in one place", "내 모든 앱을|한곳에서", "我们的全部应用，|一站直达", "हमारे सभी ऐप,|एक ही जगह"],
 "sub": ["เลือกแอปที่สนใจ|แล้วไปที่หน้าแนะนำ|ของแอปนั้นได้เลย", "Pick an app to open its own introduction page.", "앱을 고르면 해당 앱의 소개 페이지로 이동해요.", "选择一个应用，|即可打开它的介绍页面。", "कोई ऐप चुनें और उसका परिचय पेज खोलें।"],
 "chips_free": ["ใช้ฟรี", "Free", "무료", "免费", "मुफ़्त"],
 "chips_noads": ["ไม่มีโฆษณา", "No ads", "광고 없음", "无广告", "कोई विज्ञापन नहीं"],
 "chips_notrack": ["ไม่มีตัวติดตาม", "No trackers", "추적 없음", "无追踪", "कोई ट्रैकर नहीं"],
 "apps_h": ["แอปของเรา", "Our apps", "앱 목록", "我们的应用", "हमारे ऐप"],
 "open": ["ไปที่หน้าแนะนำ", "Open intro page", "소개 페이지 열기", "打开介绍页", "परिचय पेज खोलें"],
 "soon_h": ["เร็ว ๆ นี้", "Coming soon", "곧 만나요", "即将推出", "जल्द आ रहा है"],
 "soon_sub": ["แอปเหล่านี้กำลังเตรียม|หน้าแนะนำ ยังไม่เปิดให้เข้า", "These apps are getting their intro pages ready.", "이 앱들은 소개 페이지를 준비하고 있어요.", "这些应用的介绍页|正在准备中。", "इन ऐप के परिचय पेज तैयार हो रहे हैं।"],
 "soon_badge": ["เร็ว ๆ นี้", "Coming soon", "곧 공개", "即将推出", "जल्द ही"],
 "contact_h": ["ติดต่อเรา", "Contact", "문의", "联系我们", "संपर्क"],
 "contact_p": ["ข้อเสนอแนะหรือคำถามเกี่ยวกับแอป|ส่งอีเมลหาเราได้เลย", "Feedback or questions about any app? Email us.", "앱에 대한 의견이나 질문은 메일로 보내 주세요.", "对任何应用有意见或疑问，|欢迎发邮件给我们。", "किसी भी ऐप पर सुझाव या सवाल? हमें ईमेल करें।"],
 "email_btn": ["ส่งอีเมล", "Send email", "메일 보내기", "发送邮件", "ईमेल भेजें"],
 "lang": ["ภาษา", "Language", "언어", "语言", "भाषा"],
 "footer": ["ไม่มีโฆษณา ไม่มีตัวติดตาม|หน้าเว็บนี้เป็นไฟล์คงที่", "No ads, no trackers. This page is fully static.", "광고 없음, 추적 없음. 이 페이지는 정적 파일이에요.", "无广告、无追踪。|本页为纯静态页面。", "कोई विज्ञापन नहीं, कोई ट्रैकर नहीं। यह पेज पूरी तरह स्थिर है।"],
 "home": ["MOTOR AA หน้าแรก", "MOTOR AA home", "MOTOR AA 홈", "MOTOR AA 首页", "MOTOR AA होम"],
 # categories
 "cat_aaai": ["ผู้ช่วย AI", "AI assistants", "AI 비서", "AI 助手", "AI सहायक"],
 "cat_nammanthuk": ["ราคาน้ำมัน", "Fuel prices", "주유소 가격", "油价", "ईंधन के दाम"],
 "cat_aacalc": ["เครื่องคิดเลข", "Calculator", "계산기", "计算器", "कैलकुलेटर"],
 "cat_moffee": ["POS รับออเดอร์", "POS & orders", "POS·주문", "POS 点单", "POS ऑर्डर"],
 "cat_suayshot": ["แต่งภาพ", "Photo editing", "사진 보정", "照片编辑", "फ़ोटो एडिट"],
 "cat_scanner": ["สแกนรถ OBD-II", "Car OBD-II", "차량 OBD-II", "汽车 OBD-II", "कार OBD-II"],
 # one-liners
 "d_aaai": ["สร้างผู้ช่วย AI ได้หลายตัว|คุยทีละตัว หรือรวมทีมในห้องกลุ่ม|ข้อมูลอยู่ในเครื่องคุณ",
            "Create your own AI assistants and chat one-on-one or team them up in a group room. Your data stays on your phone.",
            "나만의 AI 비서를 여러 개 만들어 1:1로 대화하거나 단체방에서 함께 일하게 해요. 데이터는 내 폰에만 저장돼요.",
            "创建多个专属 AI 助手，|可单独聊天，也可拉进群聊协作。|数据只保存在你的手机上。",
            "अपने कई AI सहायक बनाएँ, अकेले बात करें या ग्रुप रूम में साथ काम कराएँ। डेटा आपके फ़ोन में रहता है।"],
 "d_nammanthuk": ["ดูราคาน้ำมันวันนี้|ปั๊มใกล้คุณบนแผนที่|และสถานะน้ำมัน มี/ใกล้หมด/หมด|จากผู้ใช้ด้วยกัน",
            "Today's fuel prices in Thailand, nearby stations on a map, and live stock status shared by other drivers.",
            "태국의 오늘 유가, 지도 위 가까운 주유소, 다른 운전자가 알려 주는 재고 상태를 한눈에 봐요.",
            "查看泰国今日油价、|地图上的附近加油站，|以及其他车主分享的油品库存状态。",
            "थाईलैंड में आज के ईंधन दाम, नक्शे पर पास के पंप और दूसरे ड्राइवरों से स्टॉक की स्थिति।"],
 "d_aacalc": ["เครื่องคิดเลขพร้อมแปลงหน่วยและแปลงสกุลเงิน|ใช้ออฟไลน์ได้|ไม่ต้องล็อกอิน",
            "A simple calculator with unit and currency converters. Works offline, no login needed.",
            "단위 변환과 환율 변환이 들어 있는 간단한 계산기. 오프라인에서 쓰고 로그인이 필요 없어요.",
            "带单位换算和汇率换算的简洁计算器。|可离线使用，无需登录。",
            "यूनिट और करेंसी कन्वर्टर वाला सरल कैलकुलेटर। ऑफ़लाइन चलता है, लॉगिन नहीं चाहिए।"],
 "d_moffee": ["แอปรับออเดอร์และพิมพ์ใบเสร็จหน้าร้าน|สำหรับร้านกาแฟ ร้านอาหาร และร้านค้า|ใช้ได้แม้ออฟไลน์ ใช้ฟรี",
            "Counter ordering and receipt printing for cafés, restaurants and shops. Works offline, free to use.",
            "카페·음식점·상점을 위한 카운터 주문·영수증 출력 앱. 오프라인 지원, 무료.",
            "适用于咖啡馆、餐厅和商店的|柜台点单与小票打印应用。|支持离线，免费使用。",
            "कैफ़े, रेस्तरां और दुकानों के लिए काउंटर ऑर्डर और रसीद प्रिंटिंग ऐप। ऑफ़लाइन चलता है, मुफ़्त।"],
 "d_suayshot": ["แต่งภาพจากมือถือให้ลุคเหมือนถ่ายด้วยกล้อง DSLR|ประมวลผลในเครื่อง|ไม่อัปโหลดภาพ",
            "Make phone photos look like DSLR shots, with background blur and light and colour tuning, all on your device.",
            "폰 사진을 DSLR로 찍은 듯한 느낌으로 보정해요. 배경 흐림, 빛과 색 조절을 모두 기기 안에서 처리해요.",
            "让手机照片拥有单反质感：|背景虚化、光线与色彩调整，|全部在本机处理。",
            "फ़ोन की फ़ोटो को DSLR जैसा लुक दें: बैकग्राउंड ब्लर, रोशनी और रंग, सब कुछ आपके डिवाइस पर।"],
 "d_scanner": ["สแกนรถ OBD-II ฟรี|อ่านรหัสปัญหา เช็กรถมือสอง|และรู้ทันก่อนเข้าอู่",
            "A free OBD-II car scanner: read trouble codes, check a used car and avoid being overcharged.",
            "무료 OBD-II 차량 스캐너. 고장 코드를 읽고 중고차를 점검하고 바가지를 피해요.",
            "免费 OBD-II 汽车检测：|读取故障码，检查二手车，|避免被多收费。",
            "मुफ़्त OBD-II कार स्कैनर: ट्रबल कोड पढ़ें, पुरानी कार जाँचें और ज़्यादा बिल से बचें।"],
 "d_assistant": ["ผู้ช่วย AI ฟรี สร้างบอตของตัวเอง ใช้คีย์ AI ของคุณเอง",
            "A free AI assistant app: build your own bots and use your own AI keys.",
            "무료 AI 비서 앱. 나만의 봇을 만들고 내 AI 키로 써요.",
            "免费 AI 助手应用：创建自己的机器人，使用你自己的 AI 密钥。",
            "मुफ़्त AI सहायक ऐप: अपने बॉट बनाएँ और अपनी AI कुंजियाँ इस्तेमाल करें।"],
}

def i18n_js():
    out = {}
    for k, v in S.items():
        for i, (code, _) in enumerate(LANGS):
            out.setdefault(code, {})[k] = v[i]
    return out

ICONS = {
 "globe": '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3c2.6 2.7 3.9 5.700 3.900 9S14.600 18.300 12 21c-2.600-2.700-3.900-5.700-3.900-9S9.400 5.700 12 3z"/></svg>',
 "arrow": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 12h14M13 6l6 6-6 6"/></svg>',
 "clock": '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/></svg>',
 "mail": '<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="3" y="5" width="18" height="14" rx="3"/><path d="m4 8 8 6 8-6"/></svg>',
 "check": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="m5 12.500 4.500 4.500L19 7.500"/></svg>',
 "shield": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 3 5 6v5c0 4.500 3 8 7 10 4-2 7-5.500 7-10V6z"/><path d="m9 12 2 2 4-4"/></svg>',
 "gift": '<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="4" y="9" width="16" height="11" rx="2"/><path d="M12 9v11M3 9h18M12 9c-3 0-4.500-1-4.500-2.500S8.500 4 10 4c1.500 0 2 2 2 5zm0 0c3 0 4.500-1 4.500-2.500S15.500 4 14 4c-1.500 0-2 2-2 5z"/></svg>',
 "eye": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M3 3l18 18M10.600 6.100A9.500 9.500 0 0 1 12 6c5 0 8.500 4.500 9.500 6a14 14 0 0 1-3 3.400M6.600 6.700A14 14 0 0 0 2.500 12C3.500 13.500 7 18 12 18c1.400 0 2.700-.4 3.800-.9"/><path d="M9.900 9.900a3 3 0 0 0 4.200 4.200"/></svg>',
}
def ic(n, cls="ic"): return ICONS[n].replace("<svg ", f'<svg class="{cls}" ', 1)

def card(a, idx):
    n = html.escape(a["name"])
    style = f'--c:{a["c"]};--a-ink:{a["ink"]};--a-soft:{a["soft"]};--dc:{a["d"]};--a-dsoft:{a["dsoft"]};--i:{idx}'
    img = f'<span class="app-ic"><img src="{a["icon"]}" alt="" width="64" height="64" decoding="async"></span>'
    head = (f'{img}<span class="app-txt"><span class="app-name">{n}</span>'
            f'<span class="cat" data-i18n="cat_{a["id"]}">{html.escape(S["cat_"+a["id"]][1])}</span></span>')
    desc = f'<span class="desc" data-i18n="d_{a["id"]}">{html.escape(S["d_"+a["id"]][1])}</span>'
    if a["live"]:
        cta = f'<span class="cta"><span data-i18n="open">{S["open"][1]}</span>{ic("arrow")}</span>'
        return (f'<li class="m-stagger" style="{style}"><a class="card" href="{a["url"]}" data-app="{a["id"]}" data-press data-ripple>'
                f'<span class="top">{head}</span>{desc}{cta}</a></li>')
    cta = f'<span class="cta soon-b">{ic("clock")}<span data-i18n="soon_badge">{S["soon_badge"][1]}</span></span>'
    return (f'<li data-reveal style="{style};--i:{idx-len([x for x in APPS if x["live"]])}"><div class="card soon" data-app="{a["id"]}" aria-disabled="true">'
            f'<span class="top">{head}</span>{desc}{cta}</div></li>')

def build():
    live = [a for a in APPS if a["live"]]; soon = [a for a in APPS if not a["live"]]
    cards = "".join(card(a, 4 + i) for i, a in enumerate(live))
    soons = "".join(card(a, 4 + len(live) + i) for i, a in enumerate(soon))
    langs = "".join(f'<li role="none"><button role="menuitemradio" aria-checked="false" lang="{"zh-Hans" if c=="zh" else c}" data-set-lang="{c}">{ic("check","ic tick")}<span>{n}</span></button></li>' for c, n in LANGS)
    dots = "".join(f'<i style="background:{a["c"]};--i:{k}"></i>' for k, a in enumerate(APPS))
    def pic(w, h, cls):
        return (f'<picture><source media="(prefers-color-scheme: dark)" srcset="icons/logo-dark.png?v=2">'
                f'<img class="{cls}" src="icons/logo.png?v=2" alt="MOTOR AA" width="{w}" height="{h}" decoding="async"></picture>')
    logo_hdr = pic(85, 44, "logo-h").replace('alt="MOTOR AA"', 'alt=""')
    logo_hero = pic(300, 155, "logo-big")
    page = f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>MOTOR AA — All our apps</title>
<meta name="description" content="MOTOR AA: every app in one place. Pick an app to open its introduction page. Free, no ads, no trackers.">
<meta name="robots" content="index, follow">
<meta name="theme-color" content="#ffffff" media="(prefers-color-scheme: light)"><meta name="theme-color" content="#0e0e12" media="(prefers-color-scheme: dark)">
<meta name="color-scheme" content="light dark">
<link rel="canonical" href="https://motoraathailand.github.io/">
<meta property="og:type" content="website"><meta property="og:site_name" content="MOTOR AA"><meta property="og:title" content="MOTOR AA — All our apps"><meta property="og:description" content="Every MOTOR AA app in one place. Pick an app to open its introduction page.">
<meta property="og:url" content="https://motoraathailand.github.io/"><meta property="og:image" content="https://motoraathailand.github.io/assets/og.jpg?v=2">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="icons/favicon-32.png?v=2" type="image/png" sizes="32x32"><link rel="icon" href="icons/favicon-192.png?v=2" type="image/png" sizes="192x192"><link rel="apple-touch-icon" href="icons/apple-touch-icon.png?v=2">
<link rel="stylesheet" href="assets/fonts.css">
<link rel="stylesheet" href="motion.css">
<link rel="stylesheet" href="assets/hub.css">
<noscript><style>[data-reveal]{{opacity:1!important;transform:none!important}}</style></noscript>
</head>
<body>
<div class="bg" aria-hidden="true"><i class="b1"></i><i class="b2"></i></div>
<header class="bar">
 <a class="brand" href="./" aria-label="MOTOR AA" data-i18n-aria="home" data-press>{logo_hdr}<span>MOTOR AA</span></a>
 <div class="langwrap">
  <button class="lang-btn" id="langBtn" type="button" aria-haspopup="menu" aria-expanded="false" aria-controls="langMenu" data-press data-ripple>{ic("globe")}<span id="langCur">English</span></button>
  <ul class="lang-menu" id="langMenu" role="menu" hidden aria-label="Language">{langs}</ul>
 </div>
</header>
<main data-lang-root>
 <section class="hero">
  <div class="hero-logo m-stagger" style="--i:0">{logo_hero}</div>
  <div class="hero-txt">
  <h1 class="m-stagger" style="--i:1" data-i18n="h1">All our apps, in one place</h1>
  <p class="sub m-stagger" style="--i:2" data-i18n="sub">Pick an app to open its own introduction page.</p>
  <ul class="chips m-stagger" style="--i:3"><li>{ic("gift")}<span data-i18n="chips_free">Free to use</span></li><li>{ic("eye")}<span data-i18n="chips_noads">No ads here</span></li><li>{ic("shield")}<span data-i18n="chips_notrack">No trackers</span></li></ul>
  </div>
 </section>
 <section aria-labelledby="appsH">
  <h2 id="appsH" class="sec" data-i18n="apps_h">Our apps</h2>
  <ul class="grid" style="--m-stagger:45ms">{cards}</ul>
 </section>
 <section aria-labelledby="soonH" class="soon-sec">
  <h2 id="soonH" class="sec" data-reveal data-i18n="soon_h">Coming soon</h2>
  <p class="soon-sub" data-reveal data-i18n="soon_sub">These apps are getting their intro pages ready.</p>
  <ul class="grid" style="--m-stagger:45ms">{soons}</ul>
 </section>
 <section class="contact" data-reveal>
  <div><h2 class="sec" data-i18n="contact_h">Contact</h2><p data-i18n="contact_p">Feedback or questions about any app? Email us.</p></div>
  <a class="btn" href="mailto:{EMAIL}" data-press data-ripple>{ic("mail")}<span data-i18n="email_btn">Send email</span><b>{EMAIL}</b></a>
 </section>
</main>
<footer class="foot"><span>© 2026 MOTOR AA</span><span data-i18n="footer">No ads, no trackers. This page is fully static.</span></footer>
<script src="motion.js"></script>
<script src="assets/strings.js"></script>
<script src="assets/hub.js"></script>
</body>
</html>
'''
    page = page.replace('|', ' ')
    open(os.path.join(ROOT, "index.html"), "w").write(page)
    js = "window.HUB_STRINGS=" + json.dumps(i18n_js(), ensure_ascii=False, separators=(",", ":")) + ";window.HUB_LANGS=" + json.dumps([c for c, _ in LANGS]) + ";\n"
    open(os.path.join(ROOT, "assets", "strings.js"), "w").write(js)

def fonts():
    """subset Noto Sans CJK SC / KR and Noto Sans Devanagari to this page's own text"""
    texts = {c: "".join(S[k][i] for k in S) + "".join(n for _, n in LANGS) for i, (c, _) in enumerate(LANGS)}
    allchars = "".join(texts.values()) + "".join(a["name"] for a in APPS) + "—·©→✓"
    def sub(src, out, chars, num=None):
        uni = ",".join(f"U+{ord(ch):04X}" for ch in sorted(set(chars)))
        cmd = ["pyftsubset", src] + ([f"--font-number={num}"] if num is not None else []) + [f"--unicodes={uni}", "--flavor=woff2", f"--output-file={out}", "--layout-features=*"]
        subprocess.check_call(cmd)
    d = os.path.join(ROOT, "fonts")
    cjk = {"SC": 2, "KR": 1}
    # find ttc indexes by family name
    from fontTools.ttLib import TTCollection
    col = TTCollection("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"); colb = TTCollection("/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc")
    def idx(c, fam):
        for i, f in enumerate(c.fonts):
            if f["name"].getDebugName(1) == fam: return i
    for w, c, tag in ((400, col, "Regular"), (700, colb, "Bold")):
        sub(f"/usr/share/fonts/opentype/noto/NotoSansCJK-{tag}.ttc", f"{d}/noto-sc-{w}.woff2", texts["zh"] + "0123456789", idx(c, "Noto Sans CJK SC"))
        sub(f"/usr/share/fonts/opentype/noto/NotoSansCJK-{tag}.ttc", f"{d}/noto-kr-{w}.woff2", texts["ko"] + "0123456789", idx(c, "Noto Sans CJK KR"))
    sub("/usr/share/fonts/truetype/sand-box/google/Noto Sans Devanagari/NotoSansDevanagari-VariableFont_wdth,wght.ttf", f"{d}/noto-deva.woff2", texts["hi"], None)

if __name__ == "__main__":
    build()
    if "--fonts" in sys.argv: fonts()
    print("built")
