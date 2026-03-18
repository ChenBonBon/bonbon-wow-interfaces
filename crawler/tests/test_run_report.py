import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from core.run_report import write_run_report
from scripts.report_run import run as run_report


class RunReportTest(unittest.TestCase):
    def test_write_run_report_writes_json_summary_with_empty_and_failed_tasks(self):
        with TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            manifest_path = temp_path / 'manifest.json'
            output_path = temp_path / 'run-report.json'
            manifest_path.write_text(
                json.dumps(
                    {
                        'run_id': '2026-03-18T10-00-00',
                        'generated_at': '2026-03-18T10:00:00+08:00',
                        'task_file': 'tasks/example.json',
                        'task_count': 4,
                        'tasks': [
                            {'task_id': 'done-task', 'status': 'fetched'},
                            {'task_id': 'empty-task', 'status': 'fetched'},
                            {'task_id': 'failed-task', 'status': 'failed'},
                            {'task_id': 'planned-task', 'status': 'planned'},
                        ],
                    },
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding='utf-8',
            )
            (temp_path / 'done-task.json').write_text(
                json.dumps(
                    {
                        'task_id': 'done-task',
                        'items': [{'itemId': 1001, 'name': 'Alpha Hood'}],
                    },
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding='utf-8',
            )
            (temp_path / 'empty-task.json').write_text(
                json.dumps(
                    {
                        'task_id': 'empty-task',
                        'items': [],
                    },
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding='utf-8',
            )
            (temp_path / 'items.unique.json').write_text(
                json.dumps(
                    [{'itemId': 1001, 'name': 'Alpha Hood'}],
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding='utf-8',
            )

            written_path = write_run_report(manifest_path, output_path=output_path)

            self.assertEqual(written_path, output_path)
            report = json.loads(output_path.read_text(encoding='utf-8'))
            self.assertEqual(report['run_id'], '2026-03-18T10-00-00')
            self.assertEqual(report['task_count'], 4)
            self.assertEqual(report['fetched_count'], 2)
            self.assertEqual(report['failed_count'], 1)
            self.assertEqual(report['planned_count'], 1)
            self.assertEqual(report['unique_item_count'], 1)
            self.assertEqual(report['failed_task_ids'], ['failed-task'])
            self.assertEqual(report['empty_result_task_ids'], ['empty-task'])

    def test_script_run_defaults_to_report_json_in_run_directory(self):
        with TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            manifest_path = temp_path / 'manifest.json'
            manifest_path.write_text(
                json.dumps(
                    {
                        'run_id': '2026-03-18T10-00-00',
                        'generated_at': '2026-03-18T10:00:00+08:00',
                        'task_file': 'tasks/example.json',
                        'task_count': 1,
                        'tasks': [{'task_id': 'done-task', 'status': 'fetched'}],
                    },
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding='utf-8',
            )
            (temp_path / 'done-task.json').write_text(
                json.dumps({'task_id': 'done-task', 'items': []}, ensure_ascii=False, indent=2),
                encoding='utf-8',
            )
            (temp_path / 'items.unique.json').write_text('[]', encoding='utf-8')

            output_path = run_report([str(manifest_path)])

            self.assertEqual(output_path, temp_path / 'run-report.json')
            self.assertTrue(output_path.exists())


if __name__ == '__main__':
    unittest.main()
