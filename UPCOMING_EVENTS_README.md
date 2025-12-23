# Upcoming Events Feature - Documentation

## Overview
A new file `trial_with_events.py` has been created which is a copy of `trial.py` with an added "Upcoming Events" feature. This feature uses Azure OpenAI (GPT-4o) to fetch and display upcoming cultural events, festivals, big parties, and other notable gatherings in the area based on the district from the entered pincode.

## What's New

### 1. New Dependencies
- **openai>=1.0.0** - Azure OpenAI Python SDK (already added to requirements.txt)

### 2. Azure OpenAI Configuration
The application is configured to use Azure OpenAI via environment variables:
```python
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT", "https://balic-gpt-contentgenerationnew.openai.azure.com")
AZURE_OPENAI_DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4o")
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-01")
```

**To configure, create a `.env` file:**
```bash
AZURE_OPENAI_API_KEY=your_api_key_here
AZURE_OPENAI_ENDPOINT=https://balic-gpt-contentgenerationnew.openai.azure.com
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4o
AZURE_OPENAI_API_VERSION=2024-02-01
```

### 3. New Function: `get_upcoming_events(district, state)`
Located at line 495, this function:
- Takes district and state names as input
- Calls Azure OpenAI to fetch upcoming events information
- Returns structured JSON data with event details
- Results are cached for 24 hours (86400 seconds) to minimize API calls
- Handles errors gracefully

**Event data structure returned:**
```json
[
  {
    "name": "Event Name",
    "date": "Date or date range",
    "address": "Specific location or venue",
    "description": "Brief description of the event",
    "expected_attendance": "Number or range, or 'Not available'",
    "sources": "Source of information or 'Local knowledge'",
    "website": "URL or 'Not available'"
  }
]
```

### 4. New UI Section: "Upcoming Events in the Area"
Located at line 1923, this section displays:
- A header showing how many events were found
- Expandable cards for each event showing:
  - Event name and date in the header
  - Location/address
  - Description
  - Website (if available)
  - Sources (if available)
  - Expected attendance
- CSV export button to download all events data

## How to Use

### Installation
1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

### Running the Application
```bash
streamlit run trial_with_events.py
```

### User Workflow
1. Enter a 6-digit pincode in the input field
2. The app will:
   - Fetch location details (district, state)
   - Display demographics, education, and occupation data as before
   - **NEW:** Fetch and display upcoming events for that district
   - Show business leads in a 10km radius
3. View upcoming events in expandable cards
4. Export events data to CSV if needed

## Features

### Smart Event Discovery
- Uses GPT-4o to intelligently find events based on district and state
- Provides information about cultural events, festivals, parties, and gatherings
- Focuses on events within the next 3-6 months
- Falls back to general regional festivals if specific information isn't available

### Caching
- Event data is cached for 24 hours to reduce API costs
- Cache is per district/state combination

### Error Handling
- Gracefully handles API failures
- Displays warning messages if events cannot be fetched
- Parses JSON from markdown code blocks if GPT returns formatted output

### Export Capability
- Export all events to CSV with one click
- Filename includes district name and pincode for easy organization

## Integration with Existing Features
The Upcoming Events section is seamlessly integrated:
- Appears after the Education/Occupation/Industrial sections
- Appears before the Business Leads section
- Uses the same styling and design language as the rest of the dashboard
- Respects the district/state from the pincode lookup

## File Structure
```
/home/engine/project/
├── trial.py                    # Original file (unchanged)
├── trial_with_events.py        # New file with events feature
├── requirements.txt            # Updated with openai package
├── pincode.csv                 # Pincode database
├── pca_demographics.xlsx       # Demographics data
└── clean_census_combined.xlsx  # Census data
```

## Technical Details

### API Integration
- Uses Azure OpenAI Chat Completions API
- Model: gpt-4o
- Temperature: 0.7 (balanced creativity and accuracy)
- Max tokens: 2000 (sufficient for event listings)

### Prompt Engineering
The function uses a carefully crafted prompt that:
- Clearly specifies the district and state
- Requests structured JSON output
- Asks for specific fields (name, date, address, description, attendance, sources, website)
- Focuses on events within the next 3-6 months
- Provides fallback instructions for limited data scenarios

### Data Validation
- Checks if response is valid JSON
- Verifies response is a list
- Handles markdown-formatted JSON responses
- Returns empty array on errors with user-friendly error messages

## Cost Considerations
- Caching reduces API calls significantly
- Only fetches events when a new district is queried
- Cache duration: 24 hours
- Estimated cost: ~$0.01-0.03 per query depending on response length

## Future Enhancements
Potential improvements:
1. Add date filtering (only show events after today's date)
2. Add event type filtering (cultural, festivals, parties, etc.)
3. Add distance-based event search using lat/lng
4. Add calendar integration
5. Add event reminders
6. Add social media integration for event promotion

## Support
For issues or questions about the Upcoming Events feature, check:
- Azure OpenAI API status
- API key validity
- Internet connectivity
- Streamlit error messages in the terminal

## License
This feature integrates with the existing Lead Intelligence Dashboard and follows the same licensing terms.
