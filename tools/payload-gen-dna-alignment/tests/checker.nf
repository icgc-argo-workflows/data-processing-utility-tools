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
 * author Junjun Zhang <junjun.zhang@oicr.on.ca>
 */

nextflow.preview.dsl=2

params.file_to_upload = "data/HCC1143_BAM_INPUT.3.20190812.wgs.grch38.bam"
params.input_payload = [
  "data/lane_seq_submission.C0HVY_2.lane.bam.json",
  "data/lane_seq_submission.D0RE2_1.lane.bam.json",
  "data/lane_seq_submission.D0RH0_2.lane.bam.json"
]
params.wf_short_name = "dna-seq-alignment"
params.wf_version = "0.2.9.2"

include "../payload-gen-dna-alignment" params(params)

Channel
  .fromPath(params.input_payload, checkIfExists: true)
  .set { input_payload_ch }

workflow {
  main:
    payloadGeneration(
      file(params.file_to_upload),
      file(getSecondaryFile(params.file_to_upload)),
      input_payload_ch.collect(),
      params.wf_short_name,
      params.wf_version
    )
  publish:
    payloadGeneration.out.payload to: 'outdir', mode: 'copy', overwrite: true
}
