import subprocess
from contextlib import contextmanager
from pathlib import Path
from tempfile import NamedTemporaryFile
from unittest import TestCase, mock

import word_occurrences


class WordOccurrencesFunctionsTestCase(TestCase):
    """
    Test separate functions of the script.
    """

    def test_split_words_func(self):
        expected = ['occurrences', 'mary\'s', 'some', 'text', 'texts', 'with']

        actual = word_occurrences.split_to_word_func(
            'some. mary\'s text\'! ;with:?! , texts, ,occurrences?'
        )

        self.assertListEqual(sorted(actual), sorted(expected))

    def test_count_word_occurrences(self):
        expected = {'w1': 1, 'w2': 2, 'w3': 3}

        actual = dict(word_occurrences.count_word_occurrences(
            'w3 w1 w2 w3 w2 w3',
            split_func=str.split
        ))

        self.assertDictEqual(actual, expected)

    def test_sorting(self):
        expected = (('w1', 3), ('w2', 2), ('w3', 2), ('w4', 1))

        actual = word_occurrences.sort_by_occurrences(
            {'w4': 1, 'w2': 2, 'w1': 3, 'w3': 2}
        )

        self.assertListEqual(list(actual), list(expected))

    def test_format_with_colon(self):
        expected = 'w1: 3'

        actual = word_occurrences.format_with_colon(('w1', 3))

        self.assertEqual(actual, expected)

    def test_print_to_stdout(self):
        with mock.patch('sys.stdout.write') as mocked_write:
            word_occurrences.print_statistic(
                (('w1', 3), ('w2', 2), ('w3', 2), ('w4', 1)),
                formatter=lambda item: f'{item[0]}: {item[1]}'
            )

        mocked_write.assert_has_calls([
            mock.call('w1: 3\n'),
            mock.call('w2: 2\n'),
            mock.call('w3: 2\n'),
            mock.call('w4: 1\n'),
        ])


class WordOccurrencesScriptTestCase(TestCase):
    """
    Test the script itself.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        script_path = Path.cwd() / Path('word_occurrences.py')
        cls.run_args = ('python3', script_path)

    @contextmanager
    def get_file_with_data(self, data: str):
        with NamedTemporaryFile() as tmp_file:
            tmp_file.write(data.encode())
            tmp_file.flush()
            yield tmp_file

    def test_script_needs_filename(self):
        with self.assertRaises(subprocess.CalledProcessError) as exc:
            subprocess.check_output(self.run_args, stderr=subprocess.PIPE)

        self.assertIn(
            'error: the following arguments are required: file',
            exc.exception.stderr.decode()
        )

    def test_script_output(self):
        data = 'Some, :word\'s! ,occurrences, :,data? to check word\'s ' \
                 'occurrences data full-stack'

        expected = 'data: 2\n' \
                   'occurrences: 2\n' \
                   'word\'s: 2\n' \
                   'Some: 1\n' \
                   'check: 1\n' \
                   'full-stack: 1\n' \
                   'to: 1\n'

        with self.get_file_with_data(data) as file:
            actual = subprocess.check_output(self.run_args + (file.name,))

        self.assertEqual(actual, expected.encode())

    def test_script_with_empty_file(self):
        expected = ''

        with self.get_file_with_data(expected) as file:
            actual = subprocess.check_output(self.run_args + (file.name,))

        self.assertEqual(actual, expected.encode())
