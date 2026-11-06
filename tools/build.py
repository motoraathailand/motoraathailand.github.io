#!/usr/bin/env python3
"""Build the independent Worldwide, Korea and Thailand MOTOR AA app hubs.

Run ``python3 tools/build.py``. Add ``--fonts`` to refresh the self-hosted
Korean, Chinese and Devanagari subsets after changing translated copy.
"""
import html
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://motoraathailand.github.io"
EMAIL = "motoraathailand@gmail.com"
LANGS = [("th", "ไทย"), ("en", "English"), ("ko", "한국어"), ("zh", "中文"), ("hi", "हिन्दी")]
PAGES = [
    {"slug": "world", "path": "", "default": "en", "regions": ("global",), "label": "Worldwide"},
    {"slug": "kr", "path": "kr/", "default": "ko", "regions": ("global", "kr"), "label": "Korea + Worldwide"},
    {"slug": "th", "path": "th/", "default": "th", "regions": ("global", "th"), "label": "Thailand + Worldwide"},
]

# Global apps appear on every hub. Country-specific apps are never rendered on
# another country's page. A live card links only to that app's external intro.
APPS = [
    dict(id="aaai", name="AAAi", icon="icons/aaai.svg", url="https://aaai-iji8.onrender.com/about", live=True),
    dict(id="autoreport", name="AutoReport", icon="icons/autoreport.png", url="https://motoraathailand.github.io/autoreport-site/", live=True),
    dict(id="aacalc", name="AA Calc", icon="icons/aacalc.svg", url="https://motoraathailand.github.io/aacalc-site/", live=True),
    dict(id="moffee", name="Moffee", icon="icons/moffee.svg", url="https://motoraathailand.github.io/moffee-site/", live=True),
    dict(id="bgaa", name="BGAA", icon="icons/bgaa.png", url="https://motoraathailand.github.io/bgaa-site/", live=True),
    dict(id="scanner", name="GREENLIGHT", icon="icons/greenlight.png", url=None, live=False, dev=True),
    dict(id="nammanthuk", name="น้ำมันถูก", icon="icons/nammanthuk.svg", url="https://motoraathailand.github.io/nammanthuk-site/", live=True, region="th"),
    dict(id="aafranchise", name="AA Franchise", icon="icons/aafranchise.png", url="https://motoraathailand.github.io/aafranchise-site/", live=True, region="th"),
    dict(id="fuelkr", name="주유소를부탁해", icon="icons/fuelkr.svg", url=None, live=False, dev=True, region="kr"),
]
for app in APPS:
    app.setdefault("region", "global")

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
}

# Text order is th, en, ko, zh, hi. Pipes are optional phrase-break hints.
S = {
    "doc_title": ["MOTOR AA — แอปทั้งหมดของเรา", "MOTOR AA — All our apps", "MOTOR AA — 모든 앱", "MOTOR AA — 我们的全部应用", "MOTOR AA — हमारे सभी ऐप"],
    "region_world": ["แอปสำหรับทั่วโลก", "Worldwide apps", "전 세계 앱", "全球应用", "दुनिया भर के ऐप"],
    "region_kr": ["เกาหลี + ทั่วโลก", "Korea + Worldwide", "한국 + 전 세계", "韩国 + 全球", "कोरिया + दुनिया भर"],
    "region_th": ["ไทย + ทั่วโลก", "Thailand + Worldwide", "태국 + 전 세계", "泰国 + 全球", "थाईलैंड + दुनिया भर"],
    "h1": ["แอปที่คุณชื่นชอบ|อยู่ที่เดียว", "Everyday apps,|one sunny place", "일상의 앱을|한곳에", "日常应用，|一站直达", "आपके रोज़मर्रा के ऐप,|एक ही जगह"],
    "sub": ["เลือกแอปที่ใช่ แล้วเปิดหน้าแนะนำได้เลย", "Find your next everyday essential, wrapped in a little tropical warmth.", "필요한 앱을 고르고 소개 페이지를 만나 보세요.", "选择所需应用，打开它的介绍页面。", "अपना अगला ज़रूरी ऐप चुनें और उसका परिचय पेज खोलें।"],
    "chips_free": ["ใช้ฟรี", "Free to use", "무료 사용", "免费使用", "मुफ़्त"],
    "chips_noads": ["", "", "", "", ""],
    "chips_notrack": ["ไม่มีตัวติดตาม", "No trackers", "추적 없음", "无追踪", "कोई ट्रैकर नहीं"],
    "apps_h": ["แอปของเรา", "Our apps", "앱 둘러보기", "我们的应用", "हमारे ऐप"],
    "local_h_kr": ["สำหรับเกาหลี", "Made for Korea", "한국을 위한 앱", "韩国本地应用", "कोरिया के लिए"],
    "local_h_th": ["สำหรับประเทศไทย", "Made for Thailand", "태국을 위한 앱", "泰国本地应用", "थाईलैंड के लिए"],
    "open": ["ดูรายละเอียด", "Explore app", "자세히 보기", "查看详情", "ऐप देखें"],
    "soon_h": ["กำลังเตรียมให้บริการ", "On the horizon", "곧 만나요", "即将推出", "जल्द आ रहा है"],
    "soon_sub": ["แอปใหม่กำลังอยู่ระหว่างการพัฒนา", "Something new is taking shape.", "새로운 앱을 준비하고 있어요.", "新应用正在准备中。", "कुछ नया तैयार हो रहा है।"],
    "soon_badge": ["เร็ว ๆ นี้", "Coming soon", "곧 공개", "即将推出", "जल्द ही"],
    "dev_badge": ["กำลังพัฒนา", "In development", "개발 중", "开发中", "विकासाधीन"],
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


def card(app, index, default_index):
    start, end, ink = PALETTES[app["id"]]
    style = f"--card-start:{start};--card-end:{end};--card-ink:{ink};--i:{index}"
    name = html.escape(app["name"])
    category = S["cat_" + app["id"]][default_index]
    description = S["d_" + app["id"]][default_index]
    copy = f'''<span class="app-copy">
  <span class="cat" data-i18n="cat_{app['id']}">{html.escape(category)}</span>
  <span class="app-name">{name}</span>
  <span class="desc" data-i18n="d_{app['id']}">{html.escape(description)}</span>
</span>'''
    picture = f'''<span class="app-ic"><img src="/{app['icon']}" alt="" width="96" height="96" decoding="async"></span>'''
    palm = '<svg class="palm" viewBox="0 0 120 120" aria-hidden="true"><path d="M13 115C34 88 51 58 67 22M65 25C46 13 32 13 13 23c23 0 36 8 50 10M67 23C55 4 43 0 30 1c18 8 23 17 32 28M69 25C78 5 88 1 104 2c-18 10-23 18-30 28M69 28c19-9 33-7 47 3-21-2-32 3-43 4M63 37C42 31 29 36 17 50c21-8 32-5 42-5"/></svg>'
    if app["live"]:
        action = f'<span class="cta"><span data-i18n="open">{S["open"][default_index]}</span>{icon("arrow")}</span>'
        return f'''<li class="m-stagger" style="{style}">
<a class="card" href="{app['url']}" data-app="{app['id']}" data-press data-ripple>{palm}{copy}{picture}{action}</a>
</li>'''
    action = f'<span class="cta status">{icon("clock")}<span data-i18n="dev_badge">{S["dev_badge"][default_index]}</span></span>'
    return f'''<li class="m-stagger" style="{style}">
<div class="card soon" data-app="{app['id']}" aria-disabled="true">{palm}{copy}{picture}{action}</div>
</li>'''


def render_page(page):
    apps = [a for a in APPS if a["region"] in page["regions"]]
    local_apps = [a for a in apps if a["region"] != "global"]
    global_live = [a for a in apps if a["region"] == "global" and a["live"]]
    global_upcoming = [a for a in apps if a["region"] == "global" and not a["live"]]
    index = LANGS.index(next(item for item in LANGS if item[0] == page["default"]))
    url = SITE + "/" + page["path"]
    title = S["doc_title"][index]
    region = S["region_" + page["slug"]][index]
    local_markup = ""
    if local_apps:
        local_key = "local_h_" + page["slug"]
        local_cards = "\n".join(card(a, i + 2, index) for i, a in enumerate(local_apps))
        local_markup = f'''<section class="apps-block">
  <ul class="app-grid">{local_cards}</ul>
</section>
'''
    cards = "\n".join(card(a, i + 2, index) for i, a in enumerate(global_live))
    upcoming_markup = ""
    if global_upcoming:
        soon_cards = "\n".join(card(a, i + 8, index) for i, a in enumerate(global_upcoming))
        upcoming_markup = f'''<section class="soon-section" aria-labelledby="soonH">
<h2 id="soonH" class="section-title" data-i18n="soon_h">{S["soon_h"][index]}</h2>
<p class="section-sub" data-i18n="soon_sub">{S["soon_sub"][index]}</p>
<ul class="app-grid">{soon_cards}</ul>
</section>'''
    languages = "\n".join(
        f'<li role="none"><button role="menuitemradio" aria-checked="false" lang="{"zh-Hans" if code == "zh" else code}" data-set-lang="{code}">{icon("check", "tick")}<span>{name}</span></button></li>'
        for code, name in LANGS
    )
    logo = '<picture><source media="(prefers-color-scheme: dark)" srcset="/icons/logo-mark-dark.png"><img src="/icons/logo-mark.png" alt="AA" width="180" height="45"></picture>'
    return f'''<!doctype html>
<html lang="{page['default']}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{html.escape(title)}</title>
<meta name="description" content="MOTOR AA — {html.escape(region)}. Pick an app to open its introduction page.">
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
<link rel="stylesheet" href="/assets/hub.css?v=8">
</head>
<body data-region="{page['slug']}">
<div class="bg" aria-hidden="true"><i class="leaf leaf-one"></i><i class="leaf leaf-two"></i></div>
<header class="bar">
 <span class="region" data-i18n="region_{page['slug']}">{html.escape(region)}</span>
 <span class="brand">{logo}</span>
 <div class="langwrap">
  <button class="lang-btn" id="langBtn" type="button" aria-haspopup="menu" aria-expanded="false" aria-controls="langMenu" aria-label="Language" data-press>{icon("globe")}<span id="langCur">{dict(LANGS)[page['default']]}</span></button>
  <ul class="lang-menu" id="langMenu" role="menu" hidden aria-label="Language">{languages}</ul>
 </div>
</header>
<main data-lang-root>
 <section class="hero">
  <span class="eyebrow m-stagger" style="--i:0">{icon("spark")}<span data-i18n="region_{page['slug']}">{html.escape(region)}</span></span>
  <h1 class="m-stagger" style="--i:1" data-i18n="h1">{html.escape(S['h1'][index])}</h1>
  <p class="sub m-stagger" style="--i:2" data-i18n="sub">{html.escape(S['sub'][index])}</p>
  <ul class="chips m-stagger" style="--i:3"><li>{icon("spark")}<span data-i18n="chips_free">{S['chips_free'][index]}</span></li><li>{icon("shield")}<span data-i18n="chips_notrack">{S['chips_notrack'][index]}</span></li></ul>
 </section>
 {local_markup}<section class="apps-block">
  <ul class="app-grid">{cards}</ul>
 </section>
 {upcoming_markup}
 <section class="contact m-stagger" style="--i:6">
  <span class="contact-icon">{icon("mail")}</span>
  <div><h2 data-i18n="contact_h">{S['contact_h'][index]}</h2><p data-i18n="contact_p">{S['contact_p'][index]}</p></div>
  <a class="btn" href="mailto:{EMAIL}" aria-label="{EMAIL}" data-press data-ripple><span data-i18n="email_btn">{S['email_btn'][index]}</span>{icon("arrow")}</a>
 </section>
</main>
<footer class="foot"><span>© 2026 MOTOR AA</span><span data-i18n="footer">{S['footer'][index]}</span></footer>
<script>window.HUB_REGION={json.dumps(page['slug'])};window.HUB_DEFAULT={json.dumps(page['default'])};</script>
<script src="/motion.js"></script>
<script>window.HUB_STRINGS={json.dumps(i18n_js(), ensure_ascii=False, separators=(',', ':'))};window.HUB_LANGS={json.dumps([c for c, _ in LANGS])};</script>
<script src="/assets/hub.js?v=8"></script>
</body>
</html>
'''


def fonts():
    """Subset installed Noto fonts to the hub's own Korean, Chinese and Hindi text."""
    text = {code: "".join(S[key][i] for key in S) + name for i, (code, name) in enumerate(LANGS)}
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
    with open(os.path.join(ROOT, "sitemap.xml"), "w", encoding="utf-8") as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n')
        f.writelines(f'<url><loc>{SITE}/{p["path"]}</loc></url>\n' for p in PAGES)
        f.write('</urlset>\n')


if __name__ == "__main__":
    build()
    if "--fonts" in sys.argv:
        fonts()
    print("Built /, /kr/, /th/ and sitemap.xml")
