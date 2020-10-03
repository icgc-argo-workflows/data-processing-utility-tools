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

nextflow.enable.dsl=2

params.bundle_type = "dna_alignment"
params.payload_schema_version = "0.1.0-rc.2"
params.user_submit_metadata = "NO_FILE"
params.file_to_upload = "data/HCC1143_BAM_INPUT.3.20190812.wgs.grch38.bam"
params.analysis_input_payload = [
  "data/lane_seq_submission.C0HVY_2.lane.bam.json",
  "data/lane_seq_submission.D0RE2_1.lane.bam.json",
  "data/lane_seq_submission.D0RH0_2.lane.bam.json"
]
params.wf_short_name = ""
params.wf_version = ""

include {payloadGeneration; getSecondaryFile} from "../payload-generation" params(params)

Channel
  .fromPath(params.analysis_input_payload, checkIfExists: false)
  .set { analysis_input_payload_ch }

workflow {
  main:
    payloadGeneration(
      params.bundle_type,
      params.payload_schema_version,
      file(params.user_submit_metadata),
      file(params.file_to_upload),
      file(getSecondaryFile(params.file_to_upload)),
      analysis_input_payload_ch.collect(),
      params.wf_short_name,
      params.wf_version
    )
}
