import os
import cloudinary
import cloudinary.uploader
import cloudinary.api
from cloudinary.utils import cloudinary_url

# Patch ssl to trust the proxy's CA so Cloudinary's custom HTTP pool works
import ssl
_orig_ctx = ssl.create_default_context
def _patched_ctx(*args, **kwargs):
    kwargs.setdefault("cafile", "/root/.ccr/ca-bundle.crt")
    return _orig_ctx(*args, **kwargs)
ssl.create_default_context = _patched_ctx

# Configure Cloudinary from CLOUDINARY_URL (or CLOUDINARY_CLOUD_NAME/API_KEY/API_SECRET) env vars
cloudinary.config(secure=True)
if not cloudinary.config().cloud_name:
    raise SystemExit(
        "Cloudinary is not configured. Set the CLOUDINARY_URL environment variable "
        "(cloudinary://<api_key>:<api_secret>@<cloud_name>) before running this script."
    )

# 1. Upload a sample image
print("Uploading image...")
upload_result = cloudinary.uploader.upload(
    "https://res.cloudinary.com/demo/image/upload/getting-started/shoes.jpg",
    public_id="shoes_onboarding",
)
print(f"Secure URL:  {upload_result['secure_url']}")
print(f"Public ID:   {upload_result['public_id']}")

# 2. Fetch and print image metadata
print("\nFetching image details...")
details = cloudinary.api.resource("shoes_onboarding")
print(f"Width:       {details['width']}px")
print(f"Height:      {details['height']}px")
print(f"Format:      {details['format']}")
print(f"File size:   {details['bytes']} bytes")

# 3. Generate a transformed URL
# f_auto — lets Cloudinary pick the best format for the visitor's browser (e.g. WebP, AVIF)
# q_auto — automatically selects the best quality level to reduce file size without visible loss
optimized_url, _ = cloudinary_url(
    "shoes_onboarding",
    fetch_format="auto",  # f_auto
    quality="auto",       # q_auto
)

print("\nDone! Click link below to see optimized version of the image. Check the size and the format.")
print(f"Transformed URL: {optimized_url}")
