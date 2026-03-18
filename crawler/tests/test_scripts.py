import json
import os
import subprocess
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from scripts.aggregate_run import run as run_aggregate
from scripts.export_lua import run as run_export_lua
from scripts.fetch_run import run as run_fetch
from scripts.generate_mappings import run as run_generate_mappings
from scripts.generate_normalized_mappings import run as run_generate_normalized_mappings
from scripts.generate_run import run as run_generate
from scripts.report_run import run as run_report
from scripts.retry_failed_run import run as run_retry_failed
from scripts.run_all import run as run_all


class ScriptsTest(unittest.TestCase):
    def test_run_all_shell_wrapper_uses_default_task_file_when_no_args(self):
        script_path = Path(__file__).resolve().parents[1] / "bin" / "run_all.sh"
        crawler_dir = Path(__file__).resolve().parents[1]

        self.assertTrue(script_path.exists())
        self.assertTrue(os.access(script_path, os.X_OK))

        with TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            fake_python = temp_path / "python3"
            argv_file = temp_path / "argv.txt"
            cwd_file = temp_path / "cwd.txt"
            fake_python.write_text(
                "#!/bin/sh\n"
                f"printf '%s\\n' \"$@\" > \"{argv_file}\"\n"
                f"pwd > \"{cwd_file}\"\n",
                encoding="utf-8",
            )
            fake_python.chmod(0o755)

            result = subprocess.run(
                [str(script_path)],
                capture_output=True,
                text=True,
                check=False,
                env={**os.environ, "PATH": f"{temp_path}:{os.environ['PATH']}"},
            )

            self.assertEqual(result.returncode, 0)
            self.assertEqual(
                argv_file.read_text(encoding="utf-8").splitlines(),
                ["-m", "scripts.run_all", "tasks/wowhead_items.json"],
            )
            self.assertEqual(cwd_file.read_text(encoding="utf-8").strip(), str(crawler_dir))

    def test_run_all_shell_wrapper_forwards_explicit_args_unchanged(self):
        script_path = Path(__file__).resolve().parents[1] / "bin" / "run_all.sh"

        self.assertTrue(script_path.exists())
        self.assertTrue(os.access(script_path, os.X_OK))

        with TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            fake_python = temp_path / "python3"
            argv_file = temp_path / "argv.txt"
            fake_python.write_text(
                "#!/bin/sh\n"
                f"printf '%s\\n' \"$@\" > \"{argv_file}\"\n",
                encoding="utf-8",
            )
            fake_python.chmod(0o755)

            result = subprocess.run(
                [str(script_path), "tasks/custom.json", "outputs/custom"],
                capture_output=True,
                text=True,
                check=False,
                env={**os.environ, "PATH": f"{temp_path}:{os.environ['PATH']}"},
            )

            self.assertEqual(result.returncode, 0)
            self.assertEqual(
                argv_file.read_text(encoding="utf-8").splitlines(),
                ["-m", "scripts.run_all", "tasks/custom.json", "outputs/custom"],
            )

    def test_retry_failed_shell_wrapper_exists_and_surfaces_usage(self):
        script_path = Path(__file__).resolve().parents[1] / "bin" / "retry_failed.sh"

        self.assertTrue(script_path.exists())
        self.assertTrue(os.access(script_path, os.X_OK))

        result = subprocess.run(
            [str(script_path)],
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Usage: python3 -m scripts.retry_failed_run", result.stderr)

    def test_report_run_shell_wrapper_exists_and_surfaces_usage(self):
        script_path = Path(__file__).resolve().parents[1] / "bin" / "report_run.sh"

        self.assertTrue(script_path.exists())
        self.assertTrue(os.access(script_path, os.X_OK))

        result = subprocess.run(
            [str(script_path)],
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Usage: python3 -m scripts.report_run", result.stderr)

    def test_fetch_filter_init_shell_wrapper_runs_fetch_then_extract(self):
        script_path = Path(__file__).resolve().parents[1] / "bin" / "fetch_filter_init.sh"

        self.assertTrue(script_path.exists())
        self.assertTrue(os.access(script_path, os.X_OK))

        with TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            fake_python = temp_path / "python3"
            argv_log = temp_path / "argv.log"
            fake_python.write_text(
                "#!/bin/sh\n"
                f"printf '%s\\n' \"$@\" >> \"{argv_log}\"\n"
                "printf -- '---\\n' >> \""
                + str(argv_log)
                + "\"\n",
                encoding="utf-8",
            )
            fake_python.chmod(0o755)

            result = subprocess.run(
                [str(script_path), "https://www.wowhead.com/items"],
                capture_output=True,
                text=True,
                check=False,
                env={**os.environ, "PATH": f"{temp_path}:{os.environ['PATH']}"},
            )

            self.assertEqual(result.returncode, 0)
            self.assertEqual(
                argv_log.read_text(encoding="utf-8").splitlines(),
                [
                    "-m",
                    "scripts.fetch_filter_page",
                    "https://www.wowhead.com/items",
                    "outputs/filter_pages/filter-page.html",
                    "---",
                    "-m",
                    "scripts.extract_filter_init",
                    "outputs/filter_pages/filter-page.html",
                    "---",
                ],
            )

    def test_fetch_filter_init_shell_wrapper_uses_custom_output_name(self):
        script_path = Path(__file__).resolve().parents[1] / "bin" / "fetch_filter_init.sh"

        self.assertTrue(script_path.exists())
        self.assertTrue(os.access(script_path, os.X_OK))

        with TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            fake_python = temp_path / "python3"
            argv_log = temp_path / "argv.log"
            fake_python.write_text(
                "#!/bin/sh\n"
                f"printf '%s\\n' \"$@\" >> \"{argv_log}\"\n"
                "printf -- '---\\n' >> \""
                + str(argv_log)
                + "\"\n",
                encoding="utf-8",
            )
            fake_python.chmod(0o755)

            result = subprocess.run(
                [str(script_path), "https://www.wowhead.com/items/weapons", "weapons"],
                capture_output=True,
                text=True,
                check=False,
                env={**os.environ, "PATH": f"{temp_path}:{os.environ['PATH']}"},
            )

            self.assertEqual(result.returncode, 0)
            self.assertEqual(
                argv_log.read_text(encoding="utf-8").splitlines(),
                [
                    "-m",
                    "scripts.fetch_filter_page",
                    "https://www.wowhead.com/items/weapons",
                    "outputs/filter_pages/weapons.html",
                    "---",
                    "-m",
                    "scripts.extract_filter_init",
                    "outputs/filter_pages/weapons.html",
                    "---",
                ],
            )

    def test_generate_mappings_shell_wrapper_runs_script_from_crawler_dir(self):
        script_path = Path(__file__).resolve().parents[1] / "bin" / "generate_mappings.sh"
        crawler_dir = Path(__file__).resolve().parents[1]

        with TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            fake_python = temp_path / "python3"
            argv_file = temp_path / "argv.txt"
            cwd_file = temp_path / "cwd.txt"
            fake_python.write_text(
                "#!/bin/sh\n"
                f"printf '%s\\n' \"$@\" > \"{argv_file}\"\n"
                f"pwd > \"{cwd_file}\"\n",
                encoding="utf-8",
            )
            fake_python.chmod(0o755)

            result = subprocess.run(
                [str(script_path), "outputs/filter_pages/normalized_mappings.json", "core/mappings_data.py"],
                capture_output=True,
                text=True,
                check=False,
                env={**os.environ, "PATH": f"{temp_path}:{os.environ['PATH']}"},
            )

            self.assertEqual(result.returncode, 0)
            self.assertEqual(
                argv_file.read_text(encoding="utf-8").splitlines(),
                ["-m", "scripts.generate_mappings", "outputs/filter_pages/normalized_mappings.json", "core/mappings_data.py"],
            )
            self.assertEqual(cwd_file.read_text(encoding="utf-8").strip(), str(crawler_dir))

    def test_update_mappings_shell_wrapper_runs_parallel_fetch_then_generators(self):
        script_path = Path(__file__).resolve().parents[1] / "bin" / "update_mappings.sh"
        crawler_dir = Path(__file__).resolve().parents[1]

        with TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            log_file = temp_path / "calls.log"
            fake_python = temp_path / "python3"
            fake_fetch = temp_path / "fetch_filter_init.sh"
            fake_generate = temp_path / "generate_mappings.sh"

            fake_python.write_text(
                "#!/bin/sh\n"
                f"printf 'python %s\\n' \"$*\" >> \"{log_file}\"\n",
                encoding="utf-8",
            )
            fake_fetch.write_text(
                "#!/bin/sh\n"
                f"printf 'fetch %s %s %s\\n' \"$1\" \"$2\" \"$(pwd)\" >> \"{log_file}\"\n",
                encoding="utf-8",
            )
            fake_generate.write_text(
                "#!/bin/sh\n"
                f"printf 'generate %s\\n' \"$(pwd)\" >> \"{log_file}\"\n",
                encoding="utf-8",
            )

            fake_python.chmod(0o755)
            fake_fetch.chmod(0o755)
            fake_generate.chmod(0o755)

            result = subprocess.run(
                [str(script_path)],
                capture_output=True,
                text=True,
                check=False,
                env={
                    **os.environ,
                    "PYTHON_BIN": str(fake_python),
                    "FETCH_FILTER_INIT_BIN": str(fake_fetch),
                    "GENERATE_MAPPINGS_BIN": str(fake_generate),
                },
            )

            self.assertEqual(result.returncode, 0)
            self.assertIn("Starting parallel Filter.init fetch for armor and weapons...", result.stdout)
            self.assertIn("Generating normalized mappings...", result.stdout)
            self.assertIn("Generating crawler mappings module...", result.stdout)
            self.assertIn("Mappings update completed successfully.", result.stdout)
            lines = log_file.read_text(encoding="utf-8").splitlines()
            self.assertEqual(
                set(lines[:2]),
                {
                    f"fetch https://www.wowhead.com/items/armor armor {crawler_dir}",
                    f"fetch https://www.wowhead.com/items/weapons weapons {crawler_dir}",
                },
            )
            self.assertEqual(
                lines[2:],
                [
                    "python -m scripts.generate_normalized_mappings",
                    f"generate {crawler_dir}",
                ],
            )

    def test_update_mappings_shell_wrapper_stops_when_fetch_fails(self):
        script_path = Path(__file__).resolve().parents[1] / "bin" / "update_mappings.sh"

        with TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            log_file = temp_path / "calls.log"
            fake_python = temp_path / "python3"
            fake_fetch = temp_path / "fetch_filter_init.sh"
            fake_generate = temp_path / "generate_mappings.sh"

            fake_python.write_text(
                "#!/bin/sh\n"
                f"printf 'python called\\n' >> \"{log_file}\"\n",
                encoding="utf-8",
            )
            fake_fetch.write_text(
                "#!/bin/sh\n"
                f"printf 'fetch %s %s\\n' \"$1\" \"$2\" >> \"{log_file}\"\n"
                "if [ \"$2\" = \"weapons\" ]; then\n"
                "  exit 9\n"
                "fi\n",
                encoding="utf-8",
            )
            fake_generate.write_text(
                "#!/bin/sh\n"
                f"printf 'generate called\\n' >> \"{log_file}\"\n",
                encoding="utf-8",
            )

            fake_python.chmod(0o755)
            fake_fetch.chmod(0o755)
            fake_generate.chmod(0o755)

            result = subprocess.run(
                [str(script_path)],
                capture_output=True,
                text=True,
                check=False,
                env={
                    **os.environ,
                    "PYTHON_BIN": str(fake_python),
                    "FETCH_FILTER_INIT_BIN": str(fake_fetch),
                    "GENERATE_MAPPINGS_BIN": str(fake_generate),
                },
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Starting parallel Filter.init fetch for armor and weapons...", result.stdout)
            self.assertIn("Failed to refresh Filter.init data.", result.stderr)
            lines = log_file.read_text(encoding="utf-8").splitlines()
            self.assertIn("fetch https://www.wowhead.com/items/armor armor", lines)
            self.assertIn("fetch https://www.wowhead.com/items/weapons weapons", lines)
            self.assertNotIn("python called", lines)
            self.assertNotIn("generate called", lines)

    def test_generate_mappings_reads_normalized_json_and_writes_module(self):
        with TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            normalized_path = temp_path / "normalized_mappings.json"
            output_path = temp_path / "mappings_data.py"
            normalized_path.write_text(
                json.dumps(
                    {
                        "categories": {"armor": {"path": "armor"}, "weapon": {"path": "weapons"}},
                        "qualities": [
                            {"value": 2, "label": "Uncommon"},
                            {"value": 3, "label": "Rare"},
                            {"value": 4, "label": "Epic"},
                        ],
                        "slots": {
                            "armor": [{"value": 1, "label": "Head"}],
                            "weapon": [{"value": 21, "label": "Main Hand"}],
                        },
                        "types": {
                            "armor": [{"value": 1, "label": "Cloth Armor"}],
                            "weapon": [{"value": 15, "label": "Daggers"}],
                        },
                        "query_filters": [
                            {"id": 8, "label": "Disenchantable", "values": [{"value": 1, "label": "Yes"}, {"value": 2, "label": "No"}]},
                            {"id": 161, "label": "Available to players", "values": [{"value": 1, "label": "Yes"}, {"value": 2, "label": "No"}]},
                            {"id": 195, "label": "Can be worn/equipped", "values": [{"value": 1, "label": "Yes"}, {"value": 2, "label": "No"}]},
                        ],
                    },
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding="utf-8",
            )

            written_path = run_generate_mappings([str(normalized_path), str(output_path)])

            self.assertEqual(written_path, output_path)
            module_text = output_path.read_text(encoding="utf-8")
            self.assertIn('"main_hand_21"', module_text)
            self.assertIn('"daggers_15"', module_text)
            self.assertIn('"can_be_worn_equipped"', module_text)
            self.assertNotIn("def normalize_task", module_text)

    def test_generate_normalized_mappings_reads_local_files_and_writes_output(self):
        with TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            armor_html = temp_path / "armor.html"
            armor_filters = temp_path / "armor.filters.json"
            weapons_html = temp_path / "weapons.html"
            weapons_filters = temp_path / "weapons.filters.json"
            output_path = temp_path / "normalized_mappings.json"

            armor_html.write_text(
                '<select id="filter-facet-quality"><option value="2">Uncommon</option><option value="3">Rare</option><option value="4">Epic</option></select>'
                '<select id="filter-facet-slot"><option value="1">Head</option></select>'
                '<select id="filter-facet-type"><option value="1">Cloth Armor</option></select>',
                encoding="utf-8",
            )
            weapons_html.write_text(
                '<select id="filter-facet-quality"><option value="2">Uncommon</option><option value="3">Rare</option><option value="4">Epic</option></select>'
                '<select id="filter-facet-slot"><option value="21">Main Hand</option></select>'
                '<select id="filter-facet-type"><option value="15">Daggers</option></select>',
                encoding="utf-8",
            )
            filters_json = json.dumps(
                {
                    "filters": [
                        {"id": 8, "name": "Disenchantable", "options": [[1, "Yes"], [2, "No"]]},
                        {"id": 161, "name": "Available to players", "options": [[1, "Yes"], [2, "No"]]},
                        {"id": 195, "name": "Can be worn/equipped", "options": [[1, "Yes"], [2, "No"]]},
                    ]
                },
                ensure_ascii=False,
            )
            armor_filters.write_text(filters_json, encoding="utf-8")
            weapons_filters.write_text(filters_json, encoding="utf-8")

            written_path = run_generate_normalized_mappings(
                [
                    str(armor_html),
                    str(armor_filters),
                    str(weapons_html),
                    str(weapons_filters),
                    str(output_path),
                ]
            )

            self.assertEqual(written_path, output_path)
            written = json.loads(output_path.read_text(encoding="utf-8"))
            self.assertEqual(written["categories"]["armor"]["path"], "armor")
            self.assertEqual(written["types"]["weapon"], [{"value": 15, "label": "Daggers"}])

    def test_generate_run_creates_manifest_file(self):
        with TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            task_file = temp_path / "tasks.json"
            task_file.write_text(
                json.dumps(
                    [
                        {
                            "task_id": "uncommon-head-cloth",
                            "enabled": True,
                            "quality": "uncommon",
                            "category": "armor",
                            "slot": "head_1",
                            "type": "cloth_armor_1",
                            "query_filters": {},
                        }
                    ],
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding="utf-8",
            )

            manifest_path = run_generate([str(task_file), str(temp_path / "outputs")])

            self.assertTrue(manifest_path.exists())
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            self.assertEqual(manifest["task_count"], 1)
            self.assertEqual(manifest["tasks"][0]["task_id"], "uncommon-head-cloth")

    def test_fetch_run_consumes_manifest_and_writes_result(self):
        with TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            manifest_path = temp_path / "manifest.json"
            manifest_path.write_text(
                json.dumps(
                    {
                        "run_id": "2026-03-14T15-30-00",
                        "generated_at": "2026-03-14T15:30:00+08:00",
                        "task_file": "tasks/example.json",
                        "task_count": 1,
                        "tasks": [
                            {
                                "task_id": "uncommon-head-cloth",
                                "status": "planned",
                                "url": "https://example.com/items/1",
                                "category": "armor",
                                "slot": "head_1",
                                "type": "cloth_armor_1",
                                "quality": "uncommon",
                                "query_filters": {},
                            }
                        ],
                    },
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding="utf-8",
            )

            processed_manifest_path = run_fetch(
                [str(manifest_path)],
                fetch_url=lambda _url: '<script>var listviewitems = [{"id":2620,"name":"Augural Shroud"}];</script>',
            )

            self.assertEqual(processed_manifest_path, manifest_path)
            results = json.loads((temp_path / "items.by-task.json").read_text(encoding="utf-8"))
            self.assertIn("uncommon-head-cloth", results)
            updated_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            self.assertEqual(updated_manifest["tasks"][0]["status"], "fetched")

    def test_aggregate_run_writes_unique_items_file(self):
        with TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            manifest_path = temp_path / "manifest.json"
            manifest_path.write_text(
                json.dumps(
                    {
                        "run_id": "2026-03-14T15-30-00",
                        "generated_at": "2026-03-14T15:30:00+08:00",
                        "task_file": "tasks/example.json",
                        "task_count": 2,
                        "tasks": [
                            {"task_id": "task-a", "status": "fetched"},
                            {"task_id": "task-b", "status": "fetched"},
                        ],
                    },
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding="utf-8",
            )
            (temp_path / "items.by-task.json").write_text(
                json.dumps(
                    {
                        "task-a": {
                            "task_id": "task-a",
                            "url": "https://example.com/a",
                            "items": [
                                {"itemId": 1001, "name": "Alpha Hood"},
                                {"itemId": 1002, "name": "Beta Hood"},
                            ],
                        },
                        "task-b": {
                            "task_id": "task-b",
                            "url": "https://example.com/b",
                            "items": [
                                {"itemId": 1002, "name": "Beta Hood Duplicate"},
                                {"itemId": 1003, "name": "Gamma Hood"},
                            ],
                        },
                    },
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding="utf-8",
            )

            output_path = run_aggregate([str(manifest_path)])

            self.assertEqual(output_path, temp_path / "items.unique.json")
            self.assertTrue(output_path.exists())
            output_items = json.loads(output_path.read_text(encoding="utf-8"))
            self.assertEqual(
                output_items,
                [
                    {"itemId": 1001, "name": "Alpha Hood"},
                    {"itemId": 1002, "name": "Beta Hood"},
                    {"itemId": 1003, "name": "Gamma Hood"},
                ],
            )

    def test_retry_failed_run_raises_when_manifest_still_contains_planned_tasks(self):
        with TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            manifest_path = temp_path / "manifest.json"
            manifest_path.write_text(
                json.dumps(
                    {
                        "run_id": "2026-03-14T15-30-00",
                        "generated_at": "2026-03-14T15:30:00+08:00",
                        "task_file": "tasks/example.json",
                        "task_count": 2,
                        "tasks": [
                            {"task_id": "planned-task", "status": "planned", "url": "https://example.com/planned"},
                            {"task_id": "failed-task", "status": "failed", "url": "https://example.com/failed"},
                        ],
                    },
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding="utf-8",
            )

            with self.assertRaisesRegex(ValueError, "planned"):
                run_retry_failed(
                    [str(manifest_path)],
                    fetch_url=lambda _url: '<script>var listviewitems = [{"id":2620,"name":"Augural Shroud"}];</script>',
                )

            results = json.loads((temp_path / "items.by-task.json").read_text(encoding="utf-8"))
            self.assertIn("failed-task", results)
            self.assertTrue((temp_path / "items.unique.json").exists())
            self.assertFalse((temp_path / "planned-task.json").exists())
            updated_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            self.assertEqual(updated_manifest["tasks"][0]["status"], "planned")
            self.assertEqual(updated_manifest["tasks"][1]["status"], "fetched")
            self.assertFalse((temp_path / "NonDisenchantableByWowhead.lua").exists())

    def test_retry_failed_run_retries_then_aggregates_and_exports(self):
        with TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            manifest_path = temp_path / "manifest.json"
            output_path = temp_path / "NonDisenchantableByWowhead.lua"
            manifest_path.write_text(
                json.dumps(
                    {
                        "run_id": "2026-03-14T15-30-00",
                        "generated_at": "2026-03-14T15:30:00+08:00",
                        "task_file": "tasks/example.json",
                        "task_count": 2,
                        "tasks": [
                            {"task_id": "done-task", "status": "fetched", "url": "https://example.com/done"},
                            {"task_id": "failed-task", "status": "failed", "url": "https://example.com/failed"},
                        ],
                    },
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding="utf-8",
            )
            (temp_path / "items.by-task.json").write_text(
                json.dumps(
                    {
                        "done-task": {
                            "task_id": "done-task",
                            "url": "https://example.com/done",
                            "items": [
                                {"itemId": 1001, "name": "Alpha Hood"},
                            ],
                        },
                    },
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding="utf-8",
            )

            processed_manifest_path = run_retry_failed(
                [str(manifest_path)],
                fetch_url=lambda _url: '<script>var listviewitems = [{"id":1002,"name":"Beta Hood"}];</script>',
                export_output_path=output_path,
            )

            self.assertEqual(processed_manifest_path, manifest_path)
            results = json.loads((temp_path / "items.by-task.json").read_text(encoding="utf-8"))
            self.assertIn("failed-task", results)
            self.assertTrue((temp_path / "items.unique.json").exists())
            self.assertTrue(output_path.exists())
            unique_items = json.loads((temp_path / "items.unique.json").read_text(encoding="utf-8"))
            self.assertEqual(
                unique_items,
                [
                    {"itemId": 1001, "name": "Alpha Hood"},
                    {"itemId": 1002, "name": "Beta Hood"},
                ],
            )
            self.assertIn("[1001] = true", output_path.read_text(encoding="utf-8"))
            self.assertIn("[1002] = true", output_path.read_text(encoding="utf-8"))

    def test_run_all_orchestrates_generate_fetch_and_aggregate(self):
        with TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            task_file = temp_path / "tasks.json"
            output_path = temp_path / "NonDisenchantableByWowhead.lua"
            task_file.write_text(
                json.dumps(
                    [
                        {
                            "task_id": "uncommon-head-cloth",
                            "enabled": True,
                            "quality": "uncommon",
                            "category": "armor",
                            "slot": "head_1",
                            "type": "cloth_armor_1",
                            "query_filters": {},
                        }
                    ],
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding="utf-8",
            )

            manifest_path = run_all(
                [str(task_file), str(temp_path / "outputs")],
                fetch_url=lambda _url: '<script>var listviewitems = [{"id":2620,"name":"Augural Shroud"}];</script>',
                export_output_path=output_path,
            )

            self.assertTrue(manifest_path.exists())
            results = json.loads((manifest_path.parent / "items.by-task.json").read_text(encoding="utf-8"))
            self.assertIn("uncommon-head-cloth", results)
            self.assertTrue((manifest_path.parent / "items.unique.json").exists())
            self.assertTrue(output_path.exists())
            unique_items = json.loads((manifest_path.parent / "items.unique.json").read_text(encoding="utf-8"))
            self.assertEqual(unique_items, [{"itemId": 2620, "name": "Augural Shroud"}])

    def test_run_all_raises_when_export_detects_incomplete_manifest(self):
        with TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            task_file = temp_path / "tasks.json"
            task_file.write_text(
                json.dumps(
                    [
                        {
                            "task_id": "will-fail",
                            "enabled": True,
                            "quality": "uncommon",
                            "category": "armor",
                            "slot": "head_1",
                            "type": "cloth_armor_1",
                            "query_filters": {},
                        }
                    ],
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding="utf-8",
            )

            with self.assertRaisesRegex(ValueError, "failed"):
                run_all(
                    [str(task_file), str(temp_path / "outputs")],
                    fetch_url=lambda _url: (_ for _ in ()).throw(RuntimeError("network fail")),
                )

    def test_export_lua_writes_lua_data_file_from_complete_manifest(self):
        with TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            manifest_path = temp_path / "manifest.json"
            items_unique_path = temp_path / "items.unique.json"
            output_path = temp_path / "NonDisenchantableByWowhead.lua"
            manifest_path.write_text(
                json.dumps(
                    {
                        "run_id": "2026-03-14T15-30-00",
                        "generated_at": "2026-03-14T15:30:00+08:00",
                        "task_file": "tasks/example.json",
                        "task_count": 2,
                        "tasks": [
                            {"task_id": "task-a", "status": "fetched"},
                            {"task_id": "task-b", "status": "fetched"},
                        ],
                    },
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding="utf-8",
            )
            items_unique_path.write_text(
                json.dumps(
                    [
                        {"itemId": 1002, "name": "Beta Hood"},
                        {"itemId": 1001, "name": "Alpha Hood"},
                    ],
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding="utf-8",
            )

            written_path = run_export_lua([str(manifest_path), str(output_path)])

            self.assertEqual(written_path, output_path)
            self.assertTrue(output_path.exists())
            self.assertIn("[1001] = true", output_path.read_text(encoding="utf-8"))

    def test_export_lua_rejects_incomplete_manifest(self):
        with TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            manifest_path = temp_path / "manifest.json"
            output_path = temp_path / "NonDisenchantableByWowhead.lua"
            manifest_path.write_text(
                json.dumps(
                    {
                        "run_id": "2026-03-14T15-30-00",
                        "generated_at": "2026-03-14T15:30:00+08:00",
                        "task_file": "tasks/example.json",
                        "task_count": 1,
                        "tasks": [
                            {"task_id": "task-a", "status": "failed"},
                        ],
                    },
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding="utf-8",
            )
            (temp_path / "items.unique.json").write_text("[]", encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "failed"):
                run_export_lua([str(manifest_path), str(output_path)])

            self.assertFalse(output_path.exists())

    def test_report_run_writes_run_report_json(self):
        with TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            manifest_path = temp_path / "manifest.json"
            output_path = temp_path / "run-report.json"
            manifest_path.write_text(
                json.dumps(
                    {
                        "run_id": "2026-03-14T15-30-00",
                        "generated_at": "2026-03-14T15:30:00+08:00",
                        "task_file": "tasks/example.json",
                        "task_count": 2,
                        "tasks": [
                            {"task_id": "done-task", "status": "fetched"},
                            {"task_id": "empty-task", "status": "fetched"},
                        ],
                    },
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding="utf-8",
            )
            (temp_path / "items.by-task.json").write_text(
                json.dumps(
                    {
                        "done-task": {"task_id": "done-task", "items": [{"itemId": 1001, "name": "Alpha Hood"}]},
                        "empty-task": {"task_id": "empty-task", "items": []},
                    },
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding="utf-8",
            )
            (temp_path / "items.unique.json").write_text(
                json.dumps(
                    [{"itemId": 1001, "name": "Alpha Hood"}],
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding="utf-8",
            )

            written_path = run_report([str(manifest_path), str(output_path)])

            self.assertEqual(written_path, output_path)
            report = json.loads(output_path.read_text(encoding="utf-8"))
            self.assertEqual(report["empty_result_task_ids"], ["empty-task"])
            self.assertEqual(report["unique_item_count"], 1)

    def test_quickdisenchant_toc_includes_wowhead_data_file(self):
        toc_path = Path(__file__).resolve().parents[2] / "QuickDisenchant" / "QuickDisenchant.toc"
        toc_text = toc_path.read_text(encoding="utf-8")
        self.assertIn("NonDisenchantableByWowhead.lua", toc_text)


if __name__ == "__main__":
    unittest.main()
