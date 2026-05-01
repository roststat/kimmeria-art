# -*- coding: utf-8 -*-
import asyncio
import os
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(encoding="utf-8")

BASE_URL = "https://art-kimmeria.ru/programmy"

PROGRAMS = [
    "afrodita", "gekata", "lilit", "lyubov",
]

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "pdf_export")


async def download_pdf(page, program: str) -> bool:
    url = f"{BASE_URL}/{program}/"
    print(f"  Открываю {url}")

    await page.goto(url, wait_until="networkidle", timeout=30000)

    btn = page.locator(".btn-pdf-main")
    if await btn.count() == 0:
        print(f"  [!] Кнопка не найдена: {program}")
        return False

    async with page.expect_download(timeout=120000) as dl_info:
        await btn.click()

    download = await dl_info.value
    filename = download.suggested_filename or f"{program}-kimmeria-art.pdf"
    dest = os.path.join(OUTPUT_DIR, filename)
    await download.save_as(dest)
    print(f"  OK: {filename}")
    return True


async def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print(f"Папка для PDF: {OUTPUT_DIR}\n")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            accept_downloads=True,
            viewport={"width": 1440, "height": 900},
        )
        page = await context.new_page()

        ok, fail = 0, []
        for program in PROGRAMS:
            print(f"[{PROGRAMS.index(program)+1}/{len(PROGRAMS)}] {program}")
            try:
                success = await download_pdf(page, program)
                if success:
                    ok += 1
                else:
                    fail.append(program)
            except Exception as e:
                print(f"  [!] Ошибка: {e}")
                fail.append(program)

        await browser.close()

    print(f"\nГотово: {ok} PDF сохранено в {OUTPUT_DIR}")
    if fail:
        print(f"Не удалось: {', '.join(fail)}")


if __name__ == "__main__":
    asyncio.run(main())
