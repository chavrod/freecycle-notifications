from datetime import datetime
import asyncio
from typing import Tuple, Dict, Optional, Literal, Any
from asgiref.sync import sync_to_async
import random
import traceback

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


class OpenBlankPageError(Exception):
    pass


# def load_proxies_from_file(path: str):
#     proxies = []
#     try:
#         with open(path, "r") as f:
#             for line in f:
#                 line = line.strip()
#                 if not line or ":" not in line:
#                     continue
#                 parts = line.split(":")
#                 if len(parts) != 4:
#                     continue  # Skip invalid format
#                 ip, port, username, password = parts
#                 proxies.append(
#                     {
#                         "server": f"http://{ip}:{port}",
#                         "username": username,
#                         "password": password,
#                     }
#                 )
#     except Exception as e:
#         print(f"Error loading proxies: {e}")

#     # Shuffle the proxies list randomly
#     random.shuffle(proxies)

#     return proxies


class Scraper:

    def __init__(self):
        self.user_agents_pool = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36 Edg/134.0.0.0",
            "Mozilla/5.0 (X11; CrOS x86_64 14541.0.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.3.1 Safari/605.1.15",
            "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
        ]

    async def run_main(self, with_proxy=True):
        print("Started Running Scraper")
        self.start_time = datetime.now()

        async with async_playwright() as p:
            for town_name, town_url_ext in TOWN_NAME_URL_EXT:

                while True:
                    proxy = None
                    if with_proxy:
                        proxy = await sync_to_async(
                            core_models.Proxy.get_relevant_proxy
                        )()

                        if proxy is None:
                            error_msg = f"🚨 ALL PROXIES FAILED"
                            print("Scraping error: ", error_msg)
                            sentry_sdk.capture_message(error_msg, level="error")
                            return  # Stop execution

                        print(
                            f"Trying proxy domain '{proxy.domain}' at port {proxy.port} for town {town_name}"
                        )

                    browser = None
                    try:
                        browser, page = await self._open_blank_browser_page(p, proxy)

                        await self._create_products_from_town(
                            page, town_name, town_url_ext
                        )
                        print(f"✅ Success")

                        if with_proxy:
                            await sync_to_async(proxy.update_usage)(True)
                        await asyncio.sleep(random.randint(10, 30))

                        await browser.close()
                        break  # Go to next town
                    except OpenBlankPageError:
                        pass  # Try again
                    except Exception as e:
                        print(f"❌ Fail - {e}")
                        traceback.print_exc()

                        if with_proxy:
                            await sync_to_async(proxy.update_usage)(False)
                        await self.send_capture_exception(e)

                        if browser:
                            await browser.close()

                        continue  # Try next proxy

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

        await self.accept_privacy_dialog_if_present(page)

        # List View shows all needed info
        await self._ensure_list_view(page)

        products_to_create = []

        global_index = 0  # will be used if we need to load more items

        all_found = False
        while not all_found:
            products_locator = page.locator("#fc-data div[data-id]")

            products_count = await products_locator.count()

            start_loop_from_index = (
                global_index + 1 if global_index > 0 else global_index
            )
            if start_loop_from_index == products_count:
                print("NEW PRODUCTS NOT LAODED")
                break  # Prevents continuous loop if more content was not loaded for some reason
            for i in range(start_loop_from_index, products_count):
                global_index = i
                product = products_locator.nth(i)

                # Is product on offer?
                is_offered_locator = product.locator(".text-offer")
                if await is_offered_locator.count() == 0:
                    continue

                # Is it a recent product?
                time_ago_span = product.locator(
                    "span.post-list-item-date.text-lighten-less"
                )
                time_ago = await time_ago_span.inner_text()
                if not "minutes" in time_ago:
                    all_found = True
                    break

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
                name_description_parent_div = product.locator(
                    ".post-list-item-content-description.hide-for-small-only"
                )
                link_element = name_description_parent_div.locator("h4 > a")
                product_name = await link_element.inner_text()

                description_element = name_description_parent_div.locator("p")
                description = None
                if await description_element.count() > 0:
                    description = await description_element.inner_text()

                # Get product image
                product_img_div = product.locator("img[data-src]")
                product_img_url = None
                if await product_img_div.count() > 0:
                    product_img_url = await product_img_div.get_attribute("data-src")

                # Get product sublocation
                sublocation_div = product.locator(
                    ".post-list-item-header-icon.location-icon"
                )
                sublocation_span = sublocation_div.locator("span")
                sublocation = None
                if await sublocation_span.count() > 0:
                    sublocation = await sublocation_span.inner_text()

                print(f"Adding new Product: {product_name}")
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

                # If the last element is on offer and is recent, load more items
                if i == products_count - 1:
                    load_more_btn = page.locator("#item-list-load-more .btn-action")

                    await load_more_btn.click()
                    await asyncio.sleep(1)
                    print("LAODED MORE")
                    # await self.send_sentry_message(
                    #     message="Last element is recent and on offer",
                    #     level="warning",
                    #     data={
                    #         "town_name": town_name,
                    #         "is_offered": "True" if is_offered else "False",
                    #         "time_ago": time_ago,
                    #         "array_index": index,
                    #     },
                    # )

        if products_to_create:
            print(f"bulk creating {len(products_to_create)} products")
            await sync_to_async(core_models.NotifiedProduct.objects.bulk_create)(
                products_to_create
            )

    def _get_town_url(self, town_ext: str) -> str:
        # https://www.freecycle.org/town/CountyWicklow
        return f"https://www.freecycle.org/town/{town_ext}"

    async def _open_blank_browser_page(
        self, playwright: Playwright, proxy: core_models.Proxy = None
    ) -> Tuple[Browser, Page]:
        try:
            # Determine proxy settings based on provided proxy
            proxy_settings = (
                {
                    "server": f"http://{proxy.domain}:{proxy.port}",
                    "username": proxy.username,
                    "password": proxy.password,
                }
                if proxy is not None
                else None
            )
            # Launch the browser and set context
            browser = await playwright.chromium.launch(proxy=proxy_settings)
            # Select a random user agent from the pool
            random_user_agent = random.choice(self.user_agents_pool)
            print("Selected user agent: ", random_user_agent)
            context = await browser.new_context(user_agent=random_user_agent)
            print("Browser and Context created")

            print("Creating new page...")
            page: Page = await context.new_page()
            return browser, page
        except Exception as e:
            print("🔴 Error getting blank page: ", e)
            traceback.print_exc()
            await self.send_sentry_message(
                message="Error getting blank page",
                level="error",
            )
            raise OpenBlankPageError

    async def accept_privacy_dialog_if_present(self, page: Page):
        # Attempt to locate and accept the consent dialog
        try:
            # You may need to tailor the selector to match the actual buttons in the dialog
            agree_button = page.locator(
                'div.qc-cmp2-summary-buttons button:has-text("AGREE")'
            )

            if await agree_button.is_visible():
                await agree_button.click()
                print("Privacy dialog accepted.")
            else:
                print("Privacy dialog not present.")

        except Exception as e:
            print(f"Could not accept privacy dialog: {e}")

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
