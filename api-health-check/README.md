# API Health Monitoring

This project monitors the health of APIs and logs their status. It is designed for easy local setup and usage.

## Features

- Monitors specified APIs for availability
- Logs status and errors using a custom logger
- Simple, extensible Python codebase

## Prerequisites

- Python 3.7 or higher installed on your system

## Setup Instructions

1. **Clone the repository:**
   ```sh
   git clone https://github.com/your-username/Pet-Projects-Python.git
   cd Pet-Projects-Python/api-health-check
   ```

2. **Create and activate a virtual environment (recommended):**
   ```sh
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```sh
   pip install -r requirements.txt
   ```

## Running the Project

To start monitoring APIs, run the following command:

```sh
python monitor.py
```

## Customization

- Edit `config.json` to add or modify the APIs you want to monitor.
- Adjust logging settings in the `logger.py` file as needed.

## License

MIT License

---
*For learning and demonstration purposes only.*