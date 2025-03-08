import pingcycle.apps.core.models as core_models
from django.db import transaction


import os
from datetime import datetime, date, timedelta
from logging import Logger
import random
import asyncio
from typing import List, Tuple

import sentry_sdk
from playwright.async_api import async_playwright, Page, Playwright, Browser

# TODO: Temporary solution////
TOWN_NAME_URL_EXT = [
    ("Dublin", "DublinIE"),
    ("County Kildare", "KildareIE"),
    ("County Wicklow", "CountyWicklow"),
    ("County Wexford", "WexfordIRE"),
    ("Waterford", "WaterfordIE"),
]


class Scraper:
    async def run_main(self):
        self.start_time = datetime.now()

        async with async_playwright() as p:
            browser, page = await self._open_blank_browser_page(p)

            for town, url_ext in TOWN_NAME_URL_EXT:
                pass

            # Close the browser
            await browser.close()
            # True is returned when all markets have been scraped
            return True

    async def _create_products_from_town(self, page: Page, town_ext: str):
        """
        Checks if there are any new products that match users keywords
        """
        # TODO: ADD SENTRY AND HEALTH CHEKING!

        # Generate the dynamic link for the current race_day
        url = self._get_town_url(town_ext)
        # Go to correct page
        await page.goto(url)
        await page.content()

        parent_div = await page.query_selector("#fc_data")
        products = await parent_div.query_selector_all("div[data-id]")

        for product in products:
            time_ago_div = await product.query_selector(".text-lighten-less")
            time_ago = time_ago_div.inner_text()
            print("time_ago: ", time_ago)

            # No Recent Entries
            if not "minutes" in time_ago:
                break

            is_offered = await product.query_selector(".text-offer")
            if not is_offered:
                continue

            product_id = await product.get_attribute("data-id")

            try:
                core_models.NotifiedProduct.objects.get(external_id=product_id)
                continue
            except core_models.NotifiedProduct.DoesNotExist:
                print("No matching product on records")
                pass

            print("Checking if product name matches Keywords")
            anchor = await product.query_selector("a[href^='/posts']")
            if anchor:
                # Get the title attribute
                product_name = await anchor.get_attribute("title")
                if product_name is None:
                    product_name = await anchor.inner_text()
                print(f"product_name: {product_name}")
            else:
                print("No anchor with href starting with '/posts' found.")
                continue

            product_img_div = await parent_div.query_selector("div[data-src]")
            product_img_url = await product_img_div.get_attribute("data-src")
            print("product_img_url: ", product_img_url)

            # TODO: make query matching smarter!
            # Not efficient to load all Keywords into memory
            keywords = core_models.Keyword.objects.all()
            # Find keywords that are in product_name
            matching_keywords = []
            for keyword in keywords:
                if keyword.name.lower() in product_name.lower():
                    matching_keywords.append(keyword)

            if matching_keywords:
                # Use Django transaction to ensure atomicity
                with transaction.atomic():
                    # Create NotifiedProduct
                    notified_product = core_models.NotifiedProduct.objects.create(
                        product_name=product_name,
                        status=core_models.NotifiedProduct.Status.QUEUED,
                        external_id=product_id,
                        img=product_img_url,
                    )

                    # Link matching keywords to the notified product
                    for keyword in matching_keywords:
                        notified_product.keywords.add(keyword)

                    notified_product.save()
                    print(f"NotifiedProduct created for {product_name}")

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
        self.logger.info("Browser and Context created")

        self.logger.debug("Creating new page...")
        page: Page = await context.new_page()
        return browser, page
