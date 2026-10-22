#!/usr/bin/env python3
"""Render every slide of the deck to PNG (1920x1080) for both themes, then assemble PDFs and contact sheets."""
import asyncio, os, sys, glob
from playwright.async_api import async_playwright
from PIL import Image
D = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(D, "render"); os.makedirs(OUT, exist_ok=True)
THEMES = sys.argv[1:] or ["dark", "light"]

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        pg = await b.new_page(viewport={"width": 1920, "height": 1080}, device_scale_factor=1)
        await pg.goto(f"file://{D}/index.html?theme=dark", wait_until="load")
        await pg.evaluate("document.fonts.ready"); await pg.wait_for_timeout(400)
        n = await pg.evaluate("window.__deck.N")
        for th in THEMES:
            await pg.evaluate(f"window.__deck.setTheme('{th}')"); await pg.wait_for_timeout(600)
            await pg.evaluate("document.getElementById('ui').style.display='none';document.getElementById('hint').style.display='none';document.getElementById('bar').style.display='none'")
            for i in range(1, n + 1):
                await pg.evaluate(f"window.__deck.show({i})"); await pg.wait_for_timeout(1300)
                await pg.screenshot(path=f"{OUT}/{th}_{i:02d}.png", type="png")
        await b.close()
    for th in THEMES:
        files = sorted(glob.glob(f"{OUT}/{th}_*.png"))
        ims = [Image.open(f).convert("RGB") for f in files]
        ims[0].save(f"{D}/The-Longevity-Masterclass-v2-{th}.pdf", save_all=True, append_images=ims[1:], resolution=144, quality=92)
        # contact sheet
        cols = 3; w, h = 640, 360; rows = (len(ims) + cols - 1) // cols
        sheet = Image.new("RGB", (cols * w + (cols + 1) * 10, rows * h + (rows + 1) * 10), (30, 30, 30))
        for k, im in enumerate(ims):
            t = im.resize((w, h), Image.LANCZOS); sheet.paste(t, (10 + (k % cols) * (w + 10), 10 + (k // cols) * (h + 10)))
        sheet.save(f"{OUT}/sheet_{th}.jpg", quality=85)
    print("done", n)

asyncio.run(main())
