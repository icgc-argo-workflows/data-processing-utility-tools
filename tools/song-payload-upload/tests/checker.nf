#!/bin/bash nextflow

/*
 * Copyright (c) 2019, Ontario Institute for Cancer Research (OICR).
 *                                                                                                               
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU Affero General Public License as published
 * by the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU Affero General Public License for more details.
 *
 * You should have received a copy of the GNU Affero General Public License
 * along with this program. If not, see <https://www.gnu.org/licenses/>.
 */

/*
 * Author: Junjun Zhang <junjun.zhang@oicr.on.ca>
 */

nextflow.preview.dsl=2

params.song_url = "https://song.qa.argo.cancercollaboratory.org"
params.song_payload = "input/song-payload.test.json"
params.token_file = "/Users/junjun/access_token"

include "../song-payload-upload"

workflow {
  main:
    SongPayloadUpload(
      params.song_url,
      file(params.song_payload),
      file(params.token_file)
    )

  publish:
    SongPayloadUpload.out.song_analysis to: 'outdir', mode: 'copy', overwrite: true
}
