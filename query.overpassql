// Output format: JSON with 30 second timeout
[out:json][timeout:30];

// Define search area using an OSM relation ID
// Find relation IDs at https://nominatim.openstreetmap.org
// ex, Portland, OR: https://www.openstreetmap.org/relation/186579
(
  area["wikipedia"="en:Boston"];
  area["wikipedia"="en:Cambridge, Massachusetts"];
  area["wikipedia"="en:Brookline, Massachusetts"];
  area["wikipedia"="en:Somerville, Massachusetts"];
)->.searchArea;

// Query: all drinking water fountains in the search area
(
  nwr["amenity"="bicycle_parking"](area.searchArea);
);

// Output full geometry
// out body geom;

// Output centroids only
out center body;