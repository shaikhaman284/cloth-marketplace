# Service area restriction
ALLOWED_DELIVERY_CITIES = ['Amravati', 'amravati', 'AMRAVATI']  # Case-insensitive

def is_city_serviceable(city):
    """Check if delivery is available in this city"""
    return city.strip().lower() in [c.lower() for c in ALLOWED_DELIVERY_CITIES]