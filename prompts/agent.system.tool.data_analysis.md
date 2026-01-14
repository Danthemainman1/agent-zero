## Tool: "data_analysis" - Advanced Data Analysis & Spreadsheet Operations

Use this tool for data analysis, spreadsheet manipulation, statistical analysis, and data visualization.

### Actions:

#### load - Load and preview data
```json
{
    "thoughts": ["Loading the sales data to understand its structure..."],
    "tool_name": "data_analysis",
    "tool_args": {
        "action": "load",
        "file_path": "data/sales.csv",
        "rows": 10
    }
}
```

#### analyze - Statistical analysis
```json
{
    "thoughts": ["Performing statistical analysis on the dataset..."],
    "tool_name": "data_analysis",
    "tool_args": {
        "action": "analyze",
        "file_path": "data/sales.csv",
        "analysis_type": "descriptive",
        "columns": ["revenue", "quantity", "profit"]
    }
}
```

#### transform - Clean and transform data
```json
{
    "thoughts": ["Cleaning the dataset and handling missing values..."],
    "tool_name": "data_analysis",
    "tool_args": {
        "action": "transform",
        "file_path": "data/raw_data.csv",
        "operations": ["dropna", "normalize", "remove_duplicates"],
        "output_path": "data/clean_data.csv"
    }
}
```

#### visualize - Create charts
```json
{
    "thoughts": ["Creating a visualization of sales trends..."],
    "tool_name": "data_analysis",
    "tool_args": {
        "action": "visualize",
        "file_path": "data/sales.csv",
        "chart_type": "line",
        "x_column": "date",
        "y_column": "revenue",
        "output_path": "charts/sales_trend.png"
    }
}
```

#### financial - Financial modeling
```json
{
    "thoughts": ["Analyzing financial metrics and returns..."],
    "tool_name": "data_analysis",
    "tool_args": {
        "action": "financial",
        "file_path": "data/stock_prices.csv",
        "model_type": "basic"
    }
}
```

#### query - SQL-like queries
```json
{
    "thoughts": ["Querying the data for specific insights..."],
    "tool_name": "data_analysis",
    "tool_args": {
        "action": "query",
        "file_path": "data/sales.csv",
        "query": "SELECT category, SUM(revenue) as total FROM df GROUP BY category ORDER BY total DESC"
    }
}
```

#### export - Export data
```json
{
    "thoughts": ["Exporting the processed data to Excel..."],
    "tool_name": "data_analysis",
    "tool_args": {
        "action": "export",
        "file_path": "data/processed.csv",
        "output_format": "excel",
        "output_path": "reports/final_report.xlsx"
    }
}
```

### Supported File Formats:
- CSV, TSV
- Excel (xlsx, xls)
- JSON
- Parquet
- SQL databases

### Chart Types:
- bar, line, scatter, histogram
- heatmap, pie, box, violin

### Best Practices:
1. Always `load` data first to understand structure
2. Use `transform` to clean before analysis
3. Use `analyze` for statistical insights
4. Use `visualize` to communicate findings
5. Use `export` for final deliverables
