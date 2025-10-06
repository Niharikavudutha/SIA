import requests
from bs4 import BeautifulSoup
from datetime import datetime
import urllib.parse

def get_todays_observances():
    today = datetime.now()
    month_day = f"{today.strftime('%B')}_{today.day}"
    wiki_url = f"https://en.wikipedia.org/wiki/{month_day}"

    try:
        page = requests.get(wiki_url, timeout=10)
        soup = BeautifulSoup(page.content, "html.parser")
    except Exception:
        return []

    observances = []
    for header in soup.find_all(["h2", "h3"]):
        if 'Observances' in header.text or 'Holidays' in header.text:
            ul = header.find_next("ul")
            if ul:
                items = [li.get_text().split("\n")[0] for li in ul.find_all("li")]
                observances = items
            break

    detailed_obs = []
    for obs in observances:
        title = obs.split("(")[0].strip()
        encoded_title = urllib.parse.quote(title.replace(" ", "_"))
        page_url = f"https://en.wikipedia.org/wiki/{encoded_title}"

        try:
            obs_page = requests.get(page_url, timeout=8)
            obs_soup = BeautifulSoup(obs_page.content, "html.parser")

            # Get main image
            image_url = None
            infobox = obs_soup.find("table", class_="infobox")
            if infobox:
                img = infobox.find("img")
                if img:
                    image_url = img.get("src")
                    if image_url and image_url.startswith("//"):
                        image_url = "https:" + image_url

            # Get first paragraph summary
            paragraphs = obs_soup.find_all("p")
            summary = ""
            for p in paragraphs:
                text = p.get_text().strip()
                if len(text) > 100:
                    summary = text
                    break

            detailed_obs.append({
                "name": title,
                "image": image_url if image_url else None,
                "link": page_url,
                "summary": summary,
            })

        except Exception:
            detailed_obs.append({
                "name": title,
                "image": None,
                "link": page_url,
                "summary": "Summary not available.",
            })

    # Sort alphabetically
    detailed_obs.sort(key=lambda x: x["name"].lower())
    return detailed_obs