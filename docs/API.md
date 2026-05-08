# Oghie Store API Documentation

Base URL:

```text
http://127.0.0.1:8000
```

All API routes use JSON unless a file upload is involved. Authenticated requests should include a JWT access token:

```http
Authorization: Bearer <access_token>
```

## Authentication

| Method | Endpoint | Auth | Description |
| --- | --- | --- | --- |
| `POST` | `/api/auth/token/` | Public | Obtain access and refresh tokens. |
| `POST` | `/api/auth/token/refresh/` | Public | Refresh an access token. |
| `POST` | `/api/auth/token/verify/` | Public | Verify a token. |
| `GET` | `/api/auth/me/` | User | Return the current authenticated user. |

### Obtain Token

Request:

```json
{
  "username": "admin",
  "password": "password"
}
```

Response:

```json
{
  "refresh": "refresh.jwt.token",
  "access": "access.jwt.token"
}
```

### Current User Response

```json
{
  "id": 1,
  "username": "admin",
  "email": "admin@example.com",
  "is_staff": true,
  "is_superuser": true,
  "profile": {
    "id": 1,
    "user": 1,
    "username": "admin",
    "email": "admin@example.com",
    "role": "super_admin",
    "phone": "",
    "address": "",
    "company_name": "",
    "is_active": true,
    "created_at": "2026-05-08T00:00:00Z",
    "updated_at": "2026-05-08T00:00:00Z"
  }
}
```

User profile roles are `super_admin`, `staff`, `vendor`, and `customer`.

## Common Query Parameters

Most list endpoints are DRF viewsets and support:

| Parameter | Description |
| --- | --- |
| `search` | Searches the fields configured for that endpoint. |
| `ordering` | Sort by an allowed field. Prefix with `-` for descending order. |

Example:

```http
GET /api/products/?search=shirt&ordering=-price
```

## Permissions

| Resource | Read | Write |
| --- | --- | --- |
| Products, categories, currencies, images, CMS sections | Public | Admin user |
| Product reviews | Public approved reviews | Authenticated users create reviews |
| Wishlist, carts, cart items, checkout, current user's orders | Authenticated user | Authenticated user |
| User profiles | Super admin | Super admin |
| Orders, order items, coupons, tracking events, payments, analytics | Admin user | Admin user |

## Products

### Product Endpoints

Products use `slug` as the detail lookup value.

| Method | Endpoint | Auth | Description |
| --- | --- | --- | --- |
| `GET` | `/api/products/` | Public | List products. |
| `POST` | `/api/products/` | Admin | Create a product. |
| `GET` | `/api/products/{slug}/` | Public | Retrieve a product. |
| `PUT/PATCH` | `/api/products/{slug}/` | Admin | Update a product. |
| `DELETE` | `/api/products/{slug}/` | Admin | Delete a product. |

Product filters:

| Parameter | Description |
| --- | --- |
| `category` | Category slug. |
| `vendor` | Vendor user id. |
| `currency` | Currency code, case-insensitive. |
| `is_active` | `true` or `false`. |
| `in_stock` | `true` for products with stock, `false` for out of stock. |
| `min_price` | Minimum product price. |
| `max_price` | Maximum product price. |
| `min_rating` | Minimum approved review rating. |
| `search` | Product name, description, or category name. |
| `ordering` | `name`, `price`, `stock_quantity`, `created_at`, or `updated_at`. |

Create or update payload:

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

Product response includes `category_detail`, `currency_detail`, `images`, `average_rating`, and `review_count`.

### Categories

Categories use `slug` as the detail lookup value.

| Method | Endpoint | Auth | Description |
| --- | --- | --- | --- |
| `GET` | `/api/products/categories/` | Public | List categories. |
| `POST` | `/api/products/categories/` | Admin | Create a category. |
| `GET` | `/api/products/categories/{slug}/` | Public | Retrieve a category. |
| `PUT/PATCH` | `/api/products/categories/{slug}/` | Admin | Update a category. |
| `DELETE` | `/api/products/categories/{slug}/` | Admin | Delete a category. |

Payload:

```json
{
  "name": "Apparel",
  "slug": "apparel",
  "description": "Clothing and accessories.",
  "is_active": true
}
```

### Currencies

| Method | Endpoint | Auth | Description |
| --- | --- | --- | --- |
| `GET` | `/api/products/currencies/` | Public | List currencies. |
| `POST` | `/api/products/currencies/` | Admin | Create a currency. |
| `GET` | `/api/products/currencies/{id}/` | Public | Retrieve a currency. |
| `PUT/PATCH` | `/api/products/currencies/{id}/` | Admin | Update a currency. |
| `DELETE` | `/api/products/currencies/{id}/` | Admin | Delete a currency. |

Payload:

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

### Product Images

| Method | Endpoint | Auth | Description |
| --- | --- | --- | --- |
| `GET` | `/api/products/images/` | Public | List product images. |
| `POST` | `/api/products/images/` | Admin | Upload a product image. |
| `GET` | `/api/products/images/{id}/` | Public | Retrieve an image record. |
| `PUT/PATCH` | `/api/products/images/{id}/` | Admin | Update an image record. |
| `DELETE` | `/api/products/images/{id}/` | Admin | Delete an image record. |

Use `multipart/form-data` for uploads. Supported image extensions are `jpg`, `jpeg`, `png`, and `webp`.

Fields:

```text
product: product id
image: file
alt_text: optional text
is_primary: true or false
```

### Wishlist

Wishlist items are scoped to the authenticated user.

| Method | Endpoint | Auth | Description |
| --- | --- | --- | --- |
| `GET` | `/api/products/wishlist/` | User | List my wishlist items. |
| `POST` | `/api/products/wishlist/` | User | Add a product to my wishlist. |
| `GET` | `/api/products/wishlist/{id}/` | User | Retrieve one wishlist item. |
| `DELETE` | `/api/products/wishlist/{id}/` | User | Remove a wishlist item. |

Payload:

```json
{
  "product": 1
}
```

### Product Reviews

Only approved reviews are visible to non-staff users. Staff users can see all review statuses.

| Method | Endpoint | Auth | Description |
| --- | --- | --- | --- |
| `GET` | `/api/products/reviews/` | Public | List reviews. |
| `POST` | `/api/products/reviews/` | User | Create a review. |
| `GET` | `/api/products/reviews/{id}/` | Public | Retrieve a review. |
| `PUT/PATCH` | `/api/products/reviews/{id}/` | User | Update a review. |
| `DELETE` | `/api/products/reviews/{id}/` | User | Delete a review. |

Filters:

| Parameter | Description |
| --- | --- |
| `product` | Product slug. |
| `search` | Product name, title, comment, or username. |
| `ordering` | `rating` or `created_at`. |

Payload:

```json
{
  "product": 1,
  "rating": 5,
  "title": "Great quality",
  "comment": "The fabric feels excellent."
}
```

Review statuses are `pending`, `approved`, and `rejected`. New reviews are created as `pending`.

## Cart and Checkout

Cart routes are scoped to the authenticated user.

| Method | Endpoint | Auth | Description |
| --- | --- | --- | --- |
| `GET` | `/api/orders/cart/` | User | List active carts for the current user. |
| `POST` | `/api/orders/cart/` | User | Create an active cart. |
| `GET` | `/api/orders/cart/active/` | User | Get or create the current active cart. |
| `GET` | `/api/orders/cart/{id}/` | User | Retrieve a cart. |
| `PATCH` | `/api/orders/cart/{id}/` | User | Update cart fields such as coupon or currency. |
| `POST` | `/api/orders/cart/{id}/checkout/` | User | Convert a cart to an order. |

Cart payload:

```json
{
  "currency": 1,
  "coupon": 1
}
```

Checkout payload:

```json
{
  "shipping_address": "123 Market Street",
  "billing_address": "123 Market Street",
  "notes": "Leave at reception."
}
```

Checkout creates an order with status `pending`, creates order items from active cart items, writes an initial tracking event, and marks the cart inactive.

### Cart Items

| Method | Endpoint | Auth | Description |
| --- | --- | --- | --- |
| `GET` | `/api/orders/cart/items/` | User | List active cart items. |
| `POST` | `/api/orders/cart/items/` | User | Add an item to the active cart. |
| `GET` | `/api/orders/cart/items/{id}/` | User | Retrieve a cart item. |
| `PUT/PATCH` | `/api/orders/cart/items/{id}/` | User | Update quantity. |
| `DELETE` | `/api/orders/cart/items/{id}/` | User | Remove an item. |

Payload:

```json
{
  "product": 1,
  "quantity": 2
}
```

## Orders

Order statuses are `draft`, `pending`, `paid`, `processing`, `shipped`, `delivered`, and `cancelled`.

### My Orders

Read-only order history for the authenticated user.

| Method | Endpoint | Auth | Description |
| --- | --- | --- | --- |
| `GET` | `/api/orders/mine/` | User | List my orders. |
| `GET` | `/api/orders/mine/{id}/` | User | Retrieve one of my orders. |

### Admin Orders

| Method | Endpoint | Auth | Description |
| --- | --- | --- | --- |
| `GET` | `/api/orders/` | Admin | List all orders. |
| `POST` | `/api/orders/` | Admin | Create an order. |
| `GET` | `/api/orders/{id}/` | Admin | Retrieve an order. |
| `PUT/PATCH` | `/api/orders/{id}/` | Admin | Update an order. |
| `DELETE` | `/api/orders/{id}/` | Admin | Delete an order. |

Order payload:

```json
{
  "customer": 1,
  "order_number": "OGH-ABC123",
  "status": "pending",
  "coupon": 1,
  "currency": 1,
  "subtotal": "59.98",
  "discount_total": "0.00",
  "shipping_total": "0.00",
  "tax_total": "0.00",
  "grand_total": "59.98",
  "shipping_address": "123 Market Street",
  "billing_address": "123 Market Street",
  "notes": ""
}
```

Order responses include nested `items` and `tracking_events`.

### Order Items

| Method | Endpoint | Auth | Description |
| --- | --- | --- | --- |
| `GET` | `/api/orders/items/` | Admin | List order items. |
| `POST` | `/api/orders/items/` | Admin | Create an order item. |
| `GET` | `/api/orders/items/{id}/` | Admin | Retrieve an order item. |
| `PUT/PATCH` | `/api/orders/items/{id}/` | Admin | Update an order item. |
| `DELETE` | `/api/orders/items/{id}/` | Admin | Delete an order item. |

Payload:

```json
{
  "order": 1,
  "product": 1,
  "product_name": "Classic T-Shirt",
  "unit_price": "29.99",
  "quantity": 2,
  "line_total": "59.98"
}
```

### Tracking Events

| Method | Endpoint | Auth | Description |
| --- | --- | --- | --- |
| `GET` | `/api/orders/tracking/` | Admin | List tracking events. |
| `POST` | `/api/orders/tracking/` | Admin | Create a tracking event. |
| `GET` | `/api/orders/tracking/{id}/` | Admin | Retrieve a tracking event. |
| `PUT/PATCH` | `/api/orders/tracking/{id}/` | Admin | Update a tracking event. |
| `DELETE` | `/api/orders/tracking/{id}/` | Admin | Delete a tracking event. |

Payload:

```json
{
  "order": 1,
  "status": "shipped",
  "location": "Riyadh warehouse",
  "message": "Package left the warehouse."
}
```

### Coupons

Coupons are admin-only.

| Method | Endpoint | Auth | Description |
| --- | --- | --- | --- |
| `GET` | `/api/orders/coupons/` | Admin | List coupons. |
| `POST` | `/api/orders/coupons/` | Admin | Create a coupon. |
| `GET` | `/api/orders/coupons/{id}/` | Admin | Retrieve a coupon. |
| `PUT/PATCH` | `/api/orders/coupons/{id}/` | Admin | Update a coupon. |
| `DELETE` | `/api/orders/coupons/{id}/` | Admin | Delete a coupon. |

Discount types are `percent` and `fixed`.

Payload:

```json
{
  "code": "WELCOME10",
  "description": "10 percent off",
  "discount_type": "percent",
  "discount_value": "10.00",
  "is_active": true,
  "usage_limit": 100,
  "starts_at": "2026-05-08T00:00:00Z",
  "expires_at": "2026-06-08T00:00:00Z"
}
```

## Payments

Payments are admin-only. When a payment is created by an authenticated admin, the API stores that user on the payment automatically.

| Method | Endpoint | Auth | Description |
| --- | --- | --- | --- |
| `GET` | `/api/payments/` | Admin | List payments. |
| `POST` | `/api/payments/` | Admin | Create a payment. |
| `GET` | `/api/payments/{id}/` | Admin | Retrieve a payment. |
| `PUT/PATCH` | `/api/payments/{id}/` | Admin | Update a payment. |
| `DELETE` | `/api/payments/{id}/` | Admin | Delete a payment. |

Payment statuses are `pending`, `authorized`, `paid`, `failed`, `refunded`, and `cancelled`.

Payload:

```json
{
  "provider": "stripe",
  "provider_reference": "pi_123",
  "amount": "59.98",
  "currency": "USD",
  "status": "paid",
  "metadata": {
    "order_id": 1
  }
}
```

## CMS Sections

CMS sections use `slug` as the detail lookup value.

| Method | Endpoint | Auth | Description |
| --- | --- | --- | --- |
| `GET` | `/api/cms/sections/` | Public | List CMS sections. |
| `POST` | `/api/cms/sections/` | Admin | Create a CMS section. |
| `GET` | `/api/cms/sections/{slug}/` | Public | Retrieve a CMS section. |
| `PUT/PATCH` | `/api/cms/sections/{slug}/` | Admin | Update a CMS section. |
| `DELETE` | `/api/cms/sections/{slug}/` | Admin | Delete a CMS section. |

Section types are `hero`, `banner`, `featured_products`, `content`, and `footer`.

Use `multipart/form-data` when uploading `image`.

Payload:

```json
{
  "title": "Homepage Hero",
  "slug": "homepage-hero",
  "section_type": "hero",
  "body": "New arrivals are here.",
  "image": null,
  "link_url": "https://example.com/new-arrivals",
  "sort_order": 1,
  "is_active": true,
  "starts_at": null,
  "ends_at": null
}
```

## Users

### Profiles

User profiles are super-admin-only.

| Method | Endpoint | Auth | Description |
| --- | --- | --- | --- |
| `GET` | `/api/auth/profiles/` | Super admin | List profiles. |
| `POST` | `/api/auth/profiles/` | Super admin | Create a profile. |
| `GET` | `/api/auth/profiles/{id}/` | Super admin | Retrieve a profile. |
| `PUT/PATCH` | `/api/auth/profiles/{id}/` | Super admin | Update a profile. |
| `DELETE` | `/api/auth/profiles/{id}/` | Super admin | Delete a profile. |

Payload:

```json
{
  "user": 1,
  "role": "customer",
  "phone": "+966500000000",
  "address": "Riyadh, Saudi Arabia",
  "company_name": "",
  "is_active": true
}
```

## Analytics

Analytics is admin-only.

| Method | Endpoint | Auth | Description |
| --- | --- | --- | --- |
| `GET` | `/api/analytics/summary/` | Admin | Return store totals and chart data. |

Response shape:

```json
{
  "totals": {
    "products": 12,
    "orders": 20,
    "customers": 18,
    "vendors": 2,
    "revenue": "950.00"
  },
  "charts": {
    "orders_by_status": {
      "pending": 3,
      "paid": 10
    },
    "payments_by_status": {
      "paid": 10,
      "failed": 1
    },
    "top_products": [
      {
        "product_name": "Classic T-Shirt",
        "quantity": 12,
        "revenue": "359.88"
      }
    ],
    "orders_over_time": [
      {
        "date": "2026-05-08",
        "total": 4,
        "revenue": "239.92"
      }
    ]
  }
}
```

## Status Codes

| Code | Meaning |
| --- | --- |
| `200` | Request succeeded. |
| `201` | Resource created. |
| `204` | Resource deleted. |
| `400` | Validation error or invalid request. |
| `401` | Authentication is missing or invalid. |
| `403` | Authenticated user does not have permission. |
| `404` | Resource was not found. |
| `429` | Request was throttled. Anonymous users are limited to `100/hour`; authenticated users are limited to `1000/hour`. |

## cURL Examples

Obtain a token:

```bash
curl -X POST http://127.0.0.1:8000/api/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"password"}'
```

List products:

```bash
curl http://127.0.0.1:8000/api/products/
```

Create a cart item:

```bash
curl -X POST http://127.0.0.1:8000/api/orders/cart/items/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{"product":1,"quantity":2}'
```

Checkout:

```bash
curl -X POST http://127.0.0.1:8000/api/orders/cart/1/checkout/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{"shipping_address":"123 Market Street","billing_address":"123 Market Street","notes":""}'
```
