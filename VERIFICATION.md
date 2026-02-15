# Verification Guide: Testing Your Tracker 🧪🕵️‍♂️

This guide provides step-by-step instructions to ensure your Wealth Tracker is running perfectly in all environments.

---

## 1. Local Verification (On Your Mac) 💻

Follow these steps to test the "Worker" and the "Dashboard" manually:

### Step A: Setup Environment
Ensure your `.venv` is active and dependencies are up to date:
```bash
source .venv/bin/activate
pip install -r requirements.txt
```

### Step B: Run the Tracker
Execute the tracker manually to fetch data and push it to Supabase:
```bash
python tracker.py
```
**What to look for:**
- [ ] Console logs saying `HTTP Request: ... "HTTP/2 201 Created"` (or 200).
- [ ] A success message showing the ACTUAL market date: `✅ Saved [TICKER] [2026-02-13]: [PRICE]`.
- [ ] A notification arriving on your **Telegram** phone app.

### Step C: Run the Dashboard
Visualize the data you just pushed:
```bash
streamlit run dashboard.py
```
**What to look for:**
- [ ] The browser opens to `localhost:8501`.
- [ ] Select a ticker from the sidebar and see the line graph populate.

---

## 2. Cloud Verification (On GitHub Actions) ☁️🤖

Ensure your daily automation is configured correctly.

### Step A: Configure Secrets & Variables
Go to **Repo Settings** -> **Secrets and variables** -> **Actions** and ensure these exist:

| Type | Name |
| :--- | :--- |
| **Secrets** | `SUPABASE_ANON_KEY`, `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID` |
| **Variables** | `SUPABASE_URL`, `TICKERS`, `DB_NAME` |

### Step B: Manually Trigger the Pipeline
You don't have to wait for the cron schedule (Thailand 06:00 AM) to test it:
1.  Go to the **Actions** tab in your GitHub Repository.
2.  Click on **"Automated Wealth Tracker"** in the left sidebar.
3.  Click the **"Run workflow"** dropdown button and select **"Run workflow"** (main branch).

### Step C: Monitor the Results
- [ ] Click on the running job to see the live logs.
- [ ] Verify the `Install dependencies` step completes (using the new clean `requirements.txt`).
- [ ] Verify the `Run Tracker` step finishes without errors and sends the Telegram alert.

---

## 3. Database Verification (On Supabase) 🐘🛡️

If you want to be 100% sure the data is stored:
1.  Log in to [Supabase Dashboard](https://supabase.com/dashboard).
2.  Go to **Table Editor** -> `assetprice` table.
3.  Verify that a new row exists for today's date with the correct price.

**Happy Tracking!** 💂‍♂️📈🚀✨🛡️
