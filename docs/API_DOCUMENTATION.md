# MegaArtsStore API Documentation

## Base URL

```
http://localhost:8000
```

## Authentication

All protected endpoints require a Bearer token in the Authorization header:

```
Authorization: Bearer <your_jwt_token>
```

---

## Endpoints Overview

### 🔐 Authentication

| Method | Endpoint                      | Auth   | Description              |
| ------ | ----------------------------- | ------ | ------------------------ |
| POST   | `/auth/register`              | Public | Register new user        |
| POST   | `/auth/login`                 | Public | Login (returns JWT)      |
| GET    | `/auth/me`                    | User   | Get current user profile |
| POST   | `/auth/admin/create-subadmin` | Admin  | Create sub-admin         |
| GET    | `/auth/admin/users`           | Admin  | List all users           |

### 🛍️ Products

| Method | Endpoint              | Auth   | Description               |
| ------ | --------------------- | ------ | ------------------------- |
| GET    | `/product/list`       | Public | List products (paginated) |
| GET    | `/product/{id}`       | Public | Get product details       |
| POST   | `/product/create`     | Admin  | Create product            |
| PUT    | `/product/{id}`       | Admin  | Update product            |
| DELETE | `/product/{id}`       | Admin  | Delete product            |
| GET    | `/product/categories` | Public | List categories           |

### 🔍 Search

| Method | Endpoint                 | Auth   | Description        |
| ------ | ------------------------ | ------ | ------------------ |
| GET    | `/search/products?q=`    | Public | Full-text search   |
| GET    | `/search/suggestions?q=` | Public | Autocomplete       |
| GET    | `/search/filters`        | Public | Get filter options |
| GET    | `/search/trending`       | Public | Trending searches  |

### 🛒 Cart

| Method | Endpoint                           | Auth | Description     |
| ------ | ---------------------------------- | ---- | --------------- |
| GET    | `/cart/`                           | User | Get cart        |
| POST   | `/cart/add`                        | User | Add item        |
| PUT    | `/cart/update/{product_id}/{size}` | User | Update quantity |
| DELETE | `/cart/remove/{product_id}/{size}` | User | Remove item     |
| DELETE | `/cart/clear`                      | User | Clear cart      |
| GET    | `/cart/count`                      | User | Get item count  |

### ❤️ Wishlist

| Method | Endpoint                        | Auth | Description          |
| ------ | ------------------------------- | ---- | -------------------- |
| GET    | `/wishlist/`                    | User | Get wishlist         |
| POST   | `/wishlist/add/{product_id}`    | User | Add to wishlist      |
| DELETE | `/wishlist/remove/{product_id}` | User | Remove from wishlist |
| DELETE | `/wishlist/clear`               | User | Clear wishlist       |
| GET    | `/wishlist/check/{product_id}`  | User | Check if in wishlist |

### 📦 Orders

| Method | Endpoint                         | Auth  | Description       |
| ------ | -------------------------------- | ----- | ----------------- |
| POST   | `/order/create`                  | User  | Create order      |
| GET    | `/order/history`                 | User  | Order history     |
| GET    | `/order/{order_id}`              | User  | Get order details |
| PUT    | `/order/admin/{order_id}/status` | Admin | Update status     |
| GET    | `/order/admin/all`               | Admin | List all orders   |

### 💳 Payments

| Method | Endpoint                     | Auth   | Description           |
| ------ | ---------------------------- | ------ | --------------------- |
| POST   | `/payment/create`            | User   | Create Razorpay order |
| POST   | `/payment/verify`            | User   | Verify payment        |
| POST   | `/payment/webhook`           | Public | Razorpay webhook      |
| POST   | `/payment/refund`            | Admin  | Process refund        |
| GET    | `/payment/status/{order_id}` | User   | Payment status        |

### 🔮 AR Analytics

| Method | Endpoint                  | Auth   | Description             |
| ------ | ------------------------- | ------ | ----------------------- |
| POST   | `/ar/try-on/log`          | User   | Log try-on event        |
| POST   | `/ar/try-on/anonymous`    | Public | Anonymous try-on        |
| POST   | `/ar/try-on/conversion`   | Public | Update conversion       |
| POST   | `/ar/wrist-measurement`   | User   | Save wrist measurement  |
| POST   | `/ar/size-recommendation` | User   | Get size recommendation |
| GET    | `/ar/size-chart`          | Public | Bangle size chart       |
| GET    | `/ar/preload/featured`    | Public | Preload featured models |
| POST   | `/ar/preload/batch`       | Public | Batch preload models    |
| GET    | `/ar/stats/{product_id}`  | Admin  | Product AR stats        |
| GET    | `/ar/dashboard`           | Admin  | AR analytics dashboard  |

### ⭐ Reviews

| Method | Endpoint                                | Auth   | Description         |
| ------ | --------------------------------------- | ------ | ------------------- |
| GET    | `/reviews/{product_id}`                 | Public | List reviews        |
| POST   | `/reviews/{product_id}`                 | User   | Add review          |
| PUT    | `/reviews/{product_id}`                 | User   | Update own review   |
| DELETE | `/reviews/{product_id}`                 | User   | Delete own review   |
| DELETE | `/reviews/admin/{product_id}/{user_id}` | Admin  | Admin delete review |

### 📊 Admin Dashboard

| Method | Endpoint                        | Auth  | Description            |
| ------ | ------------------------------- | ----- | ---------------------- |
| GET    | `/admin/overview`               | Admin | Dashboard overview     |
| GET    | `/admin/sales-report?days=30`   | Admin | Sales report           |
| GET    | `/admin/top-products?limit=10`  | Admin | Top selling products   |
| GET    | `/admin/inventory-alerts`       | Admin | Low stock alerts       |
| GET    | `/admin/user-stats?days=30`     | Admin | User statistics        |
| GET    | `/admin/ar-analytics?days=30`   | Admin | AR usage analytics     |
| GET    | `/admin/order-status-breakdown` | Admin | Order status breakdown |

### 🎨 3D Rendering

| Method | Endpoint                         | Auth   | Description          |
| ------ | -------------------------------- | ------ | -------------------- |
| POST   | `/render/upload-model`           | Admin  | Upload 3D model      |
| POST   | `/render/process`                | Admin  | Start processing job |
| GET    | `/render/job/{job_id}`           | Admin  | Get job status       |
| GET    | `/render/ar-config/{product_id}` | Public | Get AR config        |

---

## Rate Limits

- **General**: 100 requests/minute, 2000 requests/hour
- **Authentication**: 10 requests/minute (stricter)

## Response Codes

| Code | Description  |
| ---- | ------------ |
| 200  | Success      |
| 201  | Created      |
| 400  | Bad Request  |
| 401  | Unauthorized |
| 403  | Forbidden    |
| 404  | Not Found    |
| 429  | Rate Limited |
| 500  | Server Error |
