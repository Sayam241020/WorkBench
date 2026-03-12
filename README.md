# WorkBench Evaluation (Extended)

This repository evaluates the performance of open-weight LLM agents on the WorkBench benchmark, specifically augmented to support fully local execution via `llama-cpp-python` and extended with a new Slack mock service domain.

## Prerequisites

Python 3.10 is required. Ensure your system meets the basic requirements for compiling/installing numpy and python dependencies. 
This branch natively executes Llama-3-8B-Instruct quantized uniformly out-of-the-box on CPU.

## Setup Instructions

Run these commands strictly from the repository root:

1. **Initialize Environment**
   ```bash
   python -m venv venv
   .\venv\Scripts\activate  # On Unix use: source venv/bin/activate
   pip install -r requirements.txt
   ```
   *Note: If `llama-cpp-python` fails to compile locally during requirements installation, install the pre-compiled CPU wheel:*
   `pip install --no-cache-dir llama-cpp-python --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cpu`

2. **Download Model**
   Run the model downloader script to fetch the `.gguf` file locally into `/models`.
   ```bash
   python download_model.py
   ```

## Running the Evaluation

The custom evaluation hooks use the `--model_name llama-cpp` flag.

### Baseline Evaluation
To run the standard zero-shot React loop on the test data:
```bash
python scripts/inference/generate_results.py --model_name llama-cpp --queries_path data/processed/queries_and_answers/sample_email_queries_and_answers.csv --tool_selection domains
```

### Improved Agent
The improved agent injects few-shot formatting examples to coerce the model into generating correct LangChain intermediate JSON blobs.
```bash
python scripts/inference/generate_results.py --model_name llama-cpp --queries_path data/processed/queries_and_answers/sample_email_queries_and_answers.csv --tool_selection domains --improved
```

### Extra Credit: Slack Domain
The application comes pre-loaded with an entirely new domain, databases, and test queries.
```bash
python scripts/inference/generate_results.py --model_name llama-cpp --queries_path data/processed/queries_and_answers/slack_queries_and_answers.csv --tool_selection domains --improved
```

## Report
Please see `report.md` for my full detailed methodology, results, error analysis, and reflection.
