# Crypto Data Analyzer with Crew AI

## Overview

This project utilizes Crew AI to fetch and analyze cryptocurrency data from the WazirX API. The primary objective is to provide insights into recent 24-hour cryptocurrency data, including summaries, comparisons with Bitcoin, and investment ratings.

## Features

- **Data Fetching**: Retrieves the latest 24-hour cryptocurrency data from the WazirX API.
- **Data Analysis**: Summarizes the data and compares it with Bitcoin.
- **Value Extraction**: Identifies the highest price among the cryptocurrencies.
- **Report Generation**: Produces a comprehensive report summarizing the analysis.

## API Endpoint

The project fetches data from the following API endpoint:

- **URL**: `https://api.wazirx.com/sapi/v1/tickers/24hr`
- **Description**: Provides 24-hour ticker data for cryptocurrencies.

## Data Format

The data fetched from the API is in the following format:

```json
[
    {
        "symbol": "btcinr",
        "baseAsset": "btc",
        "quoteAsset": "inr",
        "openPrice": "4503151",
        "lowPrice": "4503151.0",
        "highPrice": "4503151.0",
        "lastPrice": "4503151.0",
        "volume": "0",
        "bidPrice": "4500000.0",
        "askPrice": "4512699.0",
        "at": 1723214981000
    },
    {
        "symbol": "xrpinr",
        "baseAsset": "xrp",
        "quoteAsset": "inr",
        "openPrice": "43.2",
        "lowPrice": "43.2",
        "highPrice": "43.2",
        "lastPrice": "43.2",
        "volume": "0",
        "bidPrice": "43.2",
        "askPrice": "43.99",
        "at": 1723214981000
    }
]
```

## Getting Started

### Prerequisites

- Python 3.x
- Required libraries: `requests`, `crewai`, `langchain_groq`, `google.colab`

### Installation

1. **Clone the repository:**

    ```bash
    git clone https://github.com/yourusername/crypto-data-analyzer.git
    cd crypto-data-analyzer
    ```

2. **Install the required libraries:**

    ```bash
    pip install requests crewai langchain_groq google.colab
    ```

3. **Set up environment variables:**

    - Ensure you have `GROQ_API_KEY` and `SERP_API_KEY` set in your environment variables.

### Usage

1. **Run the script:**

    ```bash
    python crytoAi.py
    ```

2. **Output:**
   - `crypto_data.json`: Contains the fetched cryptocurrency data.
   - `report.txt`: A detailed report summarizing the data analysis.

## Code Explanation

- **Data Fetching**: Uses the `requests` library to fetch data from the WazirX API and saves it to `crypto_data.json`.
- **Agent Definition**: Defines agents for data fetching, summarization, and value extraction using Crew AI.
- **Task Definition**: Creates tasks for data fetching, summarizing, and extracting maximum values.
- **Processing**: Executes tasks sequentially using Crew AI and generates a report in `report.txt`.

## Example Output

- **`crypto_data.json`**: Contains raw data from the API.
- **`report.txt`**: Includes summaries, comparisons with Bitcoin, and ratings for each cryptocurrency.

## Contributing

Feel free to open issues or submit pull requests if you have suggestions for improvements or new features.
