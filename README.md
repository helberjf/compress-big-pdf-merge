# Juntar e Comprimir PDFs com Python

Este projeto usa **Python** com a biblioteca **PyMuPDF** para:

1. Ler arquivos PDF.
2. Juntar vários PDFs em um único arquivo.
3. Salvar o PDF final com compressão/otimização básica.

---

## 1. Requisitos

Antes de começar, você precisa ter instalado:

- Python 3.10 ou superior
- pip, que normalmente já vem com o Python

Para verificar se o Python está instalado, rode no terminal:

```bash
python --version
```

ou:

```bash
python3 --version
```

Se aparecer algo como:

```bash
Python 3.11.0
```

está tudo certo.

---

## 2. Criar a pasta do projeto

Crie uma pasta para o projeto:

```bash
mkdir pdf-tools
cd pdf-tools
```

Agora crie duas pastas dentro dela:

```bash
mkdir arquivos
mkdir saida
```

A estrutura ficará assim:

```txt
pdf-tools/
├── arquivos/
├── saida/
└── main.py
```

A pasta `arquivos` será usada para colocar os PDFs originais.

A pasta `saida` será usada para salvar o PDF final.

---

## 3. Criar ambiente virtual

No Windows, rode:

```bash
python -m venv venv
```

Depois ative o ambiente virtual:

```bash
venv\Scripts\activate
```

No Linux ou Mac, rode:

```bash
python3 -m venv venv
```

Depois ative:

```bash
source venv/bin/activate
```

Quando o ambiente estiver ativo, o terminal deve mostrar algo parecido com:

```bash
(venv) C:\seu-projeto\pdf-tools>
```

---

## 4. Instalar a biblioteca

Com o ambiente virtual ativo, instale o PyMuPDF:

```bash
pip install pymupdf
```

Para conferir se instalou corretamente:

```bash
pip show pymupdf
```

---

## 5. Criar o arquivo `main.py`

Crie um arquivo chamado:

```txt
main.py
```

Dentro dele, coloque o código abaixo:

```python
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
```

---

## 6. Colocar os PDFs na pasta correta

Coloque os arquivos PDF que você quer juntar dentro da pasta:

```txt
arquivos/
```

Exemplo:

```txt
pdf-tools/
├── arquivos/
│   ├── documento1.pdf
│   ├── documento2.pdf
│   └── documento3.pdf
├── saida/
└── main.py
```

A ordem dos PDFs será alfabética.

Exemplo:

```txt
01-capa.pdf
02-contrato.pdf
03-anexos.pdf
```

Se quiser controlar a ordem, renomeie os arquivos com números no início.

---

## 7. Rodar o projeto

Com o ambiente virtual ativo, rode:

```bash
python main.py
```

ou, se estiver usando Linux/Mac:

```bash
python3 main.py
```

Se tudo estiver certo, aparecerá algo parecido com:

```bash
PDFs encontrados:
- 01-capa.pdf
- 02-contrato.pdf
- 03-anexos.pdf

PDF final criado com sucesso: saida/pdf_final_comprimido.pdf
```

---

## 8. Resultado final

O arquivo final será salvo em:

```txt
saida/pdf_final_comprimido.pdf
```

Esse arquivo já estará:

- Com todos os PDFs unidos.
- Com limpeza de objetos internos.
- Com compressão básica aplicada.

---

## 9. Observação importante sobre compressão

Essa compressão funciona bem para limpar e otimizar PDFs.

Porém, se o PDF tiver muitas imagens escaneadas, fotos ou documentos muito pesados, talvez a redução não seja grande.

Nesse caso, a compressão mais forte geralmente é feita com **Ghostscript**, mas para começar o PyMuPDF já resolve bem a maioria dos casos.

---

## 10. Comandos principais resumidos

```bash
mkdir pdf-tools
cd pdf-tools

mkdir arquivos
mkdir saida

python -m venv venv
venv\Scripts\activate

pip install pymupdf

python main.py
```

No Linux/Mac:

```bash
mkdir pdf-tools
cd pdf-tools

mkdir arquivos
mkdir saida

python3 -m venv venv
source venv/bin/activate

pip install pymupdf

python3 main.py
```
