import os
from datetime import datetime, date, timedelta
from logging import Logger
import random
import asyncio
from typing import List, Tuple

from django.db import transaction

import sentry_sdk
from playwright.async_api import async_playwright, Page, Playwright, Browser

import pingcycle.apps.core.models as core_models

# TODO: Temporary solution////
TOWN_NAME_URL_EXT = [
    ("Dublin", "DublinIE"),
    # ("County Kildare", "KildareIE"),
    # ("County Wicklow", "CountyWicklow"),
    # ("County Wexford", "WexfordIRE"),
    # ("Waterford", "WaterfordIE"),
]


class Scraper:
    async def run_main(self):
        self.start_time = datetime.now()

        async with async_playwright() as p:
            browser, page = await self._open_blank_browser_page(p)

            for town_name, town_url_ext in TOWN_NAME_URL_EXT:
                await self._create_products_from_town(page, town_name, town_url_ext)

            # Close the browser
            await browser.close()
            # True is returned when all markets have been scraped
            return True

    async def _create_products_from_town(
        self, page: Page, town_name: str, town_url_ext: str
    ):
        """
        # TODO: ADD SENTRY AND HEALTH CHEKING!

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

        for product in products:
            is_offered = await product.query_selector(".text-offer")
            if not is_offered:
                continue

            time_ago_span = await product.query_selector(
                "span.post-list-item-date.text-lighten-less"
            )
            time_ago = await time_ago_span.inner_text()
            print("time_ago: ", time_ago)
            # TODO: Enable back!
            # No Recent Entries
            # if not "minutes" in time_ago:
            #     break

            product_id = await product.get_attribute("data-id")
            print(f"product_id: {product_id}")

            try:
                core_models.NotifiedProduct.objects.get(external_id=product_id)
                continue
            except core_models.NotifiedProduct.DoesNotExist:
                print("No matching product on records")
                pass

            # post-list-item-content-description hide-for-small-only
            # print("Checking if product name matches Keywords")
            name_description_parent_div = await product.query_selector(
                ".post-list-item-content-description.hide-for-small-only"
            )
            if name_description_parent_div is None:
                # TODO: SENTRY
                return

            link_element = await name_description_parent_div.query_selector("h4 > a")
            if link_element is None:
                # TODO: SENTRY
                return
            # Get the title from the <a> element's text
            product_name = await link_element.inner_text()
            print(f"product_name: {product_name}")
            # Get the URL extension from the <a> element's href attribute
            url_extension = await link_element.get_attribute("href")
            print(f"url_extension: {url_extension}")
            # Extract the <p> element to get the description
            description_element = await parent_div.query_selector("p")
            description = await (
                description_element.inner_text() if description_element else ""
            )
            print(f"description: {description}")

            product_img_div = await parent_div.query_selector("img[data-src]")
            product_img_url = await product_img_div.get_attribute("data-src")
            print("product_img_url: ", product_img_url)

            sublocation_div = await product.query_selector(
                ".post-list-item-header-icon.location-icon"
            )
            sublocation_span = await sublocation_div.query_selector("span")
            sublocation = (
                await sublocation_span.inner_text() if sublocation_span else ""
            )
            print(f"sublocation: {sublocation}\n\n\n")

            matched_keywords = core_models.Keyword.objects.filter(
                name__trigram_similar=product_name
            )
            if matched_keywords:
                notified_product = core_models.NotifiedProduct.objects.create(
                    product_name=product_name,
                    external_id=product_id,
                    description=description,
                    location=town_name,
                    sublocation=sublocation,
                    img=product_img_url,
                )
                notified_product.keywords.set(matched_keywords)
                notified_product.save(update_fields=["keywords"])

    def _get_town_url(self, town_ext: str) -> str:
        # https://www.freecycle.org/town/CountyWicklow
        return f"https://www.freecycle.org/town/{town_ext}"

    async def _open_blank_browser_page(
        self, playwright: Playwright
    ) -> Tuple[Browser, Page]:
        # Launch the browser and set context
        browser = await playwright.chromium.launch()
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
            # TODO: Unusual SENTRY
            print("Element not found.")


if __name__ == "__main__":
    print("Starting main...")
    scraper = Scraper()
    asyncio.run(scraper.run_main())
