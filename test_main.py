import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import pymupdf

import main


class PdfToolTests(unittest.TestCase):
    def create_pdf(self, path: Path, text: str) -> None:
        document = pymupdf.open()
        page = document.new_page()
        page.insert_text((72, 72), text)
        document.save(path)
        document.close()

    def test_merge_pdfs_orders_by_file_name_and_creates_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            input_folder = base / "arquivos"
            input_folder.mkdir()
            self.create_pdf(input_folder / "02-segundo.pdf", "Segundo documento")
            self.create_pdf(input_folder / "01-primeiro.pdf", "Primeiro documento")

            output_pdf = base / "saida" / "pdf_juntado.pdf"
            processed = main.merge_pdfs(input_folder, output_pdf)

            self.assertEqual(["01-primeiro.pdf", "02-segundo.pdf"], [p.name for p in processed])
            self.assertTrue(output_pdf.exists())

            merged = pymupdf.open(output_pdf)
            try:
                self.assertEqual(2, merged.page_count)
                self.assertIn("Primeiro documento", merged[0].get_text())
                self.assertIn("Segundo documento", merged[1].get_text())
            finally:
                merged.close()

    def test_merge_pdfs_requires_existing_input_folder(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(FileNotFoundError):
                main.merge_pdfs(Path(tmp) / "nao-existe", Path(tmp) / "saida.pdf")

    def test_merge_pdfs_requires_pdf_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            input_folder = Path(tmp) / "arquivos"
            input_folder.mkdir()

            with self.assertRaises(FileNotFoundError):
                main.merge_pdfs(input_folder, Path(tmp) / "saida.pdf")

    def test_format_file_size_uses_bytes_kb_and_mb(self):
        self.assertEqual("512 bytes", main.format_file_size(512))
        self.assertEqual("1.0 KB", main.format_file_size(1024))
        self.assertEqual("1.0 MB", main.format_file_size(1024 * 1024))

    def test_calculate_reduction_percentage_handles_normal_and_zero_sizes(self):
        self.assertEqual(71.7, main.calculate_reduction_percentage(184, 52))
        self.assertEqual(0.0, main.calculate_reduction_percentage(0, 52))

    def test_normalize_quality_accepts_cli_and_ghostscript_values(self):
        self.assertEqual("/ebook", main.normalize_quality("ebook"))
        self.assertEqual("/screen", main.normalize_quality("/screen"))

        with self.assertRaises(ValueError):
            main.normalize_quality("low")

    @patch("main.subprocess.run")
    @patch("main.shutil.which")
    def test_compress_with_ghostscript_builds_expected_command(self, which, run):
        which.side_effect = lambda name: "/usr/bin/gs" if name == "gs" else None

        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            input_pdf = base / "pdf_juntado.pdf"
            output_pdf = base / "pdf_final.pdf"
            input_pdf.write_bytes(b"%PDF-1.4")

            main.compress_with_ghostscript(input_pdf, output_pdf, "screen")

        run.assert_called_once()
        command = run.call_args.args[0]
        self.assertEqual("/usr/bin/gs", command[0])
        self.assertIn("-dPDFSETTINGS=/screen", command)
        self.assertIn(f"-sOutputFile={output_pdf}", command)
        self.assertEqual(True, run.call_args.kwargs["check"])

    @patch("main.Path.glob", return_value=[])
    @patch("main.shutil.which", return_value=None)
    def test_compress_with_ghostscript_explains_missing_executable(self, _which, _glob):
        with tempfile.TemporaryDirectory() as tmp:
            input_pdf = Path(tmp) / "pdf_juntado.pdf"
            input_pdf.write_bytes(b"%PDF-1.4")

            with self.assertRaisesRegex(RuntimeError, "Ghostscript nao encontrado"):
                main.compress_with_ghostscript(input_pdf, Path(tmp) / "final.pdf", "ebook")

    @patch.dict("main.os.environ", {"GHOSTSCRIPT_PATH": r"C:\tools\gs\bin\gswin64c.exe"})
    @patch("main.Path.exists", return_value=True)
    @patch("main.shutil.which", return_value=None)
    def test_find_ghostscript_executable_accepts_environment_path(self, _which, _exists):
        self.assertEqual(r"C:\tools\gs\bin\gswin64c.exe", main.find_ghostscript_executable())

    @patch.dict("main.os.environ", {}, clear=True)
    @patch("main.os.name", "nt")
    @patch("main.Path.glob")
    @patch("main.shutil.which", return_value=None)
    def test_find_ghostscript_executable_searches_common_windows_folder(self, _which, glob):
        candidate = Path(r"C:\Program Files\gs\gs10.07.1\bin\gswin64c.exe")
        glob.side_effect = [[candidate], []]

        self.assertEqual(str(candidate), main.find_ghostscript_executable())

    def test_validate_output_path_refuses_overwrite_without_force(self):
        with tempfile.TemporaryDirectory() as tmp:
            output_pdf = Path(tmp) / "saida" / "pdf_final.pdf"
            output_pdf.parent.mkdir()
            output_pdf.write_bytes(b"arquivo existente")

            with self.assertRaises(FileExistsError):
                main.validate_output_path(output_pdf, force=False)

            main.validate_output_path(output_pdf, force=True)


if __name__ == "__main__":
    unittest.main()
