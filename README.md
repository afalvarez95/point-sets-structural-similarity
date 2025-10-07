# point-sets-structural-similarity

This repo includes all the companion files for... (TODO)

## Installation guide

In order to use this code, is it recommended to have Docker installed, as the docker compose file has all the required commands to setup a sandbox with the necessary Python and video generation libraries. Using the standalone Jupyter file is possible provided that the host machine has all the necessary python libraries and video generation libraries; although this has not been tested at the moment. Thus, this installation guide will suppose you use Docker.

1) Make sure you have Docker (https://www.docker.com/) installed in your computer and also opened.
2) Clone this repository or download it as zip and extract it.
3) Open the command line in the base folder and perform ``docker build .`` to install it for the first time. Then ``docker compose up`` (where the docker compose file is located). You may wait a little, as this allows Docker to create and setup the project and the Jupyter container. Alternatively, for Windows users, a bat file called ``docker-run.bat`` is included so you can click it to initialize the docker container without opening the command line. Note that docker should be opened before for the commands to work. The bat file will end immediately if Docker is not opened.
4) The command line will finally prompt you with a localhost (127.0.0.1) link where you can access a Jupyter instance where you can connect to a Jupyter notebook from the container with the project's kernel.


## File tree

```
point-sets-structural-similarity
├── src                   -> Where the code is stored. Includes an example Jupyter notebook to generate tests files.
├── tests                 -> Where all the tests are included. Subfolders follow the pattern: test_<timestamp>/<S<seed>_T<translation>_R<rotation>.
    └── test_<timestamp>  -> A generated test folder.
        └── S<seed>_T<translation>_R<rotation> -> A folder with the assets of an example with a given numpy seed, and a translation and rotation performed to the second point set.
├── Dockerfile            -> Dockerfile with the necessary jupyter container commands.
├── docker-compose.yml   -> Docker compose file.
├── docker-run.bat        -> Autorun docker for Windows users.
└── README.md             -> Project information.
```
