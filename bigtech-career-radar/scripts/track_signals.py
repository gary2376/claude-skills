#!/usr/bin/env python3
"""
通用「官方來源優先」職缺訊號雷達 —— 由 config.json 描述監控哪些機構、用哪種解析方式。
預設吃 config.ai-taiwan.json（跟原本大公司AI/台灣版本行為完全一致），
也可以指定別的產業設定檔：
    python3 track_signals.py --config config.psychologist-tw.json
"""
import argparse
import html
import json
import os
import re
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone, timedelta
from email.utils import parsedate_to_datetime
from typing import Optional
from urllib.error import HTTPError, URLError

UA = "Mozilla/5.0 (compatible; BigTechCareerRadar/1.0)"
TIMEOUT = 30
TZ_TW = timezone(timedelta(hours=8))
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


def fetch_text(url: str, method: str = "GET", data: Optional[bytes] = None, headers: Optional[dict] = None) -> str:
    req = urllib.request.Request(url, data=data, method=method, headers=headers or {"User-Agent": UA})
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


def strip_head(page_html: str) -> str:
    """只留<body>內容，避免<head>的meta description(常是截斷過的摘要)被誤判成正文欄位。"""
    m = re.search(r"<body[^>]*>(.*)</body>", page_html, re.S)
    return m.group(1) if m else page_html


def html_to_text(page_html: str) -> str:
    text = re.sub(r"<[^>]+>", " ", page_html)
    text = html.unescape(text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


# ============================================================
# 通用解析器 1：Workday職缺API —— 任何用Workday當徵才系統的公司都能套，
# 只要換tenant名稱，橫跨產業(零售/金融/製造/科技皆有公司用Workday)。
# ============================================================
def parse_workday_jobs(tenant: str, search_text: str = "", location_filters: Optional[list] = None, limit: int = 40) -> list:
    base = f"https://{tenant}.wd3.myworkdayjobs.com"
    jobs_url = f"{base}/wday/cxs/{tenant}/External/jobs"
    jobs = []
    offset = 0
    page_size = 20
    while len(jobs) < limit:
        payload = {"limit": page_size, "offset": offset, "searchText": search_text}
        raw = fetch_text(
            jobs_url,
            method="POST",
            data=json.dumps(payload).encode(),
            headers={
                "User-Agent": "Mozilla/5.0",
                "Content-Type": "application/json",
                "Accept": "application/json",
                "Origin": base,
                "Referer": f"{base}/External",
            },
        )
        data = json.loads(raw)
        postings = data.get("jobPostings", [])
        if not postings:
            break
        for item in postings:
            location = item.get("locationsText", "")
            if location_filters and not any(k in location for k in location_filters):
                continue
            jobs.append(
                {
                    "title": item.get("title", "").strip(),
                    "location": location.strip(),
                    "published_date": item.get("postedOn", "").replace("Posted ", ""),
                    "url": urllib.parse.urljoin(base, item.get("externalPath", "")),
                }
            )
            if len(jobs) >= limit:
                break
        if len(postings) < page_size:
            break
        offset += page_size
    return jobs


# ============================================================
# 通用解析器 2：WordPress分類頁 —— 很多產業公會/學會的「徵才專區」
# 是WordPress架的，entry-title是WP標準class，不限定哪個產業。
# ============================================================
def parse_wordpress_category(category_url: str, limit: int = 10) -> list:
    page_html = fetch_text(category_url)
    pattern = re.compile(r'<h2 class="[^"]*entry-title[^"]*"><a href="([^"]+)"[^>]*>([^<]+)</a>', re.S)
    entries = []
    for link, title in pattern.findall(page_html):
        entries.append({"title": html.unescape(title).strip(), "url": html.unescape(link).strip()})
        if len(entries) >= limit:
            break
    return entries


# ============================================================
# 通用解析器 3：中文職缺常見欄位標籤抽取 —— 不管網站怎麼刻，
# 職缺內容常見「機關/公司名稱、職稱、資格條件、工作內容、工作地點」
# 這類標籤，用別名比對抓出每個欄位內容，不用每個網站各寫一支正則。
# ============================================================
FIELD_ALIASES = {
    "org": ["機關名稱", "公司名稱"],
    "title": ["職稱與名額", "職務名稱", "職稱"],
    "qualifications": ["資格條件／需具備專長", "資格條件/需具備專長", "資格條件", "二、條件要求", "條件要求", "需求條件"],
    "salary": ["薪資", "工作待遇", "待遇"],
    "duties": ["工作項目", "一、工作內容", "工作內容"],
    "location": ["三、工作地點", "工作地點"],
}
# 只用來當「前一個欄位」的結束邊界，本身不當成獨立欄位輸出——
# 否則像「工作地點」這種欄位後面沒有下一個已知標籤時，會一路把
# 申請程序/錄取標準/聯絡資訊這些不相關內容也吃進去。
FIELD_BOUNDARY_ONLY = ["申請程序", "錄取標準", "截止日期", "預計到職日", "其他注意事項", "聯絡資訊", "投遞履歷", "福利制度"]


def extract_labeled_fields(text: str, max_field_len: int = 300) -> dict:
    hits = []  # (position, end_of_label, group_or_None)  group=None代表只當邊界用
    seen_groups = set()
    for group, aliases in FIELD_ALIASES.items():
        for alias in aliases:
            idx = text.find(alias)
            if idx >= 0 and group not in seen_groups:
                hits.append((idx, idx + len(alias), group))
                seen_groups.add(group)
                break
    for alias in FIELD_BOUNDARY_ONLY:
        idx = text.find(alias)
        if idx >= 0:
            hits.append((idx, idx + len(alias), None))
    hits.sort()
    result = {}
    for i, (start, end, group) in enumerate(hits):
        if group is None:
            continue
        next_start = hits[i + 1][0] if i + 1 < len(hits) else min(len(text), end + max_field_len)
        next_start = min(next_start, end + max_field_len)
        value = text[end:next_start].strip(" :：\n")
        result[group] = value[:max_field_len]
    return result


def parse_association_postings(category_url: str, limit: int = 10) -> list:
    """WordPress分類頁(公會/學會徵才專區常見)：先列出文章，再逐篇讀取欄位化內容。"""
    entries = parse_wordpress_category(category_url, limit=limit)
    jobs = []
    detail_failures = 0
    for entry in entries:
        job = {"title": entry["title"], "url": entry["url"]}
        try:
            body_html = strip_head(fetch_text(entry["url"]))
            text = html_to_text(body_html)
            fields = extract_labeled_fields(text)
            fields.pop("title", None)  # 保留WordPress文章標題(通常含機構名，比內文的職稱欄位完整)，不被蓋掉
            job.update(fields)
        except Exception:
            detail_failures += 1
        jobs.append(job)
    if entries and detail_failures == len(entries):
        # 分類頁本身讀得到，但每一篇detail page都抓失敗——不該讓呼叫端誤判成「這個來源成功」
        raise RuntimeError(f"分類頁抓到{len(entries)}篇文章，但逐篇讀取內容全部失敗")
    return jobs


def parse_labeled_page_jobs(url: str, block_marker: str = "職缺", limit: int = 10) -> list:
    """單一頁面裡重複出現「職缺」這類分隔標記、每段各自列職缺內容的公司官網常見格式。"""
    body_html = strip_head(fetch_text(url))
    text = html_to_text(body_html)
    blocks = text.split(block_marker)[1:]
    jobs = []
    for block in blocks:
        title_match = re.match(r"\s*([^\n]{2,40}?)(?:[一二三]、|$)", block)
        title = title_match.group(1).strip() if title_match else block[:30].strip()
        fields = extract_labeled_fields(block)
        if len(fields) < 2:
            continue  # 欄位標籤命中不到2個，多半是選單/分類標籤這類雜訊，不是真職缺
        job = {"title": title, "url": url}
        job.update(fields)
        jobs.append(job)
        if len(jobs) >= limit:
            break
    return jobs


# ============================================================
# 公司專屬解析器（內建範例）：這些是特定公司自己內部系統的串接方式，
# 不是通用平台，換一家公司不一定能直接套，但示範怎麼寫一支新的。
# ============================================================
def parse_google_careers_jobs(base_url: str, location: str = "Taiwan", limit: int = 40) -> list:
    page_html = fetch_text(f"{base_url}jobs/results/?location={urllib.parse.quote(location)}")
    pattern = re.compile(
        r'<h3 class="[^"]*">([^<]+)</h3>.*?'
        r'<span class="[^"]*">([^<]*' + re.escape(location) + r'[^<]*)</span>.*?'
        r'href="([^"]*jobs/results/[^"]+location=' + re.escape(location) + r')"',
        re.S,
    )
    jobs = []
    seen = set()
    for raw_title, raw_location, raw_href in pattern.findall(page_html):
        title = html.unescape(raw_title).strip()
        if title.lower() == "locations":
            continue
        loc = html.unescape(raw_location).strip()
        full_url = urllib.parse.urljoin(base_url, html.unescape(raw_href).strip())
        key = (title, loc, full_url)
        if key in seen:
            continue
        seen.add(key)
        jobs.append({"title": title, "location": loc, "url": full_url})
        if len(jobs) >= limit:
            break
    return jobs


def parse_mediatek_jobs(trpc_url: str, queries: list, locations: Optional[list] = None) -> list:
    """queries: [{"label": "機器學習", "keywords": ["機器學習"], "limit": 5}, ...]"""
    all_jobs = []
    for q in queries:
        payload = {
            "0": {
                "json": {
                    "locales": "zh_TW",
                    "page": 1,
                    "jobQueryInfo": {"keywords": q["keywords"], "relation": "AND"} if q.get("keywords") else {},
                    "filters": {
                        "categorys": [],
                        "workExperiences": [],
                        "locations": locations or [],
                        "programs": [],
                    },
                    "sortBy": "publishedDate",
                    "order": "DESC",
                    "limit": q.get("limit", 6),
                }
            }
        }
        qs = urllib.parse.quote(json.dumps(payload, separators=(",", ":")))
        raw = fetch_text(
            f"{trpc_url}?batch=1&input={qs}",
            headers={"User-Agent": UA, "Cookie": "NEXT_LOCALE=zh-tw", "Accept": "application/json"},
        )
        data = json.loads(raw)[0]["result"]["data"]["json"]
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
        all_jobs.append({"label": q["label"], "total": data.get("pagination", {}).get("total_items", len(jobs)), "jobs": jobs})
    return all_jobs


def parse_acer_style_jobs(all_jobs_url: str, country_code: str = "TW", limit: int = 120) -> list:
    """Acer的SuccessFactors All Jobs頁結構；其他SuccessFactors站台版型可能不同，需要重新驗證。"""
    page_html = fetch_text(all_jobs_url)
    pattern = re.compile(
        r'data-url="(?P<path>/job/[^"]+)".*?'
        r'<a class="jobTitle-link[^"]*"[^>]*>\s*(?P<title>.*?)\s*</a>.*?'
        r'id="job-[^"]*-desktop-section-country-value">\s*(?P<country>.*?)\s*</div>.*?'
        r'id="job-[^"]*-desktop-section-customfield2-value">\s*(?P<city>.*?)\s*</div>',
        re.S,
    )
    jobs = []
    seen = set()
    base = re.match(r"https?://[^/]+", all_jobs_url).group(0)
    for match in pattern.finditer(page_html):
        country = re.sub(r"\s+", " ", html.unescape(match.group("country"))).strip()
        if country != country_code:
            continue
        path = html.unescape(match.group("path")).strip()
        title = re.sub(r"\s+", " ", html.unescape(match.group("title"))).strip()
        city = re.sub(r"\s+", " ", html.unescape(match.group("city"))).strip()
        key = (title, city, path)
        if key in seen:
            continue
        seen.add(key)
        jobs.append({"title": title, "location": city, "published_date": "", "url": urllib.parse.urljoin(base, path)})
        if len(jobs) >= limit:
            break
    return jobs


def parse_auo_style_jobs(api_url: str, queries: list, limit_per_query: int = 5) -> list:
    """AUO自己的job_list/GetJobList API；其他公司若用相同系統可套，否則是專屬範例。"""
    base = re.match(r"https?://[^/]+", api_url).group(0)
    jobs = []
    seen = set()
    for query in queries:
        payload = urllib.parse.urlencode({"JobQuery": query, "JobType": "", "Site": "", "CurrentPage": "1"}).encode()
        raw = fetch_text(
            api_url,
            method="POST",
            data=payload,
            headers={
                "User-Agent": UA,
                "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                "Accept": "application/json",
                "X-Requested-With": "XMLHttpRequest",
                "Origin": base,
                "Referer": f"{base}/job_list",
            },
        )
        data = json.loads(raw)
        for item in data[:limit_per_query]:
            title = (item.get("JobTitle") or "").strip()
            if not title:
                continue
            location = (item.get("JobSite") or item.get("WorkPlaceArea") or item.get("WorkPlace") or "地點未知").strip()
            key = (title, location)
            if key in seen:
                continue
            seen.add(key)
            jobs.append({"title": title, "location": location, "published_date": "", "url": f"{base}/job_list"})
    return jobs


def score_keywords(text: str, keywords: list) -> int:
    lower = text.lower()
    return sum(1 for kw in keywords if kw.lower() in lower)


def select_focus_jobs(jobs: list, keywords: list, limit: int = 8) -> list:
    scored = []
    for job in jobs:
        blob = f"{job.get('title','')} {job.get('location','')} {job.get('qualifications','')} {job.get('duties','')}"
        score = score_keywords(blob, keywords)
        if score <= 0:
            continue
        scored.append((score, job))
    scored.sort(key=lambda item: (-item[0], item[1].get("title", "")))
    return [job for _, job in scored[:limit]]


def fetch_rss_items(url: str) -> list:
    raw = fetch_text(url)
    root = ET.fromstring(raw)
    items = []
    for item in root.findall(".//item"):
        items.append(
            {
                "title": html.unescape((item.findtext("title") or "").strip()),
                "link": html.unescape((item.findtext("link") or "").strip()),
                "desc": html.unescape(re.sub(r"<[^>]+>", " ", (item.findtext("description") or "").strip())),
                "pub_date": (item.findtext("pubDate") or "").strip(),
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


def pick_feed_signals(feed: dict, trend_keywords: list, limit: int = 3) -> list:
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
        score = score_keywords(text, trend_keywords)
        if score <= 0:
            continue
        kept.append((score, item))
    kept.sort(key=lambda x: (-x[0], x[1]["title"]))
    return [item for _, item in kept[:limit]]


ADAPTERS = {
    "workday": lambda p: parse_workday_jobs(**p),
    "wordpress_category": lambda p: parse_association_postings(**p),
    "labeled_html_page": lambda p: parse_labeled_page_jobs(**p),
    "google_careers": lambda p: parse_google_careers_jobs(**p),
    "mediatek_trpc": lambda p: parse_mediatek_jobs(**p),
    "acer_successfactors": lambda p: parse_acer_style_jobs(**p),
    "auo_joblist": lambda p: parse_auo_style_jobs(**p),
}


def load_config(path: str) -> dict:
    if not os.path.isabs(path):
        candidate = os.path.join(SCRIPT_DIR, path)
        path = candidate if os.path.exists(candidate) else path
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def print_company_entries(companies: list):
    print("## 公司監測入口\n")
    for c in companies:
        print(f"### {c['name']}")
        print(f"- 官方職缺頁：{c.get('career_url', '(未提供)')}")
        if c.get("job104_url"):
            print(f"- 104 人工複查：{c['job104_url']}")
        if c.get("adapter") == "manual":
            print(f"- 官方職缺頁狀態：{fetch_status(c['career_url']) if c.get('career_url') else '未設定自動解析器'}")
        else:
            print(f"- 解析方式：{c.get('adapter')}（實際成功/失敗見下方職缺區塊）")
        for note in c.get("notes", []):
            print(f"- 備註：{note}")
        print()


def run_adapters(companies: list, job_focus_keywords: list) -> tuple:
    api_source_status = {}
    all_focus_jobs = []
    for c in companies:
        adapter_name = c.get("adapter")
        if not adapter_name or adapter_name == "manual":
            continue
        label = f"{c['name']}官方職缺（{adapter_name}）"
        if adapter_name not in ADAPTERS:
            print(f"## {label}\n")
            print(f"- 設定檔錯誤：adapter名稱『{adapter_name}』不存在，請檢查config.json有沒有打錯字。\n")
            api_source_status[label] = False
            continue
        print(f"## {label}\n")
        try:
            result = ADAPTERS[adapter_name](c.get("adapter_params", {}))
            if adapter_name == "mediatek_trpc":
                focus_jobs = []
                for block in result:
                    print(f"- 『{block['label']}』職缺總數：{block['total']}")
                    for idx, job in enumerate(block["jobs"], 1):
                        print(f"- [{block['label']} {idx}] {job['title']} | {job['location']} | {job['published_date']}")
                        print(f"  {job['url']}")
                    focus_jobs.extend(block["jobs"])
            else:
                focus_jobs = select_focus_jobs(result, job_focus_keywords, limit=8)
                print(f"- 解析到職缺/項目數：{len(result)}")
                print(f"- 焦點項目數：{len(focus_jobs)}")
                for idx, job in enumerate(focus_jobs, 1):
                    print(f"- [{idx}] {job['title']} | {job.get('location','')}")
                    print(f"  {job['url']}")
                    if job.get("qualifications"):
                        print(f"  資格條件：{job['qualifications'][:200]}")
            all_focus_jobs.extend(focus_jobs)
            api_source_status[label] = True
        except Exception as e:
            print(f"- 解析失敗：{type(e).__name__}: {e}")
            api_source_status[label] = False
        print()
    return api_source_status, all_focus_jobs


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="config.ai-taiwan.json", help="設定檔路徑，預設用內建AI/台灣範例")
    args = parser.parse_args()
    config = load_config(args.config)

    print(f"# {config.get('title', '職缺訊號雷達')}\n")
    print("產生時間（台灣）:", datetime.now(TZ_TW).strftime("%Y-%m-%d %H:%M"))
    print()
    for line in config.get("intro_notes", []):
        print(f"- {line}")
    print()

    companies = config.get("companies", [])
    print_company_entries(companies)

    job_focus_keywords = config.get("job_focus_keywords", [])
    api_source_status, all_focus_jobs = run_adapters(companies, job_focus_keywords)

    all_trend_items = []
    feeds = config.get("official_feeds", [])
    if feeds:
        print("## 官方技術 / 產業訊號（RSS）\n")
        trend_keywords = config.get("trend_keywords", [])
        for feed in feeds:
            print(f"### {feed['label']}")
            try:
                items = pick_feed_signals(feed, trend_keywords, limit=3)
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

    print("## 本次可關注方向\n")
    buckets = config.get("focus_area_buckets", [])
    combined_text = " || ".join(job.get("title", "") for job in all_focus_jobs) + " || " + " ".join(
        item["title"] for item in all_trend_items
    )
    combined_text_lower = combined_text.lower()
    focus_areas = []
    if buckets:
        for label, keywords in buckets:
            if any(kw.lower() in combined_text_lower for kw in keywords):
                focus_areas.append(label)
    else:
        counts = {}
        for kw in job_focus_keywords:
            c = combined_text_lower.count(kw.lower())
            if c > 0:
                counts[kw] = c
        focus_areas = [f"{kw}（出現{c}次）" for kw, c in sorted(counts.items(), key=lambda x: -x[1])]
    if not focus_areas:
        print("- 這次訊號不足，先以官方職缺頁人工複查為主。")
    else:
        for idx, area in enumerate(focus_areas[:8], 1):
            print(f"- [{idx}] {area}")
    print()

    print("## 我對這版資料品質的判定\n")
    succeeded = [name for name, ok in api_source_status.items() if ok]
    failed = [name for name, ok in api_source_status.items() if not ok]
    manual_only = [c["name"] for c in companies if c.get("adapter") in (None, "manual")]
    if succeeded:
        print(f"- 本次執行可直接信任（成功讀取來源，不代表當次一定有符合關鍵字的職缺/訊號）：{'、'.join(succeeded)}。")
    if failed:
        print(f"- 本次執行失敗，暫時降級成人工複查（可能是對方站點暫時性問題，不代表這個來源永久不能用）：{'、'.join(failed)}。")
    if manual_only:
        print(f"- 僅供人工入口（本設定檔未串接官方API/RSS，結構性只能人工查）：{'、'.join(manual_only)}。")
    print("- 不再輸出未經過濾的搜尋引擎結果，避免把雜訊誤判成職缺訊號。")


if __name__ == "__main__":
    main()
