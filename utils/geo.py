
# 🙏🏻 God bless AI
import math

# Earth's radius in kilometers
EARTH_RADIUS_min = 6357
EARTH_RADIUS_max = 6378.14
EARTH_RADIUS = (EARTH_RADIUS_min + EARTH_RADIUS_max) / 2

def haversine_distance(from_location, to_location):
    """
    Calculate the great-circle distance between two points on the Earth using the Haversine formula.

    Args:
        from_location (dict): A dictionary with 'lat' and 'lng' keys for the starting location.
        to_location (dict): A dictionary with 'lat' and 'lng' keys for the destination location.

    Returns:
        float: The distance in kilometers.
    """

    # Convert latitude and longitude from degrees to radians
    lat1 = math.radians(from_location['lat'])
    lon1 = math.radians(from_location['lng'])
    lat2 = math.radians(to_location['lat'])
    lon2 = math.radians(to_location['lng'])

    # Differences in coordinates
    dlat = lat2 - lat1
    dlon = lon2 - lon1

    # Haversine formula
    a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = EARTH_RADIUS * c

    return distance

