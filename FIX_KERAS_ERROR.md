# Fix Keras 3 Compatibility Error - Manual Steps

Follow these steps in your terminal to fix the Keras 3 compatibility issue with Transformers.

---

## 🔧 Solution 1: Install tf-keras (Recommended)

This is the official solution recommended by Transformers.

### Step 1: Open Terminal/PowerShell

Navigate to your project directory:
```bash
cd C:\projects\chatbot
```

### Step 2: Activate Virtual Environment (if using one)

```bash
# If you have a virtual environment
./venv/Scripts/Activate.ps1
# Or
venv/Scripts/activate.bat
```

### Step 3: Uninstall Keras 3 (if installed)

```bash
pip uninstall keras -y
```

### Step 4: Install tf-keras

```bash
pip install tf-keras
```

**Note:** This will also install TensorFlow (~330MB download). This is required for Transformers to work with Keras 3.

### Step 5: Verify Installation

```bash
pip show tf-keras
```

### Step 6: Restart Django Server

```bash
python manage.py runserver
```

---

## 🔧 Solution 2: Downgrade Keras to 2.x (Alternative)

If you don't want to install TensorFlow, you can downgrade Keras.

### Step 1: Open Terminal/PowerShell

```bash
cd C:\projects\chatbot
```

### Step 2: Activate Virtual Environment (if using one)

```bash
.\venv\Scripts\Activate.ps1
```

### Step 3: Uninstall Keras 3

```bash
pip uninstall keras -y
```

### Step 4: Install Keras 2.x

```bash
pip install "keras<3.0"
```

### Step 5: Verify Installation

```bash
pip show keras
```

You should see version 2.x (like 2.15.0).

### Step 6: Restart Django Server

```bash
python manage.py runserver
```

---

## 🔧 Solution 3: Upgrade Transformers (If Available)

Check if a newer version of Transformers supports Keras 3.

### Step 1: Check Current Transformers Version

```bash
pip show transformers
```

### Step 2: Upgrade Transformers

```bash
pip install --upgrade transformers
```

### Step 3: Check if Keras 3 is Supported

If the latest version supports Keras 3, you can keep Keras 3 installed.

---

## ✅ Verification Steps

After applying any solution:

1. **Check Keras Version:**
   ```bash
   pip show keras
   ```

2. **Test Import:**
   ```bash
   python -c "import transformers; print('Transformers imported successfully')"
   ```

3. **Restart Django Server:**
   ```bash
   python manage.py runserver
   ```

4. **Test Upload API:**
   - Go to: http://127.0.0.1:8000/api/upload-document/
   - Try uploading a document
   - The error should be gone

---

## 🐛 Troubleshooting

### Issue: "pip: command not found"

**Solution:**
```bash
python -m pip install tf-keras
```

### Issue: "Permission denied"

**Solution:**
- On Windows: Run PowerShell as Administrator
- Or use: `pip install --user tf-keras`

### Issue: Still getting the error after installation

**Solution:**
1. Make sure you restarted the Django server
2. Clear Python cache:
   ```bash
   # Delete __pycache__ folders
   Get-ChildItem -Path . -Filter __pycache__ -Recurse -Directory | Remove-Item -Recurse -Force
   ```
3. Restart Django server again

### Issue: Multiple Python versions

**Solution:**
Make sure you're using the same Python that runs Django:
```bash
# Check which Python Django uses
python --version

# Use that Python for pip
python -m pip install tf-keras
```

---

## 📝 Quick Reference

### Complete Command Sequence (Solution 1 - Recommended)

```bash
cd C:\projects\chatbot
.\venv\Scripts\Activate.ps1
pip uninstall keras -y
pip install tf-keras
python manage.py runserver
```

### Complete Command Sequence (Solution 2 - Alternative)

```bash
cd C:\projects\chatbot
.\venv\Scripts\Activate.ps1
pip uninstall keras -y
pip install "keras<3.0"
python manage.py runserver
```

---

## ⚠️ Important Notes

1. **Solution 1 (tf-keras)** requires downloading TensorFlow (~330MB) but is the official recommended solution
2. **Solution 2 (Keras 2.x)** is lighter but may conflict with other packages that need Keras 3
3. Always restart your Django server after making changes
4. Make sure you're in the correct virtual environment (if using one)

---

**Last Updated:** January 2025

