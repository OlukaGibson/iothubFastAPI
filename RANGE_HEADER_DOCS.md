# HTTP Range Header Implementation for Firmware Downloads

## Overview

The firmware download endpoints now support HTTP Range headers, enabling:
- Partial content downloads
- Resume interrupted downloads  
- Bandwidth-efficient transfers
- Streaming large firmware files

## Supported Endpoints

### GET `/firmware/{firmware_id}/download/{file_type}`
Downloads firmware files with optional Range header support.

### HEAD `/firmware/{firmware_id}/download/{file_type}`
Gets file metadata without downloading content (useful for getting file size).

## Range Header Formats

### 1. Specific Byte Range
```
Range: bytes=0-1023
```
Downloads bytes 0 through 1023 (first 1024 bytes).

### 2. From Start Byte to End
```
Range: bytes=1000-
```
Downloads from byte 1000 to the end of the file.

### 3. Last N Bytes (Suffix Range)
```
Range: bytes=-512
```
Downloads the last 512 bytes of the file.

## HTTP Status Codes

- **200 OK**: Full file download (no Range header)
- **206 Partial Content**: Successful range request
- **416 Range Not Satisfiable**: Invalid range (e.g., start > file size)

## Response Headers

### For Full Downloads (200)
```
Content-Length: 1048576
Accept-Ranges: bytes
Content-Disposition: attachment; filename="firmware_v1.2.bin"
Content-Type: application/octet-stream
```

### For Partial Downloads (206)
```
Content-Length: 1024
Content-Range: bytes 0-1023/1048576
Accept-Ranges: bytes
Content-Disposition: attachment; filename="firmware_v1.2.bin"
Content-Type: application/octet-stream
```

### For Invalid Ranges (416)
```
Content-Range: bytes */1048576
Accept-Ranges: bytes
```

## Usage Examples

### Example 1: Resume Download
```python
import requests

# First, get file size
response = requests.head("http://localhost:8000/firmware/{id}/download/bin")
file_size = int(response.headers['Content-Length'])

# Download first chunk
headers = {"Range": "bytes=0-1023"}
response = requests.get(url, headers=headers)
first_chunk = response.content

# Resume from where we left off
headers = {"Range": "bytes=1024-"}
response = requests.get(url, headers=headers)
remaining_chunk = response.content

# Combine chunks
complete_file = first_chunk + remaining_chunk
```

### Example 2: Download Last Part of File
```python
# Download last 1KB of firmware
headers = {"Range": "bytes=-1024"}
response = requests.get(url, headers=headers)
last_chunk = response.content
```

### Example 3: Streaming Download with Chunks
```python
def download_with_progress(url, chunk_size=8192):
    # Get file size first
    head_response = requests.head(url)
    total_size = int(head_response.headers['Content-Length'])
    
    downloaded = 0
    content = b""
    
    while downloaded < total_size:
        # Calculate range for this chunk
        start = downloaded
        end = min(downloaded + chunk_size - 1, total_size - 1)
        
        # Download chunk
        headers = {"Range": f"bytes={start}-{end}"}
        response = requests.get(url, headers=headers)
        
        if response.status_code == 206:
            chunk = response.content
            content += chunk
            downloaded += len(chunk)
            print(f"Progress: {downloaded}/{total_size} bytes")
        else:
            break
    
    return content
```

## Implementation Details

### Controller Changes
- Added `range_start` and `range_end` parameters to download methods
- Implemented Google Cloud Storage range downloads using `start` and `end` parameters
- Added validation for range boundaries

### Route Changes
- Added `Request` parameter to access Range headers
- Implemented range header parsing with regex
- Added proper HTTP status code handling (206, 416)
- Added Content-Range headers for partial responses
- Added HEAD endpoint for metadata requests

### Error Handling
- Invalid range format: Ignores Range header, returns full file (200)
- Range not satisfiable: Returns 416 with Content-Range header
- Missing file: Returns 404 as before
- Invalid UUID: Returns 400 as before

## Benefits

1. **Bandwidth Efficiency**: Download only needed portions
2. **Resume Capability**: Continue interrupted downloads
3. **Progressive Loading**: Load files in chunks for large firmware
4. **Better UX**: Faster initial response for partial content
5. **Standard Compliance**: Follows HTTP/1.1 Range specification (RFC 7233)

## Testing

Use the provided `test_range_requests.py` script to verify functionality:

```bash
python test_range_requests.py
```

Update the script with your actual firmware ID and authentication token before running.

## Curl Examples

```bash
# Full download
curl -H "Authorization: Bearer YOUR_TOKEN" \
     "http://localhost:8000/firmware/{id}/download/bin"

# First 1KB
curl -H "Authorization: Bearer YOUR_TOKEN" \
     -H "Range: bytes=0-1023" \
     "http://localhost:8000/firmware/{id}/download/bin"

# Last 1KB  
curl -H "Authorization: Bearer YOUR_TOKEN" \
     -H "Range: bytes=-1024" \
     "http://localhost:8000/firmware/{id}/download/bin"

# From byte 1000 to end
curl -H "Authorization: Bearer YOUR_TOKEN" \
     -H "Range: bytes=1000-" \
     "http://localhost:8000/firmware/{id}/download/bin"
```
