# Commit Message for Geocoding Integration

## Title
[FEAT] Add Google Geocoding API integration for address coordinates

## Description
- Create geocoding service using Google Maps Python SDK
- Update configuration to support HOMEWARD_GEOCODING_API_KEY environment variable
- Enhance Location model with coordinate management methods
- Integrate geocoding into missing person form submission workflow
- Update setup.sh to create and restrict geocoding API key
- Update destroy.sh to clean up geocoding API key resources
- Add googlemaps>=4.10.0 dependency to pyproject.toml
- Populate last_seen_latitude/longitude/geo fields from form addresses
- Graceful fallback when geocoding fails or API key is missing

## Footer
🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>

---

## Files Modified

### New Files:
- `src/homeward/services/geocoding_service.py` - Google Geocoding API service implementation

### Modified Files:
- `src/homeward/config.py` - Added geocoding_api_key configuration field
- `src/homeward/models/case.py` - Enhanced Location model with geocoding helper methods
- `src/homeward/ui/pages/new_report.py` - Integrated geocoding into form submission
- `setup.sh` - Added geocoding API setup and key creation
- `destroy.sh` - Added geocoding API key cleanup
- `pyproject.toml` - Added googlemaps dependency

## Implementation Details

The implementation addresses the null geo information (last_seen_latitude, last_seen_longitude, last_seen_geo) by:

1. **Creating a geocoding service** that uses the Google Maps Python SDK to convert addresses to coordinates
2. **Configuring API key management** in both setup and destroy scripts as requested
3. **Integrating seamlessly** into the existing form submission workflow
4. **Providing graceful fallbacks** when geocoding fails or isn't configured
5. **Following best practices** with proper error handling and user notifications

The solution follows the exact specifications provided:
- Enables "geocoding-backend.googleapis.com" API
- Creates API key with gcloud services api-keys create
- Restricts API key to geocoding service only
- Populates geo fields from form address data