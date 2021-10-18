# README

Se necesita pymongo y Flask instalado, aunque el pipfile debiera solucionarlo por si solo.

Para correr el servidor con Flask que maneja la API, desde pymongo a nuestra base de datos mongodb:

Desde la consola:
- `pipenv shell`
- `python main.py` 

En caso que el `pipfile` **NO** funciona correctamente, el _troubleshoot_ sería:

- tener `python 3.7.x` instalado
- tener Flask y Pymongo instalado
- correr `python main.py` en consola