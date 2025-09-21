# Premium Service API

A Django REST Framework service for calculating and managing insurance premiums.

## Setup Instructions

1. **Clone the repository**
2. **Create and activate a virtual environment:**
   ```cmd
   python -m venv premium-venv
   premium-venv\Scripts\activate.bat
   ```
3. **Install dependencies:**
   ```cmd
   pip install -r requirements.txt
   ```
4. **Configure environment variables:**
   - Edit `.env` with your secrets and settings.
5. **Apply migrations:**
   ```cmd
   python manage.py migrate
   ```
6. **Collect static files (for Swagger UI):**
   ```cmd
   python manage.py collectstatic --noinput
   ```
7. **Run the development server:**
   ```cmd
   python manage.py runserver 8005
   ```

## API Endpoints

### Premium Calculation
- `POST /api/v1/premium/calculate`
  - Request: `{ "customer_id": "<uuid>", "policy_id": "<uuid>", "base_premium": 1000, "addon_premium": 200, "risk_adjustment": 50, "discount": 100 }`
  - Response: PremiumQuote object

### Retrieve Latest Premium Quote
- `GET /api/v1/premium/{policy_id}`
  - Response: PremiumQuote object

### Recalculate Premium
- `POST /api/v1/premium/recalculate`
  - Request: `{ "policy_id": "<uuid>", "new_premium": 1200, "reason": "Recalculation" }`
  - Response: PremiumQuote object

### Filtering
- `GET /api/v1/premium/quotes?customer_id=<uuid>&policy_id=<uuid>&status=<status>`
- `GET /api/v1/premium/history?policy_id=<uuid>`

## Swagger & API Documentation
- **OpenAPI schema:** `GET /api/schema/`
- **Swagger UI:** `GET /api/docs/`
- **Redoc:** `GET /api/redoc/`

## Postman Collection
The Postman collection for this API is included in the repository as `insurance.postman_collection.json`.

## Data Types
- All IDs are UUIDs.
- Premium fields are decimals.
- Status and factor_type are string choices.

---
For further details, see the code and docstrings in each module.
