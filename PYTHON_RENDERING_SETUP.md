# Quick Setup: Python Rendering (No Blender!)

## Install Dependencies

```bash
python -m pip install pyvista trimesh pillow numpy
```

## Update `.env`

```ini
# Disable Blender, use Python renderer
BLENDER_ENABLED=false
```

## That's It!

The backend will automatically use Python rendering when:

- `BLENDER_ENABLED=false` OR
- Blender is not installed

## Test It

```bash
# Start server
uvicorn main:app --reload

# Upload a model via API
# POST /render/upload-model

# Process it
# POST /render/process

# Check status
# GET /render/job/{job_id}
```

The Python renderer will:

- ✅ Optimize models (reduce polygons)
- ✅ Generate 360° renders
- ✅ Create thumbnails
- ✅ Extract dimensions
- ✅ Generate AR config

**No Blender needed!** 🎉
