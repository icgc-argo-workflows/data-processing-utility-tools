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
import json
from argparse import ArgumentParser


def main(args):
  with open(args.song_analysis) as s:
    song_meta = json.load(s)

  analysis_id = song_meta["analysisId"]
  manifest_file = "%s.manifest.txt" % analysis_id

  with open(manifest_file, "w") as m:
    m.write("%s\t\t\n" % song_meta["analysisId"])
    for f in song_meta["files"]:
      m.write("%s\t%s\t%s\n" % (f["objectId"], os.path.join(os.getcwd(), f["fileName"]), f["fileMd5sum"]))

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("-s", "--song-analysis-json", dest="song_analysis", required=True)
    parser.add_argument("-f", "--files", dest="files", required=True, nargs="+")
    args = parser.parse_args()

    main(args)
