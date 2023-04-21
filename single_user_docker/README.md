# Single user Pluto on JupyterLab

Inspired by [pluto-on-jupyterlab](https://github.com/pankgeorg/pluto-on-jupyterlab), used
under an [Unlicense license](https://github.com/pankgeorg/pluto-on-jupyterlab/blob/master/LICENSE).

This link was helpful:
https://jupyter-docker-stacks.readthedocs.io/en/latest/.

## Creating and using an ECR repository
This project assumes that you have a single user JupyterLab docker image in an Amazon Elastic Container Registry (ECR) repository. [This link](https://docs.aws.amazon.com/AmazonECR/latest/userguide/repository-create.html) explains how to create a repository and how to find the commands to upload a Docker image to it.

You can find the ARN and the URI of your repository with this command:
```
aws ecr describe-repositories
```
The ARN and URI are different; you must add the ARN to your config.yaml.

## Testing locally
You can check the single user Dockerfile locally:
```
docker build . -t single-user-jupyterlab-pluto
docker run --rm -it -p 8888:8888 single-user-jupyterlab-pluto
```

In a browser, navigate to one of the URLs in the output of the last command.

If you are a Windows GitBash user and you get messages from the daemon about your path, then try setting the [environment variable MSYS_NO_PATHCONV=1](https://github.com/docker/cli/issues/2204#issuecomment-638993192).

If you want to test your image from a JupyterHub on your laptop, [this is a good resource](https://github.com/jupyterhub/dockerspawner/tree/main/examples/simple). Note that if you are using a Windows laptop, you will need an extra slash (`/`) before the socket:


`docker run --rm -it -v `***`/`***`/var/run/docker.sock:/var/run/docker.sock --net jupyterhub --name jupyterhub -p8000:8000 hub`

Or try setting the [environment variable MSYS_NO_PATHCONV=1](https://github.com/docker/cli/issues/2204#issuecomment-638993192).
