## Usage

This script provides a function, `compute_path(orig, dest)`, which takes in two geopoints as the origin and destination and returns a `ParsedResult`. This result has two properties:

- `total_distance`: an integer, distance in meters between the two points.
- `steps`: a 2D array (actually it is a list of 2-tuples). Each row represents one segment of the route, with the first row being the origin and the last row being the destination. The first column is the latitude and the second one the longitude.

If there is a network problem or the Google Maps server rejects the request, this function raises an exception. If the server returns a response, but for some reason it cannot be parsed, it returns `None`.

Note that the starting and ending points returned by the API might be slightly different from what the usere provides.

```py
# example
orig = '40.6655101,-73.89188969999998'
dest = '40.6905615,-73.9976592'

result = compute_path(orig, dest)

print result.total_distance
print result.steps[0][0], results.steps[0][1]
print result.steps
```

## Reference

- [Google Maps Direction API](https://developers.google.com/maps/documentation/directions/intro)