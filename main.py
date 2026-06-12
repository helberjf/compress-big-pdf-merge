from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pymupdf


VALID_QUALITIES = {
    "screen": "/screen",
    "ebook": "/ebook",
    "printer": "/printer",
    "prepress": "/prepress",
}


def format_file_size(size_in_bytes: int) -> str:
    """Format bytes as bytes, KB, or MB."""
    if size_in_bytes < 1024:
        return f"{size_in_bytes} bytes"

    if size_in_bytes < 1024 * 1024:
        return f"{size_in_bytes / 1024:.1f} KB"

    return f"{size_in_bytes / (1024 * 1024):.1f} MB"


def calculate_reduction_percentage(original_size: int, compressed_size: int) -> float:
    """Return the percentage reduction from original_size to compressed_size."""
    if original_size <= 0:
        return 0.0

    reduction = ((original_size - compressed_size) / original_size) * 100
    return round(reduction, 1)


def normalize_quality(quality: str) -> str:
    """Accept both 'ebook' and '/ebook' and return Ghostscript's format."""
    normalized = quality.strip().lower().lstrip("/")

    if normalized not in VALID_QUALITIES:
        valid_options = ", ".join(VALID_QUALITIES)
        raise ValueError(f"Qualidade inválida: {quality}. Use uma destas: {valid_options}.")

    return VALID_QUALITIES[normalized]


def find_pdf_files(input_folder: str | Path) -> list[Path]:
    """Find PDF files in input_folder and return them sorted by file name."""
    input_path = Path(input_folder)

    if not input_path.exists():
        raise FileNotFoundError(f"A pasta de entrada não existe: {input_path}")

    if not input_path.is_dir():
        raise NotADirectoryError(f"O caminho de entrada não é uma pasta: {input_path}")

    pdf_files = sorted(
        (path for path in input_path.iterdir() if path.is_file() and path.suffix.lower() == ".pdf"),
        key=lambda path: path.name.lower(),
    )

    if not pdf_files:
        raise FileNotFoundError(f"Nenhum PDF encontrado na pasta: {input_path}")

    return pdf_files


def merge_pdfs(input_folder: str | Path, output_pdf: str | Path) -> list[Path]:
    """
    Merge every PDF from input_folder into output_pdf using PyMuPDF.

    The input PDFs are processed in alphabetical order. The returned list is the
    exact ordered list of processed files, which is useful for CLI reports.
    """
    pdf_files = find_pdf_files(input_folder)
    output_path = Path(output_pdf)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if output_path.exists():
        output_path.unlink()

    merged_document = pymupdf.open()

    try:
        for pdf_file in pdf_files:
            source_document = pymupdf.open(pdf_file)
            try:
                merged_document.insert_pdf(source_document)
            finally:
                source_document.close()

        merged_document.save(
            output_path,
            garbage=4,
            deflate=True,
            clean=True,
        )
    finally:
        merged_document.close()

    return pdf_files


def find_ghostscript_executable() -> str:
    """Find the Ghostscript executable for Windows, Linux, or macOS."""
    configured_path = os.environ.get("GHOSTSCRIPT_PATH")
    if configured_path:
        configured_executable = Path(configured_path)
        if configured_executable.exists():
            return str(configured_executable)

        raise RuntimeError(f"GHOSTSCRIPT_PATH aponta para um arquivo que não existe: {configured_executable}")

    candidates = ["gswin64c", "gswin32c", "gs"] if os.name == "nt" else ["gs"]

    for executable_name in candidates:
        executable_path = shutil.which(executable_name)
        if executable_path:
            return executable_path

    if os.name == "nt":
        program_folders = [
            Path(os.environ.get("ProgramFiles", r"C:\Program Files")),
            Path(os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)")),
        ]

        for program_folder in program_folders:
            for executable_path in program_folder.glob(r"gs\*\bin\gswin64c.exe"):
                return str(executable_path)
            for executable_path in program_folder.glob(r"gs\*\bin\gswin32c.exe"):
                return str(executable_path)

    raise RuntimeError(
        "Ghostscript nao encontrado. Instale o Ghostscript e confira se o comando "
        "'gs', 'gswin64c' ou 'gswin32c' está disponível no terminal. "
        "Se ele já estiver instalado, defina GHOSTSCRIPT_PATH com o caminho completo do executável."
    )


def compress_with_ghostscript(input_pdf: str | Path, output_pdf: str | Path, quality: str = "ebook") -> None:
    """Compress input_pdf into output_pdf using Ghostscript."""
    input_path = Path(input_pdf)
    output_path = Path(output_pdf)
    quality_setting = normalize_quality(quality)

    if not input_path.exists():
        raise FileNotFoundError(f"PDF de entrada não encontrado: {input_path}")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    ghostscript = find_ghostscript_executable()

    command = [
        ghostscript,
        "-sDEVICE=pdfwrite",
        "-dCompatibilityLevel=1.4",
        f"-dPDFSETTINGS={quality_setting}",
        "-dNOPAUSE",
        "-dQUIET",
        "-dBATCH",
        "-dDetectDuplicateImages=true",
        "-dCompressFonts=true",
        "-dSubsetFonts=true",
        f"-sOutputFile={output_path}",
        str(input_path),
    ]

    try:
        subprocess.run(command, check=True)
    except FileNotFoundError as error:
        raise RuntimeError("Ghostscript nao encontrado. Instale o Ghostscript e tente novamente.") from error
    except subprocess.CalledProcessError as error:
        raise RuntimeError(f"Ghostscript falhou ao comprimir o PDF. Código: {error.returncode}") from error


def validate_output_path(output_pdf: str | Path, force: bool = False) -> Path:
    """Create the output folder and protect the final file from accidental overwrite."""
    output_path = Path(output_pdf)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if output_path.exists() and not force:
        raise FileExistsError(
            f"O arquivo de saída já existe: {output_path}. "
            "Use --force para sobrescrever."
        )

    return output_path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Junta PDFs de uma pasta e comprime o resultado com Ghostscript."
    )
    parser.add_argument("--input", default="arquivos", help="Pasta com os PDFs de entrada.")
    parser.add_argument("--output", default="saida/pdf_final.pdf", help="Arquivo PDF final.")
    parser.add_argument(
        "--quality",
        default="ebook",
        help="Qualidade de compressão: screen, ebook, printer ou prepress.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Sobrescreve o arquivo de saída caso ele já exista.",
    )
    return parser


def run(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        input_folder = Path(args.input)
        output_pdf = validate_output_path(args.output, force=args.force)
        quality = normalize_quality(args.quality)
        merged_pdf = output_pdf.parent / "pdf_juntado.pdf"

        if merged_pdf.resolve() == output_pdf.resolve():
            raise ValueError("O arquivo de saída não pode ser o mesmo arquivo temporário pdf_juntado.pdf.")

        pdf_files = find_pdf_files(input_folder)

        print("Iniciando processamento...")
        print()
        print(f"Pasta de entrada: {input_folder}")
        print(f"Arquivo de saída: {output_pdf}")
        print(f"Qualidade escolhida: {quality}")
        print()
        print(f"PDFs encontrados: {len(pdf_files)}")
        for pdf_file in pdf_files:
            print(f"- {pdf_file.name}")

        print()
        print("Juntando PDFs...")
        merge_pdfs(input_folder, merged_pdf)
        merged_size = merged_pdf.stat().st_size
        print(f"PDF juntado criado: {merged_pdf}")
        print(f"Tamanho antes da compressão: {format_file_size(merged_size)}")

        print()
        print("Comprimindo com Ghostscript...")
        compress_with_ghostscript(merged_pdf, output_pdf, quality)
        compressed_size = output_pdf.stat().st_size
        reduction = calculate_reduction_percentage(merged_size, compressed_size)
        print(f"PDF comprimido criado: {output_pdf}")
        print(f"Tamanho depois da compressão: {format_file_size(compressed_size)}")
        print(f"Redução aproximada: {reduction}%")

        print()
        print("Processo concluído com sucesso.")
        return 0
    except Exception as error:
        print(f"Erro: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(run())
