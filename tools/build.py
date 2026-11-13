#!/usr/bin/env python3
"""Build the MOTOR AA app hub. The Thailand collection page is the site root.

Published at https://motoraath.com (custom domain). The same page is also
written at /th/ so older https://motoraathailand.github.io/th links still work.
The former Korea hub (/kr/) stays deleted; GitHub Pages answers it with 404.html.

Run ``python3 tools/build.py``. Add ``--fonts`` to refresh the self-hosted
Korean, Chinese and Devanagari subsets after changing translated copy.
"""
import html
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://motoraath.com"
EMAIL = "motoraathailand@gmail.com"
LANGS = [("th", "ไทย"), ("en", "English"), ("ko", "한국어"), ("zh", "中文"), ("hi", "हिन्दी")]
PAGES = [
    {"slug": "th", "path": "th/", "default": "th"},
]
# The collection page is the site root. No trailing slash in the canonical URL.
TH_URL = SITE

# App registry. The Thailand hub shows two fixed cards, in order, with store
# buttons. play_tester is kept on the registry for the apps' own introduction
# sites and is not used as a hub store link.
APPS = [
    dict(id="aaai", name="AAAi", icon="icons/aaai.png", url="https://aaai-iji8.onrender.com/about", live=True),
    dict(id="autoreport", name="AutoReport", icon="icons/autoreport.png", url="https://motoraathailand.github.io/autoreport-site/", live=True),
    dict(id="aacalc", name="AA Calc", icon="icons/aacalc.png", url="https://motoraathailand.github.io/aacalc-site/", live=True),
    dict(id="moffee", name="Moffee", icon="icons/moffee.png", url="https://motoraathailand.github.io/moffee-site/", live=True),
    dict(id="bgaa", name="BGAA", icon="icons/bgaa.png", url="https://motoraathailand.github.io/bgaa-site/", live=True,
         play_tester="https://motoraathailand.github.io/bgaa-site/join.html"),
    # GREENLIGHT stays in development on both stores. There is no tester URL.
    dict(id="scanner", name="GREENLIGHT", icon="icons/greenlight.png", url=None, live=False, dev=True),
    dict(id="nammanthuk", name="น้ำมันถูก", icon="icons/nammanthuk.png", url="https://motoraathailand.github.io/nammanthuk-site/", live=True, region="th",
         play_tester="https://motoraathailand.github.io/nammanthuk-site/join.html"),
    dict(id="aafranchise", name="AA Franchise", icon="icons/aafranchise.png", url="https://motoraathailand.github.io/aafranchise-site/", live=True, region="th"),
    dict(id="fuelkr", name="주유소를부탁해", icon="icons/fuelkr.png", url=None, live=False, dev=True, region="kr"),
    # Global mini-game app, kept in the registry but not shown on /th/ for now.
    dict(id="ezz", name="EZZ", icon="icons/ezz.png", url=None, live=False, dev=True, region="global"),
]
for app in APPS:
    app.setdefault("region", "global")

# Thailand hub. For now (2026-11-12): only nammanthuk and BGAA.
# AA Franchise, AAAi and other apps stay in the registry but are hidden from
# the collection page. Korea-only fuelkr stays omitted.
TH_STORE_ORDER = ("nammanthuk", "bgaa")
# These cards' store buttons open the app intro page, except BGAA's App Store
# button, which is unsupported (2026-11-12). Intro pages follow ?lang=, then
# the saved choice, then the device language, and fall back to English. Not
# join.html.
NAMMANTHUK_INTRO = "https://motoraathailand.github.io/nammanthuk-site/"
AAFRANCHISE_INTRO = "https://motoraathailand.github.io/aafranchise-site/"
AAAI_INTRO = "https://aaai-iji8.onrender.com/about"
BGAA_INTRO = "https://motoraathailand.github.io/bgaa-site/"
TH_INTRO = {
    "nammanthuk": NAMMANTHUK_INTRO,
    "aafranchise": AAFRANCHISE_INTRO,
    "aaai": AAAI_INTRO,
    "bgaa": BGAA_INTRO,
}

PALETTES = {
    "aaai": ("#eaa3aa", "#f4c6c1", "#66353e"),
    "autoreport": ("#ed967f", "#f4baa1", "#703b31"),
    "aacalc": ("#ee9c7f", "#f5c19e", "#6c3b29"),
    "moffee": ("#f5dfc7", "#fff0dc", "#704735"),
    "bgaa": ("#eeb4a9", "#f7d4c1", "#6c3c35"),
    "scanner": ("#e99b8d", "#f4c4ae", "#693a30"),
    "nammanthuk": ("#de7869", "#ef9c82", "#fffaf6"),
    "aafranchise": ("#df7768", "#efa285", "#fffaf6"),
    "fuelkr": ("#edab98", "#f8cfb8", "#663c30"),
    "ezz": ("#ee9fb6", "#f8c9d6", "#6b2a40"),
}

# Extra copy for registry apps that have no entry in S.
TH_S = {
    "cat_ezz": ["เกมออฟไลน์", "Offline games", "오프라인 게임", "离线游戏", "ऑफ़लाइन गेम"],
    "d_ezz": ["รวมมินิเกมที่เล่นได้แม้ไม่มีอินเทอร์เน็ต เช่น 2048 ซูโดกุ และบล็อกพัซเซิล", "A collection of mini games you can play without internet, like 2048, sudoku and block puzzle.", "2048, 스도쿠, 블록 퍼즐 등 인터넷 없이도 즐기는 미니게임 모음.", "无需联网即可畸玩的小游戏合集，包括 2048、数独和方块拼图。", "2048, सुडोकू और ब्लॉक पज़ल जैसे बिना इंटरनेट खेले जाने वाले मिनी गेम्स।"],
}

# Text order is th, en, ko, zh, hi. Pipes are optional phrase-break hints.
S = {
    "doc_title": ["MOTOR AA — แอปทั้งหมดของเรา", "MOTOR AA — All our apps", "MOTOR AA — 모든 앱", "MOTOR AA — 我们的全部应用", "MOTOR AA — हमारे सभी ऐप"],
    "h1": ["แอปที่คุณชื่นชอบ|อยู่ที่เดียว", "Everyday apps,|one sunny place", "일상의 앱을|한곳에", "日常应用，|一站直达", "आपके रोज़मर्रा के ऐप,|एक ही जगह"],
    "sub": ["เลือกแอปที่ใช่ แล้วเปิดหน้าแนะนำได้เลย", "Find your next everyday essential, wrapped in a little tropical warmth.", "필요한 앱을 고르고 소개 페이지를 만나 보세요.", "选择所需应用，打开它的介绍页面。", "अपना अगला ज़रूरी ऐप चुनें और उसका परिचय पेज खोलें।"],
    "apps_h": ["แอปของเรา", "Our apps", "앱 둘러보기", "我们的应用", "हमारे ऐप"],
    "open": ["ดูรายละเอียด", "Explore app", "자세히 보기", "查看详情", "ऐप देखें"],
    "dev_badge": ["กำลังพัฒนา", "In development", "개발 중", "开发中", "विकासाधीन"],
    "unsupported_badge": ["ไม่รองรับ", "Not supported", "지원하지 않음", "不支持", "समर्थित नहीं"],
    "contact_h": ["มาคุยกัน", "Let’s talk", "문의하기", "联系我们", "बात करें"],
    "contact_p": ["ข้อเสนอแนะหรือคำถาม ส่งอีเมลหาเราได้เลย", "A question, an idea, or just want to say hello?", "앱에 대한 의견이나 질문을 보내 주세요.", "有任何意见或问题，欢迎发邮件给我们。", "कोई सवाल या सुझाव? हमें ईमेल करें।"],
    "email_btn": ["ส่งอีเมล", "Send email", "메일 보내기", "发送邮件", "ईमेल भेजें"],
    "lang": ["ภาษา", "Language", "언어", "语言", "भाषा"],
    "footer": ["เว็บไซต์แบบสแตติก ไม่มีตัวติดตาม", "Static site. No trackers.", "정적 웹사이트예요. 추적 없음.", "纯静态网站，无追踪。", "स्थिर साइट। कोई ट्रैकर नहीं।"],
    "home": ["MOTOR AA หน้าแรก", "MOTOR AA home", "MOTOR AA 홈", "MOTOR AA 首页", "MOTOR AA होम"],
    "cat_aaai": ["ผู้ช่วย AI", "AI assistants", "AI 비서", "AI 助手", "AI सहायक"],
    "cat_autoreport": ["อู่ซ่อมรถ", "Car repair shops", "정비소", "汽修店", "कार रिपेयर शॉप"],
    "cat_nammanthuk": ["ราคาน้ำมันในประเทศไทย", "Fuel prices · Thailand", "태국 주유소 가격", "泰国油价", "थाईलैंड में ईंधन के दाम"],
    "cat_aacalc": ["เครื่องคิดเลข", "Calculator", "계산기", "计算器", "कैलकुलेटर"],
    "cat_moffee": ["POS รับออเดอร์", "POS & orders", "POS·주문", "POS 点单", "POS ऑर्डर"],
    "cat_aafranchise": ["แฟรนไชส์ไทย", "Thai franchises", "태국 프랜차이즈", "泰国加盟", "थाई फ्रेंचाइज़"],
    "cat_bgaa": ["เพลงประกอบร้าน", "Store background music", "매장 배경음악", "店铺背景音乐", "स्टोर बैकग्राउंड संगीत"],
    "cat_scanner": ["Benz · BMW · Audi", "Benz · BMW · Audi diagnostics", "벤츠·BMW·아우디 점검", "奔驰·宝马·奥迪诊断", "Benz · BMW · Audi जांच"],
    "cat_fuelkr": ["주유소 가격 · 한국", "Fuel prices · Korea", "주유소 가격 · 한국", "韩国油价 · 韩国", "कोरिया में ईंधन के दाम"],
    "d_aaai": ["สร้างผู้ช่วย AI ของคุณ คุยแบบตัวต่อตัวหรือรวมทีมในห้องกลุ่ม ข้อมูลอยู่ในเครื่องคุณ", "Create your own AI assistants, chat one-on-one or bring the team together. Your data stays on your phone.", "나만의 AI 비서를 만들고 1:1 또는 단체방에서 대화해요. 데이터는 내 폰에 저장돼요.", "创建你的专属 AI 助手，单独聊天或团队协作。数据保存在你的手机上。", "अपने AI सहायक बनाएँ और अकेले या टीम में बात करें। डेटा आपके फ़ोन में रहता है।"],
    "d_autoreport": ["ใบเสนอราคา ใบสั่งงาน และประวัติซ่อมสำหรับอู่ พิมพ์ A4 หรือ PDF", "Quotes, job sheets and service history for car repair shops. Print A4 or share a PDF.", "정비소를 위한 견적서·작업지시서·정비 이력. A4 인쇄와 PDF 공유를 지원해요.", "汽修店报价单、工单与维修记录，支持 A4 打印和 PDF 分享。", "कार रिपेयर शॉप के लिए कोटेशन, जॉब शीट और सर्विस हिस्ट्री।"],
    "d_aacalc": ["เครื่องคิดเลข แปลงหน่วยและสกุลเงิน ใช้ออฟไลน์ได้โดยไม่ต้องล็อกอิน", "A simple calculator with unit and currency converters. Works offline, no login needed.", "단위 변환과 환율 변환을 지원하는 계산기. 오프라인에서도 로그인 없이 사용해요.", "简洁的计算器，带单位与汇率换算。可离线使用，无需登录。", "यूनिट और करेंसी कन्वर्टर वाला सरल कैलकुलेटर। ऑफ़लाइन काम करता है।"],
    "d_moffee": ["รับออเดอร์และพิมพ์ใบเสร็จสำหรับร้านกาแฟและร้านอาหาร ใช้ออฟไลน์ได้", "Counter ordering and receipt printing for cafés, restaurants and shops. Works offline.", "카페·음식점·상점을 위한 주문·영수증 출력 앱. 오프라인에서도 사용할 수 있어요.", "适用于咖啡馆、餐厅和商店的点单与小票打印。支持离线使用。", "कैफ़े और दुकानों के लिए ऑर्डर और रसीद प्रिंटिंग। ऑफ़लाइन चलता है।"],
    "d_bgaa": ["เพลงประกอบร้านที่ปลอดภัยเรื่องลิขสิทธิ์ เลือกเพลย์ลิสต์ที่เข้ากับบรรยากาศร้าน", "Copyright-safe background music for shops and cafés. Pick a playlist that fits the mood.", "저작권 걱정 없는 매장 배경음악. 가게 분위기에 어울리는 플레이리스트를 골라 보세요.", "适用于商店和咖啡馆的版权安全背景音乐。", "दुकानों और कैफ़े के लिए कॉपीराइट-सुरक्षित बैकग्राउंड संगीत।"],
    "d_scanner": ["วิเคราะห์เชิงลึกและโค้ดดิ้งสำหรับ Mercedes-Benz, BMW และ Audi", "In-depth diagnostics and coding for Mercedes-Benz, BMW and Audi.", "벤츠·BMW·아우디를 위한 정밀진단 및 코딩 앱.", "专为奔驰、宝马和奥迪打造的深度诊断与编码应用。", "Mercedes-Benz, BMW और Audi के लिए गहन डायग्नोस्टिक्स और कोडिंग।"],
    "d_nammanthuk": ["ดูราคาน้ำมัน ปั๊มใกล้คุณ และสถานะน้ำมันจากผู้ใช้ในประเทศไทย", "Fuel prices, nearby stations and driver-shared stock updates across Thailand.", "태국의 유가, 가까운 주유소와 운전자가 공유하는 재고 정보를 확인해요.", "查看泰国油价、附近加油站以及车主分享的油品库存。", "थाईलैंड में ईंधन की कीमतें, पास के पंप और स्टॉक अपडेट।"],
    "d_aafranchise": ["ค้นหาและเปรียบเทียบแฟรนไชส์ไทย ดูเงินลงทุนและระยะคืนทุน", "Discover and compare Thai franchises, from investment to payback period.", "태국 프랜차이즈의 투자 비용과 투자 회수 기간을 비교해 보세요.", "发现泰国加盟品牌，比较投资额与回本周期。", "थाई फ्रेंचाइज़ खोजें और निवेश की तुलना करें।"],
    "d_fuelkr": ["ข้อมูลราคาน้ำมันและปั๊มใกล้เคียงสำหรับผู้ขับขี่ในเกาหลี กำลังอยู่ระหว่างการพัฒนา", "Fuel prices and nearby stations for drivers in Korea. Currently in development.", "한국 운전자를 위한 유가와 가까운 주유소 정보. 현재 개발 중이에요.", "为韩国司机提供油价和附近加油站信息，目前正在开发中。", "कोरिया के ड्राइवरों के लिए ईंधन की कीमतें और पास के पेट्रोल पंप। विकास में।"],
}


def i18n_js():
    result = {}
    for key, strings in S.items():
        for i, (code, _) in enumerate(LANGS):
            result.setdefault(code, {})[key] = strings[i]
    return result


def hub_text(key, index):
    if key in S:
        return S[key][index]
    return TH_S[key][index]


ICONS = {
    "globe": '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3c2.6 2.7 3.9 5.7 3.9 9S14.6 18.3 12 21c-2.6-2.7-3.9-5.7-3.9-9S9.4 5.7 12 3z"/></svg>',
    "arrow": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 12h14M13 6l6 6-6 6"/></svg>',
    "clock": '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/></svg>',
    "mail": '<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="3" y="5" width="18" height="14" rx="3"/><path d="m4 8 8 6 8-6"/></svg>',
    "check": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="m5 12.5 4.5 4.5L19 7.5"/></svg>',
    "spark": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="m12 3 2.1 6.9L21 12l-6.9 2.1L12 21l-2.1-6.9L3 12l6.9-2.1z"/></svg>',
    "sun": '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="4"/><path d="M12 2v2m0 16v2M2 12h2m16 0h2M5 5l1.5 1.5m11 11L19 19M5 19l1.5-1.5m11-11L19 5"/></svg>',
    "shield": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 3 5 6v5c0 4.5 3 8 7 10 4-2 7-5.5 7-10V6z"/><path d="m9 12 2 2 4-4"/></svg>',
}


def icon(name, extra=""):
    return ICONS[name].replace("<svg ", f'<svg class="ic {extra}" ', 1)


PLAY_MARK = '<svg class="store-mark" viewBox="0 0 24 24" aria-hidden="true"><path fill="#4285F4" d="M3.2 2.4c-.4.4-.6 1-.6 1.7v15.8c0 .7.2 1.3.6 1.7l.1.1 8.9-8.9v-.2L3.3 2.3l-.1.1z"/><path fill="#FBBC04" d="M16.4 15.5 12.6 11.7v-.2l3.8-3.8.1.1 4.5 2.6c1.2.7 1.2 1.9 0 2.6l-4.5 2.5-.1.1z"/><path fill="#34A853" d="M16.5 15.4 12.6 11.5 3.2 20.9c.5.5 1.2.6 2 .1l11.2-6.4.1-.2z"/><path fill="#EA4335" d="M16.5 8.8 5.2 2.3c-.8-.5-1.5-.4-2 .1l9.4 9.3 3.9-2.9z"/></svg>'
APPLE_MARK = '<svg class="store-mark" viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M16.37 12.64c-.02-2.2 1.8-3.26 1.88-3.31-1.03-1.5-2.62-1.7-3.18-1.73-1.35-.14-2.64.8-3.33.8-.69 0-1.75-.78-2.88-.76-1.48.02-2.85.86-3.61 2.19-1.54 2.67-.39 6.62 1.11 8.79.73 1.06 1.61 2.25 2.76 2.21 1.11-.04 1.53-.71 2.87-.71 1.34 0 1.72.71 2.89.69 1.19-.02 1.95-1.08 2.68-2.15.84-1.23 1.19-2.42 1.21-2.48-.03-.01-2.32-.89-2.34-3.54zM14.7 6.55c.61-.74 1.02-1.77.91-2.8-.88.04-1.94.59-2.57 1.32-.56.65-1.06 1.69-.93 2.69.98.08 1.98-.5 2.59-1.21z"/></svg>'


def store_button(kind, default_index, href, badge=None):
    """One identifiable store control.

    href set: live link. href None and badge "unsupported": not supported,
    disabled, no link. Otherwise: in-development, disabled, no link.
    """
    mark = PLAY_MARK if kind == "google-play" else APPLE_MARK
    label = "Google Play" if kind == "google-play" else "App Store"
    if href:
        return (
            f'<a class="store" data-store="{kind}" data-state="live" href="{html.escape(href, quote=True)}" rel="noopener" data-press data-ripple>'
            f'{mark}<span class="store-copy"><span class="store-name">{label}</span></span></a>'
        )
    key = "unsupported_badge" if badge == "unsupported" else "dev_badge"
    state_name = "unsupported" if badge == "unsupported" else "dev"
    state = html.escape(S[key][default_index])
    return (
        f'<button type="button" class="store" data-store="{kind}" data-state="{state_name}" disabled aria-disabled="true">'
        f'{mark}<span class="store-copy"><span class="store-name">{label}</span>'
        f'<span class="store-state" data-i18n="{key}">{state}</span></span></button>'
    )


def store_card(app, index, default_index):
    """Thailand card: same coral shell, with Google Play and App Store controls."""
    start, end, ink = PALETTES[app["id"]]
    style = f"--card-start:{start};--card-end:{end};--card-ink:{ink};--i:{index}"
    name = html.escape(app["name"])
    category = hub_text("cat_" + app["id"], default_index)
    description = hub_text("d_" + app["id"], default_index)
    copy = f'''<span class="app-copy">
  <span class="cat" data-i18n="cat_{app['id']}">{html.escape(category)}</span>
  <span class="app-name">{name}</span>
  <span class="desc" data-i18n="d_{app['id']}">{html.escape(description)}</span>
</span>'''
    picture = f'''<span class="app-ic"><img src="/{app['icon']}?v=2" alt="" width="96" height="96" decoding="async"></span>'''
    # Most cards link both stores to the intro page. BGAA's App Store button
    # is not supported (2026-11-12). A card without an intro page would show
    # the in-development control.
    href = TH_INTRO.get(app["id"])
    play = store_button("google-play", default_index, href)
    if app["id"] == "bgaa":
        store = store_button("app-store", default_index, None, badge="unsupported")
    else:
        store = store_button("app-store", default_index, href)
    buttons = play + store
    return f'''<li class="m-stagger" style="{style}">
<div class="card" data-app="{app['id']}">{copy}{picture}<span class="stores">{buttons}</span></div>
</li>'''


def render_page(page):
    """Render the Thailand hub: two fixed store cards, no region label text."""
    index = LANGS.index(next(item for item in LANGS if item[0] == page["default"]))
    url = TH_URL
    title = S["doc_title"][index]
    css_v = "14"
    by_id = {a["id"]: a for a in APPS}
    ordered_live = [by_id[i] for i in TH_STORE_ORDER]
    for app_id, intro in TH_INTRO.items():
        if by_id[app_id].get("url") != intro or "join.html" in intro:
            raise SystemExit(f"{app_id} store buttons must use the intro page, not a tester join URL")
    if "fuelkr" in TH_STORE_ORDER:
        raise SystemExit("Korea-only fuelkr must not appear on the Thailand hub")
    cards = "\n".join(store_card(a, i + 2, index) for i, a in enumerate(ordered_live))
    languages = "\n".join(
        f'<li role="none"><button role="menuitemradio" aria-checked="false" lang="{"zh-Hans" if code == "zh" else code}" data-set-lang="{code}">{icon("check", "tick")}<span>{name}</span></button></li>'
        for code, name in LANGS
    )
    logo = '<picture><source media="(prefers-color-scheme: dark)" srcset="/icons/logo-mark-dark.png"><img src="/icons/logo-mark.png" alt="AA" width="180" height="45"></picture>'
    hub_strings = i18n_js()
    for i, (code, _) in enumerate(LANGS):
        for key, values in TH_S.items():
            hub_strings[code][key] = values[i]
    return f'''<!doctype html>
<html lang="{page['default']}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{html.escape(title)}</title>
<meta name="description" content="MOTOR AA. Pick an app to open its introduction page.">
<meta name="robots" content="index,follow">
<meta name="theme-color" content="#fffaf5">
<link rel="canonical" href="{url}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="MOTOR AA">
<meta property="og:title" content="{html.escape(title)}">
<meta property="og:description" content="Everyday apps in one sunny place.">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{SITE}/assets/og.jpg">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="/icons/favicon-32.png" type="image/png" sizes="32x32">
<link rel="icon" href="/icons/favicon-192.png" type="image/png" sizes="192x192">
<link rel="apple-touch-icon" href="/icons/apple-touch-icon.png">
<link rel="stylesheet" href="/assets/fonts.css">
<link rel="stylesheet" href="/motion.css">
<link rel="stylesheet" href="/assets/hub.css?v={css_v}">
</head>
<body data-region="{page['slug']}">
<div class="bg" aria-hidden="true"><i class="leaf leaf-one"></i><i class="leaf leaf-two"></i></div>
<header class="bar">
 <span class="region" aria-hidden="true"></span>
 <span class="brand">{logo}</span>
 <div class="langwrap">
  <button class="lang-btn" id="langBtn" type="button" aria-haspopup="menu" aria-expanded="false" aria-controls="langMenu" aria-label="Language" data-press>{icon("globe")}<span id="langCur">{dict(LANGS)[page['default']]}</span></button>
  <ul class="lang-menu" id="langMenu" role="menu" hidden aria-label="Language">{languages}</ul>
 </div>
</header>
<main data-lang-root>
 <section class="hero">
  <span class="eyebrow m-stagger" style="--i:0">{icon("spark")}</span>
  <h1 class="m-stagger" style="--i:1" data-i18n="h1">{html.escape(S['h1'][index])}</h1>
  <p class="sub m-stagger" style="--i:2" data-i18n="sub">{html.escape(S['sub'][index])}</p>
 </section>
 <section class="apps-block">
  <ul class="app-grid">{cards}</ul>
 </section>
 <section class="contact m-stagger" style="--i:6">
  <span class="contact-icon">{icon("mail")}</span>
  <div><h2 data-i18n="contact_h">{S['contact_h'][index]}</h2><p data-i18n="contact_p">{S['contact_p'][index]}</p></div>
  <a class="btn" href="mailto:{EMAIL}" aria-label="{EMAIL}" data-press data-ripple><span data-i18n="email_btn">{S['email_btn'][index]}</span>{icon("arrow")}</a>
 </section>
</main>
<footer class="foot"><span>© 2026 MOTOR AA</span><span data-i18n="footer">{S['footer'][index]}</span></footer>
<script>window.HUB_REGION={json.dumps(page['slug'])};window.HUB_DEFAULT={json.dumps(page['default'])};</script>
<script src="/motion.js"></script>
<script>window.HUB_STRINGS={json.dumps(hub_strings, ensure_ascii=False, separators=(',', ':'))};window.HUB_LANGS={json.dumps([c for c, _ in LANGS])};</script>
<script src="/assets/hub.js?v=10"></script>
</body>
</html>
'''


def fonts():
    """Subset installed Noto fonts to the hub's own Korean, Chinese and Hindi text."""
    text = {code: "".join(S[key][i] for key in S) + "".join(TH_S[key][i] for key in TH_S) + name for i, (code, name) in enumerate(LANGS)}
    for weight, tag in ((400, "Regular"), (700, "Bold")):
        filename = f"/usr/share/fonts/opentype/noto/NotoSansCJK-{tag}.ttc"
        if not os.path.isfile(filename):
            print("Noto source fonts unavailable; keeping existing font subsets", file=sys.stderr)
            return
        from fontTools.ttLib import TTCollection
        collection = TTCollection(filename)
        for code, family, size in (("zh", "Noto Sans CJK SC", "sc"), ("ko", "Noto Sans CJK KR", "kr")):
            font_index = next(i for i, font in enumerate(collection.fonts) if font["name"].getDebugName(1) == family)
            characters = text[code] + "".join(name for _, name in LANGS) + "주유소를부탁해0123456789"
            unicodes = ",".join(f"U+{ord(c):04X}" for c in sorted(set(characters)))
            subprocess.check_call(["pyftsubset", filename, f"--font-number={font_index}", f"--unicodes={unicodes}", "--flavor=woff2", f"--output-file={ROOT}/fonts/noto-{size}-{weight}.woff2", "--layout-features=*"])
    src = "/usr/share/fonts/truetype/sand-box/google/Noto Sans Devanagari/NotoSansDevanagari-VariableFont_wdth,wght.ttf"
    characters = text["hi"] + "हिन्दी0123456789"
    if os.path.isfile(src):
        unicodes = ",".join(f"U+{ord(c):04X}" for c in sorted(set(characters)))
        subprocess.check_call(["pyftsubset", src, f"--unicodes={unicodes}", "--flavor=woff2", f"--output-file={ROOT}/fonts/noto-deva.woff2", "--layout-features=*"])


def build():
    for page in PAGES:
        directory = os.path.join(ROOT, page["path"])
        os.makedirs(directory, exist_ok=True)
        with open(os.path.join(directory, "index.html"), "w", encoding="utf-8") as f:
            f.write(render_page(page).replace("|", " "))
    # Same Thailand hub at the site root (motoraath.com/).
    with open(os.path.join(ROOT, "index.html"), "w", encoding="utf-8") as f:
        f.write(render_page(PAGES[0]).replace("|", " "))
    with open(os.path.join(ROOT, "sitemap.xml"), "w", encoding="utf-8") as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n')
        f.write(f'<url><loc>{TH_URL}</loc></url>\n')
        f.write('</urlset>\n')


if __name__ == "__main__":
    build()
    if "--fonts" in sys.argv:
        fonts()
    print("Built /, /th/, and sitemap.xml")
