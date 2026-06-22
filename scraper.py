import requests
from bs4 import BeautifulSoup

url = "https://www.revcomps.com/wp-admin/admin-ajax.php"

data = {
    "action": "rcfs_get_products",
    "nonce": "d5c6da7db1",
    "term_id": "10607"
}

r = requests.post(url, data=data)

html = r.json()["data"]["html"]

soup = BeautifulSoup(html, "html.parser")

cards = soup.select("a.rcfs-card")

print(f"Found {len(cards)} competitions\n")

for card in cards[:5]:

    name = card.select_one(".rcfs-name").get_text(strip=True)

    link = card["href"]

    tickets = card.select_one(".rcfs-ticket-badge-count").get_text(strip=True)

    price = card.select_one(".rcfs-badge-price").get_text(strip=True)

    sold = card.select_one(".rcfs-progress-label").get_text(strip=True)

    print(name)
    print(link)
    print(price)
    print(tickets)
    print(sold)
    print("-" * 40)