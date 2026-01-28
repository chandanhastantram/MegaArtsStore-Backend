# Local Setup - Blender 5.0.1

Update your `.env` file:

```ini
# Blender Configuration
BLENDER_ENABLED=true
BLENDER_PATH=C:\Program Files\Blender Foundation\Blender 5.0\blender.exe
```

**Find your exact path**:

```powershell
Get-Command blender | Select-Object -ExpandProperty Source
```

Or check:

- `C:\Program Files\Blender Foundation\Blender 5.0\blender.exe`
- `C:\Program Files\Blender Foundation\Blender\blender.exe`
- `C:\Users\YourName\AppData\Local\Programs\Blender Foundation\Blender 5.0\blender.exe`

Then restart your server:

```bash
uvicorn main:app --reload
```

---

# Production Deployment

## ⭐ Recommended: Deploy WITHOUT Blender

**Why?**

- Cheaper hosting ($5/month vs $15+/month)
- Faster deployment
- Better scalability
- No complex setup

**How?**

1. Process models locally on your Windows PC
2. Upload optimized `.glb` files directly
3. Set `BLENDER_ENABLED=false` in production

**Deploy to**:

- **Railway** (easiest, free tier)
- **Render** (free tier, auto-deploy)
- **Vercel** (if using Next.js frontend)

See [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md) for full details.
