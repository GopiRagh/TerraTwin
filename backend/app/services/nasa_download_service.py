
from pathlib import Path
from urllib.parse import urlparse, unquote
import re

import httpx


# Cache folder inside the backend directory
CACHE_DIR = (
    Path(__file__).resolve().parents[2]
    / "data"
    / "nasa_cache"
)

# Initially allow the trusted host used by our MOLA dataset
ALLOWED_HOSTS = {
    "pds-geosciences.wustl.edu",
    "pds.nasa.gov",
    "pds.lroc.im-ldi.com",
    "pds.mcp.nasa.gov",
    "static.mars.asu.edu",
    "hirise.lpl.arizona.edu",
}

# Maximum download size: 500 MB
MAX_DOWNLOAD_SIZE = 500 * 1024 * 1024


def download_nasa_file(
    download_url: str,
    filename: str = None
):
    """
    Download a NASA planetary data file and cache it locally.

    Existing files are reused instead of downloaded again.
    """

    parsed_url = urlparse(download_url)

    # Validate URL
    if parsed_url.scheme != "https":
        raise ValueError("Only HTTPS download URLs are allowed")

    if parsed_url.hostname not in ALLOWED_HOSTS:
        raise ValueError("Untrusted NASA data download host")

    # Get filename from URL if not supplied
    if not filename:
        filename = unquote(
            Path(parsed_url.path).name
        )

    # Prevent unsafe filenames
    filename = Path(filename).name
    filename = re.sub(r"[^A-Za-z0-9._-]", "_", filename)

    if not filename:
        raise ValueError("Invalid download filename")

    # Create cache directory
    CACHE_DIR.mkdir(parents=True, exist_ok=True)

    file_path = CACHE_DIR / filename
    temp_path = CACHE_DIR / f"{filename}.part"

    # Reuse existing downloaded file
    if file_path.exists():
        return {
            "status": "success",
            "message": "File already exists in cache",
            "filename": filename,
            "local_path": str(file_path),
            "size_bytes": file_path.stat().st_size,
            "cached": True
        }

    downloaded_size = 0

    try:
        with httpx.stream(
            "GET",
            download_url,
            follow_redirects=True,
            timeout=120.0
        ) as response:

            response.raise_for_status()

            # Validate redirect destination
            final_host = urlparse(str(response.url)).hostname

            if final_host not in ALLOWED_HOSTS:
                raise ValueError(
                    "Download redirected to an untrusted host"
                )

            content_length = response.headers.get(
                "content-length"
            )

            if content_length:
                if int(content_length) > MAX_DOWNLOAD_SIZE:
                    raise ValueError(
                        "NASA file exceeds the 500 MB download limit"
                    )

            with open(temp_path, "wb") as output_file:

                for chunk in response.iter_bytes(
                    chunk_size=1024 * 1024
                ):

                    downloaded_size += len(chunk)

                    if downloaded_size > MAX_DOWNLOAD_SIZE:
                        raise ValueError(
                            "Download exceeded the 500 MB limit"
                        )

                    output_file.write(chunk)

        # Rename only after successful download
        temp_path.replace(file_path)

        return {
            "status": "success",
            "message": "NASA file downloaded successfully",
            "filename": filename,
            "local_path": str(file_path),
            "size_bytes": downloaded_size,
            "cached": False
        }

    except Exception:
        # Remove incomplete download
        if temp_path.exists():
            temp_path.unlink()

        raise
