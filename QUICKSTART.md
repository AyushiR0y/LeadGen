# Quick Start Guide - Upcoming Events Feature

## Overview
You now have a new file `trial_with_events.py` with an "Upcoming Events" feature that shows cultural events, festivals, and parties in the queried area using AI-powered event discovery.

## Installation

### 1. Configure Environment Variables
First, create a `.env` file with your API credentials:

```bash
# Copy the example file
cp .env.example .env

# Edit .env and add your credentials
# See ENV_SETUP.md for detailed instructions
```

**Your Azure OpenAI credentials should be provided separately. See `ENV_SETUP.md` for details.**

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

This will install:
- streamlit
- pandas
- plotly
- requests
- openpyxl
- **openai** (NEW - Azure OpenAI SDK)

### 3. Verify Installation
```bash
python3 -m pip list | grep openai
```

You should see: `openai` with version >= 1.0.0

## Running the Application

### Option 1: Run the NEW version (with events)
```bash
streamlit run trial_with_events.py
```

### Option 2: Run the ORIGINAL version (without events)
```bash
streamlit run trial.py
```

## Usage

1. **Open the application** in your browser (usually http://localhost:8501)

2. **Enter a pincode** (e.g., 110001 for New Delhi)

3. **View the results:**
   - Location information with map
   - Demographics data
   - Education and employment statistics
   - Industrial and occupation breakdowns
   - **🆕 Upcoming Events** - Cultural events, festivals, parties
   - Business leads (industries, banks, colleges, etc.)

4. **Interact with events:**
   - Click on event cards to expand details
   - View event name, date, location, description
   - Check expected attendance and sources
   - Visit event websites (if available)
   - Export all events to CSV

## Testing Examples

Try these pincodes to test the feature:

| Pincode | Location | Expected Events |
|---------|----------|-----------------|
| 110001 | New Delhi | Delhi festivals, cultural events |
| 400001 | Mumbai | Mumbai events, Bollywood parties |
| 560001 | Bangalore | Tech events, cultural festivals |
| 600001 | Chennai | Tamil festivals, music events |
| 700001 | Kolkata | Durga Puja, cultural events |
| 500001 | Hyderabad | Tech events, cultural festivals |

## What to Expect

### Events Section Features:
- **Smart Discovery**: AI finds relevant events for the district
- **Rich Details**: Name, date, location, description, attendance
- **Sources**: References and official websites when available
- **Export**: Download all events as CSV
- **Caching**: Results cached for 24 hours for faster loading

### Sample Event Card:
```
🎊 Diwali Festival - October 24-28, 2024
  📍 Location: Central Park, Connaught Place, New Delhi
  📝 Description: Five-day festival of lights with traditional 
      celebrations, fireworks, and cultural programs...
  📅 Date: October 24-28, 2024
  👥 Expected Attendance: 50,000+
  🌐 Website: www.example.com
  📚 Source: Local tourism board
```

## Troubleshooting

### Issue: "Module 'openai' not found"
**Solution:**
```bash
pip install openai>=1.0.0
```

### Issue: "Error fetching events"
**Possible causes:**
1. Azure OpenAI API key invalid
2. No internet connection
3. API rate limit reached
4. API endpoint unavailable

**Solution:**
- Check internet connectivity
- Verify Azure OpenAI service status
- Wait a few minutes and try again (cached results still work)

### Issue: No events showing
**This is normal if:**
- The API is temporarily unavailable
- The district is very small or remote
- Cache is empty and API fails

**Solution:**
- Try again later (AI will generate events when available)
- Try a different, larger city pincode

### Issue: Events seem generic
**This is expected:**
- AI generates events based on general knowledge
- More specific events appear for well-known districts
- Regional festivals are always included

## Files Overview

```
project/
├── trial.py                    ← Original (unchanged)
├── trial_with_events.py        ← NEW (with events feature)
├── requirements.txt            ← Updated (added openai)
├── QUICKSTART.md              ← This file
├── UPCOMING_EVENTS_README.md  ← Detailed documentation
├── CHANGES_SUMMARY.md         ← What changed
└── FEATURE_FLOW.md           ← Technical flow diagrams
```

## Key Features

### ✅ What Works
- All original trial.py features
- AI-powered event discovery
- 24-hour caching for performance
- CSV export for events
- Rich event details with sources
- Error handling and graceful degradation

### ⚠️ Limitations
- Events are AI-generated (may not be 100% accurate)
- Requires internet connection
- Depends on Azure OpenAI availability
- Limited to India (as per original app scope)
- Cache clears after 24 hours

## Production Considerations

### Before Deploying:
1. **Environment Variables**: Move API keys to .env file
   ```bash
   # Create .env file
   echo "AZURE_OPENAI_API_KEY=your_key_here" >> .env
   ```

2. **Update Code**: Use environment variables
   ```python
   AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
   ```

3. **Security**: Never commit API keys to git
   ```bash
   # Add to .gitignore
   echo ".env" >> .gitignore
   ```

4. **Monitoring**: Set up logging for API calls
5. **Cost Control**: Monitor Azure OpenAI usage
6. **Rate Limiting**: Add request throttling if needed

## Next Steps

1. ✅ Install dependencies
2. ✅ Run the application
3. ✅ Test with different pincodes
4. ✅ Verify events display correctly
5. ✅ Test CSV export
6. 📋 Move API keys to .env (for production)
7. 📋 Set up monitoring (for production)

## Support

- **Documentation**: See UPCOMING_EVENTS_README.md
- **Technical Flow**: See FEATURE_FLOW.md
- **Changes**: See CHANGES_SUMMARY.md

## Quick Reference

**Start app with events:**
```bash
streamlit run trial_with_events.py
```

**Start original app:**
```bash
streamlit run trial.py
```

**Install dependencies:**
```bash
pip install -r requirements.txt
```

**Test syntax:**
```bash
python3 -m py_compile trial_with_events.py
```

---

**Happy Event Discovery! 🎉**
