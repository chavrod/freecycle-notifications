import traceback

from django.core.management import BaseCommand

import pingcycle.apps.core.models as core_models


class Command(BaseCommand):
    help = "Loads proxies config from a file & updates username/password if necessary"

    def add_arguments(self, parser):
        parser.add_argument(
            "--path",
            action="store",
            dest="path",
            default="/etc/scraper_proxies.txt",
            help="Specify non-default path to proxy",
        )

    def handle(self, *args, **options):
        try:
            self.stdout.write("Begin loading proxies")

            path = options["path"]
            self.stdout.write(f"Loading proxies from path: {path}")

            proxies = self.load_proxies_from_file(path)

            for proxy in proxies:
                try:
                    existing_proxy = core_models.Proxy.objects.get(
                        domain=proxy["domain"], port=proxy["port"]
                    )
                    existing_proxy.username = proxy["username"]
                    existing_proxy.password = proxy["password"]
                    existing_proxy.save(update_fields=["username", "password"])
                except core_models.Proxy.DoesNotExist:
                    core_models.Proxy.objects.create(
                        domain=proxy["domain"],
                        port=proxy["port"],
                        username=proxy["username"],
                        password=proxy["password"],
                    )

            self.stdout.write(
                self.style.SUCCESS(f"Updated/Loaded {len(proxies)} proxies")
            )

        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Error loading proxies: {e}"))
            traceback.print_exc()

    def load_proxies_from_file(self, abs_path: str):
        proxies = []

        with open(abs_path, "r") as f:
            for line in f:
                parts = line.strip().split(":")
                if len(parts) != 4:
                    self.stderr.write(
                        self.style.ERROR(f"Found invalid format: {parts}")
                    )
                    continue
                domain, port, username, password = parts
                proxies.append(
                    {
                        "domain": domain,
                        "port": port,
                        "username": username,
                        "password": password,
                    }
                )

        return proxies
