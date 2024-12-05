[Home](../README.md) \| [Anterior (1 Parser TSV mal formateado](01_Parser.md) \| [Siguiente (3 Monitoreador de eventos)](03_Stream_app.md)

# 2 Generador de eventos

Cuatro de cada cinco eventos generados han de ser `OrderAccepted` mientras que el quinto `OrderCancelled`. Podemos llegar al mismo resultado de varias formas:

- **random:** Un `80%` de las órdenes generadas serán `OrderAccepted`, con `random` generamos un valor aproximado.
- **closure:** El **closure** llevará la cuenta de las órdenes generadas, si es menor que cuatro generamos una orden `OrderAccepted` si no una `OrderCancelled` y reiniciamos.
- **número orden:** Si llevamos el control del número de orden odemos generarla el tipo como `'OrderCancelled' if order_no % 5 == 0 else 'OrderAccepted'`.

```python
# random.py
from random import random

def rand():
    if random() <= 0.8:
        return 'OrderAccepted'
    else:
        return 'OrderCancelled'

for i in range(1000):
    print(rand())
```

```python
# closure.py
def closure():
    order=1

    def do_rand():
        nonlocal order
        if order <= 4:
            order += 1
            return 'OrderAccepted'
        else:
            order=1
            return 'OrderCancelled'
    
    return do_rand

rand = closure()

for i in range(1000):
    print(rand())
```

```bash
# Generamos mil órdenes con ambas aproximaciones
$ python random.py > random
$ python closure.py > closure

# Comprobamos que con random obtenemos un porcentaje aproximado al 80% 
# y con closure el porcentaje exacto
$ sort random | uniq -c | \
awk '{arr[NR]=$1; print} END{per=arr[1]/(arr[1]+arr[2]); print "porcentaje:",per}'
    798 OrderAccepted
    202 OrderCancelled
porcentaje: 0.798
$ sort closure | uniq -c | \
awk '{arr[NR]=$1; print} END{per=arr[1]/(arr[1]+arr[2]); print "porcentaje:",per}'
    800 OrderAccepted
    200 OrderCancelled
porcentaje: 0.8
```

La descripción del ejercicio parece indicar que la generación de órdenes tiene que ser exactamente la indicada, así que no implementaremos la que usa `random`.

Para la **escritura de los ficheros de eventos**, se puede optar por escribir todo el fichero completo o por fragmentos **p. ej.** línea a línea. Lo segundo implica más `llamadas al sistema` y por tanto más lentitud, pero menor consumo de memoria.

```python
# write_file.py
import json

file = [
    json.dumps({ "Type": "OrderPlaced", "Data": { "OrderId": "3cb0f939-9398-4d29-a28f-2a1a3a6ce3b2", "TimestampUtc": "2017-05-14T19:12:32Z" }}) 
] * 500

def write_file():
    with open('file.json', 'w') as f:
        f.write('\n'.join(file) + '\n')
```

```python
# write_lines.py
import json

file = [
    json.dumps({ "Type": "OrderPlaced", "Data": { "OrderId": "3cb0f939-9398-4d29-a28f-2a1a3a6ce3b2", "TimestampUtc": "2017-05-14T19:12:32Z" }}) 
] * 500

def write_lines():
    with open('file.json', 'w') as f:
        for line in file:
            f.write(line + '\n')
```

```bash
$ strace python write_file.py 2>&1 | egrep '^write'
write(3, "{\"Type\": \"OrderPlaced\", \"Data\": "..., 62500) = 62500

$ strace python write_lines.py 2>&1 | egrep '^write'
write(3, "{\"Type\": \"OrderPlaced\", \"Data\": "..., 8125) = 8125
write(3, "{\"Type\": \"OrderPlaced\", \"Data\": "..., 8125) = 8125
write(3, "{\"Type\": \"OrderPlaced\", \"Data\": "..., 8125) = 8125
write(3, "{\"Type\": \"OrderPlaced\", \"Data\": "..., 8125) = 8125
write(3, "{\"Type\": \"OrderPlaced\", \"Data\": "..., 8125) = 8125
write(3, "{\"Type\": \"OrderPlaced\", \"Data\": "..., 8125) = 8125
write(3, "{\"Type\": \"OrderPlaced\", \"Data\": "..., 8125) = 8125
write(3, "{\"Type\": \"OrderPlaced\", \"Data\": "..., 5625) = 5625
```

Para tamaños de fichero de **5000** líneas, la diferencia memoria/tiempo es insignificante. Para ficheros de mayor tamaño **p. ej.** **5000000** la diferencia se empieza a apreciar, la solución a implementar debería ser un consenso entre nuestro objetivo, es relevante para el cliente que los ficheros tarden **8s** en generase en vez de **2s**?, y los recursos de los que disponemos en producción, podemos asumir el coste del consumo de resursos que supone mejorar en **6s** el proceso?

```python
# test_write.py
import json
import tracemalloc
import time
from functools import wraps

def timethis(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        r = func(*args, **kwargs)
        end = time.perf_counter()
        print('{}.{} : {}'.format(func.__module__, func.__name__, end - start))
        return r
    return wrapper

@timethis
def write_file(file):
    with open('file.json', 'w') as f:
        f.write('\n'.join(file) + '\n')

@timethis
def write_lines(file):
    with open('file.json', 'w') as f:
        for line in file:
            f.write(line + '\n')

def main(length):
    file = [
        json.dumps({ "Type": "OrderPlaced", "Data": { "OrderId": "3cb0f939-9398-4d29-a28f-2a1a3a6ce3b2", "TimestampUtc": "2017-05-14T19:12:32Z" }}) 
    ] * length
    tracemalloc.start()
    write_file(file)
    print('Uso de memoria: Actual {0:,d}, Pico {1}'.format(*tracemalloc.get_traced_memory()))
    tracemalloc.clear_traces()
    write_lines(file)
    print('Uso de memoria: Actual {0}, Pico {1}'.format(*tracemalloc.get_traced_memory()))


if __name__ == '__main__':
    import sys
    if len(sys.argv) != 2:
        raise SystemExit(f'Uso: {sys.argv[0]} [tamaño del fichero]')
    main(int(sys.argv[1]))
```

```bash
$ python test_write.py 5000
__main__.write_file : 0.001222284001414664
Uso de memoria: Actual 1,099, Pico 1256214
__main__.write_lines : 0.014595100990845822
Uso de memoria: Actual 547, Pico 25602

$ python test_write.py 5000000
__main__.write_file : 1.9387746319989674
Uso de memoria: Actual 1,099, Pico 1250006214
__main__.write_lines : 7.072099522993085
Uso de memoria: Actual 547, Pico 25602
```

Dado que no hay ninguna indicación al respecto en el enunciado del ejercicio, optamos por escribir el fichero completo, la solución propuesta es [bin/generate_events.py](../bin/generate_events.py).

```bash
$ ./bin/generate_events.py --help                        
usage: generate_events.py [-h] -n 1000000 -b 5000 -i 1 -d <local-dir>

Convierte fichero TSV mal formateado

optional arguments:
  -h, --help            Imprime este mensaje de ayuda y sale.
  -n 1000000, --number-of-orders 1000000
                        Número de ordenes generadas (cada orden produce dos eventos)
  -b 5000, --batch-size 5000
                        Número de eventos por archivo
  -i 1, --interval 1    Intervalo en segundos entre la creación de los ficheros
  -d <local-dir>, --output-directory <local-dir>
                        Directorio de salida,para guardar los ficheros generados

$ ./bin/generate_events.py -n 1000 -b 320 -i 1 -d results 
Generando fichero: results/orders-2024-12-04-19-06-55-668769.json
Durmiendo 1 segundo
Generando fichero: results/orders-2024-12-04-19-06-56-677025.json
Durmiendo 1 segundo
Generando fichero: results/orders-2024-12-04-19-06-57-684806.json
Durmiendo 1 segundo
Generando fichero: results/orders-2024-12-04-19-06-58-692353.json
Durmiendo 1 segundo
Generando fichero: results/orders-2024-12-04-19-06-59-699411.json
Durmiendo 1 segundo
Generando fichero: results/orders-2024-12-04-19-07-00-707296.json
Durmiendo 1 segundo
Generando fichero: results/orders-2024-12-04-19-07-01-719001.json

$ wc -l results/*.json                                   
   320 results/orders-2024-12-04-19-06-55-668769.json
   320 results/orders-2024-12-04-19-06-56-677025.json
   320 results/orders-2024-12-04-19-06-57-684806.json
   320 results/orders-2024-12-04-19-06-58-692353.json
   320 results/orders-2024-12-04-19-06-59-699411.json
   320 results/orders-2024-12-04-19-07-00-707296.json
    80 results/orders-2024-12-04-19-07-01-719001.json
  2000 total
```

[Home](../README.md) \| [Anterior (1 Parser TSV mal formateado](01_Parser.md) \| [Siguiente (3 Monitoreador de eventos)](03_Stream_app.md)