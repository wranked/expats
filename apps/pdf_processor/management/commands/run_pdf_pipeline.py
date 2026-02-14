import json
import asyncio

from django.core.management.base import BaseCommand, CommandError

from apps.pdf_processor.services import PDFCronPipelineService


class Command(BaseCommand):
    help = "Run full PDF pipeline: scrape, download, process, parse and sync companies."

    def add_arguments(self, parser):
        parser.add_argument('--page-url', required=True, help='Web page URL to scrape for PDF link.')
        parser.add_argument('--attribute-name', required=True, help='HTML attribute used to find the PDF link.')
        parser.add_argument(
            '--headers-json',
            required=False,
            help='Optional JSON object with custom request headers.',
        )

    def handle(self, *args, **options):
        page_url = options['page_url']
        attribute_name = options['attribute_name']
        headers_json = options.get('headers_json')

        headers = None
        if headers_json:
            try:
                headers = json.loads(headers_json)
                if not isinstance(headers, dict):
                    raise CommandError('--headers-json must be a JSON object.')
            except json.JSONDecodeError as exc:
                raise CommandError(f'Invalid --headers-json: {exc}') from exc

        try:
            result = asyncio.run(
                PDFCronPipelineService.run_once_async(
                    page_url=page_url,
                    attribute_name=attribute_name,
                    headers=headers,
                )
            )
        except Exception as exc:
            raise CommandError(f'Pipeline failed: {exc}') from exc

        self.stdout.write(self.style.SUCCESS('PDF pipeline completed successfully.'))
        self.stdout.write(json.dumps(result, ensure_ascii=False, indent=2, default=str))
