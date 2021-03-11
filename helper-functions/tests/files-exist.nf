#!/usr/bin/env nextflow

/*
 * Copyright (c) 2019-2021, Ontario Institute for Cancer Research (OICR).
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
 * Contributors:
 *   Junjun Zhang <junjun.zhang@oicr.on.ca>
 */

nextflow.enable.dsl = 2


process filesExist {
    input:
        val file_names  // file name shall not have spaces
        val expect  // 'exist' for files expected to exist; 'not_exist' for files expected not exist
        path files
        val dependency_flag  // any output from process(es) you'd like to make this process depend on

    script:
        file_name_arg = file_names instanceof List ? file_names.join(" ") : file_names
        """
        if [[ "${expect}" = "exist"  ]]; then
            for f in \$(echo "${file_name_arg}"); do
                if [[ ! -f \$f ]]; then
                    exit "Expected \$f not exists."
                fi
            done
        elif [[ "${expect}" = "not_exist"  ]]; then
            for f in \$(echo "${file_name_arg}"); do
                if [[ -f \$f ]]; then
                    exit "Unexpected \$f exists."
                fi
            done
        else
            exit "Second argument must be either 'exist' or 'not_exist'. '${expect}' is supplied."
        fi
        """
}
