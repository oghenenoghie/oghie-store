# Oghie Store API Reference

**Base URL**
```
http://127.0.0.1:8000
```

All endpoints return and accept `application/json` unless a file upload is involved (use `multipart/form-data` then).

---

## Authentication

JWT-based. Pass the access token on every protected request:

```http
Authorization: Bearer <access_token>
```

Tokens expire — use the refresh endpoint to get a new access token without re-logging in.

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `POST` | `/api/auth/token/` | Public | Get access + refresh tokens |
| `POST` | `/api/auth/token/refresh/` | Public | Exchange refresh token for new access token |
| `POST` | `/api/auth/token/verify/` | Public | Check if a token is valid |
| `GET`  | `/api/auth/me/` | User | Current authenticated user + profile |

### POST `/api/auth/token/`

**Request**
```json
{
  "username": "alice",
  "password": "secret"
}
```

**Response `200`**
```json
{
  "access": "<jwt>",
  "refresh": "<jwt>"
}
```

### GET `/api/auth/me/`

**Response `200`**
```json
{
  "id": 1,
  "username": "alice",
  "email": "alice@example.com",
  "is_staff": false,
  "is_superuser": false,
  "profile": {
    "id": 1,
    "user": 1,
    "username": "alice",
    "email": "alice@example.com",
    "role": "customer",
    "phone": "+1234567890",
    "address": "123 Main St",
    "company_name": "",
    "is_active": true,
    "created_at": "2026-01-01T00:00:00Z",
    "updated_at": "2026-01-01T00:00:00Z"
  }
}
```

**Roles:** `super_admin` | `staff` | `vendor` | `customer`

---

## Permissions Summary

| Resource | Read | Write |
|----------|------|-------|
| Products, categories, currencies, images, CMS | Public | Admin |
| Reviews (approved only) | Public | Authenticated user |
| Wishlist, cart, cart items, my orders | Authenticated user | Authenticated user |
| Checkout | Authenticated user | Authenticated user |
| Orders, order items, coupons, tracking, payments, analytics | Admin | Admin |
| User profiles | Super admin | Super admin |

---

## Pagination

All list endpoints are paginated. Default page size is **20**.

```
GET /api/products/?page=2
```

**Paginated response shape**
```json
{
  "count": 100,
  "next": "http://127.0.0.1:8000/api/products/?page=3",
  "previous": "http://127.0.0.1:8000/api/products/?page=1",
  "results": [ ... ]
}
```

---

## Common Query Parameters

All list endpoints support:

| Parameter | Example | Description |
|-----------|---------|-------------|
| `search` | `?search=shirt` | Full-text search on configured fields |
| `ordering` | `?ordering=-price` | Sort by field; prefix `-` for descending |
| `page` | `?page=2` | Page number |

---

## Products

### Endpoints

Product detail uses `slug` as the identifier.

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `GET` | `/api/products/` | Public | List products |
| `POST` | `/api/products/` | Admin | Create product |
| `GET` | `/api/products/{slug}/` | Public | Get product |
| `PATCH` | `/api/products/{slug}/` | Admin | Update product |
| `DELETE` | `/api/products/{slug}/` | Admin | Delete product |

### Product Filters

| Parameter | Type | Description |
|-----------|------|-------------|
| `category` | slug | Filter by category slug |
| `vendor` | int | Filter by vendor user ID |
| `currency` | string | Filter by currency code (e.g. `USD`) |
| `is_active` | `true`/`false` | Active/inactive products |
| `in_stock` | `true`/`false` | Has stock / out of stock |
| `min_price` | decimal | Minimum price |
| `max_price` | decimal | Maximum price |
| `min_rating` | int (1–5) | Minimum average rating |
| `search` | string | Search name, description, category |
| `ordering` | string | `name`, `price`, `stock_quantity`, `created_at`, `updated_at` |

**Example**
```
GET /api/products/?category=apparel&min_price=10&max_price=100&in_stock=true&ordering=-price
```

### Product Response

```json
{
  "id": 1,
  "vendor": 2,
  "category": 1,
  "category_detail": {
    "id": 1,
    "name": "Apparel",
    "slug": "apparel",
    "description": "Clothing and accessories.",
    "is_active": true,
    "created_at": "2026-01-01T00:00:00Z",
    "updated_at": "2026-01-01T00:00:00Z"
  },
  "name": "Classic T-Shirt",
  "slug": "classic-t-shirt",
  "description": "Soft cotton t-shirt.",
  "price": "29.99",
  "currency": 1,
  "currency_detail": {
    "id": 1,
    "code": "USD",
    "name": "US Dollar",
    "symbol": "$",
    "exchange_rate_to_base": "1.000000",
    "is_base": true,
    "is_active": true
  },
  "stock_quantity": 50,
  "is_active": true,
  "images": [
    {
      "id": 1,
      "product": 1,
      "image": "http://127.0.0.1:8000/media/products/shirt.jpg",
      "alt_text": "Front view",
      "is_primary": true,
      "created_at": "2026-01-01T00:00:00Z"
    }
  ],
  "average_rating": 4.5,
  "review_count": 12,
  "created_at": "2026-01-01T00:00:00Z",
  "updated_at": "2026-01-01T00:00:00Z"
}
```

### Create/Update Product Payload

```json
{
  "vendor": 2,
  "category": 1,
  "name": "Classic T-Shirt",
  "slug": "classic-t-shirt",
  "description": "Soft cotton t-shirt.",
  "price": "29.99",
  "currency": 1,
  "stock_quantity": 50,
  "is_active": true
}
```

---

## Categories

Category detail uses `slug`.

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `GET` | `/api/products/categories/` | Public | List categories |
| `POST` | `/api/products/categories/` | Admin | Create category |
| `GET` | `/api/products/categories/{slug}/` | Public | Get category |
| `PATCH` | `/api/products/categories/{slug}/` | Admin | Update category |
| `DELETE` | `/api/products/categories/{slug}/` | Admin | Delete category |

**Payload**
```json
{
  "name": "Apparel",
  "slug": "apparel",
  "description": "Clothing and accessories.",
  "is_active": true
}
```

---

## Currencies

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `GET` | `/api/products/currencies/` | Public | List currencies |
| `POST` | `/api/products/currencies/` | Admin | Create currency |
| `GET` | `/api/products/currencies/{id}/` | Public | Get currency |
| `PATCH` | `/api/products/currencies/{id}/` | Admin | Update currency |
| `DELETE` | `/api/products/currencies/{id}/` | Admin | Delete currency |

**Payload**
```json
{
  "code": "USD",
  "name": "US Dollar",
  "symbol": "$",
  "exchange_rate_to_base": "1.000000",
  "is_base": true,
  "is_active": true
}
```

---

## Product Images

Use `multipart/form-data`. Accepted formats: `jpg`, `jpeg`, `png`, `webp`. Max size: 5 MB.

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `GET` | `/api/products/images/` | Public | List images |
| `POST` | `/api/products/images/` | Admin | Upload image |
| `GET` | `/api/products/images/{id}/` | Public | Get image |
| `PATCH` | `/api/products/images/{id}/` | Admin | Update image record |
| `DELETE` | `/api/products/images/{id}/` | Admin | Delete image |

**Form fields**
```
product    integer  — product ID
image      file     — image file
alt_text   string   — optional description
is_primary boolean  — set as primary image
```

**Response**
```json
{
  "id": 1,
  "product": 1,
  "image": "http://127.0.0.1:8000/media/products/shirt.jpg",
  "alt_text": "Front view",
  "is_primary": true,
  "created_at": "2026-01-01T00:00:00Z"
}
```

---

## Wishlist

Scoped to the authenticated user. User field is auto-set.

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `GET` | `/api/products/wishlist/` | User | List my wishlist |
| `POST` | `/api/products/wishlist/` | User | Add to wishlist |
| `GET` | `/api/products/wishlist/{id}/` | User | Get wishlist item |
| `DELETE` | `/api/products/wishlist/{id}/` | User | Remove from wishlist |

**Request**
```json
{ "product": 1 }
```

**Response**
```json
{
  "id": 1,
  "user": 1,
  "product": 1,
  "product_detail": { /* full product object */ },
  "created_at": "2026-01-01T00:00:00Z"
}
```

> A product can only appear once per user wishlist — duplicate adds return `400`.

---

## Product Reviews

Only **approved** reviews are returned to non-staff users.

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `GET` | `/api/products/reviews/` | Public | List reviews |
| `POST` | `/api/products/reviews/` | User | Submit a review |
| `GET` | `/api/products/reviews/{id}/` | Public | Get review |
| `PATCH` | `/api/products/reviews/{id}/` | User (owner) | Update review |
| `DELETE` | `/api/products/reviews/{id}/` | User (owner) | Delete review |

**Filters**

| Parameter | Description |
|-----------|-------------|
| `product` | Product slug |
| `search` | Search title, comment, username, product name |
| `ordering` | `rating`, `created_at` |

**Request**
```json
{
  "product": 1,
  "rating": 5,
  "title": "Great quality",
  "comment": "The fabric feels excellent."
}
```

**Response**
```json
{
  "id": 1,
  "user": 1,
  "username": "alice",
  "product": 1,
  "rating": 5,
  "title": "Great quality",
  "comment": "The fabric feels excellent.",
  "status": "pending",
  "created_at": "2026-01-01T00:00:00Z",
  "updated_at": "2026-01-01T00:00:00Z"
}
```

**Review statuses:** `pending` (default on create) | `approved` | `rejected`

> Rating must be 1–5. Each user can only review a product once.

---

## Cart

All cart routes are scoped to the authenticated user.

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `GET` | `/api/orders/cart/active/` | User | Get or create active cart |
| `GET` | `/api/orders/cart/` | User | List active carts |
| `GET` | `/api/orders/cart/{id}/` | User | Get specific cart |
| `PATCH` | `/api/orders/cart/{id}/` | User | Update cart (coupon, currency) |
| `POST` | `/api/orders/cart/{id}/checkout/` | User | Convert cart to order |

**Always use `/api/orders/cart/active/` to get the cart** — it creates one if none exists.

### Cart Response

```json
{
  "id": 1,
  "user": 1,
  "currency": 1,
  "coupon": null,
  "is_active": true,
  "items": [
    {
      "id": 1,
      "cart": 1,
      "product": 1,
      "product_name": "Classic T-Shirt",
      "unit_price": "29.99",
      "quantity": 2,
      "line_total": "59.98",
      "created_at": "2026-01-01T00:00:00Z",
      "updated_at": "2026-01-01T00:00:00Z"
    }
  ],
  "subtotal": "59.98",
  "discount_total": "0.00",
  "grand_total": "59.98",
  "created_at": "2026-01-01T00:00:00Z",
  "updated_at": "2026-01-01T00:00:00Z"
}
```

### Apply Coupon / Currency

```
PATCH /api/orders/cart/{id}/
```
```json
{
  "coupon": 3,
  "currency": 1
}
```

---

## Cart Items

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `GET` | `/api/orders/cart/items/` | User | List items in active cart |
| `POST` | `/api/orders/cart/items/` | User | Add item to active cart |
| `GET` | `/api/orders/cart/items/{id}/` | User | Get cart item |
| `PATCH` | `/api/orders/cart/items/{id}/` | User | Update quantity |
| `DELETE` | `/api/orders/cart/items/{id}/` | User | Remove item |

**Add item**
```json
{ "product": 1, "quantity": 2 }
```

**Update quantity**
```json
{ "quantity": 3 }
```

---

## Checkout

```
POST /api/orders/cart/{cart_id}/checkout/
```

**Request**
```json
{
  "shipping_address": "123 Main St, Lagos",
  "billing_address": "123 Main St, Lagos",
  "notes": "Leave at the door."
}
```

All fields are optional.

**Response `201`** — returns the created Order object (see Order Response below).

**What happens on checkout:**
1. Coupon is validated (active, within date range, under usage limit) — returns `400` if invalid
2. Stock is checked per item — returns `400` if insufficient
3. Order is created with status `pending`
4. Order items are created from cart items
5. Product stock quantities are decremented
6. Coupon `used_count` is incremented
7. An initial tracking event is written
8. Cart is marked inactive

**Error responses**
```json
{ "detail": "Cart is empty." }
{ "detail": "Coupon is no longer valid." }
{ "detail": "Insufficient stock for \"Classic T-Shirt\"." }
```

---

## Orders

Order statuses: `draft` | `pending` | `paid` | `processing` | `shipped` | `delivered` | `cancelled`

### My Orders (customer)

Read-only view of the authenticated user's own orders.

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `GET` | `/api/orders/mine/` | User | List my orders |
| `GET` | `/api/orders/mine/{id}/` | User | Get one of my orders |

**Filters:** `search` (order number, status), `ordering` (`created_at`, `updated_at`, `grand_total`)

### Order Response

```json
{
  "id": 1,
  "customer": 1,
  "order_number": "OGH-A1B2C3D4E5F6",
  "status": "pending",
  "coupon": null,
  "currency": 1,
  "subtotal": "59.98",
  "discount_total": "0.00",
  "shipping_total": "0.00",
  "tax_total": "0.00",
  "grand_total": "59.98",
  "shipping_address": "123 Main St",
  "billing_address": "123 Main St",
  "notes": "",
  "items": [
    {
      "id": 1,
      "order": 1,
      "product": 1,
      "product_name": "Classic T-Shirt",
      "unit_price": "29.99",
      "quantity": 2,
      "line_total": "59.98"
    }
  ],
  "tracking_events": [
    {
      "id": 1,
      "order": 1,
      "status": "pending",
      "location": "",
      "message": "Order placed",
      "created_at": "2026-01-01T00:00:00Z"
    }
  ],
  "created_at": "2026-01-01T00:00:00Z",
  "updated_at": "2026-01-01T00:00:00Z"
}
```

### Admin Orders

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `GET` | `/api/orders/` | Admin | List all orders |
| `POST` | `/api/orders/` | Admin | Create order |
| `GET` | `/api/orders/{id}/` | Admin | Get order |
| `PATCH` | `/api/orders/{id}/` | Admin | Update order (e.g. change status) |
| `DELETE` | `/api/orders/{id}/` | Admin | Delete order |

---

## Order Tracking Events

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `GET` | `/api/orders/tracking/` | Admin | List tracking events |
| `POST` | `/api/orders/tracking/` | Admin | Create tracking event |
| `GET` | `/api/orders/tracking/{id}/` | Admin | Get event |
| `PATCH` | `/api/orders/tracking/{id}/` | Admin | Update event |
| `DELETE` | `/api/orders/tracking/{id}/` | Admin | Delete event |

**Payload**
```json
{
  "order": 1,
  "status": "shipped",
  "location": "Lagos warehouse",
  "message": "Package has left the warehouse."
}
```

---

## Coupons

Admin only.

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `GET` | `/api/orders/coupons/` | Admin | List coupons |
| `POST` | `/api/orders/coupons/` | Admin | Create coupon |
| `GET` | `/api/orders/coupons/{id}/` | Admin | Get coupon |
| `PATCH` | `/api/orders/coupons/{id}/` | Admin | Update coupon |
| `DELETE` | `/api/orders/coupons/{id}/` | Admin | Delete coupon |

**Discount types:** `percent` | `fixed`

**Payload**
```json
{
  "code": "WELCOME10",
  "description": "10% off for new customers",
  "discount_type": "percent",
  "discount_value": "10.00",
  "is_active": true,
  "usage_limit": 100,
  "starts_at": "2026-01-01T00:00:00Z",
  "expires_at": "2026-12-31T23:59:59Z"
}
```

**Response includes** `used_count` (read-only — incremented automatically on checkout).

---

## Payments

Admin only. The `user` field is auto-set from the authenticated admin making the request.

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `GET` | `/api/payments/` | Admin | List payments |
| `POST` | `/api/payments/` | Admin | Create payment |
| `GET` | `/api/payments/{id}/` | Admin | Get payment |
| `PATCH` | `/api/payments/{id}/` | Admin | Update payment |
| `DELETE` | `/api/payments/{id}/` | Admin | Delete payment |

**Payment statuses:** `pending` | `authorized` | `paid` | `failed` | `refunded` | `cancelled`

**Payload**
```json
{
  "order": 1,
  "provider": "stripe",
  "provider_reference": "pi_3ABC123",
  "amount": "59.98",
  "currency": "USD",
  "status": "paid",
  "metadata": {}
}
```

**Response**
```json
{
  "id": 1,
  "user": 1,
  "order": 1,
  "provider": "stripe",
  "provider_reference": "pi_3ABC123",
  "amount": "59.98",
  "currency": "USD",
  "status": "paid",
  "metadata": {},
  "created_at": "2026-01-01T00:00:00Z",
  "updated_at": "2026-01-01T00:00:00Z"
}
```

> `order` links this payment directly to an Order — use `order.payments.all()` server-side or filter by order ID.

---

## CMS Sections

Public read, admin write. Detail uses `slug`.

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `GET` | `/api/cms/sections/` | Public | List sections |
| `POST` | `/api/cms/sections/` | Admin | Create section |
| `GET` | `/api/cms/sections/{slug}/` | Public | Get section |
| `PATCH` | `/api/cms/sections/{slug}/` | Admin | Update section |
| `DELETE` | `/api/cms/sections/{slug}/` | Admin | Delete section |

**Section types:** `hero` | `banner` | `featured_products` | `content` | `footer`

**Payload** (use `multipart/form-data` when uploading an image)
```json
{
  "title": "Summer Sale",
  "slug": "summer-sale-hero",
  "section_type": "hero",
  "body": "Up to 50% off all apparel.",
  "link_url": "/products?category=apparel",
  "sort_order": 1,
  "is_active": true,
  "starts_at": "2026-06-01T00:00:00Z",
  "ends_at": "2026-08-31T23:59:59Z"
}
```

**Response**
```json
{
  "id": 1,
  "title": "Summer Sale",
  "slug": "summer-sale-hero",
  "section_type": "hero",
  "body": "Up to 50% off all apparel.",
  "image": "http://127.0.0.1:8000/media/cms/hero.jpg",
  "link_url": "/products?category=apparel",
  "sort_order": 1,
  "is_active": true,
  "starts_at": "2026-06-01T00:00:00Z",
  "ends_at": "2026-08-31T23:59:59Z",
  "created_at": "2026-01-01T00:00:00Z",
  "updated_at": "2026-01-01T00:00:00Z"
}
```

**Typical frontend usage:**
- Filter `section_type=hero` → render as homepage hero banner
- Filter `section_type=featured_products` → render as curated product row
- Filter `section_type=banner` → render as promotional strip

---

## User Profiles

Super admin only.

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `GET` | `/api/auth/profiles/` | Super admin | List profiles |
| `POST` | `/api/auth/profiles/` | Super admin | Create profile |
| `GET` | `/api/auth/profiles/{id}/` | Super admin | Get profile |
| `PATCH` | `/api/auth/profiles/{id}/` | Super admin | Update profile |
| `DELETE` | `/api/auth/profiles/{id}/` | Super admin | Delete profile |

**Payload**
```json
{
  "user": 1,
  "role": "customer",
  "phone": "+2348000000000",
  "address": "12 Lagos Street",
  "company_name": "",
  "is_active": true
}
```

> A profile is automatically created when a new User is registered via Django signals — you only need this endpoint to update it.

---

## Analytics

Admin only. Single endpoint returning all dashboard data.

```
GET /api/analytics/summary/
```

**Response**
```json
{
  "totals": {
    "products": 24,
    "orders": 120,
    "customers": 95,
    "vendors": 4,
    "revenue": "8540.00"
  },
  "charts": {
    "orders_by_status": {
      "pending": 10,
      "paid": 55,
      "shipped": 30,
      "delivered": 20,
      "cancelled": 5
    },
    "payments_by_status": {
      "paid": 55,
      "failed": 3,
      "refunded": 2
    },
    "top_products": [
      {
        "product_name": "Classic T-Shirt",
        "quantity": 45,
        "revenue": "1349.55"
      }
    ],
    "orders_over_time": [
      {
        "date": "2026-06-01",
        "total": 8,
        "revenue": "479.92"
      }
    ]
  }
}
```

Revenue includes only `paid`, `processing`, `shipped`, and `delivered` orders.
`orders_over_time` returns the last 30 days.
`top_products` returns the top 10 by quantity sold.

---

## HTTP Status Codes

| Code | Meaning |
|------|---------|
| `200` | OK |
| `201` | Created |
| `204` | Deleted (no body) |
| `400` | Validation error or bad request |
| `401` | Missing or invalid token |
| `403` | Authenticated but not authorized |
| `404` | Resource not found |
| `429` | Rate limited — anon: 100/hr, authenticated: 1000/hr |

**Error body shape**
```json
{ "detail": "Authentication credentials were not provided." }
```
or field-level errors:
```json
{
  "rating": ["Ensure this value is less than or equal to 5."],
  "product": ["This field is required."]
}
```

---

## Quick-Start Flow (Customer)

```
1.  POST /api/auth/token/                    → get access token
2.  GET  /api/products/                      → browse products
3.  GET  /api/products/{slug}/               → view product detail
4.  GET  /api/orders/cart/active/            → get/create cart
5.  POST /api/orders/cart/items/             → add item to cart
6.  PATCH /api/orders/cart/{id}/             → apply coupon (optional)
7.  POST /api/orders/cart/{id}/checkout/     → place order
8.  GET  /api/orders/mine/                   → view order history
9.  POST /api/products/reviews/              → submit review
10. POST /api/products/wishlist/             → save to wishlist
```

---

## cURL Examples

**Get token**
```bash
curl -X POST http://127.0.0.1:8000/api/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{"username":"alice","password":"secret"}'
```

**List products with filters**
```bash
curl "http://127.0.0.1:8000/api/products/?category=apparel&in_stock=true&ordering=-price"
```

**Get active cart**
```bash
curl http://127.0.0.1:8000/api/orders/cart/active/ \
  -H "Authorization: Bearer <access_token>"
```

**Add item to cart**
```bash
curl -X POST http://127.0.0.1:8000/api/orders/cart/items/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{"product":1,"quantity":2}'
```

**Apply a coupon**
```bash
curl -X PATCH http://127.0.0.1:8000/api/orders/cart/1/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{"coupon":3}'
```

**Checkout**
```bash
curl -X POST http://127.0.0.1:8000/api/orders/cart/1/checkout/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{"shipping_address":"123 Main St","billing_address":"123 Main St","notes":""}'
```

**Upload product image**
```bash
curl -X POST http://127.0.0.1:8000/api/products/images/ \
  -H "Authorization: Bearer <access_token>" \
  -F "product=1" \
  -F "image=@/path/to/photo.jpg" \
  -F "alt_text=Front view" \
  -F "is_primary=true"
```

**Submit a review**
```bash
curl -X POST http://127.0.0.1:8000/api/products/reviews/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{"product":1,"rating":5,"title":"Great!","comment":"Love it."}'
```
