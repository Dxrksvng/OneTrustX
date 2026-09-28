from common import fetch


def main():
    return fetch(
        "caat",
        "https://www.caat.or.th/wp-content/uploads/2025/07/Air-Transport-Daily-23-Apr-25.xlsx",
        "daily-2025-04-23.xlsx",
        "TH",
        "2025-04-23",
        "CAAT preliminary public aviation statistics; source attribution required",
    )


if __name__ == "__main__":
    main()
