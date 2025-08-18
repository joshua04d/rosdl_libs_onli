#!/usr/bin/env python3
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.align import Align

console = Console()

def main():
    # --- Intro panel (centered) ---
    console.print(
        Panel(
            Align.center(
                "[bold blue]📦 Welcome to rosdl - Research Oriented Smart Data Library CLI 📦[/]\n\n"
                "[white]Rosdl is a Python lib designed to make data handling easier for \n"
                "students, researchers,etc.[/]\n\n"
                "[green]• PDFs → split, merge, extract text/images[/]\n"
                "[green]• CSVs → clean messy data for analysis[/]\n"
                "[green]• Archives → extract ZIP/TAR files[/]\n"
                "[green]• OCR → convert scanned images into text[/]\n"
                "[green]• Metadata → inspect files for hidden info[/]\n"
                "[green]• Text utilities → tokenize, clean, keyword extraction[/]\n"
                "[green]• Image tools → convert, resize, strip metadata[/]\n"
                "[green]• File converters → CSV ↔ XLSX[/]\n"
                "[green]• EDA & drift detection → understand dataset shifts[/]\n"
                "[green]• Synthetic data generation → create test datasets[/]\n\n"
                "[yellow]👉 Think of it as a Swiss-army knife for research.[/]"
            ),
            title="rosdl",
            border_style="blue",
            expand=False
        )
    )

    # --- 2-column menu table ---
    table = Table(show_lines=True, title="[bold yellow]Choose an option[/]")

    table.add_column("Option", justify="left", style="cyan", no_wrap=True)
    table.add_column("Feature", style="magenta", no_wrap=False)
    table.add_column("Option", justify="left", style="cyan", no_wrap=True)
    table.add_column("Feature", style="magenta", no_wrap=False)

    # Two-column layout
    menu_items = [
        ("1", "PDF Tools", "6", "Text Utilities"),
        ("2", "CSV Cleaner", "7", "Image Tools"),
        ("3", "Archive Manager", "8", "File Converter (CSV ↔ XLSX)"),
        ("4", "OCR (Image → Text)", "9", "EDA & Drift Detection"),
        ("5", "Metadata Extractor", "10", "Synthetic Data Generator"),
    ]

    for row in menu_items:
        table.add_row(*row)

    console.print(Align.left(table))

    # --- User choice ---
    choice = console.input("[bold cyan]Enter your choice (1-10): [/] ")

    if choice in [str(i) for i in range(2, 11)]:
        console.print(f"[bold green]👉 You selected option {choice}. (Feature coming soon...)[/]")

    elif choice == "1":  # PDF Tools
            console.print("\n[bold green]👉 You selected PDF Tools.[/]")
            console.print("\n[bold yellow]Available PDF Tools:[/]")
            console.print("\n1. Split PDF")
            console.print("\n2. Merge PDFs")
            console.print("\n3. Extract Text from PDF")
            console.print("\n4. Convert PDF to Images")
            console.print("\n5. OCR Image")
            console.print("\n6. OCR PDF")
            console.print("\n7. Merge PDFs in Folder")

    else:
        console.print("[bold red]❌ Invalid choice. Please try again.[/]")

if __name__ == "__main__":
    main()
