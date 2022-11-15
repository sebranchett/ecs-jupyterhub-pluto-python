# Build a JupyterHub docker image

This project assumes that you have a JupyterHub docker image in an Amazon Elastic Container Registry (ECR) repository.
Here is one way to set this up, from the command line of your local computer.
For more details, see [this freeCodeCamp article](https://www.freecodecamp.org/news/build-and-push-docker-images-to-aws-ecr/).

## Set up an ECR repository
First make sure you are logged into you AWS account.

You can create an ECR repository with this command:
```
aws ecr create-repository --repository-name <repo_name>
```
`<repo_name>` could be 'serverless-hub', for example.

You can find the ARN and the URI of your repository with this command:
```
aws ecr describe-repositories
```
The ARN and URI are different and you will need both: the URI is used here; the ARN is used in your config.yaml.

## Add admin user(s) and allowed users
The file `admin` should contain the JupyterHub administrator user names, one per line.

The file `allowed_users` should contain the user names, one per line, of all non-admin user who are allowed to access JupyterHub.

Please [read this](https://jupyterhub.readthedocs.io/en/stable/getting-started/authenticators-users-basics.html#authentication-and-user-basics) for explanation and warnings.

## Build and tag the Docker image
Make sure your Docker Desktop is active and then build and tag an image:
```
docker build -t <your_username>/<serverless_hub>:<version_number> .
```
Now give it a tag for the ECR repository:
```
docker tag <your_username>/<serverless_hub>:<version_number> <ecr_repository_uri>
```

## Connect Docker to your AWS account
Please [see here for temporary authentication details](https://awscli.amazonaws.com/v2/documentation/api/latest/reference/ecr/get-login-password.html).

Use this command to get temporary login credentials from AWS, and use them to allow Docker to access your ECR repository:

```
aws ecr get-login-password --region <region> | docker login --username AWS --password-stdin <ecr_repository_uri>
```
You should receive the message: Login Succeeded.

You can now push your Docker image to ECR as follows:
```
docker push <ecr_repository_uri>
```

## Next time
If you want to update the Docker image you use for JupyterHub, you can copy and paste the 4 commands you need by opening the ECR management console, selecting your repository and clicking on 'View push commands'.

## Notes to future self
I decided to use `preferred_username` as the `OAUTH_LOGIN_USERNAME_KEY`. The JupyterHub file system cannot create users' home directories with `@` or `.` in the name. Custom home directories replace these characters with `_`. Admin users are created before `OAUTH`, so their username(, home directory) and `preferred_username` should be the same and not have difficult characters.

The allowed_users are passed in an environmental variable. I wanted to create a Cognito group of allowed users and do the administration from there. Unfortunately, Cognito passes the group information in the ACCESS token and Jupyter looks for group membership in the USERDATA_URL.
