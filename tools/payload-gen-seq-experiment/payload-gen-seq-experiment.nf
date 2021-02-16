#!/usr/bin/env nextflow

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
 * Author Linda Xiang <linda.xiang@oicr.on.ca>
 */

nextflow.enable.dsl=2
version = '0.2.1'

params.metadata_json = "NO_FILE1"
params.experiment_info_tsv = "NO_FILE2"
params.read_group_info_tsv = "NO_FILE3"
params.file_info_tsv = "NO_FILE4"

params.container_version = ''
params.cpus = 1
params.mem = 1  // GB
params.publish_dir = ""

process payloadGenSeqExperiment {
  container "quay.io/icgc-argo/payload-gen-seq-experiment:payload-gen-seq-experiment.${params.container_version ?: version}"
  cpus params.cpus
  memory "${params.mem} GB"
  publishDir "${params.publish_dir}/${task.process.replaceAll(':', '_')}", mode: "copy", enabled: "${params.publish_dir ? true : ''}"

  input:
    path metadata_json
    path experiment_info_tsv
    path read_group_info_tsv
    path file_info_tsv

  output:
    path "*.sequencing_experiment.payload.json", emit: payload

  script:
    args_metadata_json = !metadata_json.name.startsWith("NO_FILE") ? "-m ${metadata_json}" : ""
    args_experiment_info_tsv = !experiment_info_tsv.name.startsWith("NO_FILE") ? "-x ${experiment_info_tsv}" : ""
    args_read_group_info_tsv = !read_group_info_tsv.name.startsWith("NO_FILE") ? "-r ${read_group_info_tsv}" : ""
    args_file_info_tsv = !file_info_tsv.name.startsWith("NO_FILE") ? "-f ${file_info_tsv}" : ""

    """
    payload-gen-seq-experiment.py \
         ${args_metadata_json} \
         ${args_experiment_info_tsv} \
         ${args_read_group_info_tsv} \
         ${args_file_info_tsv}
    """
}
