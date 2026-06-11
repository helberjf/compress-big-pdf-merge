import pymupdf
from pathlib import Path


def merge_and_compress_pdfs(input_folder: str, output_pdf: str):
    input_path = Path(input_folder)
    output_path = Path(output_pdf)

    if not input_path.exists():
        raise FileNotFoundError(f"A pasta não foi encontrada: {input_path}")

    pdf_files = sorted(input_path.glob("*.pdf"))

    if not pdf_files:
        raise FileNotFoundError(f"Nenhum PDF encontrado na pasta: {input_path}")

    merged_doc = pymupdf.open()

    print("PDFs encontrados:")

    for pdf_file in pdf_files:
        print(f"- {pdf_file.name}")

        pdf = pymupdf.open(pdf_file)
        merged_doc.insert_pdf(pdf)
        pdf.close()

    output_path.parent.mkdir(parents=True, exist_ok=True)

    merged_doc.save(
        output_path,
        garbage=4,
        deflate=True,
        clean=True
    )

    merged_doc.close()

    print()
    print(f"PDF final criado com sucesso: {output_path}")


if __name__ == "__main__":
    merge_and_compress_pdfs(
        input_folder="arquivos",
        output_pdf="saida/pdf_final_comprimido.pdf"
    )