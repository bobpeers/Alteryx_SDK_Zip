# Alteryx SDK Tool - Compressed File Extractor
Alteryx tool to extract files from compressed archives


## Installation
Download the yxi file and double click to install in Alteyrx. The tool will be installed in the __File System__ category.

![alt text](https://github.com/bobpeers/Alteryx_SDK_Zip/blob/master/images/AlteryxCategory.png "Alteryx Developer Category")

## Usage
Takes the incoming mapped file path and extracts the contained files into the supplied location. By default it will not overwrite
exisiting files but this can be changed in the tools configuration.

## Outputs
Sucessful operations will be output to the O-Output. The full path to the extracted file is appended to the incoming stream.
If there are no compressed files fed into the tool there will be no output.

## Example Workflow
Map the filepath in the tool configuration and set the extraction path and overwrite options.

![alt text](https://github.com/bobpeers/Alteryx_SDK_Zip/blob/master/images/Zip_example_workflow.png "Exampe Alteryx Workflow")

