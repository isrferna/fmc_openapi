
# FMC OpenAPI

**fmc_openapi** is a Python package that simplifies interaction with Cisco Firepower Management Center (FMC) APIs. It dynamically parses the OpenAPI (Swagger) specification to discover available endpoints and interact with them using the `operationId`.

To identify which operations are supported, you can refer to the [`Operation ID table`](OPERATIONID_TABLE.md).

---

## 🚀 Features

- 🔍 Parses the Swagger file to discover endpoints
- 💡 Calls API operations by operationId
- 🔐 Session handling (login/logout)
- 🧰 Simplifies complex API interactions
- ⚠️ Error handling built-in
- 🏢 SCC/CDO Token-Based Authentication
- 🔄 Automatic pagination handling (manual pagination is also possible)
- 📦 Bulk operations
- 📄 All endpoints defined in the Swagger spec

---

## 📦 Installation

```bash
pip install fmc_openapi
```

Import API client

```python
from fmc_openapi import FMCOpenAPIClient
```

---

## 🧑‍💻 Usage Example

### Connecting to FMC (username/password)

```python
from fmc_openapi import FMCOpenAPIClient

with FMCOpenAPIClient(
    hostname="fmc.example.com",
    username="your_username",
    password="your_password",
    verify=False
) as fmc:
    domains = fmc.operation("getAllDomain")
```

### Connecting to SCC (token-based)

```python
from fmc_openapi import FMCOpenAPIClient

with FMCOpenAPIClient(
    hostname="scc.example.com",
    token="your_token_here",
    verify=False
) as fmc:
    domains = fmc.operation("getAllDomain")
```

---

### Get all access policy rules

```python
import jmespath

with FMCOpenAPIClient(
    hostname="fmc.example.com",
    username="your_username",
    password="your_password",
    verify=False
) as fmc:
    # Get domain UUID
    domains = fmc.operation("getAllDomain")
    domain_uuid = jmespath.search("items[?name=='my-domain'].uuid | [0]", domains)

    # Get ACP UUID
    acp_response = fmc.operation("getAllAccessPolicy", domainUUID=domain_uuid)
    acp_uuid = jmespath.search("items[?name=='my-policy'].uuid | [0]", acp_response)

    # Get all access policy rules (with automatic pagination)
    rules = fmc.operation(
        "getAllAccessRule", 
        limit=1000, 
        domainUUID=domain_uuid, 
        containerUUID=acp_uuid, 
        expanded=True
    )
```

---

### Manual Pagination

```python
rules = fmc.operation(
    "getAllAccessRule",
    limit=1000,
    domainUUID=domain_uuid,
    containerUUID=acp_uuid,
    expanded=True,
    manual_pagination=True
)
```

---

### Creating Objects

```python
payload = {
    "name": "obj-192.168.1.0",
    "type": "Network",
    "value": "192.168.1.0/24",
}

fmc.operation("createMultipleNetworkObject", payload=payload, domainUUID=domain_uuid)
```

---

### Bulk Operations

```python
response = fmc.operation(
    "getHitCount", 
    limit=1000, 
    domainUUID=domain_uuid, 
    containerUUID=ac_uuid_selected, 
    filter=f"deviceId:{device_uuid}", 
    expanded=True,
    bulk=True
)
```

---

## 🧪 Running Tests

Tests are written using `pytest`.

To run tests:

```bash
poetry run pytest
```

Or activate the environment first:

```bash
poetry shell
pytest
```

---

## 🛠 Project Structure

```
fmc_openapi/
├── __init__.py           # Imports FMCOpenAPIClient
├── client.py             # Main client class
├── swagger.py            # Swagger parser
├── utils.py              # Logging and request helpers
tests/
├── test_swagger.py       # Tests for Swagger JSON fetching and operation extraction
├── test_operation.py     # Tests for executing API operations using operationId
├── test_auth.py          # Tests for authentication: login and logout
├── test_client.py        # General client behavior and utility method tests
```

---

## 📄 License

GNU GPL v3 License. See `LICENSE` for details.

---

## 🤝 Contributing

Pull requests are welcome! If you plan to add new features, open an issue first to discuss it.

1. Fork the project
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Open a pull request

---

## ✉️ Contact

Questions? Ideas? [Open an issue](https://github.com/isrferna/fmc_openapi/issues) or drop a message.
