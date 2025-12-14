# Phi-3 Quick Start Guide

## Prerequisites

- Python 3.8+
- Ollama installed
- At least 4GB RAM available for Phi-3

## Step 1: Install Ollama

### Windows
1. Download from: https://ollama.ai/download
2. Run installer
3. Ollama will start automatically

### Linux/Mac
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

## Step 2: Install Phi-3 Model

```bash
ollama pull phi3
```

This will download the Phi-3 model (~2.5GB). Wait for completion.

## Step 3: Start Ollama Server

```bash
ollama serve
```

The server should start on `http://localhost:11434`

Verify it's running:
```bash
curl http://localhost:11434/api/tags
```

## Step 4: Test Phi-3 Integration

```bash
cd perfectcv-backend
python test_phi3_integration.py
```

Expected output:
```
✅ PASS: Phi-3 Availability
✅ PASS: Phi-3 Extraction
✅ PASS: Validation Gate
✅ PASS: Extraction Orchestrator
✅ PASS: CV Improvement
```

## Step 5: Test API Endpoint

Start the backend server:
```bash
cd perfectcv-backend
python run.py
```

Test Phi-3 status:
```bash
curl http://localhost:5000/api/files/phi3/status \
  -H "Authorization: Bearer YOUR_TOKEN"
```

Expected response:
```json
{
  "success": true,
  "phi3_available": true,
  "message": "Phi-3 is ready"
}
```

## Step 6: Upload a Test CV

Use the frontend or curl to upload a CV and see Phi-3 in action.

## Verification Checklist

- [ ] Ollama installed and running
- [ ] Phi-3 model downloaded
- [ ] Integration tests pass
- [ ] API endpoint responds
- [ ] CV upload works with extraction

## Troubleshooting

### Ollama not found
```bash
# Check if Ollama is in PATH
ollama --version

# If not, add to PATH or use full path
/path/to/ollama serve
```

### Port 11434 already in use
```bash
# Find process using port
# Windows
netstat -ano | findstr :11434

# Linux/Mac
lsof -i :11434

# Kill the process or change port in phi3_service.py
```

### Phi-3 extraction slow
```bash
# Use smaller model variant
ollama pull phi3:mini

# Update phi3_service.py:
OLLAMA_MODEL = "phi3:mini"
```

### Connection refused
1. Make sure Ollama is running: `ollama serve`
2. Check firewall settings
3. Verify URL in phi3_service.py matches Ollama server

## Next Steps

1. Review [PHI3_INTEGRATION.md](PHI3_INTEGRATION.md) for detailed documentation
2. Check logs during CV upload to see Phi-3 in action
3. Monitor extraction_metadata in API responses
4. Optimize primary extraction to reduce AI fallback rate

## Configuration Options

Edit `perfectcv-backend/app/services/phi3_service.py`:

```python
# Change Ollama URL (if running on different host/port)
OLLAMA_BASE_URL = "http://localhost:11434"

# Change model (use smaller/faster variant)
OLLAMA_MODEL = "phi3"  # or "phi3:mini"

# Adjust timeout (for slower systems)
OLLAMA_TIMEOUT = 60  # seconds
```

## Production Considerations

1. **Auto-start Ollama**: Set up as system service
2. **Monitoring**: Add health checks for Ollama availability
3. **Resource Limits**: Monitor CPU/RAM usage during AI calls
4. **Fallback Strategy**: System works without Phi-3 (graceful degradation)
5. **Scaling**: Consider dedicated Ollama server for multiple instances

## Support

If issues persist:
1. Check Ollama logs: `journalctl -u ollama` (Linux) or Event Viewer (Windows)
2. Test Ollama directly: `ollama run phi3 "test prompt"`
3. Review backend logs for detailed error messages
4. Run integration tests with verbose logging

---

**Setup Time:** 5-10 minutes  
**Disk Space:** ~3GB (Ollama + Phi-3)  
**RAM Required:** 4GB+ for optimal performance
