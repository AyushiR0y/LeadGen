# Environment Setup Guide

## Required Environment Variables

The application requires Azure OpenAI credentials to be configured via environment variables for security.

### Step 1: Create .env File

Create a file named `.env` in the project root directory:

```bash
cp .env.example .env
```

### Step 2: Edit .env File

Open the `.env` file in a text editor and add your credentials. The structure should look like:

```
AZURE_OPENAI_API_KEY=<your_api_key_here>
AZURE_OPENAI_ENDPOINT=https://balic-gpt-contentgenerationnew.openai.azure.com
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4o
AZURE_OPENAI_API_VERSION=2024-02-01
```

**Note:** Replace `<your_api_key_here>` with the actual API key that was provided to you separately.

### Step 3: Verify .gitignore

The `.gitignore` file has been configured to exclude `.env` from version control. Verify this:

```bash
cat .gitignore | grep .env
```

You should see `.env` listed.

### Step 4: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 5: Run the Application

```bash
streamlit run trial_with_events.py
```

## Security Best Practices

✅ **DO:**
- Keep your `.env` file private
- Add `.env` to `.gitignore`
- Use different API keys for development/production
- Rotate API keys regularly
- Store backups of `.env` securely

❌ **DON'T:**
- Commit `.env` to git
- Share API keys in chat/email
- Hardcode credentials in source files
- Include credentials in screenshots
- Push credentials to public repositories

## Troubleshooting

### Issue: "API key not found"
**Solution:** Verify that:
1. `.env` file exists in project root
2. Variable names match exactly: `AZURE_OPENAI_API_KEY`
3. No quotes around the values
4. No spaces before/after the `=` sign

### Issue: "Module 'openai' not found"
**Solution:**
```bash
pip install openai>=1.0.0
```

### Issue: Events not loading
**Possible causes:**
- API key is incorrect
- No internet connection
- Azure OpenAI service is down
- API rate limit reached

**Solution:**
- Verify API key is correct
- Check internet connectivity
- Wait a few minutes and try again
- Check Azure OpenAI service status

## Alternative: Using Streamlit Secrets

For Streamlit Cloud deployment, you can also use Streamlit secrets:

1. Create `.streamlit/secrets.toml`:
```toml
AZURE_OPENAI_API_KEY = "your_key_here"
AZURE_OPENAI_ENDPOINT = "https://balic-gpt-contentgenerationnew.openai.azure.com"
AZURE_OPENAI_DEPLOYMENT_NAME = "gpt-4o"
AZURE_OPENAI_API_VERSION = "2024-02-01"
```

2. Update code to support both methods:
```python
# The code already uses os.getenv() which works with both
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY") or st.secrets.get("AZURE_OPENAI_API_KEY")
```

## Where to Get Your API Key

Your Azure OpenAI API key should have been provided to you separately by:
- Email from Azure/admin
- Secure credential sharing service
- Azure Portal (if you have access)

If you don't have the API key, please contact the system administrator or refer to the secure communication channel where it was shared.

## Verification

To verify your setup is correct, check that:

```bash
# 1. .env file exists
ls -la .env

# 2. Contains AZURE_OPENAI_API_KEY
cat .env | grep AZURE_OPENAI_API_KEY

# 3. .env is in .gitignore
cat .gitignore | grep .env

# 4. Dependencies are installed
pip list | grep openai
```

All checks should pass before running the application.
