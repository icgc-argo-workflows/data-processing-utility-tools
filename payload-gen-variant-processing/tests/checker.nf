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
    Linda Xiang (linda.xiang@oicr.on.ca)
*/

/*
 This is an auto-generated checker workflow to test the generated main template workflow, it's
 meant to illustrate how testing works. Please update to suit your own needs.
*/

/********************************************************************/
/* this block is auto-generated based on info from pkg.json where   */
/* changes can be made if needed, do NOT modify this block manually */
nextflow.enable.dsl = 2
version = '0.2.0'  // package version

container = [
    'ghcr.io': 'ghcr.io/icgc-argo/data-processing-utility-tools.payload-gen-variant-processing'
]
default_container_registry = 'ghcr.io'
/********************************************************************/

// universal params
params.container_registry = ""
params.container_version = ""
params.container = ""

// tool specific parmas go here, add / change as needed
params.analysis = ""
params.files_to_upload = []
params.wf_name = ""
params.wf_short_name = ""
params.wf_version = ""
params.open = false
params.expected_output = ""

include { payloadGenVariantProcessing } from '../main'

process file_smart_diff {
  container "${params.container ?: container[params.container_registry ?: default_container_registry]}:${params.container_version ?: version}"

  input:
    path output_file
    path expected_file

  output:
    stdout()

  script:
    """
    diff <( cat ${output_file} | jq -S . | sed '/\"run_id\"/d' | sed '/\"session_id\"/d' ) \
         <( cat ${expected_file} | jq -S . | sed '/\"run_id\"/d' | sed '/\"session_id\"/d' ) \
    && ( echo "Test PASSED" && exit 0 ) || ( echo "Test FAILED, output file mismatch." && exit 1 )
    """
}


workflow checker {
  take:
    analysis
    files_to_upload
    wf_name
    wf_short_name
    wf_version
    open
    expected_output

  main:
    payloadGenVariantProcessing(
      analysis,
      files_to_upload,
      wf_name,
      wf_short_name,
      wf_version,
      open
    )

    file_smart_diff(
      payloadGenVariantProcessing.out.payload,
      expected_output
    )
}


workflow {
  checker(
    file(params.analysis),
    Channel.fromPath(params.files_to_upload).collect(),
    params.wf_name,
    params.wf_short_name,
    params.wf_version,
    params.open,
    file(params.expected_output)
  )
}
