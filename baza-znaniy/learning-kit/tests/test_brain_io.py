import importlib.util
from pathlib import Path
import tempfile
import unittest

MODULE = Path(__file__).resolve().parents[1] / 'brain_io.py'
spec = importlib.util.spec_from_file_location('brain_io', MODULE)
io = importlib.util.module_from_spec(spec)
spec.loader.exec_module(io)


class LocalAdapterTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.vault = self.root / 'vault'
        self.vault.mkdir()
        (self.vault / '04_inbox').mkdir()
        (self.vault / 'public.md').write_text('Факт: 7 проверок', encoding='utf-8')
        (self.vault / 'credentials.md').write_text('FAKE-SECRET', encoding='utf-8')
        self.addCleanup(self.temp.cleanup)

    def test_export_only_explicit_files_and_hash(self):
        result = io.export_context(self.vault, ['public.md'])
        self.assertIn('Факт: 7 проверок', result)
        self.assertIn('SHA256:', result)
        self.assertNotIn('FAKE-SECRET', result)

    def test_sensitive_name_refused_even_if_explicit(self):
        for name in ['credentials.md', 'CREDENTIALS.md', '.env.md', '.obsidian/data.md']:
            with self.subTest(name=name), self.assertRaises(ValueError):
                io.read_note(self.vault, name)

    def test_traversal_absolute_and_ambiguous_paths_refused(self):
        for name in ['../public.md', '/etc/public.md', 'x/../public.md', 'x//a.md', './public.md', 'x\\a.md']:
            with self.subTest(name=name), self.assertRaises(ValueError):
                io.read_note(self.vault, name)

    def test_symlink_file_and_directory_refused(self):
        (self.root / 'outside.md').write_text('outside')
        (self.vault / 'link.md').symlink_to(self.root / 'outside.md')
        (self.vault / 'linked').symlink_to(self.root, target_is_directory=True)
        for name in ['link.md', 'linked/outside.md']:
            with self.subTest(name=name), self.assertRaises(OSError):
                io.read_note(self.vault, name)

    def test_new_note_roundtrip_and_duplicate_preserved(self):
        name = io.import_reviewed(self.vault, 'lesson.md', 'Проверенный опыт', True)
        self.assertEqual(io.read_note(self.vault, name), 'Проверенный опыт')
        with self.assertRaises(FileExistsError):
            io.import_reviewed(self.vault, 'lesson.md', 'Новый текст', True)
        self.assertEqual(io.read_note(self.vault, name), 'Проверенный опыт')

    def test_import_requires_review_and_safe_name(self):
        with self.assertRaises(ValueError):
            io.import_reviewed(self.vault, 'lesson.md', 'text', False)
        for name in ['../other.md', '/tmp/other.md', 'x/y.md', '.hidden.md']:
            with self.subTest(name=name), self.assertRaises(ValueError):
                io.import_reviewed(self.vault, name, 'text', True)

    def test_import_rejects_symlink_inbox_and_existing_symlink(self):
        (self.vault / '04_inbox' / 'lesson.md').symlink_to(self.root / 'outside.md')
        with self.assertRaises(FileExistsError):
            io.import_reviewed(self.vault, 'lesson.md', 'text', True)
        (self.vault / '04_inbox' / 'lesson.md').unlink()
        (self.vault / '04_inbox').rmdir()
        (self.vault / '04_inbox').symlink_to(self.root, target_is_directory=True)
        with self.assertRaises(OSError):
            io.import_reviewed(self.vault, 'lesson.md', 'text', True)
        self.assertFalse((self.root / 'lesson.md').exists())

    def test_oversize_and_empty_rejected(self):
        for value in ['', 'a' * (io.MAX_BYTES + 1)]:
            with self.assertRaises(ValueError):
                io.import_reviewed(self.vault, 'lesson.md', value, True)
        (self.vault / 'big.md').write_text('a' * (io.MAX_BYTES + 1))
        with self.assertRaises(ValueError):
            io.export_context(self.vault, ['big.md'])

    def test_symlink_root_refused(self):
        link = self.root / 'root-link'
        link.symlink_to(self.vault, target_is_directory=True)
        with self.assertRaises(ValueError):
            io.read_note(link, 'public.md')


if __name__ == '__main__':
    unittest.main()
