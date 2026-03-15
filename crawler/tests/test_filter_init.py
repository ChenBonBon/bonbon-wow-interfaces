import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from core.filter_init import (
    extract_filter_init_payload,
    write_filter_init_json,
    write_filter_page_html,
)


class FilterInitTest(unittest.TestCase):
    def test_extract_filter_init_payload_parses_embedded_json_object(self):
        html_text = """
        <html>
          <script>
            Filter.init({"filters":[{"id":8,"name":"Disenchantable"}]});
          </script>
        </html>
        """

        payload = extract_filter_init_payload(html_text)

        self.assertEqual(
            payload,
            {"filters": [{"id": 8, "name": "Disenchantable"}]},
        )

    def test_write_filter_init_json_reads_local_html_and_writes_json(self):
        with TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            html_path = temp_path / "items.html"
            output_path = temp_path / "items.filters.json"
            html_path.write_text(
                """
                <script>
                  Filter.init({"filters":[{"id":161,"name":"Available to players"}]});
                </script>
                """,
                encoding="utf-8",
            )

            written_path = write_filter_init_json(html_path, output_path=output_path)

            self.assertEqual(written_path, output_path)
            self.assertEqual(
                json.loads(output_path.read_text(encoding="utf-8")),
                {"filters": [{"id": 161, "name": "Available to players"}]},
            )

    def test_write_filter_page_html_fetches_url_and_writes_html(self):
        with TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            output_path = temp_path / "items.html"

            written_path = write_filter_page_html(
                "https://www.wowhead.com/items",
                output_path=output_path,
                fetch_url=lambda _url: "<html>ok</html>",
            )

            self.assertEqual(written_path, output_path)
            self.assertEqual(output_path.read_text(encoding="utf-8"), "<html>ok</html>")


if __name__ == "__main__":
    unittest.main()
