# 네이버 블로그 RSS를 읽어서 files/blog.json 으로 저장하는 스크립트
# GitHub Actions(.github/workflows/blog-rss.yml)가 하루 여러 번 자동 실행합니다.
import json, re, html, urllib.request, xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime

BLOG_ID = "chjun071900"          # 네이버 블로그 아이디
MAX_POSTS = 6                     # 홈페이지에 보여줄 최대 글 수
# 특정 카테고리 글만 보여주고 싶으면 이름을 넣으세요. 비워두면 전체 글을 보여줍니다.
# 예) ALLOW_CATEGORIES = ["알뜰차저 소개", "i-SENSOR 화재감지"]
ALLOW_CATEGORIES = []

url = f"https://rss.blog.naver.com/{BLOG_ID}.xml"
req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
root = ET.fromstring(urllib.request.urlopen(req, timeout=30).read())

posts = []
for item in root.iter("item"):
    cat = (item.findtext("category") or "").strip()
    if ALLOW_CATEGORIES and cat not in ALLOW_CATEGORIES:
        continue
    raw = item.findtext("description") or ""
    # 본문 첫 이미지를 썸네일로 사용
    m = re.search(r'<img[^>]+src="([^"]+)"', raw)
    thumb = html.unescape(m.group(1)) if m else ""
    # 태그 제거 후 요약문 만들기
    text = re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", raw))).strip()
    link = (item.findtext("link") or "").split("?")[0]
    try:
        date = parsedate_to_datetime(item.findtext("pubDate")).strftime("%Y.%m.%d")
    except Exception:
        date = ""
    posts.append({
        "title": html.unescape((item.findtext("title") or "").strip()),
        "link": link,
        "date": date,
        "category": cat,
        "summary": text[:90] + ("…" if len(text) > 90 else ""),
        "thumb": thumb,
    })
    if len(posts) >= MAX_POSTS:
        break

with open("files/blog.json", "w", encoding="utf-8") as f:
    json.dump({"blog": f"https://blog.naver.com/{BLOG_ID}", "posts": posts}, f, ensure_ascii=False, indent=2)
print(f"{len(posts)}개 글 저장 완료")
