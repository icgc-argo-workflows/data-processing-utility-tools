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
 * Authors:
 *   Junjun Zhang <junjun.zhang@oicr.on.ca>
 */

nextflow.preview.dsl=2

params.seq_experiment_analysis = ""
params.qc_files = [ ]
params.wf_name = "dna-seq-alignment"
params.wf_version = "0.5.0-dev"
params.container_version = ""

include "../payload-gen-dna-seq-qc" params(params)

workflow {
  main:
    payloadGenDnaSeqQc(
      file(params.seq_experiment_analysis),
      Channel.fromPath(params.qc_files).collect(),
      params.wf_name,
      params.wf_version
    )
  publish:
    payloadGenDnaSeqQc.out.payload to: 'outdir', overwrite: true
    payloadGenDnaSeqQc.out.qc_files to: 'outdir', overwrite: true
}
