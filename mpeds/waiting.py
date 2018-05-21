# -*- coding: utf-8 -*-
# ABOUT:
#   This script is used to check if CLIFF is ready
#

import urllib
import urllib2

import json
import time

def urlencode_utf8(params):
    '''
    Workaround to allow for UTF-8 characters in urlencode
    See http://stackoverflow.com/questions/6480723/urllib-urlencode-doesnt-like-unicode-values-how-about-this-workaround

    :param params: parameters to encode
    :type params: a dictionary or list of tuples containing parameters to be encoded

    :return: utf-8 encoded URL parameters
    :rtype: string
    '''
    if hasattr(params, 'items'):
        params = params.items()
    return '&'.join(
        (urllib.quote_plus(k.encode('utf8'), safe='/') + '=' + urllib.quote_plus(v.encode('utf8'), safe='/')
            for k, v in params) )

def wait_for_cliff(host_port, timeout = 15):
    '''
    Perform CLIFF-2.3.0 parsing request to see if the service is up and running.

    :param host_port: string giving host and port in form host:port
    :type host_port: string

    :param timeout: how many seconds to wait before timing out
    :type timeout: integer

    '''

    print 'Trying to connect to ' + host_port + ' with a timeout of ' + str(timeout) + ' seconds'

    test_string = 'Sailing to Philadelphia'

    url = 'http://%s/CLIFF-2.3.0/parse/text' % host_port
    data = urlencode_utf8({ 'q': test_string.decode('utf-8') })


    start_time = time.time()

    while time.time() - start_time < timeout:
        req = urllib2.Request(url, data)
        try:
            res = urllib2.urlopen(req)
        except urllib2.URLError:
            res = None

        if res is not None and 200 == res.getcode():

            # in this case we've managed to connect to the service, but it could still be setting up internally
            # to make sure it's actually running, want to check that it does not return an error
            obj = json.loads(res.read())

            if 'ok' == obj['status']:
                print 'Successfully connected to CLIFF after ' + str(time.time() - start_time) + ' seconds'
                return

    # if still not able to connect, throw an error to prevent other script from being run
    raise StandardError('Timeout after ' + str(timeout) + ' seconds')


wait_for_cliff('cliff:8080', timeout = 3600)
