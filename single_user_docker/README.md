# Single user Pluto on JupyterLab
Inspired by [pluto-on-jupyterlab](https://github.com/pankgeorg/pluto-on-jupyterlab), used
under an [Unlicense license](https://github.com/pankgeorg/pluto-on-jupyterlab/blob/master/LICENSE).

This link was helpful:
https://jupyter-docker-stacks.readthedocs.io/en/latest/.

## Testing locally
You can check this Dockerfile locally:
```
docker build . -t single-user-jupyterlab-pluto
docker run --rm -it -p 8888:8888 single-user-jupyterlab-pluto
```

In a browser, navigate to one of the URLs in the output of the last command.

If you are a Windows GitBash user and you get messages from the daemon about your path, then try setting the [environment variable MSYS_NO_PATHCONV=1](https://github.com/docker/cli/issues/2204#issuecomment-638993192).

If you want to test your image from a JupyterHub on your laptop, [this is a good resource](https://github.com/jupyterhub/dockerspawner/tree/main/examples/simple). Note that if you are using a Windows laptop, you will need an extra slash (`/`) before the socket:


`docker run --rm -it -v `***`/`***`/var/run/docker.sock:/var/run/docker.sock --net jupyterhub --name jupyterhub -p8000:8000 hub`

Or try setting the [environment variable MSYS_NO_PATHCONV=1](https://github.com/docker/cli/issues/2204#issuecomment-638993192).

## Uploading the image
Once you are happy with the Docker image, you can upload it to AWS ECR in the same way as for the JupyterHub Docker image:

First make sure you are logged into you AWS account.

Create an ECR repository:
```
aws ecr create-repository --repository-name <repo_name>
```
`<repo_name>` could be 'single-user-jupyterlab-pluto', for example.

Find the URI of your repository:
```
aws ecr describe-repositories
```

Give the image a tag for the ECR repository:
```
docker tag single-user-jupyterlab-pluto <ecr_repository_uri>
```

Allow Docker to access your ECR repository:

```
aws ecr get-login-password --region <region> | docker login --username AWS --password-stdin <ecr_repository_uri>
```
You should receive the message: Login Succeeded.

Push your Docker image to ECR:
```
docker push <ecr_repository_uri>
