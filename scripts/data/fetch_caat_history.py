import sys, re, time
from common import fetch

for page in [3, 6, 9, 12, 15, 18]:
    p = fetch(
        "caat",
        f"https://www.caat.or.th/publication-category/air-tran-stat-daily/page/{page}/",
        f"archive-{page}.html",
        "TH",
        "Historical archive",
        "CAAT public statistics",
    )
    if not p:
        continue
    urls = list(
        dict.fromkeys(
            re.findall(r"https://www.caat.or.th/publication/\d+/", p.read_text())
        )
    )
    if not urls:
        continue
    q = fetch(
        "caat",
        urls[0],
        f"publication-{page}.html",
        "TH",
        "Historical archive",
        "CAAT public statistics",
    )
    if not q:
        continue
    xlsx = re.findall(r"https://[^\"\s<>]+\.xlsx", q.read_text())
    if xlsx:
        fetch(
            "caat",
            xlsx[0],
            f"history-{page}.xlsx",
            "TH",
            "Dates in workbook",
            "CAAT preliminary public statistics",
        )
    time.sleep(1)
