#!/usr/bin/env python3

"""
 Copyright (c) 2019, Ontario Institute for Cancer Research (OICR).
                                                                                                               
 This program is free software: you can redistribute it and/or modify
 it under the terms of the GNU Affero General Public License as published
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
from argparse import ArgumentParser
import subprocess


def run_command(cmd):
    p = subprocess.Popen(cmd,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE,
                         shell=True)
    stdout, stderr = p.communicate()

    return (p, stdout, stderr)


def main(args):
  with open(args.token_file, 'r') as t:
    token = t.read().strip()

  parts = args.path.split('/')
  if not (parts[0] == 'score:' and parts[1] == '' and len(parts) == 5):
    sys.exit("Error: path for SCORE object must start with 'score://(collab|aws)/(analysis_id)/(object_id)'. Found: %s" % args.path)
  else:
    repository = parts[2]
    object_id = parts[4]

  if args.song_url: os.environ["METADATA_URL"] = args.song_url
  if args.score_url: os.environ["STORAGE_URL"] = args.score_url
  os.environ["ACCESSTOKEN"] = token

  cmd = "score-client --profile %s download --object-id %s --output-dir out" % \
    (repository, object_id)

  ret = run_command(cmd)

  if ret[0].returncode != 0:
    sys.exit('Download failed, error msg: %s' % ret[2])


if __name__ == "__main__":
  parser = ArgumentParser()
  parser.add_argument("-p", "--path", dest="path", required=True)
  parser.add_argument("-s", "--song-url", dest="song_url")
  parser.add_argument("-c", "--score-url", dest="score_url")
  parser.add_argument("-t", "--token-file", dest="token_file")
  args = parser.parse_args()

  main(args)
