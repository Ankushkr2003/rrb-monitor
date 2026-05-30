
import requests
from bs4 import BeautifulSoup
from telegram import Bot
from urllib.parse import urljoin
from io import BytesIO
import asyncio
import time

TOKEN = "8914032839:AAE0pYrpD-fk56mnB0dDvw9_S-9eMfzjvPc"
CHAT_ID = 1502039772

RRB_URLS = [
    "https://www.rrbcdg.gov.in/",
    "https://www.rrbajmer.gov.in/",
    "https://www.rrbbhopal.gov.in/",
    "https://www.rrbbnc.gov.in/",
    "https://www.rrbchennai.gov.in/",
    "https://www.rrbguwahati.gov.in/",
    "https://www.rrbkolkata.gov.in/",
    "https://www.rrbpatna.gov.in/"
]

try:
    with open("seen.txt", "r") as f:
        seen = set(f.read().splitlines())
except:
    seen = set()

FIRST_RUN = False
async def send_pdf(pdf_url, name):
    bot = Bot(token=TOKEN)

    r = requests.get(pdf_url, timeout=30)

    pdf_file = BytesIO(r.content)
    pdf_file.name = name

    await bot.send_document(
        chat_id=CHAT_ID,
        document=pdf_file,
        caption=f"📄 नई PDF मिली\n{name}"
    )
async def send_msg(text):
    bot = Bot(token=TOKEN)
    await bot.send_message(chat_id=CHAT_ID, text=text)

async def check_rrb():
    for url in RRB_URLS:
        try:
            r = requests.get(
                url,
                headers={"User-Agent": "Mozilla/5.0"},
                timeout=20
            )

            soup = BeautifulSoup(r.text, "html.parser")

            for link in soup.find_all("a", href=True):
                text = link.get_text(" ", strip=True)
                href = link["href"]


                href = urljoin(url, href)

                if href.lower().endswith(".pdf"):
                    await send_pdf(
                        href,
                        href.split("/")[-1]
                    )

                item = f"{text}|{href}"

                if item not in seen:
                    seen.add(item)
                    with open("seen.txt", "a") as f:
                        f.write(item + "\n")

                    if FIRST_RUN:
                        continue

                    if any(k in text.lower() for k in [
                        "result",
                        "notification",
                        "notice",
                        "admit",
                        "exam",
                        "cen",
                        "pdf"
                    ]):

                        rrb_name = url.split("//")[1].split(".")[0]
                        rrb_name = rrb_name.replace("rrb", "RRB ").title()

                        await send_msg(
                            f"🚨 *RRB NEW UPDATE*\n\n"
                            f"📢 Notice: {text}\n\n"
                            f"🔗 Link:\n{href}\n\n"
                            f"⏰ Source: {url}"
                       )

        except Exception as e:
            print(url, e)

async def main():

     await send_msg("🚆 RRB Monitor Started")

     while True:
        await check_rrb()
        await asyncio.sleep(600)

asyncio.run(main())
