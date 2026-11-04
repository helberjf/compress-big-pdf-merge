# PDF Merge and Compression CLI

A Python command-line utility that merges PDFs in filename order with PyMuPDF, then compresses the merged document with Ghostscript. It reports input files, output sizes and the resulting size change.

## Setup

Use **Python 3.10+** and install Ghostscript separately from the Python requirements.

```bash
git clone https://github.com/helberjf/compress-big-pdf-merge.git
cd compress-big-pdf-merge
python -m venv .venv
```

Activate the environment with `.venv\Scripts\Activate.ps1` in PowerShell or `source .venv/bin/activate` on macOS/Linux, then install the Python dependency:

```bash
python -m pip install -r requirements.txt
```

Install [Ghostscript](https://ghostscript.com/releases/gsdnld.html) using its installer or your operating system's package manager. Confirm `gswin64c --version` on Windows or `gs --version` on macOS/Linux. If it is not on `PATH`, set `GHOSTSCRIPT_PATH` to the full executable path. The code also checks standard Windows Ghostscript installation directories.

## Example workflow

Place fictional sample PDFs in `arquivos` with numeric prefixes to control the order:

```text
arquivos/
  01-cover.pdf
  02-document.pdf
  03-appendix.pdf
```

```bash
python main.py --input arquivos --output saida/pdf_final.pdf --quality ebook
```

The tool writes the merged intermediate file `saida/pdf_juntado.pdf` and the compressed final file. Inspect the resulting page order and readability before using it. Keep the output directory separate from the input directory so a later run does not pick up previous outputs as inputs.

| Option | Behavior |
| --- | --- |
| `--input` | Directory of PDFs; defaults to `arquivos` |
| `--output` | Final file; defaults to `saida/pdf_final.pdf` |
| `--quality` | `screen`, `ebook` (default), `printer` or `prepress` |
| `--force` | Permits replacement of an existing final output |

The final file is protected from replacement by default. The fixed intermediate file is recreated on each run; `--force` is not a general protection mechanism for every generated file.

## Code and checks

[main.py](main.py) separates discovery, merge, executable lookup, Ghostscript invocation and output validation. [test_main.py](test_main.py) uses Python's `unittest` framework; [runPythonEasy.md](runPythonEasy.md) retains additional usage notes in Portuguese.

```bash
python -m unittest -v
python main.py --help
```

Install the requirements before running tests because the application imports PyMuPDF. Automated cases do not establish a universal compression ratio or visual fidelity for arbitrary PDFs.

## Design tradeoffs

- **Two specialized tools:** PyMuPDF handles assembly and Ghostscript handles compression, but Ghostscript is a native executable outside the Python environment.
- **Preset compression:** a small set of quality levels keeps the CLI simple; results depend on document contents and can reduce image clarity without guaranteeing a smaller file.
- **Filename ordering:** predictable numeric prefixes avoid a separate manifest, but users must prepare the naming order explicitly.
- **Retained intermediate PDF:** makes the merged result available for inspection and comparison, while using extra disk space and a fixed intermediate filename.
