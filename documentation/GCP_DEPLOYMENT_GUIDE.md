# Google Cloud Credentials Setup for Linux Deployment

This guide shows how to deploy your FastAPI application with the new file-based Google Cloud credentials setup.

## What Changed

- **Before**: GCP credentials were stored as a long JSON string in the `.env` file
- **After**: GCP credentials are stored in a separate `service-account.json` file

## Benefits

1. **Cleaner `.env` file**: No more huge JSON strings
2. **Better security**: Easier to manage file permissions
3. **Standard approach**: Uses Google's recommended credential file method
4. **Easier deployment**: No issues with JSON parsing in systemd

## Deployment Steps

### 1. On Your Local Machine

Test that everything works:

```bash
# Test the credentials
python test_gcp_credentials.py

# Start the server locally to verify
python server.py
```

### 2. On Your Linux Server

#### Copy the credentials file:

```bash
# Copy service-account.json to your server
scp service-account.json gibsonoluka7@alx-lb:~/iothubFastAPI/

# Copy updated .env file
scp .env gibsonoluka7@alx-lb:~/iothubFastAPI/
```

#### Set proper permissions:

```bash
# On the server, secure the credentials file
chmod 600 ~/iothubFastAPI/service-account.json
chmod 600 ~/iothubFastAPI/.env

# Make sure only you can read these files
ls -la ~/iothubFastAPI/service-account.json
ls -la ~/iothubFastAPI/.env
```

#### Update your systemd service (if needed):

Your existing systemd service should work, but if you want to be explicit:

```bash
sudo nano /etc/systemd/system/fastapi.service
```

Make sure it includes:

```ini
[Unit]
Description=FastAPI Service
After=network.target

[Service]
Type=simple
User=gibsonoluka7
WorkingDirectory=/home/gibsonoluka7/iothubFastAPI
Environment=PATH=/home/gibsonoluka7/iothubFastAPI/venv/bin
EnvironmentFile=/home/gibsonoluka7/iothubFastAPI/.env
ExecStart=/home/gibsonoluka7/iothubFastAPI/venv/bin/gunicorn -k uvicorn.workers.UvicornWorker server:app --bind 0.0.0.0:8000
Restart=always

[Install]
WantedBy=multi-user.target
```

#### Restart the service:

```bash
# Reload systemd configuration
sudo systemctl daemon-reload

# Restart your service
sudo systemctl restart fastapi

# Check status
sudo systemctl status fastapi

# Check logs for any issues
sudo journalctl -u fastapi -f
```

### 3. Test the Deployment

```bash
# On the server, test the credentials
cd ~/iothubFastAPI
source venv/bin/activate
python test_gcp_credentials.py

# Test API endpoints (replace with your server IP/domain)
curl http://your-server:8000/api/v1/status
```

## Credential Loading Priority

The system will try to load credentials in this order:

1. **GOOGLE_APPLICATION_CREDENTIALS** environment variable (file path)
2. **service-account.json** in project root
3. **GOOGLE_APPLICATION_CREDENTIALS_JSON** environment variable (JSON string) - fallback

## Troubleshooting

### If you get credential errors:

1. **Check file exists**: `ls -la ~/iothubFastAPI/service-account.json`
2. **Check file permissions**: `ls -la ~/iothubFastAPI/service-account.json`
3. **Test credentials**: `python test_gcp_credentials.py`
4. **Check service logs**: `sudo journalctl -u fastapi -f`

### If you want to use the old JSON method:

Simply set the `GOOGLE_APPLICATION_CREDENTIALS_JSON` environment variable in your `.env` file and remove the `service-account.json` file. The system will fall back to the old method.

### Common Issues:

1. **File not found**: Make sure `service-account.json` is in the correct directory
2. **Permission denied**: Run `chmod 600 service-account.json`
3. **Invalid JSON**: Validate the JSON format in the credentials file
4. **Wrong path**: Ensure the working directory in systemd is correct

## Security Notes

- The `service-account.json` file is automatically added to `.gitignore`
- Set file permissions to `600` (read/write for owner only)
- Never commit credentials files to version control
- Consider using Google Cloud IAM for even better security in production

## Rolling Back

If you need to revert to the old method:

1. Copy the JSON content from `service-account.json`
2. Add it back to `.env` as `GOOGLE_APPLICATION_CREDENTIALS_JSON={"type":"service_account"...}`
3. Remove or rename `service-account.json`
4. Restart the service