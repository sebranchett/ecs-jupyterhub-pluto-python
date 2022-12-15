# Single user Pluto on JupyterLab
Inspired by [pluto-on-jupyterlab](https://github.com/pankgeorg/pluto-on-jupyterlab), used
under an [Unlicense license](https://github.com/pankgeorg/pluto-on-jupyterlab/blob/master/LICENSE).

This link was helpful:
https://jupyter-docker-stacks.readthedocs.io/en/latest/.

## Testing locally
You can check this Dockerfile locally:
```
docker build . -t local
docker run -d -p 8888:8888 --name jupyter local
<outputs a very long server hash>

docker exec -it jupyter bash
  jovyan@<shorter server hash>:~$ jupyter server list
Currently running servers:
http://<shorter server hash>:8888/?token=<long token hash> :: /home/jovyan
```

In a browser, navigate to:
```
http://localhost:8888/?token=<long token hash>
```

If you want to test your image from a JupyterHub on your laptop, [this is a good resource](https://github.com/jupyterhub/dockerspawner/tree/main/examples/simple). Note that if you are using a Windows laptop, you will need an extra slash (`/`) before the socket:


`docker run --rm -it -v `***`/`***`/var/run/docker.sock:/var/run/docker.sock --net jupyterhub --name jupyterhub -p8000:8000 hub`


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
docker tag local <ecr_repository_uri>
```

Allow Docker to access your ECR repository:

```
aws ecr get-login-password --region <region> | docker login --username AWS --password-stdin <ecr_repository_uri>
```
You should receive the message: Login Succeeded.

Push your Docker image to ECR:
```
docker push <ecr_repository_uri>