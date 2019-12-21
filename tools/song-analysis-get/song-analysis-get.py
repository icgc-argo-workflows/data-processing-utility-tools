#!/usr/bin/env python3

"""
 Copyright (c) 2019, Ontario Institute for Cancer Research (OICR).
                                                                                                               
 This program is free software: you can redistribute it and/or modify
 it under the terms of the GNU Affero General Public License as geted
 by the Free Software Foundation, either version 3 of the License, or
 (at your option) any later version.

 This program is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 GNU Affero General Public License for more details.

 You should have received a copy of the GNU Affero General Public License
 along with this program. If not, see <https://www.gnu.org/licenses/>.

 Author: Junjun Zhang <junjun.zhang@oicr.on.ca>
 """


import os
import sys
import json
import requests
from argparse import ArgumentParser


def main(args):
  headers = {
    "Content-Type": "application/json",
    "Accept": "application/json"
  }

  if args.token_file:
    with open(args.token_file, 'r') as t:
      token = t.read().strip()
    headers["Authorization"] = "Bearer %s" % token

  try:
    res = requests.get("%s/studies/%s/analysis/%s" % (args.song_url, args.study, args.analysis_id),
                        headers=headers)
    res.raise_for_status()
  except requests.exceptions.HTTPError as err:
    sys.exit("SONG analysis get failed, HTTPError: %s" % err)
  except requests.exceptions.RequestException as err:
    sys.exit("SONG analysis get failed, RequestException: %s" % err)

  if res.status_code != 200:
    sys.exit("SONG analysis get failed HTTP status code not 200: %s" % res)
  else:
    analysis_json_str = json.dumps(res.json(), indent=2)
    analysis_dict = json.loads(analysis_json_str)
    analysis_type = analysis_dict.get('analysisType', {}).get('name')
    analysis_version = analysis_dict.get('analysisType', {}).get('version')
    with open("%s.%s.%s.analysis.json" % (args.analysis_id, analysis_type, analysis_version), 'w') as s:
      s.write(analysis_json_str)


if __name__ == "__main__":
  parser = ArgumentParser()
  parser.add_argument("-a", "--analysis-id", dest="analysis_id", required=True)
  parser.add_argument("-p", "--study", dest="study", required=True)
  parser.add_argument("-s", "--song-url", dest="song_url", required=True)
  parser.add_argument("-t", "--token-file", dest="token_file")
  args = parser.parse_args()

  main(args)
