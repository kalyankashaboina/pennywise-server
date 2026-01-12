# Recurring Transaction API - Test Guide

## API Endpoints Summary

All endpoints are accessible at: `/api/recurring` (based on router prefix configuration)

### 1. **POST** - Create Recurring Transaction
**Endpoint:** `POST /api/recurring/`
**Status Code:** 201

**Request Body:**
```json
{
  "amount": 5000.0,
  "type": "income",
  "category": "Salary",
  "description": "Monthly salary from company",
  "frequency": "monthly",
  "next_run_at": "2026-02-05T10:00:00",
  "parent_recurring_id": null
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "rec1",
    "user_id": "user1",
    "amount": 5000.0,
    "type": "income",
    "category": "Salary",
    "description": "Monthly salary from company",
    "frequency": "monthly",
    "next_run_at": "2026-02-05T10:00:00",
    "active": true,
    "parent_recurring_id": null,
    "last_executed_at": "2025-12-05T10:00:00",
    "created_at": "2025-11-01T10:00:00",
    "updated_at": "2025-12-05T10:00:00"
  }
}
```

---

### 2. **GET** - List Recurring Transactions
**Endpoint:** `GET /api/recurring/?page=1&limit=20`
**Status Code:** 200

**Query Parameters:**
- `page` (int, default=1): Page number for pagination
- `limit` (int, default=20, max=100): Items per page
- `frequency` (optional): Filter by frequency (daily|weekly|monthly|yearly)
- `category` (optional): Filter by category
- `type` (optional): Filter by type (income|expense)
- `active_only` (bool, default=true): Show only active recurring transactions

**Response:**
```json
{
  "success": true,
  "page": 1,
  "limit": 20,
  "total": 8,
  "count": 8,
  "pages": 1,
  "data": [
    {
      "id": "rec1",
      "user_id": "user1",
      "amount": 5000.0,
      "type": "income",
      "category": "Salary",
      "description": "Monthly salary from company",
      "frequency": "monthly",
      "next_run_at": "2026-02-05T10:00:00",
      "active": true,
      "parent_recurring_id": null,
      "last_executed_at": "2025-12-05T10:00:00",
      "created_at": "2025-11-01T10:00:00",
      "updated_at": "2025-12-05T10:00:00"
    }
  ]
}
```

---

### 3. **GET** - Get Recurring Transaction by ID
**Endpoint:** `GET /api/recurring/{recurring_id}`
**Status Code:** 200

**Path Parameters:**
- `recurring_id` (string): 24-character MongoDB ID

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "rec1",
    "user_id": "user1",
    "amount": 5000.0,
    "type": "income",
    "category": "Salary",
    "description": "Monthly salary from company",
    "frequency": "monthly",
    "next_run_at": "2026-02-05T10:00:00",
    "active": true,
    "parent_recurring_id": null,
    "last_executed_at": "2025-12-05T10:00:00",
    "created_at": "2025-11-01T10:00:00",
    "updated_at": "2025-12-05T10:00:00"
  }
}
```

---

### 4. **PUT** - Update Recurring Transaction
**Endpoint:** `PUT /api/recurring/{recurring_id}`
**Status Code:** 200

**Path Parameters:**
- `recurring_id` (string): 24-character MongoDB ID

**Request Body (all fields optional):**
```json
{
  "amount": 5100.0,
  "type": "income",
  "category": "Salary",
  "description": "Monthly salary - updated",
  "frequency": "monthly",
  "next_run_at": "2026-02-05T10:00:00",
  "active": true
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "rec1",
    "user_id": "user1",
    "amount": 5100.0,
    "type": "income",
    "category": "Salary",
    "description": "Monthly salary - updated",
    "frequency": "monthly",
    "next_run_at": "2026-02-05T10:00:00",
    "active": true,
    "parent_recurring_id": null,
    "last_executed_at": "2025-12-05T10:00:00",
    "created_at": "2025-11-01T10:00:00",
    "updated_at": "2026-01-07T15:30:00"
  }
}
```

---

### 5. **DELETE** - Delete (Deactivate) Recurring Transaction
**Endpoint:** `DELETE /api/recurring/{recurring_id}`
**Status Code:** 200

**Path Parameters:**
- `recurring_id` (string): 24-character MongoDB ID

**Response:**
```json
{
  "success": true
}
```

---

### 6. **POST** - Execute Recurring Transaction NOW (Real-Time Testing)
**Endpoint:** `POST /api/recurring/{recurring_id}/execute-now`
**Status Code:** 200

**Path Parameters:**
- `recurring_id` (string): 24-character MongoDB ID

**Response:**
```json
{
  "success": true,
  "message": "Recurring transaction executed successfully"
}
```

**Note:** This endpoint immediately creates a transaction from the recurring rule, regardless of the `next_run_at` date. Perfect for real-time testing.

---

### 7. **GET** - Get Generated Transactions from Recurring Rule
**Endpoint:** `GET /api/recurring/{recurring_id}/transactions`
**Status Code:** 200

**Path Parameters:**
- `recurring_id` (string): 24-character MongoDB ID

**Query Parameters:**
- `page` (int, default=1): Page number for pagination
- `limit` (int, default=20, max=100): Items per page

**Response:**
```json
{
  "success": true,
  "recurring_id": "rec1",
  "page": 1,
  "limit": 20,
  "total": 3,
  "count": 3,
  "pages": 1,
  "data": [
    {
      "id": "tx123",
      "user_id": "user1",
      "date": "2026-01-05T10:00:00",
      "amount": 5000.0,
      "type": "income",
      "category": "Salary",
      "description": "Monthly salary from company",
      "source": "recurring",
      "import_id": null,
      "is_recurring": true,
      "is_deleted": false,
      "deleted_at": null,
      "created_at": "2026-01-05T10:00:00",
      "updated_at": "2026-01-05T10:00:00"
    }
  ]
}
```

---

## Testing with cURL Examples

### Create Recurring Transaction
```bash
curl -X POST http://localhost:8000/api/recurring/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 5000.0,
    "type": "income",
    "category": "Salary",
    "description": "Monthly salary",
    "frequency": "monthly",
    "next_run_at": "2026-02-05T10:00:00"
  }'
```

### List Recurring Transactions
```bash
curl -X GET "http://localhost:8000/api/recurring/?page=1&limit=20&frequency=monthly" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Get by ID
```bash
curl -X GET http://localhost:8000/api/recurring/rec1 \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Update Recurring Transaction
```bash
curl -X PUT http://localhost:8000/api/recurring/rec1 \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 5100.0,
    "description": "Updated monthly salary"
  }'
```

### Delete Recurring Transaction
```bash
curl -X DELETE http://localhost:8000/api/recurring/rec1 \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Execute Now (Real-Time Testing)
```bash
curl -X POST http://localhost:8000/api/recurring/rec1/execute-now \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Get Generated Transactions
```bash
curl -X GET "http://localhost:8000/api/recurring/rec1/transactions?page=1&limit=20" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## Key Features Implemented

✅ **Recurring Transaction Logic**: Full CRUD operations with recursive support
✅ **Pagination & Filtering**: List endpoint supports pagination and filters by frequency, category, type
✅ **Get by ID**: Fetch specific recurring transaction by ID
✅ **Real-Time Testing**: `/execute-now` endpoint for immediate testing
✅ **Transaction Traceability**: `/transactions` endpoint to view all generated transactions
✅ **Frequency Support**: daily, weekly, monthly, yearly
✅ **Status Tracking**: Track last execution time and active status
✅ **Mock Data**: 8 mock recurring transactions for testing

---

## Route Priority

Routes are ordered to prevent conflicts:
1. `POST /` - Create
2. `POST /{id}/execute-now` - Execute immediately
3. `GET /{id}/transactions` - Get generated transactions
4. `GET /{id}` - Get by ID
5. `PUT /{id}` - Update
6. `DELETE /{id}` - Delete
7. `GET /` - List all

This ordering ensures specific routes are matched before generic {id} routes.
