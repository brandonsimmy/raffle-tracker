import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime

AJAX_URL = "https://www.revcomps.com/wp-admin/admin-ajax.php"
COMPETITIONS_URL = "https://www.revcomps.com/current-competitions/"

TERM_ID = "10607"


def get_nonce():

    response = requests.get(
        COMPETITIONS_URL,
        timeout=10
    )

    match = re.search(
        r'data-nonce="([^"]+)"',
        response.text
    )

    if not match:
        raise Exception("Could not find nonce")

    return match.group(1)


def calculate_time_bonus(days_remaining):

    if days_remaining <= 1:
        return 15

    if days_remaining <= 2:
        return 10

    if days_remaining <= 5:
        return 5

    return 0


def parse_draw_date(draw_text):

    try:

        current_year = datetime.now().year

        draw_text = draw_text.upper()

        match = re.search(
            r'(\d{1,2})(?:ST|ND|RD|TH)\s+([A-Z]{3})\s+@\s+(\d{1,2})(AM|PM)',
            draw_text
        )

        if not match:
            return None

        day = int(match.group(1))
        month = match.group(2)
        hour = int(match.group(3))
        ampm = match.group(4)

        if ampm == "PM" and hour != 12:
            hour += 12

        if ampm == "AM" and hour == 12:
            hour = 0

        draw_date = datetime.strptime(
            f"{day} {month} {current_year} {hour}",
            "%d %b %Y %H"
        )

        if draw_date < datetime.now():
            draw_date = draw_date.replace(
                year=current_year + 1
            )

        return draw_date

    except:
        return None


def get_competitions():

    nonce = get_nonce()

    response = requests.post(
        AJAX_URL,
        data={
            "action": "rcfs_get_products",
            "nonce": nonce,
            "term_id": TERM_ID
        },
        timeout=15
    )

    data = response.json()

    if not data.get("success"):
        raise Exception(
            f"Rev Comps returned: {data}"
        )

    html = data["data"]["html"]

    soup = BeautifulSoup(
        html,
        "html.parser"
    )

    competitions = []

    for card in soup.select("a.rcfs-card"):

        try:

            name = card.select_one(
                ".rcfs-name"
            ).get_text(strip=True)

            url = card["href"]

            draw_text = card.select_one(
                ".product_info"
            ).get_text(strip=True)

            tickets_text = card.select_one(
                ".rcfs-ticket-badge-count"
            ).get_text(strip=True)

            total_tickets = int(
                re.sub(
                    r"[^\d]",
                    "",
                    tickets_text
                )
            )

            sold_text = card.select_one(
                ".rcfs-progress-label"
            ).get_text(strip=True)

            sold_pct = int(
                re.search(
                    r"\d+",
                    sold_text
                ).group()
            )

            unsold_pct = 100 - sold_pct

            remaining_tickets = round(
                total_tickets *
                (unsold_pct / 100)
            )

            price_text = card.select_one(
                ".rcfs-badge-price"
            ).get_text(strip=True)

            prices = re.findall(
                r"\d+\.\d+",
                price_text
            )

            if prices:
                price = float(prices[-1])
            else:
                price = 999

            draw_date = parse_draw_date(
                draw_text
            )

            if draw_date:

                days_remaining = round(
                    (
                        draw_date
                        - datetime.now()
                    ).total_seconds()
                    / 86400,
                    1
                )

            else:

                days_remaining = 999

            time_bonus = calculate_time_bonus(
                days_remaining
            )

            score = round(
                (
                    remaining_tickets / price
                )
                * (
                    1 + (time_bonus / 20)
                ),
                1
            )

            competitions.append({
                "name": name,
                "url": url,
                "price": price,
                "tickets": total_tickets,
                "remaining_tickets": remaining_tickets,
                "sold_pct": sold_pct,
                "unsold_pct": unsold_pct,
                "draw_text": draw_text,
                "days_remaining": days_remaining,
                "score": score
            })

        except Exception as e:

            print(
                f"Skipped competition: {e}"
            )

    competitions.sort(
        key=lambda x: x["score"],
        reverse=True
    )

    return competitions


if __name__ == "__main__":

    print(
        "Getting latest nonce..."
    )

    print(
        f"Nonce: {get_nonce()}"
    )

    comps = get_competitions()

    print(
        f"\nFound {len(comps)} competitions\n"
    )

    for c in comps[:10]:

        print(
            f"{c['score']:>10} | "
            f"{c['remaining_tickets']:>8} left | "
            f"£{c['price']} | "
            f"{c['name']}"
        )