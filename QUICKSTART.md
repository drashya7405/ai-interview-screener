# 🚀 Quick Start Guide - AI Interview Screener

Get your interview screener running in **5 minutes**!

---

## Step 1: Install Dependencies

```bash
# Navigate to project folder
cd ai-interview-screener

# Activate virtual environment (if not already active)
source venv/bin/activate  # macOS/Linux
# OR
venv\Scripts\activate     # Windows

# Install packages
pip install -r requirements.txt
```

**Expected output:**
```
Successfully installed fastapi-0.115.0 groq-0.11.0 ...
```

---

## Step 2: Get FREE Groq API Key

1. **Go to:** https://console.groq.com/
2. **Sign up** (completely free, no credit card!)
3. Click **"API Keys"** in sidebar
4. Click **"Create API Key"**
5. **Copy** your key (starts with `gsk_...`)

⚠️ **Important:** Save your key immediately - you can't view it again!

---

## Step 3: Configure API Key

**Option A: Quick command**
```bash
echo "GROQ_API_KEY=gsk_your_key_here" > .env
```

**Option B: Manual creation**

Create a file named `.env` in your project root:
```
GROQ_API_KEY=gsk_paste_your_actual_key_here
```

✅ **Verify:** Your `.env` file should have one line with your actual key

---

## Step 4: Run Server

```bash
python main.py
```

**Expected output:**
```
🚀 Starting AI Interview Screener with Groq API...
📚 API Documentation: http://localhost:8000/docs
🔍 Health Check: http://localhost:8000/
INFO:     Started server process [12345]
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

✅ **Success!** Your backend is now running!

---

## Step 5: Test with Postman

### Import Collection

1. **Open Postman**
2. Click **Import** (top left)
3. Select **`AI_Interview_Screener.postman_collection.json`**
4. Click **Import**

✅ You should see "AI Interview Screener (Groq)" collection with 9 requests

### Run Your First Test

1. **Select:** `Health Check` request
2. **Click:** Send button
3. **See:** Server status response! 🎉

**Expected Response:**
```json
{
  "status": "running",
  "service": "AI Interview Screener",
  "ai_provider": "Groq (Free API)",
  "model": "llama-3.3-70b-versatile",
  "groq_status": "✅ Connected"
}
```

### Evaluate Your First Answer

1. **Select:** `Evaluate Answer - Excellent` request
2. **Click:** Send
3. **See:** AI evaluation with score, summary, and improvement! 🚀

---

## 🎉 You're Done!

Your AI Interview Screener is now fully operational!

---

## 📋 What to Test Next

Try these requests in order:

1. ✅ **Health Check** - Verify connection
2. ✅ **Evaluate Answer - Excellent** - See high score (4-5)
3. ✅ **Evaluate Answer - Poor** - See low score (1-2)
4. ✅ **Rank 4 Candidates** - See full ranking system
5. ✅ **Error - Empty Answer** - See error handling

---

## 🚨 Troubleshooting

### ❌ "GROQ_API_KEY not found"

**Check:**
```bash
# View .env file
cat .env

# Should show:
GROQ_API_KEY=gsk_...
```

**Fix:**
- Ensure `.env` file exists in project root
- Key should start with `gsk_`
- No spaces around the `=`
- No quotes around the key

---

###