#!/usr/bin/env python
import glob
import time
import json
import os
from functools import wraps
from collections import Counter
import signal

def signal_handling(signum, frame):
    '''
    Para cortar menos bruscamente el programa.
    '''
    raise SystemExit(f'Pechamos stream de ficheros amistosamente')

def stream(dirname, target):
    '''
    Stremea solo los nuevos fichero añadidos al directorio.
    '''
    file_cache = set()
    while True:
        for file in glob.glob(f'{dirname}/*.json'):
            if file not in file_cache:
                file_cache.add(file)
                target.send(file)
        time.sleep(5)

# Decorador que inicializa las corutinas, enviando primero send(None)
def consumer(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        f = func(*args, **kwargs)
        f.send(None)
        return f
    return wrapper

def receive(expected_type):
    msg = yield
    assert isinstance(msg, expected_type), f'Expected type {expected_type}'
    return msg

@consumer
def create_tuple(field, target):
    '''
    Lee un fichero lo parsea los campos para convertirlo un objeto python
    y lo filtra for el campo field.
    '''
    while True:
        file = yield from receive(str)
        with open(file) as f:
            lines = f.read().strip().split('\n')
            lines_tuple = tuple(json.loads(l)[field] for l in lines)
            target.send(lines_tuple)

@consumer
def create_counter(target):
    '''
    Mantiene un contador con los campos recibidos.
    '''
    counter = Counter()
    while True:
        fields = yield from receive(tuple)
        counter.update(fields)
        target.send(counter)

@consumer
def printer():
    '''
    Limpia la pantalla e imprime el contador.
    '''
    while True:
        counter = yield from receive(Counter)
        os.system('clear||cls')
        for k, v in counter.items():
            print(f'"{k}": {v}')


if __name__ == '__main__':
    import sys
    signal.signal(signal.SIGINT, signal_handling)
    if len(sys.argv) != 2:
        raise SystemExit(f'Uso: {sys.argv[0]} dirname')
    stream(sys.argv[1], 
        create_tuple('Type',
        create_counter(
        printer())))