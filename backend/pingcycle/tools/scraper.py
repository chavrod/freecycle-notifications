from datetime import datetime
import asyncio
from typing import Tuple, Dict, Optional, Literal, Any
from asgiref.sync import sync_to_async

import sentry_sdk
from playwright.async_api import async_playwright, Page, Playwright, Browser

import pingcycle.apps.core.models as core_models
from config.settings import ENV

# TODO: Temporary solution
TOWN_NAME_URL_EXT = [
    ("Dublin", "DublinIE"),
    ("County Kildare", "KildareIE"),
    ("County Wicklow", "CountyWicklow"),
    ("County Wexford", "WexfordIRE"),
    ("Waterford", "WaterfordIE"),
]


def load_proxies_from_file(path: str):
    proxies = []
    try:
        with open(path, "r") as f:
            for line in f:
                line = line.strip()
                if not line or ":" not in line:
                    continue
                parts = line.split(":")
                if len(parts) != 4:
                    continue  # Skip invalid format
                ip, port, username, password = parts
                proxies.append(
                    {
                        "server": f"http://{ip}:{port}",
                        "username": username,
                        "password": password,
                    }
                )
    except Exception as e:
        print(f"Error loading proxies: {e}")
    return proxies


class Scraper:
    async def run_main(self):
        print("Started Running Scraper")
        self.start_time = datetime.now()

        proxy_configs = load_proxies_from_file("/etc/scraper_proxies.txt")
        if not proxy_configs:
            sentry_sdk.capture_message(
                "❌ No proxies found in /etc/scraper_proxies.txt", level="fatal"
            )
            return

        async with async_playwright() as p:
            current_town_index = 0

            while current_town_index < len(TOWN_NAME_URL_EXT):
                town_name, town_url_ext = TOWN_NAME_URL_EXT[current_town_index]

                success = False

                for proxy_config in proxy_configs.copy():
                    print(f"Trying proxy {proxy_config['server']} for town {town_name}")

                    try:
                        browser, page = await self._open_blank_browser_page(
                            p, proxy_config
                        )

                        await self._create_products_from_town(
                            page, town_name, town_url_ext
                        )
                        print(
                            f"✅ Success for {town_name} using {proxy_config['server']}"
                        )
                        await asyncio.sleep(2)

                        success = True
                        current_town_index += 1
                        await browser.close()
                        break  # Go to next town
                    except Exception as e:
                        print(f"❌ Proxy failed: {proxy_config['server']} - {e}")
                        await self.send_capture_exception(e)

                        await browser.close()
                        proxy_configs.remove()

                        continue  # Try next proxy

                if not success:
                    error_msg = f"🚨 ALL PROXIES FAILED"
                    print(error_msg)
                    sentry_sdk.capture_message(error_msg, level="error")
                    break  # Stop execution

            print("🏁 Finished Running Scraper")

    async def _create_products_from_town(
        self, page: Page, town_name: str, town_url_ext: str
    ):
        """
        # TODO: TESTS + REFACTOR

        Checks if there are any new products that match users keywords
        """
        print(f"Checking products for town: {town_name}")
        # Generate the dynamic link for the current race_day
        url = self._get_town_url(town_url_ext)
        # Go to correct page
        await page.goto(url)
        await page.content()

        # List View shows all needed info
        await self._ensure_list_view(page)

        parent_div = await page.query_selector("#fc-data")
        products = await parent_div.query_selector_all("div[data-id]")

        products_to_create = []

        for index, product in enumerate(products):
            # Is product on offer?
            is_offered = await product.query_selector(".text-offer")
            if not is_offered:
                continue

            # Is it a recent product?
            time_ago_span = await product.query_selector(
                "span.post-list-item-date.text-lighten-less"
            )
            time_ago = await time_ago_span.inner_text()
            if not "minutes" in time_ago:
                break

            # If the last element is on offer and is recent, send Sentry alert
            # TODO: Should just 'load more' automatically
            if index == len(products) - 1:
                await self.send_sentry_message(
                    message="Last element is recent and on offer",
                    level="warning",
                    data={
                        "town_name": town_name,
                        "is_offered": "True" if is_offered else "False",
                        "time_ago": time_ago,
                        "array_index": index,
                    },
                )

            # Do we have this product in db?
            try:
                product_id = await product.get_attribute("data-id")
                await sync_to_async(core_models.NotifiedProduct.objects.get)(
                    external_id=product_id
                )
                continue
            except core_models.NotifiedProduct.DoesNotExist:
                pass

            # Get product name and description
            name_description_parent_div = await product.query_selector(
                ".post-list-item-content-description.hide-for-small-only"
            )
            link_element = await name_description_parent_div.query_selector("h4 > a")

            product_name = await link_element.inner_text()

            description_element = await name_description_parent_div.query_selector("p")
            description = await (
                description_element.inner_text() if description_element else ""
            )

            # Get product image
            product_img_url = None
            product_img_div = await product.query_selector("img[data-src]")
            if product_img_div:
                product_img_url = await product_img_div.get_attribute("data-src")

            # Get product sublocation
            sublocation_div = await product.query_selector(
                ".post-list-item-header-icon.location-icon"
            )
            sublocation_span = await sublocation_div.query_selector("span")
            sublocation = (
                await sublocation_span.inner_text() if sublocation_span else ""
            )

            print(f"Addingg new Product: {product_name}")
            products_to_create.append(
                core_models.NotifiedProduct(
                    product_name=product_name,
                    external_id=product_id,
                    description=description,
                    location=town_name,
                    sublocation=sublocation,
                    img=product_img_url,
                )
            )

        if products_to_create:
            print(f"bulk creating {len(products_to_create)} products")
            await sync_to_async(core_models.NotifiedProduct.objects.bulk_create)(
                products_to_create
            )

    def _get_town_url(self, town_ext: str) -> str:
        # https://www.freecycle.org/town/CountyWicklow
        return f"https://www.freecycle.org/town/{town_ext}"

    async def _open_blank_browser_page(
        self, playwright: Playwright, proxy_config: dict
    ) -> Tuple[Browser, Page]:
        # Launch the browser and set context
        browser = await playwright.chromium.launch(
            proxy={
                "server": proxy_config["server"],
                "username": proxy_config["username"],
                "password": proxy_config["password"],
            }
        )
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36"
        )
        print("Browser and Context created")

        print("Creating new page...")
        page: Page = await context.new_page()
        return browser, page

    async def _ensure_list_view(self, page: Page) -> bool:
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
            await self.send_sentry_message(
                "Unable to find List View selector", "warning"
            )

    @sync_to_async
    def send_sentry_message(
        self,
        message: str,
        level: Literal["fatal", "critical", "error", "warning", "info", "debug"],
        data: Optional[Dict[str, Any]] = None,
    ):
        print(f"Sending Sentry message with level '{level}': {message}")
        if ENV == "DEV":
            print("Abort sending in DEV")
            return

        with sentry_sdk.new_scope() as scope:
            scope.set_tag("module", "scraper")
            if data:
                scope.set_context("town_product_details", data)
            sentry_sdk.capture_message(message, level)

    @sync_to_async
    def send_capture_exception(
        self,
        e,
    ):
        print(f"Capturing Sentry exception: {e}")
        if ENV == "DEV":
            print("Abort sending in DEV")
            return

        with sentry_sdk.new_scope() as scope:
            scope.set_tag("module", "scraper")
            sentry_sdk.capture_exception(e)
