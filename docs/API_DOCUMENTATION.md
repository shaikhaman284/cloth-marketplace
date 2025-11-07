# API Documentation - Cloth Marketplace

Base URL: `http://127.0.0.1:8000` (Development)
Production: `https://api.awm27.shop`

---

## Authentication

### Register/Login
**POST** `/api/auth/register`

**Request Body:**
```json
{
    "phone_number": "+919876543210",
    "full_name": "John Doe",
    "user_type": "seller" | "customer"
}
```

**Response:**
```json
{
    "success": true,
    "message": "User registered successfully",
    "token": "abc123...",
    "user": {
        "id": 1,
        "phone_number": "+919876543210",
        "full_name": "John Doe",
        "user_type": "seller",
        "has_shop": false
    }
}
```

---

## Shops

### Register Shop (Seller Only)
**POST** `/api/shops/register`

**Headers:**
- `Authorization: Token {your_token}`

**Request Body:**
```json
{
    "shop_name": "Fashion Hub",
    "business_address": "MG Road, Rajkamal Chowk",
    "city": "Amravati",
    "pincode": "444601",
    "owner_contact_number": "+919876543210",
    "gst_number": "22AAAAA0000A1Z5" (optional)
}
```

**Note:** Only shops in Amravati city are accepted.

**Response:**
```json
{
    "success": true,
    "message": "Shop registered successfully. Waiting for approval.",
    "shop": { ... }
}
```

### Get My Shop
**GET** `/api/shops/me`

**Headers:**
- `Authorization: Token {your_token}`

### List Approved Shops (Public)
**GET** `/api/shops/approved?city=Amravati`

**Response:**
```json
{
    "success": true,
    "count": 5,
    "city": "Amravati",
    "shops": [ ... ]
}
```

---

## Categories

### List All Categories
**GET** `/api/categories`

**Response:**
```json
{
    "success": true,
    "categories": [
        {
            "id": 1,
            "name": "Men's Wear",
            "slug": "mens-wear",
            "subcategories": [
                {"id": 2, "name": "Shirts", ...},
                {"id": 3, "name": "T-Shirts", ...}
            ]
        }
    ]
}
```

---

## Products

### Create Product (Seller Only)
**POST** `/api/products/create`

**Headers:**
- `Authorization: Token {your_token}`

**Request Body:**
```json
{
    "category": 1,
    "name": "Blue Cotton Shirt",
    "description": "Comfortable cotton shirt",
    "base_price": "1000.00",  ← What you receive
    "stock_quantity": 50,
    "sizes": ["S", "M", "L", "XL"],
    "colors": ["Blue", "White"],
    "material": "Cotton",
    "brand": "Local Brand"
}
```

**Response:**
```json
{
    "success": true,
    "message": "Product created successfully",
    "product": {
        "id": 1,
        "base_price": "1000.00",      ← You receive
        "commission_rate": "15.00",
        "display_price": "1150.00",   ← Customer pays
        ...
    },
    "pricing_info": {
        "your_price": "₹1000",
        "commission": "15%",
        "customer_pays": "₹1150",
        "note": "You receive the base price. Commission is added to customer's price."
    }
}
```

### Upload Product Images
**POST** `/api/products/{product_id}/images`

**Headers:**
- `Authorization: Token {your_token}`
- `Content-Type: multipart/form-data`

**Request Body:** (form-data)
- `image1`: file
- `image2`: file
- ... (up to 5 images)

### List Products (Public)
**GET** `/api/products?category={id}&shop={id}&search={query}&min_price={price}&max_price={price}&sort={option}`

**Query Parameters:**
- `category`: Category ID
- `shop`: Shop ID
- `search`: Search in name/description
- `min_price`: Minimum display_price
- `max_price`: Maximum display_price
- `sizes`: Comma-separated (e.g., "S,M,L")
- `colors`: Comma-separated
- `sort`: `newest` | `price_low` | `price_high` | `popular`
- `page`: Page number (20 items per page)

**Response:**
```json
{
    "success": true,
    "count": 20,
    "next": "...",
    "previous": null,
    "products": [
        {
            "id": 1,
            "name": "Blue Cotton Shirt",
            "display_price": "1150.00",  ← Customer sees this
            "stock_quantity": 50,
            "shop_name": "Fashion Hub",
            "shop_city": "Amravati",
            "images": [ ... ]
        }
    ]
}
```

**Note:** Customers and anonymous users don't see `base_price` or `commission_rate`.

### Get Product Detail
**GET** `/api/products/{product_id}`

### Update Product (Seller Only)
**PUT** `/api/products/{product_id}/update`

**Headers:**
- `Authorization: Token {your_token}`

**Body:** Same as create (partial updates allowed)

### Delete Product (Seller Only)
**DELETE** `/api/products/{product_id}/delete`

---

## Pricing Model Explanation

### How Commission Works:

1. **Seller Sets Base Price:**
   - This is what the seller wants to receive (their offline price)
   - Example: ₹1000

2. **Platform Adds Commission:**
   - Default: 15%
   - Display Price = Base Price × (1 + Commission Rate / 100)
   - Example: ₹1000 × 1.15 = ₹1150

3. **Customer Pays Display Price:**
   - Customer sees and pays ₹1150

4. **Money Flow:**
   - Customer pays: ₹1150
   - Seller receives: ₹1000 (same as offline!)
   - Platform earns: ₹150 (commission)

**Benefits:**
- Seller gets same profit as offline sales
- Platform earns commission without affecting seller
- Customer gets convenience (pays 15% for home delivery)

---

## Service Area

**Currently Available:** Amravati city only

When registering a shop or placing an order, the city must be "Amravati".

**Coming Soon:** Expansion to nearby cities

---

## Error Codes

- `400`: Bad Request (validation error)
- `401`: Unauthorized (invalid/missing token)
- `403`: Forbidden (insufficient permissions)
- `404`: Not Found
- `500`: Server Error

---

## Rate Limiting

Development: No limits
Production: 100 requests per minute per IP

---