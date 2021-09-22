#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import json
import re
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ElementTree


TIMESPAN_HOURS = 6
TIMESPAN_SECONDS = TIMESPAN_HOURS * 3600
CHANNEL_FILE = 'channels.sql'

qs = {'country': 'USA', 'headendId': 'lineupId', 'timespan': TIMESPAN_HOURS, 'postalCode': 66062}

t_start = int(time.time() // 1800) * 1800
# t_end = t_start + 14 * 24 * 60 * 60
t_end = t_start + 1

print(t_start, t_end)

xml_data = ElementTree.Element('tv')

for t in range(t_start, t_end, TIMESPAN_SECONDS):
    print(t)
    url = 'https://tvlistings.zap2it.com/api/grid?'
    qs.update(time=t)
    url += urllib.parse.urlencode(qs)
    print(url)
    json_data = urllib.request.urlopen(url)
    data = json.load(json_data)

    with open(CHANNEL_FILE, mode='w') as channel_file:
        pass  # To erase any existing file

    for channel in data['channels']:
        raw_channel = float(channel['channelNo'])
        underscore_channel = re.sub('\.', '_', channel['channelNo'])
        channel_num = f"{int(10000 + 100 * int(raw_channel) + 10 * (raw_channel % 1))}"
        with open(CHANNEL_FILE, mode='a') as channel_file:
            channel_file.write(f"update channel set xmltvid='{channel_num}' "
                               f"where sourceid=1 and channum='{underscore_channel}';\n")
        for event in channel['events']:
            program = ElementTree.SubElement(xml_data, 'programme')
            program.set('channel', channel_num)
            program.set('start', re.sub('[-:TZ]', '', event['startTime']))
            program.set('stop', re.sub('[-:TZ]', '', event['endTime']))
            title = ElementTree.SubElement(program, 'title')
            title.text = event['program']['title']
            desc = ElementTree.SubElement(program, 'desc')
            desc.text = event['program']['shortDesc']

    time.sleep(1)

with open('output.xml', mode='wb') as xmlfile:
    xmlfile.write(ElementTree.tostring(xml_data, encoding='utf8'))
