import os
import asyncio
import traceback
import random

from playwright.async_api import async_playwright, Page, Playwright, Browser
from playwright.sync_api import sync_playwright


class OpenBlankPageError(Exception):
    pass


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


async def _open_blank_browser_page(playwright: Playwright, proxy: dict = None):
    # Launch the browser and set context
    proxy_settings = (
        {
            "server": proxy["server"],
            "username": proxy["username"],
            "password": proxy["password"],
        }
        if proxy is not None
        else None
    )
    browser = await playwright.chromium.launch(
        proxy=proxy_settings,
    )
    context = await browser.new_context(
        user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) HeadlessChrome/133.0.6943.16 Safari/537.36",
    )
    print("Browser and Context created")

    print("Creating new page...")
    page: Page = await context.new_page()

    return browser, page


async def _ensure_list_view(page: Page) -> bool:
    selector = "li.item-list-header-filter-icon.item-list-list-view.hover-state"

    # Find the element
    element = await page.query_selector(selector)

    if element is not None:
        # Check if 'inactive' class is present
        class_attribute = await element.get_attribute("class")

        if "inactive" in class_attribute:
            # Click the element to toggle inactive class
            await element.click()

        print("List view is active.")
    else:
        raise Exception("Unable to open list view.")


async def try_go(should_succeed, proxy=None):
    async with async_playwright() as p:
        browser = None
        try:
            print("Opening Browser")
            browser, page = await _open_blank_browser_page(p, proxy)

            print("Going to page")
            if not should_succeed:
                raise OpenBlankPageError
            await page.goto("https://www.freecycle.org/town/DublinIE")
            await page.content()

            await _ensure_list_view(page)

            products_locator = page.locator("#fc-data div[data-id]")

            products_count = await products_locator.count()
            print("products_count: ", products_count)

            product = products_locator.nth(0)
            name_description_parent_div = product.locator(
                ".post-list-item-content-description.hide-for-small-only"
            )
            link_element = name_description_parent_div.locator("h4 > a")
            product_name = await link_element.inner_text()
            print("Top product: ", product_name)

            print(f"✅ Success")
        except OpenBlankPageError:
            # Set debug environment variables
            print("OpenBlankPageError encountered. Enabling debug mode.")
            os.environ["DEBUG"] = "pw:api"
            os.environ["DEBUG_FILE"] = (
                f"/Users/dmitry/projects/freecycle-notifications/backend/playwright_debug.log"
            )
        except Exception as e:
            if browser:
                browser.close()
            raise e

        await asyncio.sleep(random.randint(2, 10))


if __name__ == "__main__":
    try:
        proxies = load_proxies_from_file("scraper_proxies.txt")
        proxy = get_proxy_by_port(proxies, 6069)
        assert proxy is not None

        # proxy = None

        # asyncio.run(check_ip(proxy))
        for i, should_succeed in enumerate([True]):
            print("RUN #: ", i + 1)
            asyncio.run(try_go(should_succeed, proxy))
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
