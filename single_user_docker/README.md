# Single user Pluto on JupyterLab
Inspired by [pluto-on-jupyterlab](https://github.com/pankgeorg/pluto-on-jupyterlab), used
under an [Unlicense license](https://github.com/pankgeorg/pluto-on-jupyterlab/blob/master/LICENSE).

This link was helpful:
https://jupyter-docker-stacks.readthedocs.io/en/latest/.

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
