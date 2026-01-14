"""
Advanced Data Analysis and Spreadsheet Manipulation Tool.
Provides comprehensive data processing, analysis, and visualization capabilities.
"""

import os
import json
from python.helpers.tool import Tool, Response
from python.helpers import files


class DataAnalysisTool(Tool):
    """
    Advanced data analysis tool for spreadsheet manipulation,
    statistical analysis, and data visualization.
    """

    async def execute(self,
                     action: str = "",
                     file_path: str = "",
                     **kwargs) -> Response:
        """
        Execute data analysis operations.
        
        Actions:
        - load: Load and preview data from file
        - analyze: Perform statistical analysis
        - transform: Transform/clean data
        - visualize: Create charts and visualizations
        - financial: Financial modeling and analysis
        - export: Export processed data
        - query: Query data with SQL-like syntax
        """
        
        if not action:
            return Response(
                message="Error: No action specified. Available: load, analyze, transform, visualize, financial, export, query",
                break_loop=False
            )

        if action == "load":
            return await self._load_data(file_path, **kwargs)
        elif action == "analyze":
            return await self._analyze_data(file_path, **kwargs)
        elif action == "transform":
            return await self._transform_data(file_path, **kwargs)
        elif action == "visualize":
            return await self._visualize_data(file_path, **kwargs)
        elif action == "financial":
            return await self._financial_model(file_path, **kwargs)
        elif action == "export":
            return await self._export_data(file_path, **kwargs)
        elif action == "query":
            return await self._query_data(file_path, **kwargs)
        else:
            return Response(
                message=f"Error: Unknown action '{action}'",
                break_loop=False
            )

    async def _load_data(self, file_path: str, rows: int = 10, **kwargs) -> Response:
        """Load and preview data from a file."""
        if not file_path:
            return Response(
                message="Error: file_path is required for load action",
                break_loop=False
            )

        ext = os.path.splitext(file_path)[1].lower()
        
        response = f"""## Data Loading: {os.path.basename(file_path)}

### File Type: {ext}

### Loading Script:
```python
import pandas as pd

# Load data based on file type
"""
        if ext in ['.csv', '.tsv']:
            response += f"""df = pd.read_csv("{file_path}")"""
        elif ext in ['.xlsx', '.xls']:
            response += f"""df = pd.read_excel("{file_path}")"""
        elif ext == '.json':
            response += f"""df = pd.read_json("{file_path}")"""
        elif ext == '.parquet':
            response += f"""df = pd.read_parquet("{file_path}")"""
        else:
            response += f"""# Unsupported format, trying CSV
df = pd.read_csv("{file_path}")"""

        response += f"""

# Preview data
print("Shape:", df.shape)
print("\\nColumns:", df.columns.tolist())
print("\\nData Types:")
print(df.dtypes)
print("\\nFirst {rows} rows:")
print(df.head({rows}))
print("\\nBasic Statistics:")
print(df.describe())
```

### Quick Analysis:
Run the above script with `code_execution_tool` (runtime="python") to see your data.

### Supported Formats:
- CSV / TSV
- Excel (xlsx, xls)
- JSON
- Parquet
- SQL databases (via connection string)
"""
        return Response(message=response, break_loop=False)

    async def _analyze_data(self, file_path: str, 
                            analysis_type: str = "descriptive",
                            columns: list = None, **kwargs) -> Response:
        """Perform statistical analysis on data."""
        
        columns_filter = f"[{', '.join(repr(c) for c in columns)}]" if columns else "None"
        
        response = f"""## Statistical Analysis

### File: {file_path}
### Analysis Type: {analysis_type}
### Target Columns: {columns or 'All numeric columns'}

### Analysis Script:
```python
import pandas as pd
import numpy as np
from scipy import stats

# Load data
df = pd.read_csv("{file_path}")  # Adjust reader as needed

# Select columns
columns = {columns_filter}
if columns:
    df_analysis = df[columns]
else:
    df_analysis = df.select_dtypes(include=[np.number])

print("=== Descriptive Statistics ===")
print(df_analysis.describe())

print("\\n=== Additional Metrics ===")
for col in df_analysis.columns:
    print(f"\\n{{col}}:")
    print(f"  Skewness: {{df_analysis[col].skew():.4f}}")
    print(f"  Kurtosis: {{df_analysis[col].kurtosis():.4f}}")
    print(f"  Missing: {{df_analysis[col].isna().sum()}}")
    print(f"  Unique: {{df_analysis[col].nunique()}}")

print("\\n=== Correlation Matrix ===")
print(df_analysis.corr())

# Normality test (for each column)
print("\\n=== Normality Tests (Shapiro-Wilk) ===")
for col in df_analysis.columns:
    if len(df_analysis[col].dropna()) >= 3:
        stat, p_value = stats.shapiro(df_analysis[col].dropna()[:5000])  # Limit for performance
        print(f"{{col}}: stat={{stat:.4f}}, p-value={{p_value:.4f}}")
```

### Analysis Types Available:
- **descriptive**: Basic statistics (mean, std, quartiles)
- **correlation**: Correlation analysis between variables
- **distribution**: Distribution analysis and normality tests
- **outliers**: Outlier detection (IQR, Z-score)
- **trends**: Trend analysis for time series
- **comparison**: Group comparison (t-test, ANOVA)
"""
        return Response(message=response, break_loop=False)

    async def _transform_data(self, file_path: str,
                              operations: list = None,
                              output_path: str = "", **kwargs) -> Response:
        """Transform and clean data."""
        
        operations = operations or []
        output_path = output_path or file_path.replace(".", "_transformed.")

        response = f"""## Data Transformation

### Source: {file_path}
### Output: {output_path}

### Transformation Script:
```python
import pandas as pd
import numpy as np

# Load data
df = pd.read_csv("{file_path}")  # Adjust reader as needed
print(f"Original shape: {{df.shape}}")

# Common transformations:

# 1. Handle missing values
df_clean = df.copy()

# Fill numeric columns with median
numeric_cols = df_clean.select_dtypes(include=[np.number]).columns
df_clean[numeric_cols] = df_clean[numeric_cols].fillna(df_clean[numeric_cols].median())

# Fill categorical columns with mode
cat_cols = df_clean.select_dtypes(include=['object']).columns
for col in cat_cols:
    df_clean[col] = df_clean[col].fillna(df_clean[col].mode()[0] if not df_clean[col].mode().empty else 'Unknown')

# 2. Remove duplicates
df_clean = df_clean.drop_duplicates()

# 3. Standardize column names
df_clean.columns = df_clean.columns.str.lower().str.replace(' ', '_').str.replace('[^a-z0-9_]', '', regex=True)

# 4. Convert data types
# df_clean['date_column'] = pd.to_datetime(df_clean['date_column'])
# df_clean['numeric_column'] = pd.to_numeric(df_clean['numeric_column'], errors='coerce')

# 5. Create derived columns
# df_clean['new_column'] = df_clean['col1'] + df_clean['col2']

# 6. Filter rows
# df_clean = df_clean[df_clean['column'] > 0]

# 7. Normalize/Scale numeric columns
from sklearn.preprocessing import StandardScaler, MinMaxScaler
# scaler = StandardScaler()
# df_clean[numeric_cols] = scaler.fit_transform(df_clean[numeric_cols])

print(f"Transformed shape: {{df_clean.shape}}")

# Save transformed data
df_clean.to_csv("{output_path}", index=False)
print(f"Saved to: {output_path}")
```

### Common Operations:
| Operation | Description |
|-----------|-------------|
| dropna | Remove rows with missing values |
| fillna | Fill missing values |
| drop_duplicates | Remove duplicate rows |
| rename | Rename columns |
| astype | Convert data types |
| filter | Filter rows by condition |
| sort | Sort by columns |
| groupby | Group and aggregate |
| pivot | Create pivot table |
| melt | Unpivot data |
| merge | Join with another dataset |
"""
        return Response(message=response, break_loop=False)

    async def _visualize_data(self, file_path: str,
                              chart_type: str = "auto",
                              x_column: str = "",
                              y_column: str = "",
                              output_path: str = "", **kwargs) -> Response:
        """Create data visualizations."""
        
        output_path = output_path or "chart.png"

        response = f"""## Data Visualization

### Source: {file_path}
### Chart Type: {chart_type}
### Output: {output_path}

### Visualization Script:
```python
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Set style
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_palette("husl")

# Load data
df = pd.read_csv("{file_path}")

# Create figure
fig, ax = plt.subplots(figsize=(12, 6))

"""
        if chart_type == "bar" or (x_column and y_column):
            response += f"""# Bar Chart
df.plot(kind='bar', x='{x_column or "x"}', y='{y_column or "y"}', ax=ax)
ax.set_xlabel('{x_column or "X Axis"}')
ax.set_ylabel('{y_column or "Y Axis"}')
"""
        elif chart_type == "line":
            response += f"""# Line Chart
df.plot(kind='line', x='{x_column or "x"}', y='{y_column or "y"}', ax=ax, marker='o')
ax.set_xlabel('{x_column or "X Axis"}')
ax.set_ylabel('{y_column or "Y Axis"}')
"""
        elif chart_type == "scatter":
            response += f"""# Scatter Plot
df.plot(kind='scatter', x='{x_column or "x"}', y='{y_column or "y"}', ax=ax, alpha=0.6)
ax.set_xlabel('{x_column or "X Axis"}')
ax.set_ylabel('{y_column or "Y Axis"}')
"""
        elif chart_type == "histogram":
            response += f"""# Histogram
df['{y_column or df.select_dtypes(include="number").columns[0]}'].hist(bins=30, ax=ax, edgecolor='white')
ax.set_xlabel('Value')
ax.set_ylabel('Frequency')
"""
        elif chart_type == "heatmap":
            response += """# Correlation Heatmap
numeric_df = df.select_dtypes(include=['number'])
sns.heatmap(numeric_df.corr(), annot=True, cmap='coolwarm', center=0, ax=ax)
"""
        elif chart_type == "pie":
            response += f"""# Pie Chart
df['{x_column or "category"}'].value_counts().plot(kind='pie', autopct='%1.1f%%', ax=ax)
ax.set_ylabel('')
"""
        else:
            response += """# Auto-detect best chart
numeric_cols = df.select_dtypes(include=['number']).columns[:4]
if len(numeric_cols) >= 2:
    # Correlation heatmap for multiple numeric columns
    sns.heatmap(df[numeric_cols].corr(), annot=True, cmap='coolwarm', ax=ax)
elif len(numeric_cols) == 1:
    # Histogram for single numeric column
    df[numeric_cols[0]].hist(bins=30, ax=ax, edgecolor='white')
else:
    # Bar chart for categorical data
    df[df.columns[0]].value_counts().head(10).plot(kind='bar', ax=ax)
"""

        response += f"""
plt.title('Data Visualization')
plt.tight_layout()
plt.savefig('{output_path}', dpi=150, bbox_inches='tight')
plt.show()
print(f"Chart saved to: {output_path}")
```

### Available Chart Types:
| Type | Best For |
|------|----------|
| bar | Categorical comparisons |
| line | Trends over time |
| scatter | Relationships between variables |
| histogram | Distribution of values |
| heatmap | Correlation matrices |
| pie | Part-to-whole relationships |
| box | Distribution and outliers |
| violin | Distribution shape |
"""
        return Response(message=response, break_loop=False)

    async def _financial_model(self, file_path: str,
                               model_type: str = "basic",
                               **kwargs) -> Response:
        """Perform financial modeling and analysis."""
        
        response = f"""## Financial Analysis

### Source: {file_path}
### Model Type: {model_type}

### Financial Analysis Script:
```python
import pandas as pd
import numpy as np

# Load financial data
df = pd.read_csv("{file_path}")

# Common financial calculations:

# 1. Returns calculation
def calculate_returns(prices):
    return prices.pct_change().dropna()

# 2. Moving averages
def moving_average(data, window):
    return data.rolling(window=window).mean()

# 3. Volatility (standard deviation of returns)
def volatility(returns, window=252):
    return returns.rolling(window=window).std() * np.sqrt(252)

# 4. Sharpe Ratio
def sharpe_ratio(returns, risk_free_rate=0.02):
    excess_returns = returns - risk_free_rate/252
    return np.sqrt(252) * excess_returns.mean() / returns.std()

# 5. Maximum Drawdown
def max_drawdown(prices):
    peak = prices.expanding(min_periods=1).max()
    drawdown = (prices - peak) / peak
    return drawdown.min()

# 6. CAGR (Compound Annual Growth Rate)
def cagr(start_value, end_value, years):
    return (end_value / start_value) ** (1/years) - 1

# Example usage (adjust column names):
# Assuming 'close' column exists
if 'close' in df.columns:
    prices = df['close']
    returns = calculate_returns(prices)
    
    print("=== Financial Metrics ===")
    print(f"Total Return: {{(prices.iloc[-1] / prices.iloc[0] - 1) * 100:.2f}}%")
    print(f"Annualized Volatility: {{volatility(returns).iloc[-1] * 100:.2f}}%")
    print(f"Sharpe Ratio: {{sharpe_ratio(returns):.2f}}")
    print(f"Max Drawdown: {{max_drawdown(prices) * 100:.2f}}%")
    
    # Moving averages
    df['MA_20'] = moving_average(prices, 20)
    df['MA_50'] = moving_average(prices, 50)
    df['MA_200'] = moving_average(prices, 200)
    
    print("\\n=== Latest Moving Averages ===")
    print(df[['close', 'MA_20', 'MA_50', 'MA_200']].tail())

# For income statement / balance sheet data:
# Calculate financial ratios
def financial_ratios(data):
    ratios = {{}}
    
    # Profitability
    if 'revenue' in data and 'net_income' in data:
        ratios['net_margin'] = data['net_income'] / data['revenue']
    
    if 'revenue' in data and 'gross_profit' in data:
        ratios['gross_margin'] = data['gross_profit'] / data['revenue']
    
    # Liquidity
    if 'current_assets' in data and 'current_liabilities' in data:
        ratios['current_ratio'] = data['current_assets'] / data['current_liabilities']
    
    # Leverage
    if 'total_debt' in data and 'total_equity' in data:
        ratios['debt_to_equity'] = data['total_debt'] / data['total_equity']
    
    return ratios
```

### Financial Model Types:
| Type | Description |
|------|-------------|
| basic | Basic financial metrics |
| dcf | Discounted Cash Flow valuation |
| ratios | Financial ratio analysis |
| risk | Risk metrics (VaR, CVaR) |
| portfolio | Portfolio optimization |
| forecast | Financial forecasting |

### Key Metrics Calculated:
- Returns (daily, monthly, annual)
- Volatility
- Sharpe Ratio
- Maximum Drawdown
- CAGR
- Financial Ratios
- Moving Averages
"""
        return Response(message=response, break_loop=False)

    async def _export_data(self, file_path: str,
                           output_format: str = "csv",
                           output_path: str = "", **kwargs) -> Response:
        """Export processed data to various formats."""
        
        output_path = output_path or f"output.{output_format}"

        response = f"""## Data Export

### Source: {file_path}
### Format: {output_format}
### Output: {output_path}

### Export Script:
```python
import pandas as pd

# Load data
df = pd.read_csv("{file_path}")  # Adjust reader as needed

# Export to selected format
"""
        if output_format == "csv":
            response += f"""df.to_csv("{output_path}", index=False)"""
        elif output_format == "excel":
            response += f"""df.to_excel("{output_path}", index=False, engine='openpyxl')"""
        elif output_format == "json":
            response += f"""df.to_json("{output_path}", orient='records', indent=2)"""
        elif output_format == "parquet":
            response += f"""df.to_parquet("{output_path}", index=False)"""
        elif output_format == "html":
            response += f"""df.to_html("{output_path}", index=False)"""
        elif output_format == "markdown":
            response += f"""with open("{output_path}", 'w') as f:
    f.write(df.to_markdown(index=False))"""
        else:
            response += f"""df.to_csv("{output_path}", index=False)  # Default to CSV"""

        response += f"""

print(f"Data exported to: {output_path}")
print(f"Shape: {{df.shape}}")
```

### Supported Formats:
| Format | Extension | Best For |
|--------|-----------|----------|
| csv | .csv | Universal compatibility |
| excel | .xlsx | Spreadsheet applications |
| json | .json | Web applications, APIs |
| parquet | .parquet | Big data, analytics |
| html | .html | Web display |
| markdown | .md | Documentation |
"""
        return Response(message=response, break_loop=False)

    async def _query_data(self, file_path: str,
                          query: str = "",
                          **kwargs) -> Response:
        """Query data using SQL-like syntax."""
        
        if not query:
            return Response(
                message="Error: query is required for query action",
                break_loop=False
            )

        response = f"""## Data Query

### Source: {file_path}
### Query: {query}

### Query Script:
```python
import pandas as pd
import pandasql as ps

# Load data
df = pd.read_csv("{file_path}")  # Adjust reader as needed

# Execute SQL query
query = \"\"\"
{query}
\"\"\"

# Using pandasql
result = ps.sqldf(query, locals())
print(result)

# Alternative: Using pandas query method for simple filters
# result = df.query("column > value")
```

### Query Examples:
```sql
-- Select specific columns
SELECT column1, column2 FROM df WHERE column1 > 100

-- Aggregation
SELECT category, COUNT(*) as count, AVG(value) as avg_value
FROM df GROUP BY category

-- Filtering
SELECT * FROM df WHERE date >= '2024-01-01' AND status = 'active'

-- Sorting
SELECT * FROM df ORDER BY value DESC LIMIT 10

-- Joins (if multiple DataFrames)
SELECT a.*, b.info FROM df1 a LEFT JOIN df2 b ON a.id = b.id
```

### Note:
Install pandasql if needed: `pip install pandasql`
"""
        return Response(message=response, break_loop=False)

    def get_log_object(self):
        return self.agent.context.log.log(
            type="tool",
            heading=f"icon://analytics {self.agent.agent_name}: Data Analysis",
            content="",
            kvps=self.args
        )
