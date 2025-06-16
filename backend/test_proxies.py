import os
import asyncio
import traceback

from playwright.async_api import async_playwright, Page, Playwright, Browser
from playwright.sync_api import sync_playwright


def load_proxies_from_file(relative_path: str):
    proxies = []
    try:
        print("os.getcwd(): ", os.getcwd())
        full_path = os.path.join(os.getcwd(), relative_path)
        print("full_path: ", full_path)
        with open(full_path, "r") as f:
            for line in f:
                parts = line.strip().split(":")
                if len(parts) != 4:
                    # TODO: Report invalid format
                    print("Found invalid format")
                    continue
                domain, port, username, password = parts
                proxies.append(
                    {
                        "server": f"http://{domain}:{port}",
                        "username": username,
                        "password": password,
                    }
                )
    except Exception as e:
        print(f"Error loading proxies: {e}")

    return proxies


def get_proxy_by_port(proxies, port):
    matched_proxy = None
    for proxy in proxies:
        matched_proxy = proxy if str(port) in proxy["server"] else None

        if matched_proxy:
            break

    return matched_proxy


async def check_ip(test_proxy):
    async with async_playwright() as p:
        browser, page = await _open_blank_browser_page(p, test_proxy)

        await page.goto("https://www.whatismyip.com/")
        # Wait until the IPv4 address element is available in the DOM
        await page.wait_for_selector(".the-ipv4")

        # print("content: ", content)
        ip_address = await page.query_selector(".the-ipv4")
        print("ip_address: ", await ip_address.text_content())

        await browser.close()


async def _open_blank_browser_page(playwright: Playwright, proxy_config: dict):
    # Launch the browser and set context
    # browser = await playwright.chromium.launch()
    browser = await playwright.chromium.launch(
        proxy={
            "server": proxy_config["server"],
            "username": proxy_config["username"],
            "password": proxy_config["password"],
        },
    )
    context = await browser.new_context(
        user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) HeadlessChrome/133.0.6943.16 Safari/537.36",
    )
    print("Browser and Context created")

    print("Creating new page...")
    page: Page = await context.new_page()

    return browser, page


if __name__ == "__main__":
    try:
        proxies = load_proxies_from_file("scraper_proxies.txt")
        proxy = get_proxy_by_port(proxies, 10088)
        assert proxy is not None

        asyncio.run(check_ip(proxy))
    except Exception as e:
        print("Error: ", e)
        traceback.print_exc()


# https://whatismyipaddress.com/


def get_user_agent():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        context = browser.new_context()
        page = context.new_page()
        # Get the user agent from the browser context
        user_agent = page.evaluate("navigator.userAgent")
        browser.close()
        return user_agent
