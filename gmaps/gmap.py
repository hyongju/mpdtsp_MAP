import urllib2
import json
from urllib2 import HTTPError

API_URL = 'https://maps.googleapis.com/maps/api/directions/json?mode=driving&units=metric'
OK = 'OK'
STATUS = 'status'
ROUTES = 'routes'
LEGS = 'legs'
STEPS = 'steps'
LAT = 'lat'
LNG = 'lng'
DISTANCE = 'distance'
VALUE = 'value'
START_LOCATION = 'start_location'
END_LOCATION = 'end_location'
TOTAL_DISTANCE = 'total_distance'

LOG_LV = 1


def log(msg):
  print msg


def vlog(lv, msg):
  if LOG_LV >= lv:
    log(msg)


def send_request(orig, dest):
  try:
    url = API_URL + '&origin={}&destination={}'.format(orig, dest)
    vlog(3, url)
    response = urllib2.urlopen(url)
    return response.read()
  except HTTPError as e:
    log('Google Maps failed to handle the request {} with error: {}'.format(url, e))
    raise
  except URLError as e:
    log('Failed to reach a server: {}'.format(e.reason))
    raise


def get_lat_lng(location):
  return (location[LAT], location[LNG])


class ParsedResult(object):

  def __init__(self, d, s):
    self._total_distance = d
    self._steps = s

  @property
  def total_distance(self):
    return self._total_distance

  @property
  def steps(self):
    return self._steps

  def __str__(self):
    s = '{}: {} m\n'.format(TOTAL_DISTANCE, self.total_distance)
    s += '{}: \n'.format(STEPS)
    for step in self.steps:
      s += '  {}\n'.format(step)
    s = s.rstrip('\n')
    return s

  def __repr__(self):
    return str(self)


def parse_response(resp):
  resp_dict = json.loads(resp)
  try:
    # all sorts of checks
    top_status = resp_dict[STATUS]
    if top_status != OK:
      raise ValueError('Top-level status is not OK, {}'.format(top_status))
    routes = resp_dict[ROUTES]
    if len(routes) != 1:
      raise ValueError('Unexpected number of routes.')
    legs = routes[0][LEGS]
    if len(legs) != 1:
      raise ValueError('Unexpected number of legs in a route.')

    # parse the response
    leg = legs[0]
    total_distance = leg[DISTANCE][VALUE]
    steps = [get_lat_lng(leg[START_LOCATION])]
    for step_data in leg[STEPS]:
      lat_lng = get_lat_lng(step_data[END_LOCATION])
      steps.append(lat_lng)
    return ParsedResult(total_distance, steps)
  except e:
    log(resp)
    raise


def compute_path(orig, dest):
  resp = send_request(orig, dest)
  vlog(3, 'Got response: {}'.format(resp))
  try:
    return parse_response(resp)
  except e:
    log('Error when parsing response: {}'.format(resp))
    log(e)
    # raise
    return None


def main():
  # sample input
  orig = '40.6655101,-73.89188969999998'
  dest = '40.6905615,-73.9976592'

  orig_dest = 'origin: {}, dest: {}'.format(orig, dest)
  vlog(1, 'Computing path for {}'.format(orig_dest))

  result = compute_path(orig, dest)
  if result is not None:
    vlog(1, 'Result for {}:'.format(orig_dest))
    vlog(1, result)
    # sample usage
    #
    # result.total_distance
    # result.steps
  else:
    vlog(1, 'Could not find path for {}'.format(orig_dest))

if __name__ == '__main__':
  main()
