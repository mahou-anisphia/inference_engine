# Inference Engine

A propositional logic inference engine implementation supporting Truth Table (TT), Forward Chaining (FC), and Backward Chaining (BC) algorithms for evaluating queries against Horn-form knowledge bases.

## Features

- Truth Table (TT) checking algorithm for all knowledge base types
- Forward Chaining (FC) for Horn-form knowledge bases
- Backward Chaining (BC) for Horn-form knowledge bases
- Command-line interface supporting batch operations
- File-based input for knowledge bases and queries
- Support for Horn clauses with standard logical operators

## Requirements

- Python 3.8 or higher
- pip (Python package installer)

## Setup

### Windows

1. Create a virtual environment:
```bash
python -m venv venv
```

2. Activate the virtual environment:
```bash
venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

### Linux/macOS

1. Create a virtual environment:
```bash
python3 -m venv venv
```

2. Activate the virtual environment:
```bash
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

The program operates via command line with the following syntax:

```bash
python iengine.py <filename> <method>
```

Where:
- `<filename>` is the path to your input file containing the knowledge base and query
- `<method>` is one of: TT (Truth Table), FC (Forward Chaining), or BC (Backward Chaining)

Example:
```bash
python iengine.py test1.txt FC
```

### Input File Format

The input file should contain:
1. Knowledge base following the keyword TELL
2. Query following the keyword ASK

Example (test1.txt):
```
TELL
p2=> p3; p3 => p1; c => e; b&e => f; f&g => h; p2&p1&p3 =>d; p1&p3 => c; a; b; p2;
ASK
d
```

### Output Format

The program outputs either YES or NO, depending on whether the query follows from the knowledge base:

- For TT method: `YES: <number_of_models>` or `NO`
- For FC/BC methods: `YES: <list_of_entailed_symbols>` or `NO`

Example outputs:
```
# Truth Table
> YES: 3

# Forward Chaining
> YES: a, b, p2, p3, p1, c, e, f, d

# Backward Chaining
> YES: p2, p3, p1, d
```

## Logical Operators

- `~` for negation (¬)
- `&` for conjunction (∧)
- `||` for disjunction (∨)
- `=>` for implication (⇒)
- `<=>` for biconditional (⇔)


## Development

To create a requirements.txt file for your development environment:

```bash
pip freeze > requirements.txt
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details

## Acknowledgments

- Based on algorithms from "Artificial Intelligence: A Modern Approach" (3rd Edition)
- Developed as part of COS30019 Introduction to Artificial Intelligence
