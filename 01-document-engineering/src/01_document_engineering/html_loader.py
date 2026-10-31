
from pathlib import Path
from bs4 import BeautifulSoup


def inspect_html(file_path: str | Path) -> None:
    path = Path(file_path)

    html = path.read_text(encoding="utf-8")
    soup = BeautifulSoup(html, "lxml")

    print("=== Entire page ===")
    print(soup.get_text(" ", strip=True))

    print("\n=== Main content only ===")
    main = soup.find("main")

    if main is not None:
        print(main.get_text(" ", strip=True))

    print("\n=== Headings ===")
    if main is not None:
        for heading in main.find_all(["h1", "h2", "h3"]):
            print(heading.name, heading.get_text(strip=True))
            
            
def inspect_html_tables(file_path: str | Path) -> None:
    path = Path(file_path)
    soup = BeautifulSoup(
        path.read_text(encoding="utf-8"),
        "lxml",
    )

    main = soup.find("main")

    if main is None:
        return

    for table in main.find_all("table"):
        rows = []

        for tr in table.find_all("tr"):
            cells = tr.find_all(["th", "td"])
            rows.append([
                cell.get_text(" ", strip=True)
                for cell in cells
            ])

        for row in rows:
            print(row)


if __name__ == "__main__":
    inspect_html_tables("data/payment_service.html")
