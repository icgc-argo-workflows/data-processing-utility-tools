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
version = '0.2.0'

container = [
    'ghcr.io': 'ghcr.io/icgc-argo-workflows/data-processing-utility-tools.json-parser'
]
default_container_registry = 'ghcr.io'
/********************************************************************/

// universal params
params.container_registry = ""
params.container_version = ""
params.container = ""

// tool specific parmas go here, add / change as needed
params.metadata_analysis = ""
params.expected_output = ""

include { jsonParser } from '../main'

workflow checker {
  take:
    metadata_analysis

  main:
    jsonParser(
      metadata_analysis
    )
    jsonParser.out.study_id.set{study_id}
    study_id.view()
    jsonParser.out.donor_id.view()
    jsonParser.out.experimental_strategy.view()
    jsonParser.out.analysis_tools.view()
    jsonParser.out.paired.view()
    jsonParser.out.library_strandedness.view()
}


workflow {
  checker(
    file(params.metadata_analysis)
  )
}
