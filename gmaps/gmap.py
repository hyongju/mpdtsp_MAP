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
    leg = legs[0]
    steps_data = leg[STEPS]
    steps = []
    for step_data in steps_data:
      step = {DISTANCE: step_data[DISTANCE][VALUE], START_LOCATION: get_lat_lng(step_data[
          START_LOCATION]), END_LOCATION: get_lat_lng(step_data[END_LOCATION])}
      steps.append(step)
    total_distance = leg[DISTANCE][VALUE]
    return {TOTAL_DISTANCE: total_distance, STEPS: steps}
  except e:
    log(resp)
    raise


def strfmt_parsed_result(parsed):
  s = '{}: {}\n'.format(TOTAL_DISTANCE, parsed[TOTAL_DISTANCE])
  s += '{}: \n'.format(STEPS)
  for step in parsed[STEPS]:
    s += '  {\n'
    s += '    {}: {}\n'.format(DISTANCE, step[DISTANCE])
    s += '    {}: {}\n'.format(START_LOCATION, step[START_LOCATION])
    s += '    {}: {}\n'.format(END_LOCATION, step[END_LOCATION])
    s += '  },\n'
  s = s.rstrip('\n')
  return s


def compute_path(orig, dest):
  orig_dest = 'origin: {}, dest: {}'.format(orig, dest)
  vlog(1, 'Computing distance for {}'.format(orig_dest))
  resp = send_request(orig, dest)
  vlog(3, 'Got response: {}'.format(resp))
  # return
  result = parse_response(resp)
  try:
    vlog(1, 'Result for {} is:'.format(orig_dest))
    vlog(1, strfmt_parsed_result(result))
  except:
    log('Error when parsing response: {}'.format(resp))
    raise


def main():
  orig = '40.6655101,-73.89188969999998'
  dest = '40.6905615,-73.9976592'
  compute_path(orig, dest)

if __name__ == '__main__':
  main()
