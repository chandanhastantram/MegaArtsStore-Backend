# Blender 3D/AR Pipeline Setup Guide

Complete guide for setting up Blender integration with MegaArtsStore for automated 3D model processing.

---

## 📋 Prerequisites

- Windows 10/11
- Python 3.10+
- MegaArtsStore backend running
- Admin access for Blender installation

---

## 🔧 Step 1: Install Blender

### Download Blender

1. Visit [https://www.blender.org/download/](https://www.blender.org/download/)
2. Download **Blender 3.6 LTS** (Long Term Support) or newer
3. Choose the **Windows Installer (.msi)**

### Install Blender

1. Run the installer
2. **Important**: Install to the default location:
   ```
   C:\Program Files\Blender Foundation\Blender 3.6\
   ```
3. Complete the installation wizard
4. Verify installation by opening Blender

### Locate Blender Executable

The Blender executable should be at:

```
C:\Program Files\Blender Foundation\Blender 3.6\blender.exe
```

---

## ⚙️ Step 2: Configure Environment Variables

### Update `.env` File

1. Open your `.env` file in the MegaArtsStore root directory
2. Update the Blender configuration:

```ini
# Blender Configuration
BLENDER_ENABLED=true
BLENDER_PATH=C:\Program Files\Blender Foundation\Blender 3.6\blender.exe
```

### Verify Configuration

Run this command to test:

```bash
"C:\Program Files\Blender Foundation\Blender 3.6\blender.exe" --version
```

You should see output like:

```
Blender 3.6.0
```

---

## 📦 Step 3: Install Python Dependencies

The backend already has the necessary dependencies, but verify:

```bash
pip install cloudinary aiofiles
```

---

## 🎨 Step 4: Prepare 3D Models for Upload

### Supported Formats

The pipeline accepts these 3D formats:

- `.obj` (Wavefront OBJ)
- `.fbx` (Autodesk FBX)
- `.gltf` / `.glb` (GL Transmission Format)
- `.blend` (Blender native)
- `.stl` (Stereolithography)

### Model Requirements

For best results, ensure your models:

- Are centered at origin (0, 0, 0)
- Have appropriate scale (bangles ~6-8cm diameter)
- Include UV maps for textures
- Have clean geometry (no overlapping faces)

---

## 🚀 Step 5: Upload and Process Models

### Using the API

#### 1. Upload a 3D Model

```bash
curl -X POST "http://localhost:8000/render/upload-model" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -F "product_id=YOUR_PRODUCT_ID" \
  -F "file=@path/to/your/model.obj"
```

**Response:**

```json
{
  "message": "Model uploaded successfully",
  "model_url": "https://res.cloudinary.com/...",
  "original_url": "https://res.cloudinary.com/..."
}
```

#### 2. Start Processing Job

```bash
curl -X POST "http://localhost:8000/render/process" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "product_id": "YOUR_PRODUCT_ID",
    "operations": ["optimize", "render_360", "generate_thumbnail"]
  }'
```

**Response:**

```json
{
  "job_id": "job-abc123",
  "status": "queued",
  "operations": ["optimize", "render_360", "generate_thumbnail"]
}
```

#### 3. Check Job Status

```bash
curl -X GET "http://localhost:8000/render/job/job-abc123" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

**Response:**

```json
{
  "job_id": "job-abc123",
  "status": "completed",
  "progress": 100,
  "results": {
    "optimized_model": "https://res.cloudinary.com/.../optimized.glb",
    "renders": [
      "https://res.cloudinary.com/.../render_0.png",
      "https://res.cloudinary.com/.../render_90.png"
    ],
    "thumbnail": "https://res.cloudinary.com/.../thumb.png"
  }
}
```

---

## 🔄 Step 6: Understanding the Processing Pipeline

### What Happens When You Process a Model?

1. **Upload**: Model is uploaded to Cloudinary
2. **Queue**: Processing job is added to task queue
3. **Blender Processing**:
   - Model is downloaded to temp directory
   - Blender script runs in headless mode
   - Operations are performed (optimize, render, etc.)
4. **Upload Results**: Processed files uploaded to Cloudinary
5. **Database Update**: Product record updated with new URLs

### Available Operations

| Operation            | Description                                   | Output                |
| -------------------- | --------------------------------------------- | --------------------- |
| `optimize`           | Reduce polygon count, apply Draco compression | `.glb` file           |
| `render_360`         | Generate 360° product images                  | Multiple `.png` files |
| `generate_thumbnail` | Create product thumbnail                      | Single `.png` file    |
| `extract_dimensions` | Calculate model dimensions                    | JSON metadata         |

---

## 🎯 Step 7: Blender Scripts Explained

The backend includes these Blender scripts in `app/services/blender_scripts/`:

### `optimize_model.py`

- Reduces polygon count using decimation
- Applies Draco compression for smaller file size
- Exports as `.glb` format for AR

### `render_360.py`

- Sets up camera and lighting
- Renders product from multiple angles (0°, 45°, 90°, etc.)
- Saves high-quality PNG images

### `generate_thumbnail.py`

- Renders a single hero shot
- Optimized for product listings

---

## 🧪 Step 8: Testing the Pipeline

### Test with Sample Model

1. **Create a test product**:

```bash
curl -X POST "http://localhost:8000/product/create" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Gold Bangle",
    "description": "Test product",
    "price": 50000,
    "category": "Bangles",
    "material": "Gold",
    "sizes": ["2-6"],
    "stock": 10
  }'
```

2. **Upload a test model** (use the product ID from step 1)

3. **Process the model** with all operations

4. **Check the results** in the product details

---

## 📊 Step 9: Monitoring and Troubleshooting

### Check Task Queue Status

```bash
curl -X GET "http://localhost:8000/tasks/stats" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

### Common Issues

#### Blender Not Found

**Error**: `Blender executable not found`

**Solution**:

- Verify `BLENDER_PATH` in `.env`
- Check Blender is installed correctly
- Ensure path has no typos

#### Processing Stuck

**Error**: Job status remains "processing"

**Solution**:

- Check server logs for Blender errors
- Verify model file is not corrupted
- Restart the backend server

#### Out of Memory

**Error**: Blender crashes during processing

**Solution**:

- Reduce model complexity before upload
- Increase system RAM
- Process models one at a time

---

## 🎨 Step 10: Best Practices

### Model Preparation

1. **Clean Geometry**: Remove duplicate vertices, fix normals
2. **Optimize Before Upload**: Pre-reduce polygon count if very high
3. **Proper Scale**: Ensure model is real-world scale
4. **Materials**: Use PBR materials for best AR results

### Batch Processing

For multiple models:

```python
import asyncio
from app.services import job_service

async def batch_process():
    product_ids = ["id1", "id2", "id3"]

    for pid in product_ids:
        job_id = await job_service.create_processing_job(
            product_id=pid,
            operations=["optimize", "render_360"]
        )
        print(f"Queued job {job_id} for product {pid}")

asyncio.run(batch_process())
```

### Performance Tips

- Process during off-peak hours
- Use `optimize` operation for all AR models
- Generate thumbnails for faster page loads
- Cache rendered images on CDN

---

## 🔐 Security Considerations

- Only admins can upload/process models
- Uploaded files are scanned for malicious content
- Temporary files are deleted after processing
- All operations are logged for audit

---

## 📚 Additional Resources

- [Blender Python API Docs](https://docs.blender.org/api/current/)
- [glTF 2.0 Specification](https://www.khronos.org/gltf/)
- [Cloudinary Upload API](https://cloudinary.com/documentation/upload_images)

---

## 🆘 Getting Help

If you encounter issues:

1. Check server logs: `uvicorn main:app --log-level debug`
2. Verify Blender works standalone: `blender --background --python test_script.py`
3. Review task queue status: `/tasks/stats`
4. Contact support with job ID and error logs
