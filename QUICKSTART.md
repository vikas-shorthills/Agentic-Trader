# Quick Start Guide 🚀

Get the portfolio analysis feature running in 3 simple steps!

## Step 1: Start the Backend (Terminal 1)

```bash
cd /home/shtlp_0170/Videos/hackthon/Agentic-Trader
python3 -m app.main
```

**Wait for:**
```
✅ Server: http://0.0.0.0:8000
✅ API Docs: http://0.0.0.0:8000/docs
```

## Step 2: Start the Frontend (Terminal 2)

```bash
cd /home/shtlp_0170/Videos/hackthon/Agentic-Trader/frontend
npm run dev
```

**Wait for:**
```
✅ Local: http://localhost:5173/
```

## Step 3: Test the Feature

1. **Open browser:** http://localhost:5173

2. **Click:** "Select Companies" button

3. **Choose 2-3 companies** from Nifty 50 tab

4. **Fill in:**
   - Tenure: `12` weeks
   - Amount: `10000`

5. **Click:** "Calculate Portfolio"

6. **Wait:** ~1-2 minutes for AI analysis

7. **View:** Comprehensive investment analysis with BUY/SELL/HOLD recommendations!

---

## What You'll See

### While Analyzing:
```
🔄 Analyzing Portfolio...
   Analyzing 3 companies... This may take 1-2 minutes.
```

### After Complete:
```
✅ AI Analysis Complete
   Request ID: PA-20251219-173000
   Successful: 3/3
   Failed: 0

   [Company Cards with expandable AI reports]
   📋 Click "View Full Analysis" to see details
```

---

## Troubleshooting

### Backend won't start?
```bash
pip3 install -r app/requirements.txt
```

### Frontend error?
```bash
cd frontend
npm install
```

---

## That's It! 🎉

You now have a fully functional AI-powered portfolio analysis system!

For detailed documentation, see:
- `IMPLEMENTATION_SUMMARY.md` - Complete overview
- `TESTING_GUIDE.md` - Detailed testing instructions
- `frontend/PORTFOLIO_API.md` - API documentation

