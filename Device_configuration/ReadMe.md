# Device Configuration Validation Service

[cite_start]This is a backend service built to validate and track network device configurations, focusing on backend fundamentals, async programming, and API design.

---

## 🛠 Tech Stack
[cite_start]This project adheres to the following mandatory tech stack[cite: 4]:
* [cite_start]**Python 3.9+** [cite: 5]
* [cite_start]**FastAPI:** Modern web framework for the API[cite: 6].
* [cite_start]**AsyncIO:** For non-blocking validation and simulated processing delays[cite: 7].
* [cite_start]**Pandas:** Used to generate summary metrics and data analysis[cite: 8].
* [cite_start]**SQLite:** Used for persistent data storage[cite: 9].
* [cite_start]**Docker:** To ensure a consistent and portable environment[cite: 10].

---

## 🚀 Key Features
* [cite_start]**Asynchronous Validation:** The `/validate` endpoint runs asynchronously (non-blocking) and simulates processing delays using async logic[cite: 22, 24].
* [cite_start]**Vendor-Specific Logic:** Automated validation checks based on specific network vendor requirements[cite: 24].
* [cite_start]**Pandas Integration:** High-speed data aggregation for system-wide summaries[cite: 35].
* [cite_start]**Persistent Storage:** Device details and validation statuses are stored in a database where `device_id` is unique[cite: 21].

---

## 📋 Validation Rules
[cite_start]The service applies the following rules during the `POST /validate` process[cite: 24]:
1. **Valid IPv4 Format:** Validates that the device IP is a correctly formatted IPv4 address.
2. **Mandatory Keywords:** Checks the configuration text for vendor-specific terms:
   * **Cisco:** must contain `interface`.
   * **Juniper:** must contain `set`.
   * **Versa:** must contain `system`.

---

## 📡 API Endpoints

### 1. Device Registration
* [cite_start]**`POST /devices`**: Registers a new device with `device_id`, `vendor`, `ip`, and `config`[cite: 12, 13, 15].

### 2. Configuration Validation
* [cite_start]**`POST /validate`**: Triggers a non-blocking validation process and simulates delay[cite: 23, 24].

### 3. Retrieval & Summary
* [cite_start]**`GET /devices/{device_id}`**: Returns device details, including the last validation status and timestamp[cite: 31, 32, 33].
* **`GET /summary`**: Uses Pandas to generate metrics for total devices, passed validations, and failed validations[cite: 34, 35, 36, 37, 38, 39].

---

## 🐳 Docker Execution
To build and run the service using Docker[cite: 47], use the following commands:

**1. Build the Image:**
```bash
docker build -t device-config-service .



## Populate mock device data directly into the SQLite DB for the Device Configuration Validation Service

- Multi-threaded inserts  
- Creates table if missing  
- Optional reset (delete existing rows)

### Default DB path
Assumes you run this from your project root:

- `./devices.db`

### Usage

```bash
python populate_mock_db.py --count 200 --threads 10
python populate_mock_db.py --count 500 --threads 20 --db ./devices.db
python populate_mock_db.py --count 200 --threads 10 --reset
