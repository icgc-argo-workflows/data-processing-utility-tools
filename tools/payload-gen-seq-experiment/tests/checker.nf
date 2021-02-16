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

params.metadata_json = "NO_FILE1"
params.experiment_info_tsv = "NO_FILE2"
params.read_group_info_tsv = "NO_FILE3"
params.file_info_tsv = "NO_FILE4"

include {payloadGenSeqExperiment} from "../payload-gen-seq-experiment" params(params)

workflow {
  main:
    payloadGenSeqExperiment(
      file(params.metadata_json),
      file(params.experiment_info_tsv),
      file(params.read_group_info_tsv),
      file(params.file_info_tsv)
    )
}
