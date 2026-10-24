
# Offline Data Dictionary Generator

A lightweight Python tool that converts Excel and CSV files into standalone, interactive HTML data dictionaries.

The generated HTML page allows users to explore tabular data using global search, column-specific filters, sorting, and pagination — without requiring an internet connection or a web server.

## Live Demo

Try the interactive data dictionary directly in your browser:

**[Open Live Demo](https://h23pouladi.github.io/offline-data-dictionary-generator/)**

No installation or download is required to explore the demo.

To generate a data dictionary from your own Excel or CSV file, follow the installation and usage instructions below.

## Features

- **Multiple input formats:** Supports `.xlsx`, `.xls`, and `.csv` files.
- **Flexible column support:** Works with datasets containing any number of columns.
- **Automatic column-name normalization:** Replaces empty column headers and resolves duplicate names.
- **Global search:** Searches across all columns simultaneously.
- **Column-specific filters:** Provides dropdown filters for selected columns.
- **Sorting:** Sorts records in ascending or descending order by clicking column headers.
- **Pagination:** Displays 15, 25, 50, or 100 records per page, or all matching records.
- **Custom display labels:** Allows column headers to have alternative display names without changing the underlying dataset.
- **Standalone HTML output:** Embeds the dataset and application logic directly into a single HTML file.
- **Offline operation:** Requires no external services, internet connection, or backend server.
- **Responsive interface:** Supports desktop and mobile screen sizes.
- **Unicode support:** Handles Persian text and other Unicode characters.

## Requirements

- Python 3.9 or later
- pandas
- openpyxl for `.xlsx` files
- xlrd for legacy `.xls` files

## Installation

### 1. Clone the repository

Replace `YOUR_USERNAME` and `YOUR_REPOSITORY` with your GitHub username and repository name.

```bash
git clone https://github.com/h23pouladi/offline-data-dictionary-generator.git
cd YOUR_REPOSITORY
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate it on Windows:

```bash
.venv\Scripts\activate
```

Activate it on macOS or Linux:

```bash
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

If you do not have a `requirements.txt` file, install the packages directly:

```bash
pip install pandas openpyxl xlrd
```

## Usage

1. Place your Excel or CSV input file in the project directory.
2. Update the input and output paths in `main.py`.
3. Configure display labels and filter columns if needed.
4. Run the application:

```bash
python main.py
```

5. Open the generated HTML file in a modern web browser.

The generated page works locally without a web server.

## Configuration

The following variables control the input file, output file, display labels, and column filters:

```python
INPUT_FILE = "form_dictionary.xlsx"
OUTPUT_HTML = "form_dictionary.html"

DISPLAY_HEADERS = {
    "CustomerName": "Customer Name",
    "RequestType": "Request Type",
}

FILTER_COLUMNS = [
    "Columnselection1",
    "Columnselection2",
    "Columnselection3",
]
```

### Input and output paths

- `INPUT_FILE`: Path to the source Excel or CSV file.
- `OUTPUT_HTML`: Destination path for the generated HTML file. Missing parent directories are created automatically.

### Custom display headers

The `DISPLAY_HEADERS` dictionary maps original column names to alternative labels displayed in the HTML interface.

For example:

```python
DISPLAY_HEADERS = {
    "CustomerName": "Customer Name",
    "RequestType": "Request Type",
}
```

The dictionary keys must match the original column names in the input file. Columns not specified in this dictionary retain their original names.

Changing a display label does not change the underlying dataset or the column names used for filtering.

### Column filters

The `FILTER_COLUMNS` list specifies which columns receive dropdown filters.

Each entry must exactly match an existing column name in the input dataset.

For example:

```python
FILTER_COLUMNS = [
    "Columnselection1",
    "Columnselection2",
]
```

To disable column-specific filters, use an empty list:

```python
FILTER_COLUMNS = []
```

The global search remains available even when no column filters are configured.

## Data Processing

The application normalizes the input dataset before generating the HTML file.

- CSV files are read using UTF-8 with BOM support.
- Excel and CSV values are converted to strings.
- Missing cell values are replaced with empty strings.
- Leading and trailing whitespace is removed from column names and cell values.
- Empty column names are replaced with generated names.
- Duplicate column names are made unique using case-insensitive comparison.

The original input file is not modified.

**Important:** The application is designed for data exploration. It does not preserve Excel formatting, formulas as spreadsheet features, or original cell data types.

## Search, Filtering, and Sorting

### Global search

The search field checks all columns and returns rows containing the search term.

Search is case-insensitive and includes basic normalization for Persian and Arabic character variants.

### Column filters

Dropdown filters are available only for columns specified in `FILTER_COLUMNS`.

Selecting a value limits the displayed records to rows matching the selected value in every active filter.

### Sorting

Click a column header to sort the records in ascending order. Click it again to reverse the sorting direction.

Sorting is performed on normalized string values, with numeric-aware comparison.

### Pagination

Choose the number of records displayed per page:

- 15 records
- 25 records
- 50 records
- 100 records
- All matching records

Pagination automatically adjusts when the search query or filter selections change.

## Output and Privacy

The generated HTML file contains the dataset embedded directly in the document.

This makes the output portable and suitable for offline use. However, anyone who obtains the HTML file may be able to access its embedded data.

**Do not commit generated HTML files containing confidential, personal, or sensitive information to a public repository.**

The application does not require an external database or transmit data to a remote server during normal operation.

## Limitations

- Large datasets may produce large HTML files and slower browser rendering.
- All records are embedded in the HTML document and loaded into browser memory.
- Original Excel formatting and cell data types are not preserved.
- Column filters use exact value matching.
- Filter options are generated from the original dataset and do not dynamically update based on other active filters.
- The user interface currently uses Persian labels and a right-to-left layout.

## Project Structure

```text
.
├── main.py
├── requirements.txt
├── README.md
├── .gitignore
├── docs/
│   └── index.html             # Live demo / GitHub Pages
└── examples/
    ├── form_dictionary.xlsx   # Sample input data
    └── form_dictionary.html   # Sample generated output

```

The input dataset and generated HTML file are runtime files and do not necessarily need to be committed to the repository.

## Contributing

Contributions, bug reports, and feature requests are welcome.

Please open an issue to report a problem or propose an improvement. Pull requests are also welcome.

## License

Choose an open-source license before distributing the project.

For example, the MIT License is a permissive option for projects that allow reuse, modification, and redistribution subject to its license terms.


## Example

The `examples/` directory contains a sample Excel dataset and
the corresponding HTML file generated by this application.

- [Download the sample Excel file](examples/sample_data.xlsx)
- [View the generated HTML source](examples/sample_dictionary.html)

Download `sample_data.xlsx` and run the application to generate
your own interactive HTML data dictionary.