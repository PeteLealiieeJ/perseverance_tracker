# Perseverance Tracker
This repository contains an API which tracks the Perseverance rover's traversal across the Martain surface 

# Data Format 
The data from the source URL is formatted ass seen below:

    {
        "type": "FeatureCollection",
        "name": "M20_Rover_Localizations_tosol0402",
        "features": [
        { 
            "type": "Feature", 
            "properties": { 
                "RMC": "3_0", 
                "site": 3,
                "drive": 0, 
                "sol": 13, 
                "SCLK_START": 0.0, 
                "SCLK_END": 0.0, 
                "easting": 4354494.086, 
                "northing": 1093299.695, 
                "elev_geoid": -2569.91, 
                "elev_radii": -4253.47, 
                "radius": 3391936.53, 
                "lon": 77.45088572, 
                "lat": 18.44462715, 
                "roll": -1.1817, 
                "pitch": -0.0251, 
                "yaw": 130.8816, 
                "yaw_rad": 2.2843, 
                "tilt": 1.18, 
                "dist_m": 0.0, 
                "dist_total": 0.0,
                "dist_km": 0.0, 
                "dist_mi": 0.0, 
                "final": "y", 
                "Note": "Site increment, no motion." 
            }, 
            "geometry": { 
                "type": "Point", 
                "coordinates": [ 77.450885720000031, 18.444627149999974, -2569.909999999999854 ] } 
        },
        …
        ]
    }

# EXAMPLE USES 

    curl localhost:5015/perseverance/orientation/yaw -X POST  -H 'Content-Type: application/json' -d '{"start":"0","end":"400"}'