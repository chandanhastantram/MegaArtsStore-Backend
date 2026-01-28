# Quick Start: 3D/AR Pipeline

Get your 3D models ready for AR in 5 minutes.

---

## ⚡ Quick Setup (5 minutes)

### 1. Install Blender

```bash
# Download from https://www.blender.org/download/
# Install to: C:\Program Files\Blender Foundation\Blender 3.6\
```

### 2. Update `.env`

```ini
BLENDER_ENABLED=true
BLENDER_PATH=C:\Program Files\Blender Foundation\Blender 3.6\blender.exe
```

### 3. Restart Server

```bash
uvicorn main:app --reload
```

---

## 🚀 Upload Your First Model

### Using Postman/API Client

**1. Upload Model**

```
POST /render/upload-model
Authorization: Bearer YOUR_TOKEN
Content-Type: multipart/form-data

product_id: YOUR_PRODUCT_ID
file: your_model.obj
```

**2. Process Model**

```
POST /render/process
Authorization: Bearer YOUR_TOKEN
Content-Type: application/json

{
  "product_id": "YOUR_PRODUCT_ID",
  "operations": ["optimize", "render_360"]
}
```

**3. Check Status**

```
GET /render/job/{job_id}
Authorization: Bearer YOUR_TOKEN
```

---

## 📱 Enable AR for Product

After processing, update product:

```
PUT /product/{product_id}
Authorization: Bearer YOUR_TOKEN

{
  "ar_enabled": true
}
```

---

## ✅ Verify AR Works

Get AR config:

```
GET /render/ar-config/{product_id}
```

Should return:

```json
{
  "model_url": "https://res.cloudinary.com/.../model.glb",
  "ar_enabled": true,
  "scale": 1.0,
  "rotation": [0, 0, 0]
}
```

---

## 🎯 That's It!

Your product is now AR-ready. Users can:

- View 3D model in browser
- Try on using AR on mobile devices
- See 360° product images

For detailed setup, see [BLENDER_SETUP_GUIDE.md](./BLENDER_SETUP_GUIDE.md)
