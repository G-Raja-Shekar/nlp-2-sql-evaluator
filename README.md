# SQL Evaluator

A modular Python library for evaluating SQL semantic equivalence and performing batch evaluations with export capabilities.

## Features

- **SQL Semantic Equivalence Evaluation**: Compare SQL queries for semantic similarity
- **Batch Processing**: Evaluate multiple SQL queries at once
- **Modular Architecture**: Well-structured, maintainable codebase
- **Export Capabilities**: Export results to Excel format
- **Custom Evaluators**: Support for custom evaluation functions
- **Comprehensive Analysis**: Detailed analysis of SQL differences

## Installation

1. Clone the repository:

```bash
git clone <repository-url>
cd sql-evaluator
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

## Quick Start

### Basic SQL Evaluation

```python
from sql_evaluator import SQLEvaluator
from sql_evaluator.models import EvaluationRequest

# Initialize evaluator
evaluator = SQLEvaluator()

# Create evaluation request
request = EvaluationRequest(
    input_query="How many users are active?",
    expected_output="SELECT COUNT(*) FROM users WHERE status = 'active';",
    model_output="select count(*) from users where status='active'",
    session_id="test_session"
)

# Evaluate
result = evaluator.evaluate_sql_semantic_equivalence(request)
print(f"Score: {result.score:.2f}, Passed: {result.passed}")
```

### Batch Evaluation

```python
from sql_evaluator import BatchEvaluator
from sql_evaluator.exporters import ExcelExporter

# Initialize batch evaluator
batch_evaluator = BatchEvaluator()

# Prepare evaluation data
evaluations = [
    {
        'natural_query': 'Count active users',
        'expected_sql': 'SELECT COUNT(*) FROM users WHERE status = "active"',
        'generated_sql': 'select count(*) from users where status="active"'
    }
    # ... more evaluations
]

# Run batch evaluation
results = batch_evaluator.evaluate_batch(evaluations)

# Export to Excel
exporter = ExcelExporter()
filename = exporter.export(results)
print(f"Results exported to: {filename}")
```

## Project Structure

```
sql_evaluator/
├── core/
│   ├── evaluator.py          # Core SQL evaluation logic
│   └── batch_evaluator.py    # Batch processing functionality
├── models/
│   ├── evaluation_result.py  # Result data models
│   └── evaluation_request.py # Request data models
├── sql/
│   ├── normalizer.py         # SQL normalization utilities
│   └── parser.py             # SQL parsing utilities
├── utils/
│   └── similarity.py         # Similarity calculation utilities
├── exporters/
│   ├── base_exporter.py      # Base exporter interface
│   └── excel_exporter.py     # Excel export implementation
└── __init__.py
```

## Running Examples

### Run Demo Scenarios

```bash
python main.py demo
```

### Run Batch Evaluation from Test Data

```bash
python main.py
```

## Configuration

The evaluator uses a default passing threshold of 0.8 (80%). You can customize this:

```python
evaluator = SQLEvaluator(passing_threshold=0.85)
```

## Contributing

1. Follow the modular structure
2. Add tests for new functionality
3. Update documentation
4. Ensure code quality with linting

## License

MIT License
