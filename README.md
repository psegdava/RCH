# RCH Algorithm Project

This project implements the RCH (Route Choice Heuristic) algorithm for route optimization and volume calculation in logistics and transportation planning.

## Project Structure

```
RCH_Algorithm/
├── RCH_module/           # Main algorithm implementation
├── input_RCH/           # Input data for RCH calculations
├── input_total/         # Total input data
├── viajes_prueba/       # Test trips data
├── soluciones/          # Solutions directory
├── pruebas/             # Test directory
├── not_loaded.xlsx      # Data file for unloaded items
├── requirements.txt     # Project dependencies
└── *.ipynb             # Jupyter notebooks for analysis
```

## Requirements

- Python 3.x
- See [requirements.txt](requirements.txt) for all dependencies
- Key dependencies include:
  - pandas
  - numpy
  - scikit-learn
  - tensorflow
  - fastai
  - various data processing and analysis libraries

## Setup

1. Clone the repository
2. Create a virtual environment (recommended)
3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

The project includes several Jupyter notebooks for different purposes:
- `reading.ipynb`: For reading and processing input data
- `fetch_input.ipynb`: For fetching input data
- `carga_dinamica.ipynb`: For dynamic loading calculations

The main functionality is implemented in the `RCH_module` directory, with the core algorithm in `RCH.py`.

## Input Data

The project works with Excel files containing:
- Viajes (Trips) data
- Partidas (Shipments) data
- Volume calculations
- Route optimization parameters

## Output

The project generates optimized routes and volume calculations for logistics operations, with results stored in the `soluciones` directory.

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
