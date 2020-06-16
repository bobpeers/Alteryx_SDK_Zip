# Alteryx SDK Tool - File Archive Extractor
Alteryx tool to extract files from compressed archives


## Installation
Download the yxi file and double click to install in Alteyrx. The tool will be installed in the __File System__ category.

![alt text](https://github.com/bobpeers/Alteryx_SDK_Data_Hash/blob/master/images/Alteryx_Category.png "Alteryx Developer Category")

## Usage
Takes the incoming mapped file path and extracts the contained files into the supplied location. By default it will not overwrite
exisiting files but this can be changed in the tools configuration.

## Outputs
Sucessful operations will be output to the O-Output. The full path to the extracted file is appended to the incoming stream.

## Example Workflow
Map the data to be hashed in the tool and select the hashing algorithm.

![alt text](https://github.com/bobpeers/Alteryx_SDK_Data_Hash/blob/master/images/Dash%20Hash%20flow.png "Exampe Alteryx Workflow")

