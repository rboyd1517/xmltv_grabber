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

qs = {'country': 'USA', 'headendId': 'lineupId', 'timespan': TIMESPAN_HOURS, 'postalCode': 66062}

t_start = int(time.time() // 1800) * 1800
t_end = t_start + 15 * 24 * 60 * 60

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

    for channel in data['channels']:
        raw_channel = float(channel['channelNo'])
        channel_num = f"{int(10000 + 100 * int(raw_channel) + 10 * (raw_channel % 1))}"
        for event in channel['events']:
            program = ElementTree.SubElement(xml_data, 'programme')
            program.set('channel', channel_num)
            program.set('start', re.sub('[-:TZ]', '', event['startTime']))
            program.set('stop', re.sub('[-:TZ]', '', event['endTime']))
            title = ElementTree.SubElement(program, 'title')
            title.text = event['program']['title']
            desc = ElementTree.SubElement(program, 'desc')
            desc.text = event['program']['shortDesc']
            episode_num = ElementTree.SubElement(program, 'episode-num')
            episode_num.set('system', 'xmltv_ns')
            season = event['program']['season']
            if season is None:
                season_str = ""
            else:
                season_str = str(int(season) - 1)
            episode = event['program']['episode']
            if episode is None:
                episode_str = ""
            else:
                episode_str = str(int(episode) - 1)
            episode_num.text = f"{season_str}.{episode_str}."
            episode_title = ElementTree.SubElement(program, 'sub-title')
            episode_title.set('lang', 'en')
            episode_title.text = event['program']['episodeTitle']
            rating = ElementTree.SubElement(program, 'rating')
            rating.text = event['rating']
            if event['rating'] in ('TV-Y', 'TV-Y7', 'TV-Y7-FV', 'TV-G', 'TV-PG', 'TV-14', 'TV-MA'):
                rating.set('system', 'VCHIP')
            elif event['rating'] in ('G', 'PG', 'PG-13', 'R', 'NC-17'):
                rating.set('system', 'MPAA')

    time.sleep(1)

with open('output.xml', mode='wb') as xmlfile:
    xmlfile.write(ElementTree.tostring(xml_data, encoding='utf8'))
