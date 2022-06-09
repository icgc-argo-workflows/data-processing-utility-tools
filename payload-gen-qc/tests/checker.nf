#!/usr/bin/env nextflow

/*
  Copyright (C) 2021,  Ontario Institute for Cancer Research

  This program is free software: you can redistribute it and/or modify
  it under the terms of the GNU Affero General Public License as published by
  the Free Software Foundation, either version 3 of the License, or
  (at your option) any later version.

  This program is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  GNU Affero General Public License for more details.

  You should have received a copy of the GNU Affero General Public License
  along with this program.  If not, see <http://www.gnu.org/licenses/>.

  Authors:
    Linda Xiang
*/

/*
 This is an auto-generated checker workflow to test the generated main template workflow, it's
 meant to illustrate how testing works. Please update to suit your own needs.
*/

/********************************************************************/
/* this block is auto-generated based on info from pkg.json where   */
/* changes can be made if needed, do NOT modify this block manually */
nextflow.enable.dsl = 2
version = '0.1.0'  // package version

container = [
    'ghcr.io': 'ghcr.io/icgc-argo-workflows/data-processing-utility-tools.payload-gen-qc'
]
default_container_registry = 'ghcr.io'
/********************************************************************/

// universal params
params.container_registry = ""
params.container_version = ""
params.container = ""

// tool specific parmas go here, add / change as needed
params.files_to_upload = ""
params.metadata_analysis = ""
params.wf_name = ""
params.wf_version = ""
params.genome_annotation = ""
params.genome_build = ""
params.expected_output = ""

include { payloadGenQc } from '../main'


process file_smart_diff {
  container "${params.container ?: container[params.container_registry ?: default_container_registry]}:${params.container_version ?: version}"

  input:
    path output_file
    path expected_file

  output:
    stdout()

  script:
    """
    cat ${output_file} \
      | sed -e 's/"run_id": ".*"/"run_id": "run_id"/' \
      | sed -e 's/"session_id": ".*"/"session_id": "session_id"/' \
      | sed -e 's/"fileName": ".*"/"fileName": "_normalized_file_name_"/' \
      > normalized_output
    ([[ '${expected_file}' == *.gz ]] && gunzip -c ${expected_file} || cat ${expected_file}) \
      | sed -e 's/"run_id": ".*"/"run_id": "run_id"/' \
      | sed -e 's/"session_id": ".*"/"session_id": "session_id"/' \
      | sed -e 's/"fileName": ".*"/"fileName": "_normalized_file_name_"/' \
      > normalized_expected
    diff normalized_output normalized_expected \
      && ( echo "Test PASSED" && exit 0 ) || ( echo "Test FAILED, output file mismatch." && exit 1 )
    """
}


workflow checker {
  take:
    files_to_upload
    metadata_analysis
    genome_annotation
    genome_build
    wf_name
    wf_version
    expected_output

  main:
    payloadGenQc(
      Channel.fromPath(files_to_upload).collect(),
      file(metadata_analysis),
      genome_annotation,
      genome_build,
      wf_name,
      wf_version
    )

    file_smart_diff(
      payloadGenQc.out.payload,
      file(expected_output)
    )
}


workflow {
  checker(
    params.files_to_upload,
    params.metadata_analysis,
    params.genome_annotation,
    params.genome_build,
    params.wf_name,
    params.wf_version,
    params.expected_output
  )
}
