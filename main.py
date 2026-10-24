
import json
from pathlib import Path

import pandas as pd


def load_dataset(file_path):
    """
    Load an Excel or CSV file into a pandas DataFrame.
    The function supports datasets with any number of columns.
    It normalizes column names, removes leading and trailing
    whitespace, and converts missing values to empty strings.
    Args:
        file_path: Path to the input CSV or Excel file.
    Returns:
        A pandas DataFrame containing normalized string values.
    Raises:
        ValueError: If the file format is unsupported or the
            dataset does not contain any columns.
    """
    path = Path(file_path)
    suffix = path.suffix.lower()

    if suffix == ".csv":
        df = pd.read_csv(
            path,
            encoding="utf-8-sig",
            dtype=object
        )

    elif suffix in (".xlsx", ".xls"):
        df = pd.read_excel(
            path,
            dtype=object
        )

    else:
        raise ValueError(
            "Unsupported file format. Supported formats: CSV, XLSX, XLS."
        )

    if len(df.columns) == 0:
        raise ValueError("The input file contains no columns.")

    # Normalize empty and duplicate column names.
    columns = []
    used = set()

    for i, col in enumerate(df.columns, start=1):

        name = str(col).strip() if pd.notna(col) else ""
        name = name or f"column_{i}"

        base = name
        counter = 2

        while name.casefold() in used:
            name = f"{base}_{counter}"
            counter += 1

        used.add(name.casefold())
        columns.append(name)

    df.columns = columns

    # Replace missing cell values with empty strings.
    df = df.astype(object).where(pd.notna(df), "")

    for col in df.columns:
        df[col] = df[col].map(
            lambda value: str(value).strip()
            if value is not None
            else ""
        )

    return df
HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="en" dir="ltr">
<head>
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Offline Data Dictionary Generator</title>

<style>
* {
    box-sizing: border-box;
}

body {
    font-family: Tahoma, Arial, sans-serif;
    background: #f1f5f9;
    color: #1e293b;
    margin: 0;
    padding: 18px;
}

.card {
    background: white;
    padding: 20px;
    border-radius: 12px;
    box-shadow: 0 2px 10px #0000000c;
}

h2 {
    margin-top: 0;
}

.toolbar {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin: 16px 0;
}

input, select, button {
    font: inherit;
    padding: 9px;
    border: 1px solid #cbd5e1;
    border-radius: 6px;
}

input, select {
    min-width: 0;
}

button {
    cursor: pointer;
    background: white;
}

button:hover {
    background: #e2e8f0;
}

.primary {
    background: #172554;
    color: white;
    border-color: #172554;
}

.primary:hover {
    background: #1e40af;
}

.search-box {
    width: 100%;
    padding: 12px;
    margin: 8px 0;
}

.filters {
    display: grid;
    grid-template-columns: repeat(
        auto-fit,
        minmax(180px, 1fr)
    );
    gap: 10px;
    margin: 15px 0;
}

.filter-item label {
    display: block;
    font-size: 13px;
    margin-bottom: 5px;
    overflow-wrap: anywhere;
}

.filter-item select {
    width: 100%;
}

.table-wrap {
    overflow: auto;
    max-height: 65vh;
    border: 1px solid #dbe3ee;
}

table {
    width: 100%;
    border-collapse: collapse;
    background: white;
}

th, td {
    border: 1px solid #dbe3ee;
    padding: 9px;
    text-align: right;
    vertical-align: top;
    white-space: pre-wrap;
    overflow-wrap: anywhere;
    min-width: 110px;
}

th {
    position: sticky;
    top: 0;
    z-index: 1;
    background: #172554;
    color: white;
}

.sort-button {
    color: white;
    background: transparent;
    border: 0;
    padding: 3px;
}

.edit-button {
    padding: 3px 6px;
    margin-right: 4px;
}

tbody tr:nth-child(even) {
    background: #f8fafc;
}

tbody tr:hover {
    background: #dbeafe;
}

.footer {
    display: flex;
    align-items: center;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 10px;
    margin-top: 15px;
}

.panel {
    display: none;
    margin: 15px 0;
    padding: 15px;
    border: 1px solid #cbd5e1;
    border-radius: 8px;
    background: #f8fafc;
}

.panel.open {
    display: block;
}

.mapping-row {
    display: grid;
    grid-template-columns: minmax(120px, 1fr)
                           minmax(120px, 1fr);
    gap: 10px;
    align-items: center;
    margin: 8px 0;
}

.mapping-row input {
    width: 100%;
    background: white;
}

.muted {
    color: #64748b;
    font-size: 13px;
}

@media(max-width: 700px) {
    body {
        padding: 7px;
    }

    .card {
        padding: 10px;
    }

    .mapping-row {
        grid-template-columns: 1fr;
        gap: 4px;
    }
}
</style>
</head>

<body>
<div class="card">

<h2>Offline Data Dictionary Generator</h2>
<p>Search and data exploration work entirely offline.</p>

<p>
   All Records:
    <strong id="total">۰</strong>
    |
    Results:
    <strong id="count">۰</strong>
    |
    Columns:
    <strong id="columnCount">۰</strong>
</p>

<input
    id="search"
    class="search-box"
    type="search"
    placeholder="Search in all columns..."
>

<div id="filters" class="filters"></div>

<div class="table-wrap">
    <table>
        <thead>
            <tr id="headers"></tr>
        </thead>

        <tbody id="results"></tbody>
    </table>
</div>

<div class="footer">

    <label>
        Number of row:

        <select id="pageSize">
            <option value="15">15</option>
            <option value="25" selected>25</option>
            <option value="50">50</option>
            <option value="100">100</option>
            <option value="all">ALL</option>
        </select>
    </label>

    <span id="info"></span>

    <div>
        <button id="first">First</button>
        <button id="prev">Previous</button>
        <button id="next">Next</button>
        <button id="last">Last</button>
    </div>

</div>
</div>

<script id="initial-state" type="application/json">__STATE__</script>

<script>
"use strict";

const initialState = JSON.parse(
    document.getElementById("initial-state").textContent
);

const columns = initialState.columns;
const data = initialState.data;
const originalHeaders = [...columns];

const displayHeaders = columns.map(col =>
    initialState.displayHeaders?.[col] || col
);

const filterColumns = initialState.filterColumns || [];

let query = "";
let filters = {};
let page = 1;
let pageSize = 25;
let sortCol = -1;
let sortDir = 1;

const $ = id => document.getElementById(id);


function norm(value) {
    return String(value ?? "")
        .toLocaleLowerCase()
        .replace(/ي/g, "ی")
        .replace(/ك/g, "ک")
        .replace(/\u200c/g, " ")
        .trim();
}


function shownHeader(index) {
    return displayHeaders[index] || originalHeaders[index];
}


// Build the table headers.
function buildHeaders() {
    const tr = $("headers");
    tr.replaceChildren();

    columns.forEach((col, index) => {
        const th = document.createElement("th");

        const sortButton = document.createElement("button");
        sortButton.className = "sort-button";
        sortButton.textContent = shownHeader(index);
        sortButton.title = "Click to sort";

        sortButton.addEventListener("click", () => {
            if (sortCol === index) {
                sortDir *= -1;
            } else {
                sortCol = index;
                sortDir = 1;
            }

            render();
        });

        th.appendChild(sortButton);
        tr.appendChild(th);
    });
}


// Create a separate dropdown filter for each configured column.
function buildFilters() {
    const container = $("filters");
    container.replaceChildren();

    filters = {};

    filterColumns.forEach(col => {
        const index = columns.indexOf(col);

        if (index === -1) {
            return;
        }

        const wrapper = document.createElement("div");
        wrapper.className = "filter-item";

        const label = document.createElement("label");
        label.textContent = "Filter: " + shownHeader(index);

        const select = document.createElement("select");

        const allOption = document.createElement("option");
        allOption.value = "";
        allOption.textContent = "All value";
        select.appendChild(allOption);

        const values = [
            ...new Set(data.map(row => String(row[col] ?? "")))
        ].filter(value => value !== "");

        values.sort((a, b) => a.localeCompare(b, "fa"));

        values.forEach(value => {
            const option = document.createElement("option");
            option.value = value;
            option.textContent = value;
            select.appendChild(option);
        });

        filters[index] = "";

        select.addEventListener("change", () => {
            filters[index] = select.value;
            reset();
        });

        wrapper.appendChild(label);
        wrapper.appendChild(select);
        container.appendChild(wrapper);
    });
}


// Search and filter the original dataset.

function filteredData() {
    let result = data.filter(row => {

        // Apply a global search across all columns.
        if (
            query &&
            !columns.some(col =>
                norm(row[col]).includes(norm(query))
            )
        ) {
            return false;
        }

        // Apply filters only to the configured columns.
        for (const [index, value] of Object.entries(filters)) {
            if (!value) {
                continue;
            }

            const col = columns[Number(index)];

            if (String(row[col] ?? "") !== value) {
                return false;
            }
        }

        return true;
    });

    if (sortCol >= 0) {
        const col = columns[sortCol];

        result.sort((a, b) =>
            norm(a[col]).localeCompare(
                norm(b[col]),
                "fa",
                { numeric: true }
            ) * sortDir
        );
    }

    return result;
}


// Render the matching records and update pagination.
function render() {
    const result = filteredData();

    const totalPages = pageSize === "all"
        ? 1
        : Math.max(1, Math.ceil(result.length / pageSize));

    page = Math.min(Math.max(1, page), totalPages);

    const start = pageSize === "all"
        ? 0
        : (page - 1) * pageSize;

    const visible = pageSize === "all"
        ? result
        : result.slice(start, start + pageSize);

    const tbody = $("results");
    tbody.replaceChildren();

    if (!visible.length) {
        const tr = document.createElement("tr");
        const td = document.createElement("td");

        td.colSpan = Math.max(columns.length, 1);
        td.textContent = "No matching records found.";

        tr.appendChild(td);
        tbody.appendChild(tr);

    } else {
        visible.forEach(row => {
            const tr = document.createElement("tr");

            columns.forEach(col => {
                const td = document.createElement("td");
                td.textContent = row[col] ?? "";
                tr.appendChild(td);
            });

            tbody.appendChild(tr);
        });
    }

    $("total").textContent =
        data.length.toLocaleString("en-US");

    $("count").textContent =
        result.length.toLocaleString("en-US");

    $("columnCount").textContent =
        columns.length.toLocaleString("en-US");

    $("info").textContent = result.length
        ? `display ${(start + 1).toLocaleString("en-US")} to ${
            (start + visible.length).toLocaleString("en-US")
          } from ${result.length.toLocaleString("en-US")}`
        : "Without result";

    $("first").disabled = page <= 1;
    $("prev").disabled = page <= 1;
    $("next").disabled = page >= totalPages;
    $("last").disabled = page >= totalPages;
}


function reset() {
    page = 1;
    render();
}


// Safely serialize JSON for embedding in HTML.
function safeJson(value) {
    return JSON.stringify(value)
        .replace(/</g, "\\u003c")
        .replace(/>/g, "\\u003e")
        .replace(/&/g, "\\u0026");
}

$("search").addEventListener("input", event => {
    query = event.target.value;
    reset();
});

$("pageSize").addEventListener("change", event => {
    pageSize = event.target.value === "all"
        ? "all"
        : Number(event.target.value);

    reset();
});

$("first").addEventListener("click", () => {
    page = 1;
    render();
});

$("prev").addEventListener("click", () => {
    page = Math.max(1, page - 1);
    render();
});

$("next").addEventListener("click", () => {
    page++;
    render();
});

$("last").addEventListener("click", () => {
    const total = filteredData().length;

    page = pageSize === "all"
        ? 1
        : Math.max(1, Math.ceil(total / pageSize));

    render();
});

buildHeaders();
buildFilters();
render();
</script>
</body>
</html>
"""


# ==========================================
# Input and output configuration
# ==========================================

# csv or xls or xlsx
INPUT_FILE = "input.xlsx"
OUTPUT_HTML = "output.html"


# Optional display labels for column headers.
# Keys must match the original column names in the input file.
# Values are the labels displayed in the HTML interface.
# Columns not specified here retain their original names.

DISPLAY_HEADERS = {
  #  "CustomerName": "Customer Name",
}

# Specify which columns should have dropdown filters.
# Each entry must exactly match an original column name
# in the input dataset.

FILTER_COLUMNS = [
    "Columnselection1",
    "Columnselection2",
    "Columnselection3",
]

def generate_html(df, output_file):
    """
    Generate a standalone HTML data explorer from a DataFrame.

    The dataset, display labels, and filter configuration are
    embedded in the generated HTML document. The output can be
    opened directly in a modern web browser without a server.

    Args:
        df: The normalized pandas DataFrame to export.
        output_file: Destination path for the generated HTML file.

    Returns:
        The absolute path to the generated HTML file.

    Raises:
        ValueError: If a configured filter column does not exist.
        OSError: If the output file cannot be written.
    """
    columns = list(df.columns)

    # Validate the configured filter columns.
    invalid_filters = set(FILTER_COLUMNS) - set(columns)

    if invalid_filters:
        raise ValueError(
            "Filter columns not found in the input file: "
            + ", ".join(sorted(invalid_filters))
        )

    # Apply custom display labels without modifying the original column names used by the dataset.
    display_headers = {
        col: DISPLAY_HEADERS.get(col, col)
        for col in columns
    }

    state = {
        "columns": columns,
        "data": df.to_dict(orient="records"),
        "displayHeaders": display_headers,
        "filterColumns": FILTER_COLUMNS,
    }

    state_json = (
        json.dumps(state, ensure_ascii=False)
        .replace("<", "\\u003c")
        .replace(">", "\\u003e")
        .replace("&", "\\u0026")
    )

    page = HTML_TEMPLATE.replace("__STATE__", state_json)

    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    output_path.write_text(page, encoding="utf-8")

    return output_path.resolve()


def main():
    """
    Run the complete data dictionary generation workflow.
    Validate the input path, load and normalize the dataset,
    generate the standalone HTML file, and print a summary
    of the operation.
    """
    try:
        input_path = Path(INPUT_FILE)
        output_path = Path(OUTPUT_HTML)

        # Validate that the input file exists.
        if not input_path.is_file():
            raise FileNotFoundError(
                f"Input file not found: {input_path.resolve()}"
            )

        # Load and normalize the input dataset.
        df = load_dataset(input_path)

        # Generate the standalone HTML document.
        result = generate_html(df, output_path)

        print("=" * 50)
        print("HTML file successfully generated.")
        print(f"Input file: {input_path.resolve()}")
        print(f"Output file: {result}")
        print(f"Number of records: {len(df)}")
        print(f"Number of columns: {len(df.columns)}")
        print("=" * 50)

    except Exception as exc:
        print(f"Error: {type(exc).__name__}: {exc}")
        raise


if __name__ == "__main__":
    main()

