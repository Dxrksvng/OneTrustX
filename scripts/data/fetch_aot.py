import re
from urllib.parse import quote
from common import fetch


def main():
    url = (
        "https://corporatestrategy.airportthai.co.th/ats/"
        + quote("รายงานปริมาณการขนส่ง")
        + "/"
    )
    p = fetch(
        "aot", url, "reports.html", "TH", "Archive", "Official AOT published reports"
    )
    if p:
        links = re.findall(r"(?:href|src)=[\"\x27]([^\"\x27]+)", p.read_text())
        print(
            [
                x
                for x in links
                if any(t in x for t in ["pdf", "sharepoint", "xls", "drive.google"])
            ]
        )


if __name__ == "__main__":
    main()
