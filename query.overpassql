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
  area["wikipedia"="en:Belmont, Massachusetts"];
  area["wikipedia"="en:Everett, Massachusetts"];
  area["wikipedia"="en:Medford, Massachusetts"];
  area["wikipedia"="en:Malden, Massachusetts"];
  area["wikipedia"="en:Watertown, Massachusetts"];
  area["wikipedia"="en:Arlington, Massachusetts"];
  area["wikipedia"="en:Lexington, Massachusetts"];
  area["wikipedia"="en:Chelsea, Massachusetts"];
  area["wikipedia"="en:Revere, Massachusetts"];
  area["wikipedia"="en:Winthrop, Massachusetts"];
  area["wikipedia"="en:Newton, Massachusetts"];
  area["wikipedia"="en:Waltham, Massachusetts"];
  area["wikipedia"="en:Milton, Massachusetts"];
  area["wikipedia"="en:Dedham, Massachusetts"];
  area["wikipedia"="en:Quincy, Massachusetts"];
  area["wikipedia"="en:Winchester, Massachusetts"];
  area["wikipedia"="en:Woburn, Massachusetts"];
  area["wikipedia"="en:Melrose, Massachusetts"];
  area["wikipedia"="en:Stoneham, Massachusetts"];
)->.searchArea;

// Query: all drinking water fountains in the search area
(
  nwr["amenity"="bicycle_parking"](area.searchArea);
);

// Output full geometry
// out body geom;

// Output centroids only
out center body;