#!/usr/bin/env python3
import html
import json
import re
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from collections import OrderedDict
from datetime import datetime, timezone, timedelta
from email.utils import parsedate_to_datetime
from typing import Optional, Tuple
from urllib.error import HTTPError, URLError

UA = "Mozilla/5.0 (compatible; BigTechCareerRadar/1.0)"
TIMEOUT = 30
TZ_TW = timezone(timedelta(hours=8))
GOOGLE_BASE = "https://www.google.com/about/careers/applications/"
MEDIATEK_TRPC = "https://careers.mediatek.com/api/trpc/job.getJobs"
MEDIATEK_TW_LOCATIONS = ["0000009255", "0000009256", "0000073451", "9031"]
ACER_ALL_JOBS_URL = "https://careers.acer.com/go/All-Jobs/7865610/?locale=en_US"
TREND_WORKDAY_JOBS_URL = "https://trendmicro.wd3.myworkdayjobs.com/wday/cxs/trendmicro/External/jobs"
ADVANTECH_WORKDAY_JOBS_URL = "https://advantech.wd3.myworkdayjobs.com/wday/cxs/advantech/External/jobs"
AUO_JOB_LIST_API = "https://career.auo.com/job_list/GetJobList"

COMPANIES = OrderedDict([
    (
        "台積電",
        {
            "company_keywords": ["台積電", "TSMC"],
            "career_url": "https://careers.tsmc.com/zh_TW/careers/SearchJobs",
            "job104_url": "https://www.104.com.tw/jobs/search/?keyword=%E5%8F%B0%E7%A9%8D%E9%9B%BB%20AI",
            "notes": [
                "官方 SearchJobs 頁目前仍被 Cloudflare challenge 擋住，腳本抓取會回 403。",
            ],
        },
    ),
    (
        "聯發科",
        {
            "company_keywords": ["聯發科", "MediaTek"],
            "career_url": "https://careers.mediatek.com/zh-tw/jobs",
            "job104_url": "https://www.104.com.tw/jobs/search/?keyword=%E8%81%AF%E7%99%BC%E7%A7%91%20AI",
            "notes": [
                "官方 jobs 頁本身有 locale redirect 問題，但底層官方 tRPC API 可直接查詢。",
            ],
        },
    ),
    (
        "瑞昱",
        {
            "company_keywords": ["瑞昱", "Realtek"],
            "career_url": "https://www.realtek.com/",
            "job104_url": "https://www.104.com.tw/jobs/search/?keyword=%E7%91%9E%E6%98%B1%20AI",
            "notes": [
                "官方站可進，但未找到穩定、可直接解析的職缺列表頁。",
            ],
        },
    ),
    (
        "宏碁",
        {
            "company_keywords": ["宏碁", "Acer"],
            "career_url": "https://careers.acer.com/go/All-Jobs/7865610/?locale=en_US",
            "job104_url": "https://www.104.com.tw/jobs/search/?keyword=Acer%20AI",
            "notes": [
                "官方 SuccessFactors All Jobs 頁可直接解析職缺卡片。",
            ],
        },
    ),
    (
        "趨勢科技",
        {
            "company_keywords": ["趨勢科技", "Trend Micro"],
            "career_url": "https://trendmicro.wd3.myworkdayjobs.com/External",
            "job104_url": "https://www.104.com.tw/jobs/search/?keyword=%E8%B6%A8%E5%8B%A2%E7%A7%91%E6%8A%80%20AI",
            "notes": [
                "官方 Workday API 可直接查詢台北職缺。",
            ],
        },
    ),
    (
        "華碩",
        {
            "company_keywords": ["華碩", "ASUS"],
            "career_url": "https://careers.asus.com/",
            "job104_url": "https://www.104.com.tw/jobs/search/?keyword=ASUS%20AI",
            "notes": [
                "官方 careers 首頁可開，底層使用 Jobvite，但這次尚未補到台灣職缺的穩定解析規則。",
            ],
        },
    ),
    (
        "緯穎",
        {
            "company_keywords": ["緯穎", "Wiwynn"],
            "career_url": "https://www.wiwynn.com/careers",
            "job104_url": "https://www.104.com.tw/jobs/search/?keyword=Wiwynn%20AI",
            "notes": [
                "官方 careers 頁可開，目前偏品牌/人才頁，尚未補到可重複解析的職缺列表。",
            ],
        },
    ),
    (
        "台達電",
        {
            "company_keywords": ["台達電", "Delta"],
            "career_url": "https://www.deltaww.com/zh-TW/careers",
            "job104_url": "https://www.104.com.tw/jobs/search/?keyword=%E5%8F%B0%E9%81%94%E9%9B%BB%20AI",
            "notes": [
                "官方 careers 頁可開，但目前較像人才品牌入口，尚未補到穩定職缺清單。",
            ],
        },
    ),
    (
        "友達",
        {
            "company_keywords": ["友達", "AUO"],
            "career_url": "https://career.auo.com/job_list",
            "job104_url": "https://www.104.com.tw/jobs/search/?keyword=AUO%20AI",
            "notes": [
                "官方 job_list 與 GetJobList API 可直接查詢；這次已補到 AI / 全端 / 資料整合相關職缺。",
            ],
        },
    ),
    (
        "研華",
        {
            "company_keywords": ["研華", "Advantech"],
            "career_url": "https://www.advantech.com/zh-tw/careers",
            "job104_url": "https://www.104.com.tw/jobs/search/?keyword=Advantech%20AI",
            "notes": [
                "官方 careers 頁可開，且底層 Workday API 可直接查詢。",
            ],
        },
    ),
    (
        "光寶",
        {
            "company_keywords": ["光寶", "Liteon"],
            "career_url": "https://www.liteon.com/zh-tw/hroverview/hr-overview",
            "job104_url": "https://www.104.com.tw/jobs/search/?keyword=Liteon%20AI",
            "notes": [
                "官方人才頁可開，但目前主要是招募品牌與 104 入口，尚未補到穩定職缺 API。",
            ],
        },
    ),
    (
        "廣達",
        {
            "company_keywords": ["廣達", "Quanta"],
            "career_url": "https://www.quantatw.com/Quanta/chinese/04_careers/01_careers.aspx",
            "job104_url": "https://www.104.com.tw/jobs/search/?keyword=%E5%BB%A3%E9%81%94%20AI",
            "notes": [
                "官方招募頁目前會被 Radware bot challenge 攔下，暫時只能當官方入口。",
            ],
        },
    ),
    (
        "和碩",
        {
            "company_keywords": ["和碩", "Pegatron"],
            "career_url": "https://www.pegatroncorp.com/",
            "job104_url": "https://www.104.com.tw/jobs/search/?keyword=Pegatron%20AI",
            "notes": [
                "官方企業站可開，但尚未找到明確公開的職缺列表頁。",
            ],
        },
    ),
    (
        "英業達",
        {
            "company_keywords": ["英業達", "Inventec"],
            "career_url": "https://www.inventec.com/",
            "job104_url": "https://www.104.com.tw/jobs/search/?keyword=Inventec%20AI",
            "notes": [
                "官方企業站可開，首頁可見人才招募入口，但尚未補到穩定職缺列表。",
            ],
        },
    ),
    (
        "鴻海",
        {
            "company_keywords": ["鴻海", "Foxconn"],
            "career_url": "https://www.foxconn.com/zh-tw",
            "job104_url": "https://www.104.com.tw/jobs/search/?keyword=Foxconn%20AI",
            "notes": [
                "官方企業站可開，但尚未找到公開且穩定的職缺列表頁。",
            ],
        },
    ),
    (
        "Google",
        {
            "company_keywords": ["Google"],
            "career_url": "https://www.google.com/about/careers/applications/jobs/results/?location=Taiwan",
            "job104_url": "https://www.104.com.tw/jobs/search/?keyword=Google%20AI",
            "notes": [
                "Google Careers 台灣頁面可直接解析，這次輸出以官方職缺為主。",
            ],
        },
    ),
    (
        "NVIDIA",
        {
            "company_keywords": ["NVIDIA"],
            "career_url": "https://jobs.nvidia.com/careers?location=Taiwan",
            "job104_url": "https://www.104.com.tw/jobs/search/?keyword=NVIDIA%20AI",
            "notes": [
                "NVIDIA Taiwan careers 落地頁可開，但 job cards 為前端渲染，這次先保留官方搜尋入口。",
            ],
        },
    ),
])

OFFICIAL_FEEDS = [
    {
        "label": "Google Blog / AI",
        "url": "https://blog.google/technology/ai/rss/",
        "allow_domains": ["blog.google", "blog.google/technology/ai"],
        "require_any": ["ai", "gemini", "agent", "agents", "model", "reasoning", "multimodal", "inference"],
        "block_any": ["shopping", "thrift", "search tips"],
    },
    {
        "label": "NVIDIA Blog",
        "url": "https://blogs.nvidia.com/feed/",
        "allow_domains": ["blogs.nvidia.com"],
        "require_any": ["ai", "agent", "agents", "robot", "robotics", "inference", "omniverse", "blackwell", "gr00t", "llm"],
        "block_any": ["nvidia-life", "employee spotlight"],
    },
]

TREND_KEYWORDS = [
    "ai",
    "agent",
    "agents",
    "multimodal",
    "document",
    "ocr",
    "robot",
    "robotics",
    "inference",
    "serving",
    "infrastructure",
    "cloud",
    "platform",
    "edge",
    "on-device",
    "vision",
    "silicon",
    "reasoning",
    "enterprise",
]

JOB_FOCUS_KEYWORDS = [
    "ai",
    "machine learning",
    "software",
    "firmware",
    "hardware",
    "silicon",
    "cloud",
    "platform",
    "pixel",
    "automation",
    "reliability",
    "infrastructure",
    "verification",
    "systems",
    "test",
    "runtime",
    "embedded",
    "security",
    "cyber",
    "robotics",
]


def fetch_text(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
        return resp.read().decode("utf-8", "ignore")


def fetch_status(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            final_url = resp.geturl()
            return f"HTTP {resp.status}" + (f" -> {final_url}" if final_url != url else "")
    except HTTPError as e:
        return f"HTTP {e.code}"
    except URLError as e:
        return f"連線失敗: {e.reason}"
    except Exception as e:
        return f"失敗: {type(e).__name__}: {e}"


def company_status(name: str, info: dict) -> str:
    if name == "聯發科":
        return "官方 jobs HTML 會遇 locale 問題，改走官方 tRPC API；實際成功/失敗見下方職缺區塊"
    return fetch_status(info["career_url"])


def parse_google_taiwan_jobs() -> list[dict]:
    html_text = fetch_text(GOOGLE_BASE + "jobs/results/?location=Taiwan")
    pattern = re.compile(
        r'<h3 class="[^\"]*">([^<]+)</h3>.*?'
        r'<span class="[^\"]*">([^<]*Taiwan[^<]*)</span>.*?'
        r'href="([^\"]*jobs/results/[^\"]+location=Taiwan)"',
        re.S,
    )
    jobs = []
    seen = set()
    for raw_title, raw_location, raw_href in pattern.findall(html_text):
        title = html.unescape(raw_title).strip()
        if title.lower() == "locations":
            continue
        location = html.unescape(raw_location).strip()
        href = html.unescape(raw_href).strip()
        full_url = urllib.parse.urljoin(GOOGLE_BASE, href)
        key = (title, location, full_url)
        if key in seen:
            continue
        seen.add(key)
        jobs.append({"title": title, "location": location, "url": full_url})
    return jobs


def parse_mediatek_jobs(
    keywords: list[str],
    locations: Optional[list[str]] = None,
    limit: int = 6,
) -> Tuple[int, list[dict]]:
    payload = {
        "0": {
            "json": {
                "locales": "zh_TW",
                "page": 1,
                "jobQueryInfo": {"keywords": keywords, "relation": "AND"} if keywords else {},
                "filters": {
                    "categorys": [],
                    "workExperiences": [],
                    "locations": locations or [],
                    "programs": [],
                },
                "sortBy": "publishedDate",
                "order": "DESC",
                "limit": limit,
            }
        }
    }
    qs = urllib.parse.quote(json.dumps(payload, separators=(",", ":")))
    url = f"{MEDIATEK_TRPC}?batch=1&input={qs}"
    req = urllib.request.Request(
        url,
        headers={"User-Agent": UA, "Cookie": "NEXT_LOCALE=zh-tw", "Accept": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
        raw = json.loads(resp.read().decode("utf-8", "ignore"))
    data = raw[0]["result"]["data"]["json"]
    jobs = []
    for item in data.get("jobs", []):
        jobs.append(
            {
                "id": item.get("id", ""),
                "title": item.get("title", "").strip(),
                "location": item.get("properties", {}).get("location", {}).get("code", "地點未知"),
                "published_date": (item.get("publishedDate") or "")[:10],
                "url": f"https://careers.mediatek.com/zh-tw/jobs/{item.get('id', '')}",
            }
        )
    return data.get("pagination", {}).get("total_items", len(jobs)), jobs


def parse_acer_jobs(limit: int = 120) -> list[dict]:
    html_text = fetch_text(ACER_ALL_JOBS_URL)
    pattern = re.compile(
        r'data-url="(?P<path>/job/[^"]+)".*?'
        r'<a class="jobTitle-link[^"]*"[^>]*>\s*(?P<title>.*?)\s*</a>.*?'
        r'id="job-[^"]*-desktop-section-country-value">\s*(?P<country>.*?)\s*</div>.*?'
        r'id="job-[^"]*-desktop-section-customfield2-value">\s*(?P<city>.*?)\s*</div>',
        re.S,
    )
    jobs = []
    seen = set()
    for match in pattern.finditer(html_text):
        country = re.sub(r"\s+", " ", html.unescape(match.group("country"))).strip()
        if country != "TW":
            continue
        path = html.unescape(match.group("path")).strip()
        title = re.sub(r"\s+", " ", html.unescape(match.group("title"))).strip()
        city = re.sub(r"\s+", " ", html.unescape(match.group("city"))).strip()
        key = (title, city, path)
        if key in seen:
            continue
        seen.add(key)
        jobs.append(
            {
                "title": title,
                "location": city,
                "published_date": "",
                "url": urllib.parse.urljoin("https://careers.acer.com", path),
            }
        )
        if len(jobs) >= limit:
            break
    return jobs


def parse_trend_jobs(limit: int = 40) -> list[dict]:
    jobs = []
    offset = 0
    page_size = 20
    while len(jobs) < limit:
        payload = {"limit": page_size, "offset": offset, "searchText": "Taipei"}
        req = urllib.request.Request(
            TREND_WORKDAY_JOBS_URL,
            data=json.dumps(payload).encode(),
            method="POST",
            headers={
                "User-Agent": "Mozilla/5.0",
                "Content-Type": "application/json",
                "Accept": "application/json",
                "Origin": "https://trendmicro.wd3.myworkdayjobs.com",
                "Referer": "https://trendmicro.wd3.myworkdayjobs.com/External",
            },
        )
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            data = json.loads(resp.read().decode("utf-8", "ignore"))
        postings = data.get("jobPostings", [])
        if not postings:
            break
        for item in postings:
            location = item.get("locationsText", "")
            if "Taipei" not in location:
                continue
            jobs.append(
                {
                    "title": item.get("title", "").strip(),
                    "location": location.strip(),
                    "published_date": item.get("postedOn", "").replace("Posted ", ""),
                    "url": urllib.parse.urljoin("https://trendmicro.wd3.myworkdayjobs.com", item.get("externalPath", "")),
                }
            )
            if len(jobs) >= limit:
                break
        if len(postings) < page_size:
            break
        offset += page_size
    return jobs


def parse_advantech_jobs(limit: int = 40) -> list[dict]:
    jobs = []
    offset = 0
    page_size = 20
    while len(jobs) < limit:
        payload = {"limit": page_size, "offset": offset, "searchText": "Taiwan"}
        req = urllib.request.Request(
            ADVANTECH_WORKDAY_JOBS_URL,
            data=json.dumps(payload).encode(),
            method="POST",
            headers={
                "User-Agent": "Mozilla/5.0",
                "Content-Type": "application/json",
                "Accept": "application/json",
                "Origin": "https://advantech.wd3.myworkdayjobs.com",
                "Referer": "https://advantech.wd3.myworkdayjobs.com/zh-TW/External",
            },
        )
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            data = json.loads(resp.read().decode("utf-8", "ignore"))
        postings = data.get("jobPostings", [])
        if not postings:
            break
        for item in postings:
            location = item.get("locationsText", "")
            if not any(k in location for k in ["Taipei", "Linkou", "Kaohsiung", "Taoyuan", "Taiwan"]):
                continue
            jobs.append(
                {
                    "title": item.get("title", "").strip(),
                    "location": location.strip(),
                    "published_date": item.get("postedOn", "").replace("Posted ", ""),
                    "url": urllib.parse.urljoin("https://advantech.wd3.myworkdayjobs.com", item.get("externalPath", "")),
                }
            )
            if len(jobs) >= limit:
                break
        if len(postings) < page_size:
            break
        offset += page_size
    return jobs


def parse_auo_jobs(queries: list[str], limit_per_query: int = 5) -> list[dict]:
    jobs = []
    seen = set()
    for query in queries:
        payload = urllib.parse.urlencode(
            {"JobQuery": query, "JobType": "", "Site": "", "CurrentPage": "1"}
        ).encode()
        req = urllib.request.Request(
            AUO_JOB_LIST_API,
            data=payload,
            method="POST",
            headers={
                "User-Agent": UA,
                "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                "Accept": "application/json",
                "X-Requested-With": "XMLHttpRequest",
                "Origin": "https://career.auo.com",
                "Referer": "https://career.auo.com/job_list",
            },
        )
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            data = json.loads(resp.read().decode("utf-8", "ignore"))
        for item in data[:limit_per_query]:
            title = (item.get("JobTitle") or "").strip()
            if not title:
                continue
            location = (
                item.get("JobSite")
                or item.get("WorkPlaceArea")
                or item.get("WorkPlace")
                or "地點未知"
            ).strip()
            key = (title, location)
            if key in seen:
                continue
            seen.add(key)
            jobs.append(
                {
                    "title": title,
                    "location": location,
                    "published_date": "",
                    "url": "https://career.auo.com/job_list",
                }
            )
    return jobs


def score_keywords(text: str, keywords: list[str]) -> int:
    lower = text.lower()
    return sum(1 for kw in keywords if kw in lower)


def select_focus_jobs(jobs: list[dict], limit: int = 8) -> list[dict]:
    scored = []
    for job in jobs:
        blob = f"{job['title']} {job['location']}"
        score = score_keywords(blob, JOB_FOCUS_KEYWORDS)
        if score <= 0:
            continue
        scored.append((score, job))
    scored.sort(key=lambda item: (-item[0], item[1]["title"]))
    return [job for _, job in scored[:limit]]


def fetch_rss_items(url: str) -> list[dict]:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
        raw = resp.read()
    root = ET.fromstring(raw)
    items = []
    for item in root.findall(".//item"):
        title = (item.findtext("title") or "").strip()
        link = (item.findtext("link") or "").strip()
        desc = (item.findtext("description") or "").strip()
        pub_date = (item.findtext("pubDate") or "").strip()
        items.append(
            {
                "title": html.unescape(title),
                "link": html.unescape(link),
                "desc": html.unescape(re.sub(r"<[^>]+>", " ", desc)),
                "pub_date": pub_date,
            }
        )
    return items


def format_date(text: str) -> str:
    if not text:
        return "日期未知"
    try:
        dt = parsedate_to_datetime(text)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(TZ_TW).strftime("%Y-%m-%d")
    except Exception:
        return text


def pick_feed_signals(feed: dict, limit: int = 3) -> list[dict]:
    items = fetch_rss_items(feed["url"])
    kept = []
    required = [kw.lower() for kw in feed.get("require_any", [])]
    blocked = [kw.lower() for kw in feed.get("block_any", [])]
    for item in items:
        link_lower = item["link"].lower()
        text = f"{item['title']} {item['desc']} {item['link']}".lower()
        if feed.get("allow_domains") and not any(domain in link_lower for domain in feed["allow_domains"]):
            continue
        if required and not any(kw in text for kw in required):
            continue
        if blocked and any(kw in text for kw in blocked):
            continue
        score = score_keywords(text, TREND_KEYWORDS)
        if score <= 0:
            continue
        kept.append((score, item))
    kept.sort(key=lambda x: (-x[0], x[1]["title"]))
    return [item for _, item in kept[:limit]]


def summarize_focus_areas(jobs: list[dict], trend_items: list[dict]) -> list[str]:
    bullets = []
    titles = " | ".join(job["title"] for job in jobs)
    trends = " | ".join(item["title"] for item in trend_items)

    mapping = [
        ("AI infrastructure / 系統可靠性", ["ai infrastructure", "reliability", "system hardware", "ai-infrastructure"]),
        ("Cloud platform / release engineering", ["cloud", "platform", "release engineering"]),
        ("Silicon / verification / test", ["silicon", "verification", "test", "packaging", "cpu", "antenna"]),
        ("Firmware / embedded power", ["firmware", "power", "embedded", "runtime"]),
        ("Automation / TPM", ["automation", "program manager"]),
        ("Agent / multimodal / robotics", ["agent", "multimodal", "robot", "robotics"]),
        ("On-device / edge AI", ["pixel", "wearables", "edge", "on-device"]),
        ("Security / cyber platform", ["security", "cyber", "tippingpoint"]),
    ]

    combined = f"{titles} || {trends}".lower()
    for label, keywords in mapping:
        if any(keyword in combined for keyword in keywords):
            bullets.append(label)
    return bullets[:5]


print("# 大科技 AI / 職缺監測（官方來源優先版）\n")
print("產生時間（台灣）:", datetime.now(TZ_TW).strftime("%Y-%m-%d %H:%M"))
print()
print("說明：")
print("- 這版不再使用 Bing RSS 去猜 104 搜尋結果，避免產出字典、股市、下載站等雜訊。")
print("- 優先使用官方 careers 頁、官方部落格 / RSS，以及可直接驗證的台灣職缺頁。")
print("- 104 目前改成『人工複查入口』，保留連結但不把搜尋引擎結果當正式訊號。\n")

# 追蹤本次執行每個官方可解析來源(API/RSS/careers頁)實際成功/失敗，避免最後的品質判定寫死跟實際結果對不上
api_source_status: dict[str, bool] = {}

print("## 公司監測入口\n")
for name, info in COMPANIES.items():
    print(f"### {name}")
    print(f"- 官方職缺頁：{info['career_url']}")
    print(f"- 104 人工複查：{info['job104_url']}")
    print(f"- 官方職缺頁狀態：{company_status(name, info)}")
    for note in info.get("notes", []):
        print(f"- 備註：{note}")
    print()

print("## Google 台灣官方職缺（可直接解析）\n")
try:
    google_jobs = parse_google_taiwan_jobs()
    focus_jobs = select_focus_jobs(google_jobs, limit=8)
    print(f"- 官方頁面總職缺數（頁面解析到）：{len(google_jobs)}")
    print(f"- 焦點職缺（依 AI / software / hardware / platform 關鍵字篩選）：{len(focus_jobs)}")
    if not focus_jobs:
        print("- 這次沒有篩到焦點職缺")
    else:
        for idx, job in enumerate(focus_jobs, 1):
            print(f"- [{idx}] {job['title']} | {job['location']}")
            print(f"  {job['url']}")
    api_source_status["Google 台灣官方職缺"] = True
except Exception as e:
    google_jobs = []
    focus_jobs = []
    print(f"- 解析失敗：{type(e).__name__}: {e}")
    api_source_status["Google 台灣官方職缺"] = False
print()

print("## 聯發科官方職缺（tRPC API，可直接查詢）\n")
try:
    mediatek_ml_total, mediatek_ml_jobs = parse_mediatek_jobs(["機器學習"], locations=MEDIATEK_TW_LOCATIONS, limit=5)
    mediatek_runtime_total, mediatek_runtime_jobs = parse_mediatek_jobs(["AI Runtime"], locations=MEDIATEK_TW_LOCATIONS, limit=3)
    mediatek_llm_total, mediatek_llm_jobs = parse_mediatek_jobs(["LLM"], locations=MEDIATEK_TW_LOCATIONS, limit=3)
    print(f"- 台灣『機器學習』職缺總數：{mediatek_ml_total}")
    for idx, job in enumerate(mediatek_ml_jobs, 1):
        print(f"- [ML {idx}] {job['title']} | {job['location']} | {job['published_date']}")
        print(f"  {job['url']}")
    print(f"- 台灣『AI Runtime』職缺總數：{mediatek_runtime_total}")
    for idx, job in enumerate(mediatek_runtime_jobs, 1):
        print(f"- [Runtime {idx}] {job['title']} | {job['location']} | {job['published_date']}")
        print(f"  {job['url']}")
    print(f"- 台灣『LLM』職缺總數：{mediatek_llm_total}")
    for idx, job in enumerate(mediatek_llm_jobs, 1):
        print(f"- [LLM {idx}] {job['title']} | {job['location']} | {job['published_date']}")
        print(f"  {job['url']}")
    api_source_status["聯發科官方 tRPC 職缺 API"] = True
except Exception as e:
    mediatek_ml_jobs = []
    mediatek_runtime_jobs = []
    mediatek_llm_jobs = []
    print(f"- 解析失敗：{type(e).__name__}: {e}")
    api_source_status["聯發科官方 tRPC 職缺 API"] = False
print()

print("## 宏碁官方職缺（SuccessFactors，可直接解析）\n")
try:
    acer_jobs = parse_acer_jobs(limit=120)
    acer_focus_jobs = select_focus_jobs(acer_jobs, limit=8)
    print(f"- 台灣官方職缺總數（頁面解析到）：{len(acer_jobs)}")
    print(f"- 焦點職缺數：{len(acer_focus_jobs)}")
    for idx, job in enumerate(acer_focus_jobs, 1):
        print(f"- [{idx}] {job['title']} | {job['location']}")
        print(f"  {job['url']}")
    api_source_status["宏碁官方 All Jobs 頁"] = True
except Exception as e:
    acer_jobs = []
    acer_focus_jobs = []
    print(f"- 解析失敗：{type(e).__name__}: {e}")
    api_source_status["宏碁官方 All Jobs 頁"] = False
print()

print("## 趨勢科技官方職缺（Workday API，可直接查詢）\n")
try:
    trend_jobs = parse_trend_jobs(limit=80)
    trend_focus_jobs = select_focus_jobs(trend_jobs, limit=8)
    print(f"- 台北官方職缺總數（API 篩到）：{len(trend_jobs)}")
    print(f"- 焦點職缺數：{len(trend_focus_jobs)}")
    for idx, job in enumerate(trend_focus_jobs, 1):
        print(f"- [{idx}] {job['title']} | {job['location']} | {job['published_date']}")
        print(f"  {job['url']}")
    api_source_status["趨勢科技官方 Workday API"] = True
except Exception as e:
    trend_jobs = []
    trend_focus_jobs = []
    print(f"- 解析失敗：{type(e).__name__}: {e}")
    api_source_status["趨勢科技官方 Workday API"] = False
print()

print("## 研華官方職缺（Workday API，可直接查詢）\n")
try:
    advantech_jobs = parse_advantech_jobs(limit=80)
    advantech_focus_jobs = select_focus_jobs(advantech_jobs, limit=8)
    print(f"- 台灣官方職缺總數（API 篩到）：{len(advantech_jobs)}")
    print(f"- 焦點職缺數：{len(advantech_focus_jobs)}")
    for idx, job in enumerate(advantech_focus_jobs, 1):
        print(f"- [{idx}] {job['title']} | {job['location']} | {job['published_date']}")
        print(f"  {job['url']}")
    api_source_status["研華官方 Workday API"] = True
except Exception as e:
    advantech_jobs = []
    advantech_focus_jobs = []
    print(f"- 解析失敗：{type(e).__name__}: {e}")
    api_source_status["研華官方 Workday API"] = False
print()

print("## 友達官方職缺（job_list API，可直接查詢）\n")
try:
    auo_jobs = parse_auo_jobs(["AI", "全端", "資料"], limit_per_query=4)
    auo_focus_jobs = select_focus_jobs(auo_jobs, limit=8)
    print(f"- 官方查詢命中職缺數（去重後）：{len(auo_jobs)}")
    print(f"- 焦點職缺數：{len(auo_focus_jobs)}")
    for idx, job in enumerate(auo_focus_jobs, 1):
        print(f"- [{idx}] {job['title']} | {job['location']}")
        print(f"  {job['url']}")
    api_source_status["友達官方 job_list API"] = True
except Exception as e:
    auo_jobs = []
    auo_focus_jobs = []
    print(f"- 解析失敗：{type(e).__name__}: {e}")
    api_source_status["友達官方 job_list API"] = False
print()

print("## 官方技術 / 產業訊號（RSS）\n")
all_trend_items = []
for feed in OFFICIAL_FEEDS:
    print(f"### {feed['label']}")
    try:
        items = pick_feed_signals(feed, limit=3)
        if not items:
            print("- 無符合關鍵字的官方訊號")
        else:
            all_trend_items.extend(items)
            for idx, item in enumerate(items, 1):
                print(f"- [{idx}] {item['title']} ({format_date(item['pub_date'])})")
                print(f"  {item['link']}")
        api_source_status[f"{feed['label']}（RSS）"] = True
    except Exception as e:
        print(f"- 取得失敗：{type(e).__name__}: {e}")
        api_source_status[f"{feed['label']}（RSS）"] = False
    print()

print("## 本週可關注的學習主題\n")
all_focus_jobs = focus_jobs + mediatek_ml_jobs + mediatek_runtime_jobs + mediatek_llm_jobs + acer_focus_jobs + trend_focus_jobs + advantech_focus_jobs + auo_focus_jobs
focus_areas = summarize_focus_areas(all_focus_jobs, all_trend_items)
if not focus_areas:
    print("- 這次訊號不足，先以官方職缺頁人工複查為主。")
else:
    for idx, area in enumerate(focus_areas, 1):
        print(f"- [{idx}] {area}")
print()

print("## 我對這版資料品質的判定\n")
succeeded = [name for name, ok in api_source_status.items() if ok]
failed = [name for name, ok in api_source_status.items() if not ok]
if succeeded:
    print(f"- 本次執行可直接信任（成功讀取來源，不代表當次一定有符合關鍵字的職缺/訊號）：{'、'.join(succeeded)}。")
if failed:
    print(f"- 本次執行失敗，暫時降級成人工複查（可能是對方站點暫時性問題，不代表這個來源永久不能用）：{'、'.join(failed)}。")
print("- 僅供人工入口（本腳本未串接官方API/RSS，結構性只能人工查）：104 搜尋連結、NVIDIA Taiwan careers 落地頁、台積電 / 瑞昱 / 華碩 / 緯穎 / 台達電 / 光寶 / 廣達 / 和碩 / 英業達 / 鴻海 官方入口。")
print("- 不再輸出未經過濾的搜尋引擎結果，避免把雜訊誤判成職缺訊號。")
