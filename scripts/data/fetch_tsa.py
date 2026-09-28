from common import fetch

if __name__ == "__main__":
    fetch(
        "tsa",
        "https://www.tsa.gov/travel/passenger-volumes",
        "passenger-volumes.html",
        "US national",
        "Published historical dates",
        "TSA public passenger volumes; never airport-specific",
    )
