# JupyterHub docker image

## Creating and using an ECR repository
This project assumes that you have a JupyterHub docker image in an Amazon Elastic Container Registry (ECR) repository. [This link](https://docs.aws.amazon.com/AmazonECR/latest/userguide/repository-create.html) explains how to create a repository and how to find the commands to upload a Docker image to it.

You can find the ARN and the URI of your repository with this command:
```
aws ecr describe-repositories
```
The ARN and URI are different; you must add the ARN to your config.yaml.

## Add admin user(s) and allowed users
The file `admin` should contain the JupyterHub administrator user names, one per line.

The file `allowed_users` should contain the user names, one per line, of all non-admin user who are allowed to access JupyterHub.

Please [read this](https://jupyterhub.readthedocs.io/en/stable/getting-started/authenticators-users-basics.html#authentication-and-user-basics) for explanation and warnings.

## Notes to future self
I decided to use `preferred_username` as the `OAUTH_LOGIN_USERNAME_KEY`. The JupyterHub file system cannot create users' home directories with `@` or `.` in the name. Custom home directories replace these characters with `_`. Non-TU Delft users are created before `OAUTH`, so their username(, home directory) and `preferred_username` should be the same and not have difficult characters.

Users are passed in environmental variables. If you want to create a Cognito group of users and do the administration from there, be aware that Cognito passes group information in the ACCESS token and Jupyter looks for group membership in the USERDATA_URL. Also, do not forget to create persistent storage for the users.
