[Home](../README.md) \| [Anterior (2 Generador de eventos)](02_Generate_events.md)

# 3 Monitoreador de eventos

Creamos un pipeline con corutinas para procesar los ficheros que vamos a ir recibiendo en un directorio.

```markdown
\`\`\`mermaid
graph LR
    A[stream] -->|send#40;#41;| B[create_tuple]
    B -->|send#40;#41;| C[create_counter]
    C -->|send#40;#41;| D[printer]
\`\`\`
```

Para las corutinas utilizamos **generadores** que reciben `yield` como expresión, *estos necesitan ser inicializados enviándoles `send(None)`*.

```python
>>> def counter(n):
...     print(f'Empezamos contando desde {n}')
...     while True:
...             increment = yield
...             n += increment
...             print(n)
... 
>>> c = counter(5)
>>> c.send(None)
Empezamos contando desde 5
>>> c.send(1)
6
>>> c.send(1)
7
>>> c.send(3)
10
```

La solución propuesta es [bin/stream_app.py](../bin/stream_app.py):

```bash
# Si ejecutamos en otro terminal 
# $ ./bin/generate_events.py -n 1000 -b 320 -i 1 -d results
# los resultados se irán actualizando.
$ ./bin/stream_app.py results
"OrderPlaced": 40
"OrderAccepted": 32
"OrderCancelled": 8
```

Con esto ya estaría todo, un saludo!!!

[Home](../README.md) \| [Anterior (2 Generador de eventos)](02_Generate_events.md)