# PDF Tools

Ferramenta de linha de comando em Python para juntar vários PDFs e comprimir o resultado com Ghostscript.

O projeto usa:

- Python 3.10+
- PyMuPDF para juntar os PDFs
- Ghostscript para comprimir o PDF final

## Estrutura

```txt
pdf-tools/
├── arquivos/
├── saida/
├── main.py
├── requirements.txt
└── README.md
```

A pasta `arquivos/` é onde você coloca os PDFs de entrada.
A pasta `saida/` é onde o PDF juntado temporário e o PDF final serão criados.

## Instalar Python

Baixe e instale o Python em:

```txt
https://www.python.org/downloads/
```

Durante a instalação no Windows, marque a opção para adicionar o Python ao `PATH`.

Confira a instalação:

```bash
python --version
```

No Linux ou Mac, talvez o comando seja:

```bash
python3 --version
```

## Criar Ambiente Virtual

No Windows:

```bash
python -m venv venv
venv\Scripts\activate
```

No Linux ou Mac:

```bash
python3 -m venv venv
source venv/bin/activate
```

## Instalar Dependências Python

Com o ambiente virtual ativo:

```bash
pip install -r requirements.txt
```

O arquivo `requirements.txt` instala apenas:

```txt
pymupdf
```

## Instalar Ghostscript

### Windows com winget

```bash
winget install ArtifexSoftware.Ghostscript
```

Depois feche e abra o terminal novamente.

Se o `winget` não existir, abra o PowerShell como administrador e tente com Chocolatey:

```bash
choco install ghostscript -y
```

Se a instalação terminar, mas `gswin64c --version` ainda não funcionar, instale ou reinstale o pacote do aplicativo:

```bash
choco install ghostscript.app -y --force
```

Depois feche e abra o terminal novamente.

### Linux

Ubuntu/Debian:

```bash
sudo apt update
sudo apt install ghostscript
```

Fedora:

```bash
sudo dnf install ghostscript
```

### Mac

Com Homebrew:

```bash
brew install ghostscript
```

## Testar se o Ghostscript Está Instalado

No Windows, teste:

```bash
gswin64c --version
```

Se não funcionar, tente:

```bash
gswin32c --version
```

No Linux ou Mac:

```bash
gs --version
```

Se nenhum desses comandos funcionar, o Ghostscript não está instalado ou não está no `PATH`.

Se o Ghostscript estiver instalado, mas o comando não for encontrado, você também pode apontar o caminho completo do executável.

Primeiro tente localizar o executável:

```powershell
Get-ChildItem "C:\Program Files" -Recurse -Filter gswin64c.exe -ErrorAction SilentlyContinue | Select-Object -First 1 -ExpandProperty FullName
```

No PowerShell:

```powershell
$env:GHOSTSCRIPT_PATH="C:\Program Files\gs\gs10.07.1\bin\gswin64c.exe"
python main.py --input arquivos --output saida/pdf_final.pdf --quality ebook --force
```

Ajuste o caminho conforme a versão instalada na sua máquina.

## Como Usar

Coloque os PDFs dentro da pasta:

```txt
arquivos/
```

Exemplo:

```txt
arquivos/
├── 01-documento.pdf
├── 02-anexo.pdf
└── 03-comprovante.pdf
```

Os arquivos são juntados em ordem alfabética. Para controlar a ordem, coloque números no início dos nomes.

Rode:

```bash
python main.py --input arquivos --output saida/pdf_final.pdf --quality ebook
```

Para comprimir mais:

```bash
python main.py --input arquivos --output saida/pdf_final.pdf --quality screen
```

Se o arquivo final já existir, o programa não sobrescreve por padrão. Para permitir sobrescrita:

```bash
python main.py --input arquivos --output saida/pdf_final.pdf --quality ebook --force
```

## Qualidade de Compressão

O Ghostscript aceita estes modos:

- `screen`: menor tamanho, maior perda de qualidade. Útil para visualização em tela.
- `ebook`: bom equilíbrio entre tamanho e qualidade. É o padrão do projeto.
- `printer`: qualidade maior, arquivo geralmente maior.
- `prepress`: qualidade alta para impressão profissional, arquivo geralmente bem maior.

Use `screen` quando precisar reduzir muito o tamanho, mas confira o PDF final porque textos escaneados e imagens podem perder nitidez.

## Exemplo de Saída

```txt
Iniciando processamento...

Pasta de entrada: arquivos
Arquivo de saída: saida/pdf_final.pdf
Qualidade escolhida: /ebook

PDFs encontrados: 3
- 01-documento.pdf
- 02-anexo.pdf
- 03-comprovante.pdf

Juntando PDFs...
PDF juntado criado: saida/pdf_juntado.pdf
Tamanho antes da compressão: 18.4 MB

Comprimindo com Ghostscript...
PDF comprimido criado: saida/pdf_final.pdf
Tamanho depois da compressão: 5.2 MB
Redução aproximada: 71.7%

Processo concluído com sucesso.
```

## Se o Arquivo Continuar Grande

PDFs escaneados, documentos com fotos grandes e imagens em alta resolução podem continuar pesados mesmo após compressão.

Tente nesta ordem:

1. Rode com `--quality screen`.
2. Verifique se o PDF tem imagens escaneadas em resolução muito alta.
3. Reduza as imagens antes de criar o PDF original, quando possível.
4. Confira se o arquivo final ainda está legível antes de enviar ou arquivar.

## Rodar Testes

Os testes usam apenas `unittest`, que já vem com o Python:

```bash
python -m unittest -v
```
