from django.core.management.base import BaseCommand
from django.contrib.sites.models import Site

from config.settings import SITE_ID, APP_NAME, BASE_DOMAIN


class Command(BaseCommand):
    help = "Update the site domain and name."

    def handle(self, *args, **kwargs):
        site, created = Site.objects.update_or_create(
            id=SITE_ID, defaults={"domain": BASE_DOMAIN, "name": APP_NAME}
        )
        if created:
            self.stdout.write(
                self.style.SUCCESS(f"Site created with domain {site.domain}")
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(f"Site updated to domain {site.domain}")
            )
