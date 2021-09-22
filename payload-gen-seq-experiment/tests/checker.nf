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
version = '0.5.0.1'

container = [
    'ghcr.io': 'ghcr.io/icgc-argo-workflows/data-processing-utility-tools.payload-gen-seq-experiment'
]
default_container_registry = 'ghcr.io'
/********************************************************************/

// universal params
params.container_registry = ""
params.container_version = ""
params.container = ""

// tool specific parmas go here, add / change as needed
params.experiment_info_tsv = "NO_FILE1"
params.read_group_info_tsv = "NO_FILE2"
params.file_info_tsv = "NO_FILE3"
params.extra_info_tsv = "NO_FILE4"
params.expected_output = ""

include { payloadGenSeqExperiment } from '../main'


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
    # remove date field before comparison eg, <div id="header_filename">Tue 19 Jan 2021<br/>test_rg_3.bam</div>
    # sed -e 's#"header_filename">.*<br/>test_rg_3.bam#"header_filename"><br/>test_rg_3.bam</div>#'

    diff <( cat ${output_file} | sed -e 's#"header_filename">.*<br/>#"header_filename"><br/>#' ) \
         <( ([[ '${expected_file}' == *.gz ]] && gunzip -c ${expected_file} || cat ${expected_file}) | sed -e 's#"header_filename">.*<br/>#"header_filename"><br/>#' ) \
    && ( echo "Test PASSED" && exit 0 ) || ( echo "Test FAILED, output file mismatch." && exit 1 )
    """
}


workflow checker {
  take:
    experiment_info_tsv
    read_group_info_tsv
    file_info_tsv
    extra_info_tsv
    expected_output

  main:
    payloadGenSeqExperiment(
      experiment_info_tsv,
      read_group_info_tsv,
      file_info_tsv,
      extra_info_tsv
    )

    file_smart_diff(
      payloadGenSeqExperiment.out.payload,
      expected_output
    )
}


workflow {
  checker(
    file(params.experiment_info_tsv),
    file(params.read_group_info_tsv),
    file(params.file_info_tsv),
    file(params.extra_info_tsv),
    file(params.expected_output)
  )
}
