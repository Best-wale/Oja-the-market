# OJA Backend

This is the backend for the OJA e-commerce project, built with Django and Django REST Framework.

---

## Features

- User authentication (JWT)
- Product, Category, and Featured product APIs
- Cart and CartItem support for both authenticated and guest users (session-based)
- Order and OrderItem models for checkout and purchase history
- Admin dashboard (Django admin)
- CORS support for frontend integration

---

## Requirements

- Python 3.8+
- Django 4.x+
- Django REST Framework
- django-cors-headers

Install requirements:
```bash
pip install -r requirements.txt
```

---

## Setup

1. **Clone the repository and navigate to the backend directory:**
   ```bash
   cd OJA/backend
   ```

2. **Set up environment variables (optional):**
   - Create a `.env` file for secrets if needed.

3. **Apply migrations:**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

4. **Create a superuser:**
   ```bash
   python manage.py createsuperuser
   ```

5. **Run the development server:**
   ```bash
   python manage.py runserver
   ```

---

## API Endpoints

- `/api/products/` — List and filter products (supports `?category=CategoryName`)
- `/api/categories/` — List categories
- `/api/cart-items/` — Add, update, or remove cart items
- `/api/cart-items/my-cart/` — Get current user's or session's cart items
- `/api/orders/` — Create and view orders (authenticated users)
- `/api/profile/` — Get current user profile (authenticated users)

---

## CORS Configuration

The backend is configured to work with a frontend running at `http://localhost:5173`.  
If you use a different frontend URL, update `CORS_ALLOWED_ORIGINS` in `settings.py`.

---

## Notes

- The SQLite database (`db.sqlite3`) and media files are excluded from version control.
- Use the Django admin at `/admin/` for management.
- Test HTTP requests can be made using the included `test.http` file (VS Code REST Client).

---

## License

This project is for educational purposes.
