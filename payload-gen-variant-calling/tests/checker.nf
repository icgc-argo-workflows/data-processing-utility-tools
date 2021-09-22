#!/usr/bin/env nextflow

/*
  Copyright (c) 2021, Your Organization Name

  Permission is hereby granted, free of charge, to any person obtaining a copy
  of this software and associated documentation files (the "Software"), to deal
  in the Software without restriction, including without limitation the rights
  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
  copies of the Software, and to permit persons to whom the Software is
  furnished to do so, subject to the following conditions:

  The above copyright notice and this permission notice shall be included in all
  copies or substantial portions of the Software.

  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
  SOFTWARE.

  Authors:
    Junjun Zhang
*/

/*
 This is an auto-generated checker workflow to test the generated main template workflow, it's
 meant to illustrate how testing works. Please update to suit your own needs.
*/

/********************************************************************/
/* this block is auto-generated based on info from pkg.json where   */
/* changes can be made if needed, do NOT modify this block manually */
nextflow.enable.dsl = 2
version = '0.6.0.1'

container = [
    'ghcr.io': 'ghcr.io/icgc-argo/data-processing-utility-tools.payload-gen-variant-calling'
]
default_container_registry = 'ghcr.io'
/********************************************************************/

// universal params
params.container_registry = ""
params.container_version = ""
params.container = ""

// tool specific parmas go here, add / change as needed
params.normal_analysis = ""
params.tumour_analysis = ""
params.files_to_upload = []
params.wf_name = ""
params.wf_short_name = ""
params.wf_version = ""

params.expected_output = ""

include { payloadGenVariantCalling } from '../main'


process file_smart_diff {
  container "${params.container ?: container[params.container_registry ?: default_container_registry]}:${params.container_version ?: version}"

  input:
    path output_file
    path expected_file

  output:
    stdout()

  script:
    """
    # Note: this is only for demo purpose, please write your own 'diff' according to your own needs.
    # in this example, we need to remove date field before comparison eg, <div id="header_filename">Tue 19 Jan 2021<br/>test_rg_3.bam</div>
    # sed -e 's#"header_filename">.*<br/>test_rg_3.bam#"header_filename"><br/>test_rg_3.bam</div>#'

    cat ${output_file} \
      | sed -e 's/"run_id": ".*"/"run_id": "run_id"/' \
      | sed -e 's/"session_id": ".*"/"session_id": "session_id"/' \
      | sed -e 's/"fileName": "TEST-PR.DO.*.SA.*..*"/"fileName": "TEST-PR.DO_id_.SA_id_._normalized_file_name_"/' \
      > normalized_output

    ([[ '${expected_file}' == *.gz ]] && gunzip -c ${expected_file} || cat ${expected_file}) \
      | sed -e 's/"run_id": ".*"/"run_id": "run_id"/' \
      | sed -e 's/"session_id": ".*"/"session_id": "session_id"/' \
      | sed -e 's/"fileName": "TEST-PR.DO.*.SA.*..*"/"fileName": "TEST-PR.DO_id_.SA_id_._normalized_file_name_"/' \
      > normalized_expected

    diff normalized_output normalized_expected \
      && ( echo "Test PASSED" && exit 0 ) || ( echo "Test FAILED, output file mismatch." && exit 1 )
    """
}


workflow checker {
  take:
    normal_analysis
    tumour_analysis
    files_to_upload
    wf_name
    wf_short_name
    wf_version
    expected_output

  main:
    payloadGenVariantCalling(
      normal_analysis,
      tumour_analysis,
      files_to_upload,
      wf_name,
      wf_short_name,
      wf_version
    )

    file_smart_diff(
      payloadGenVariantCalling.out.payload,
      expected_output
    )
}


workflow {
  checker(
    file(params.normal_analysis),
    file(params.tumour_analysis),
    Channel.fromPath(params.files_to_upload).collect(),
    params.wf_name,
    params.wf_short_name,
    params.wf_version,
    file(params.expected_output)
  )
}
