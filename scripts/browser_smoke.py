"""Real browser + HTTP smoke test. Uses Chromium WebGL software fallback on CI."""
import json
import urllib.request
from playwright.sync_api import sync_playwright, expect


def api_check():
    with urllib.request.urlopen("http://127.0.0.1:8000/api/ready", timeout=10) as response:
        ready = json.load(response)
    assert ready["cities"] == 240
    assert ready["lexicon_entries"] >= 100
    for dream, language in [
        ("I was flying over a blue ocean beneath the stars", "en"),
        ("حلمت أني أمشي على شاطئ البحر والمطر ينزل في الليل", "ar")
    ]:
        payload=json.dumps({"dream":dream,"language":language}).encode()
        request=urllib.request.Request(
            "http://127.0.0.1:8000/api/analyze",
            data=payload,headers={"Content-Type":"application/json"},method="POST"
        )
        with urllib.request.urlopen(request,timeout=15) as response:
            body=json.load(response)
        assert body["language"]==language, body
        assert body["city"]["id"].startswith("dream-city-"), body
        assert len(body["alternatives"]) == 5, body
        assert body["city"]["scene_config"], body
    print("PASS real FastAPI readiness and Arabic/English analyze endpoints")


def browser_check():
    errors=[]
    with sync_playwright() as p:
        browser=p.chromium.launch(
            headless=True,
            args=["--no-sandbox","--enable-webgl","--use-gl=angle","--use-angle=swiftshader","--ignore-gpu-blocklist"]
        )
        page=browser.new_page(viewport={"width":1365,"height":900})
        page.on("pageerror",lambda err: errors.append(str(err)))
        page.goto("http://127.0.0.1:5173/",wait_until="domcontentloaded")
        expect(page.get_by_text("Dream Atlas",exact=True)).to_be_visible()
        page.get_by_label("نص الحلم").fill("حلمت أني أمشي على شاطئ البحر والمطر ينزل في الليل")
        page.get_by_role("button",name="حوّل الحلم إلى مدينة").click()
        expect(page.get_by_role("heading",name="هذه هي البصمة التي صنعها حلمك")).to_be_visible(timeout=20000)
        expect(page.locator(".scene-shell canvas")).to_be_visible(timeout=25000)
        assert page.locator(".scene-shell canvas").count()==1
        if errors:
            raise AssertionError("Uncaught browser errors: "+"; ".join(errors))
        browser.close()
    print("PASS actual Vite + Chromium + React Three Fiber scene with API analysis")


if __name__=="__main__":
    api_check()
    browser_check()
