# 🎨 MegaArtsStore Backend

A production-grade FastAPI backend for an AR-enabled jewelry e-commerce platform with advanced 3D rendering capabilities using Blender.

## ✨ Features

### 🛍️ E-Commerce Core

- **Product Management**: Complete CRUD operations with image optimization
- **Shopping Cart & Wishlist**: Real-time cart management with session handling
- **Order Processing**: Full order lifecycle management with status tracking
- **Payment Integration**: Razorpay payment gateway integration
- **Reviews & Ratings**: Product review system with moderation

### 🔮 AR & 3D Capabilities

- **3D Model Processing**: Automated Blender-based rendering pipeline
- **AR Analytics**: Track AR session metrics and user engagement
- **Model Validation**: Automated quality checks for 3D assets
- **Texture Optimization**: Automatic texture compression and optimization
- **GLB Export**: Optimized model export for web AR

### 🔐 Security & Performance

- **JWT Authentication**: Secure token-based authentication
- **Role-Based Access Control (RBAC)**: Admin, user, and guest roles
- **Rate Limiting**: Configurable request throttling
- **Request Validation**: Comprehensive input validation
- **Caching**: Redis-based caching for improved performance

### 📊 Admin Features

- **Analytics Dashboard**: Sales, revenue, and user metrics
- **Bulk Operations**: Batch product updates and imports
- **Email Notifications**: Order confirmations and updates
- **Task Queue**: Background job processing
- **Advanced Search**: Elasticsearch-powered product search

## 🚀 Tech Stack

- **Framework**: FastAPI 0.115.12
- **Database**: MongoDB Atlas
- **Authentication**: JWT (PyJWT)
- **Payment**: Razorpay
- **Storage**: Cloudinary (images & 3D models)
- **Email**: SMTP (Gmail)
- **3D Processing**: Blender 3.6+ (Python API)
- **Caching**: Redis (optional)
- **Task Queue**: Background task processing

## 📋 Prerequisites

- Python 3.8+
- MongoDB Atlas account
- Cloudinary account
- Razorpay account (for payments)
- Blender 3.6+ (optional, for 3D rendering)

## 🛠️ Installation

### 1. Clone the Repository

```bash
git clone https://github.com/chandanhastantram/MegaArtsStore-Backend.git
cd MegaArtsStore-Backend
```

### 2. Create Virtual Environment

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux/Mac
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
# Core dependencies
pip install -r requirements.txt

# For 3D rendering (optional)
pip install -r requirements-rendering.txt
```

### 4. Environment Configuration

Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
```

Edit `.env` with your credentials:

```env
# MongoDB
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/
DATABASE_NAME=megaartsstore

# JWT
JWT_SECRET_KEY=your-secret-key-here

# Cloudinary
CLOUDINARY_CLOUD_NAME=your-cloud-name
CLOUDINARY_API_KEY=your-api-key
CLOUDINARY_API_SECRET=your-api-secret

# Razorpay
RAZORPAY_KEY_ID=rzp_test_xxxxxxxxxxxx
RAZORPAY_KEY_SECRET=your-razorpay-secret

# Email
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

### 5. Run the Server

```bash
# Development
uvicorn main:app --reload

# Production
uvicorn main:app --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

## 📚 API Documentation

Once the server is running, access:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Postman Collection**: See `docs/MegaArtsStore.postman_collection.json`

## 🗂️ Project Structure

```
MegaArtsStore-Backend/
├── app/
│   ├── models/          # MongoDB models
│   ├── routes/          # API endpoints
│   ├── schemas/         # Pydantic schemas
│   ├── services/        # Business logic
│   ├── middleware/      # Custom middleware
│   └── utils/           # Helper functions
├── blender_scripts/     # 3D processing scripts
├── docs/                # Documentation
├── tests/               # Unit tests
├── main.py              # Application entry point
└── requirements.txt     # Dependencies
```

## 🧪 Testing

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_auth.py

# Run with coverage
pytest --cov=app tests/
```

## 📖 Documentation

- [Local Setup Guide](docs/LOCAL_SETUP.md)
- [Deployment Guide](docs/DEPLOYMENT_GUIDE.md)
- [Blender Setup](docs/BLENDER_SETUP_GUIDE.md)
- [Python Rendering](docs/PYTHON_RENDERING.md)
- [Quick Start 3D](docs/QUICK_START_3D.md)
- [API Documentation](docs/API_DOCUMENTATION.md)

## 🔧 Configuration

### Blender Setup (Optional)

For 3D rendering capabilities:

1. Install Blender 3.6+
2. Set `BLENDER_ENABLED=true` in `.env`
3. Configure `BLENDER_PATH` to your Blender executable
4. See [BLENDER_SETUP_GUIDE.md](docs/BLENDER_SETUP_GUIDE.md)

### Rate Limiting

Configure in `.env`:

```env
RATE_LIMIT_PER_MINUTE=100
RATE_LIMIT_PER_HOUR=2000
```

## 🌐 API Endpoints

### Authentication

- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `GET /api/auth/me` - Get current user

### Products

- `GET /api/products` - List products
- `GET /api/products/{id}` - Get product details
- `POST /api/products` - Create product (Admin)
- `PUT /api/products/{id}` - Update product (Admin)
- `DELETE /api/products/{id}` - Delete product (Admin)

### Cart & Wishlist

- `GET /api/cart` - Get cart items
- `POST /api/cart` - Add to cart
- `DELETE /api/cart/{id}` - Remove from cart
- `GET /api/wishlist` - Get wishlist
- `POST /api/wishlist` - Add to wishlist

### Orders

- `POST /api/orders` - Create order
- `GET /api/orders` - List user orders
- `GET /api/orders/{id}` - Get order details
- `PUT /api/orders/{id}/status` - Update order status (Admin)

### Payments

- `POST /api/payment/create-order` - Create Razorpay order
- `POST /api/payment/verify` - Verify payment

### 3D Rendering

- `POST /api/render/submit` - Submit render job
- `GET /api/render/status/{job_id}` - Check render status
- `GET /api/render/result/{job_id}` - Get rendered output

## 🚀 Deployment

See [DEPLOYMENT_GUIDE.md](docs/DEPLOYMENT_GUIDE.md) for detailed deployment instructions.

### Quick Deploy Options

- **Railway**: One-click deploy
- **Render**: Free tier available
- **AWS EC2**: Full control
- **Heroku**: Easy setup

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License.

## 👨‍💻 Author

**Chandan Hastantram**

- GitHub: [@chandanhastantram](https://github.com/chandanhastantram)

## 🙏 Acknowledgments

- FastAPI for the excellent framework
- Blender for 3D processing capabilities
- MongoDB for flexible data storage
- Cloudinary for asset management

## 📧 Support

For support, email your-email@example.com or open an issue on GitHub.

---

**Note**: This is the backend repository. For the frontend, see [MegaArtsStore-Frontend](https://github.com/chandanhastantram/MegaArtsStore-Frontend)
