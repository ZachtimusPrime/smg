# serverless-migrator
A cli tool to convert pre-existing lambda functions to the serverless framework. The files generated are structured to allow you to easily set up configurations for the overall project as well as each individual function for as many environments as are needed.

## Currently Supported Clouds
* Amazon Web Services (AWS)

## Currently Supported Program Languages
* Python
* Node.js

## Installation
```sh
pip install -e git+https://github.com/ZachtimusPrime/smg.git@master#egg=smg\&subdirectory=cli
```

## Project Structure Assumptions
Smg makes the following assumptions when generating the necessary serverless files:
* Python lambda files follow the naming of their parent folder with _lmbd appended
* Python lambda main function is named lambda_handler
* Nodejs lambda files are named index
* Nodejs lambda main function is named handler

You can find an example of the project structure [here](https://github.com/ZachtimusPrime/smg/tree/master/example-migration-project). Of course, you are free to change any of this as you see fit once the files are generated. Just know what you're doing.

## Usage 
```sh
# migrate cwd
smg migrate2aws

# migrate specific dir
smg migrate2aws -p <path-to-project>
```