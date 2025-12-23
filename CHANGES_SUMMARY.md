# Changes Summary: trial.py → trial_with_events.py

## Files Modified/Created

### 1. New File: `trial_with_events.py`
- Copy of `trial.py` with Upcoming Events feature added
- Original `trial.py` remains unchanged

### 2. Updated: `requirements.txt`
- Added: `openai>=1.0.0`

### 3. New Documentation: `UPCOMING_EVENTS_README.md`
- Comprehensive documentation for the new feature

## Code Changes in trial_with_events.py

### Imports (Lines 10-11)
```python
+ import json
+ from openai import AzureOpenAI
```

### Configuration (Lines 24-29)
```python
+ # Azure OpenAI Configuration (via environment variables)
+ AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
+ AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT", "https://balic-gpt-contentgenerationnew.openai.azure.com")
+ AZURE_OPENAI_DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4o")
+ AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-01")
```

### New Function (Lines 488-562, ~74 lines)
```python
+ @st.cache_data(ttl=86400)
+ def get_upcoming_events(district: str, state: str):
+     """Fetch upcoming events for a district using Azure OpenAI"""
+     # ... implementation ...
```

### New UI Section (Lines 1916-1963, ~47 lines)
```python
+ # Upcoming Events Section
+ st.markdown('<div class="section-header">🎉 Upcoming Events in the Area</div>', ...)
+ # ... event display logic ...
```

## Line Count
- Original `trial.py`: 1,890 lines
- New `trial_with_events.py`: 2,009 lines
- **Net Addition: 119 lines**

## Key Features Added

1. **Azure OpenAI Integration**
   - Credentials configuration
   - API client setup
   - Error handling

2. **Event Fetching Function**
   - Cached for 24 hours
   - Structured JSON output
   - Graceful error handling

3. **Events UI Section**
   - Expandable event cards
   - Rich event information display
   - CSV export functionality

## Testing Recommendations

### Basic Functionality Test
```bash
# Run the new file
streamlit run trial_with_events.py

# Test with a known pincode
# Example: 110001 (New Delhi)
# Example: 400001 (Mumbai)
# Example: 560001 (Bangalore)
```

### Verification Checklist
- [ ] App starts without errors
- [ ] Can enter pincode
- [ ] Demographics section loads
- [ ] Upcoming Events section appears
- [ ] Events are displayed in expandable cards
- [ ] CSV export works
- [ ] Business Leads section still works
- [ ] No console errors

## Backward Compatibility
- ✅ Original `trial.py` unchanged
- ✅ All existing features preserved
- ✅ New feature is additive, not disruptive
- ✅ Same data files used
- ✅ Same styling and design

## Deployment Notes
- Requires `openai` package installation
- Azure OpenAI credentials are hardcoded (consider using .env for production)
- Events are cached per district for 24 hours
- API costs apply per unique district query

## Rollback Plan
If issues occur:
1. Use original `trial.py` instead
2. Remove `openai` from requirements.txt if needed
3. No database changes required
4. No data migration needed
