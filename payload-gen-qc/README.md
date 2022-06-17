# Nextflow Package `payload-gen-qc`

A simple wrapper written in `nextflow` for the payload generation tool to generate ARGO Song payloads containing QC metrics files.  

## Package development

The initial version of this package was created by the WorkFlow Package Manager CLI tool, please refer to
the [documentation](https://wfpm.readthedocs.io) for details on the development procedure including
versioning, updating, CI testing and releasing.


## Inputs
### Required
- `files_to_upload`: All files to upload
- `metadata_analysis`: JSON file contains donor/sample/specimen/experiment/read_groups/files metadata for input data
- `wf_name`: Workflow name
- `wf_version`: Workflow version

### Optional
- `genome_annotation`: Genome annotation version
- `genome_build`: Genome build version
- `cpus`: Set cpu number for running the tool
- `mem`: Set memory(G) for running the tool
- `publish_dir`: Specify directory for getting output files

## Outputs
- `payload`: Payload contains metadata
- `files_to_upload`: All files to upload with normalized name convention 

## Usage

### Run the package directly

With inputs prepared, you should be able to run the package directly using the following command.
Please replace the params file with a real one (with all required parameters and input files). Example
params file(s) can be found in the `tests` folder.

```
nextflow run icgc-argo-workflows/data-processing-utility-tools/payload-gen-qc/main.nf -r payload-gen-qc.v0.1.0 -params-file <your-params-json-file>
```

### Import the package as a dependency

To import this package into another package as a dependency, please follow these steps at the
importing package side:

1. add this package's URI `github.com/icgc-argo-workflows/data-processing-utility-tools/payload-gen-qc@0.1.0` in the `dependencies` list of the `pkg.json` file
2. run `wfpm install` to install the dependency
3. add the `include` statement in the main Nextflow script to import the dependent package from this path: `./wfpr_modules/github.com/icgc-argo-workflows/data-processing-utility-tools/payload-gen-qc@0.1.0/main.nf`
