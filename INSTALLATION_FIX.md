# Python 3D Rendering - Installation Fix

## Issue

You're using Python 3.14 (experimental), which doesn't have pre-compiled packages for numpy/pyvista.

## Solution: Skip Python Rendering for Now

Since the installation is problematic, here are your options:

### Option 1: Use Blender (You Already Have It!)

Update `.env`:

```ini
BLENDER_ENABLED=true
BLENDER_PATH=C:\Program Files\Blender Foundation\Blender 5.0\blender.exe
```

**Pros**: Works immediately, professional quality
**Cons**: Larger installation

### Option 2: Deploy Without 3D Processing

Update `.env`:

```ini
BLENDER_ENABLED=false
```

**Workflow**:

1. Process models locally with Blender 5.0.1
2. Upload optimized `.glb` files directly
3. Skip automated processing

**Pros**: Simplest, works everywhere
**Cons**: Manual processing

### Option 3: Install Python 3.11 (Recommended for Python Rendering)

Download Python 3.11 from [python.org](https://www.python.org/downloads/release/python-31110/)

Then:

```bash
py -3.11 -m pip install pyvista trimesh pillow numpy
```

**Pros**: Python rendering works
**Cons**: Extra Python installation

---

## My Recommendation

**For Now**: Use **Option 1** (Blender)

- You already have Blender 5.0.1 installed
- Just update `.env` with the correct path
- Everything will work immediately

**For Production**: Use **Option 2** (No processing)

- Deploy to Railway/Render without Blender
- Process models locally before upload
- Simplest deployment

---

## Quick Test with Blender

1. Find your Blender path:

```powershell
Get-ChildItem "C:\Program Files\Blender Foundation" -Recurse -Filter "blender.exe"
```

2. Update `.env`:

```ini
BLENDER_ENABLED=true
BLENDER_PATH=C:\Program Files\Blender Foundation\Blender 5.0\blender.exe
```

3. Restart server:

```bash
uvicorn main:app --reload
```

That's it! The 3D processing will work with Blender.
