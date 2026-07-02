# Oghie Store — API

A Django REST Framework backend powering a headless ecommerce storefront: product catalog, cart/checkout, orders, payments, and CMS-driven content sections — consumed by a separate Next.js frontend.

**API root:** https://oghie-store.vercel.app

---

## Stack

![Django](https://img.shields.io/badge/Django-092E20?style=flat&logo=django&logoColor=white)
![DRF](https://img.shields.io/badge/Django_REST_Framework-A30000?style=flat&logo=django&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?style=flat&logo=postgresql&logoColor=white)
![JWT](https://img.shields.io/badge/Auth-JWT-black?style=flat&logo=jsonwebtokens&logoColor=white)

## Endpoints

| Purpose | Method | Path |
|---|---|---|
| Admin | — | `/admin/` |
| Get JWT token | `POST` | `/api/auth/token/` |
| Refresh JWT token | `POST` | `/api/auth/token/refresh/` |
| Current user | `GET` | `/api/auth/me/` |
| Product list | `GET` | `/api/products/` |
| Product filters | `GET` | `/api/products/?search=&category=&currency=&min_price=&max_price=&in_stock=true&min_rating=&ordering=price` |
| Currencies | `GET` | `/api/products/currencies/` |
| Wishlist | `GET`/`POST` | `/api/products/wishlist/` |
| Reviews | `GET`/`POST` | `/api/products/reviews/` |
| Active cart | `GET` | `/api/orders/cart/active/` |
| Checkout | `POST` | `/api/orders/cart/{cart_id}/checkout/` |
| Orders | `GET` | `/api/orders/` |
| My orders | `GET` | `/api/orders/mine/` |
| Order tracking | `GET` | `/api/orders/tracking/` |
| Payments | `GET`/`POST` | `/api/payments/` |
| CMS sections | `GET` | `/api/cms/sections/` |

Full endpoint documentation: [docs/API.md](docs/API.md)

## Architecture

```mermaid
flowchart LR
    A["Next.js frontend"] -->|"JWT bearer token"| B["DRF API"]
    B --> C["PostgreSQL"]
    B --> D["Payments provider"]
    B --> E["CMS content sections"]
```

## Getting started

```bash
git clone https://github.com/oghenenoghie/oghie-store.git
cd oghie-store
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

The API root at `/` returns a compact list of the main endpoints.

### Environment variables

```bash
SECRET_KEY=
DJANGO_DEBUG=True
DATABASE_URL=postgres://user:password@localhost:5432/oghie_store
CLOUDINARY_URL=cloudinary://<api_key>:<api_secret>@<cloud_name>
```

`DJANGO_DEBUG` defaults to `False` if unset, so set it explicitly to `True` for local development.

`DATABASE_URL` falls back to a local sqlite file when unset, but only for local development — **on Vercel, `DATABASE_URL` is required.** The deployment filesystem is read-only outside `/tmp`, so without a real Postgres `DATABASE_URL` the app cannot write sessions, admin changes, orders, etc. Set it in the Vercel project's environment variables to your Postgres connection string.

## Testing

```bash
python manage.py test
```

CI runs migrations and the test suite against Postgres on every push/PR to `main` — see [.github/workflows/ci.yml](.github/workflows/ci.yml).

## What I'd do differently

- Add `drf-spectacular` for auto-generated OpenAPI docs rather than relying on the endpoint table above
- Add rate limiting on `/api/auth/token/` to guard against brute-force attempts
- Move cart/checkout logic into a dedicated service layer, separate from the viewsets, for easier testing

## License

MIT
