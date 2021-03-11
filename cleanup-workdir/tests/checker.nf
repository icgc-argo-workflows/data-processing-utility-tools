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

nextflow.enable.dsl = 2

// universal params
params.container_registry = ""
params.container_version = ""
params.container = ""

// tool specific parmas go here, add / change as needed
params.input_file = ""
params.expected_output = ""

params.cpus = 1
params.mem = 1  // GB

include { cleanupWorkdir } from '../main'

include {
    generateDummyFile as gFile1;
    generateDummyFile as gFile2;
} from './generate-dummy-file.nf'

include {
    filesExist as fExist1;
    filesExist as fExist2;
    filesExist as fExist3;
    filesExist as fExist4;
} from './files-exist.nf'

Channel.from(params.file_name).set{ file_name_ch }


workflow {
    // generate the file
    gFile1(
        file_name_ch.flatten(),
        params.file_size
    )

    // generate the same file again
    gFile2(
        file_name_ch.flatten(),
        params.file_size
    )

    // test file exists
    fExist1(
        params.file_name,
        'exist',
        gFile1.out.file.collect(),
        true  // no need to wait
    )

    // test file exist
    fExist2(
        params.file_name,
        'exist',
        gFile2.out.file.collect(),
        true  // no need to wait
    )

    // perform cleanup in gFile1 workdir
    cleanupWorkdir(
        gFile1.out.collect(),
        fExist1.out.collect()  // flag enables waiting for fExist1 before cleaning up gFile1 workdir
    )

    // test cleaned up workdir from gFile1 indeed does not have previous files
    fExist3(
        gFile1.out.collect(),
        'not_exist',
        gFile1.out.collect(),
        cleanupWorkdir.out  // wait for cleanup is done
    )

    // test not cleaned up workdir from gFile2 indeed still have the exptected files
    fExist4(
        gFile2.out.collect(),
        'exist',
        gFile2.out.collect(),
        cleanupWorkdir.out  // wait for cleanup is done
    )
}
