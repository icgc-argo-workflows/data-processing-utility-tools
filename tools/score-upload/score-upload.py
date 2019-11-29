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

  os.environ["METADATA_URL"] = args.song_url
  os.environ["STORAGE_URL"] = args.score_url
  os.environ["ACCESSTOKEN"] = token

  cmd = "score-client upload --manifest %s" % args.manifest_file

  ret = run_command(cmd)

  if ret[0].returncode != 0:
    print('')
    sys.exit('Upload failed, error msg: %s' % ret[2])
  else:
    print('OK')


if __name__ == "__main__":
  parser = ArgumentParser()
  parser.add_argument("-m", "--manifest-file", dest="manifest_file", required=True)
  parser.add_argument("-s", "--song-url", dest="song_url", required=True)
  parser.add_argument("-c", "--score-url", dest="score_url", required=True)
  parser.add_argument("-t", "--token-file", dest="token_file", required=True)
  args = parser.parse_args()

  main(args)
