import os
import tempfile
import unittest
from contextlib import contextmanager

from linkml.validator.loaders import CsvLoader, TsvLoader


@contextmanager
def data_file(test_data: str):
    file = tempfile.NamedTemporaryFile(mode="w+", delete=False)
    file.write(test_data)
    file.close()

    yield file.name

    os.unlink(file.name)


class TestDelimitedFileLoader(unittest.TestCase):
    def test_load(self):
        for d, loader_cls in [(",", CsvLoader), ("\t", TsvLoader)]:
            with self.subTest(loader=loader_cls):
                data = f"""one{d} two{d} three{d} four
1{d} 2.0001{d} three{d} 4.4.4
"""
                with data_file(data) as f:
                    loader = loader_cls(f)
                    instances = loader.iter_instances()
                    self.assertEqual(
                        next(instances),
                        {"one": 1, "two": 2.0001, "three": "three", "four": "4.4.4"},
                    )
                    self.assertRaises(StopIteration, lambda: next(instances))

    def test_load_empty_rows(self):
        data = """one, two, three
a, b, c
,,
d, e, f
"""
        with data_file(data) as csv_file:
            loader = CsvLoader(csv_file)
            instances = loader.iter_instances()
            self.assertEqual(next(instances), {"one": "a", "two": "b", "three": "c"})
            self.assertEqual(next(instances), {"one": "", "two": "", "three": ""})
            self.assertEqual(next(instances), {"one": "d", "two": "e", "three": "f"})
            self.assertRaises(StopIteration, lambda: next(instances))

            loader = CsvLoader(csv_file, skip_empty_rows=True)
            instances = loader.iter_instances()
            self.assertEqual(next(instances), {"one": "a", "two": "b", "three": "c"})
            self.assertEqual(next(instances), {"one": "d", "two": "e", "three": "f"})
            self.assertRaises(StopIteration, lambda: next(instances))

    def test_load_index_slot(self):
        data = """one, two, three
a, b, c
d, e, f
"""
        with data_file(data) as csv_file:
            loader = CsvLoader(csv_file, index_slot_name="some_things")
            instances = loader.iter_instances()
            self.assertEqual(
                next(instances),
                {
                    "some_things": [
                        {"one": "a", "two": "b", "three": "c"},
                        {"one": "d", "two": "e", "three": "f"},
                    ]
                },
            )
            self.assertRaises(StopIteration, lambda: next(instances))
