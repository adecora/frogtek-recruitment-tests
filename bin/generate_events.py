#!/usr/bin/env python
import argparse
from datetime import datetime
from pathlib import Path
import json
import uuid
import time

def is_path(path):
    '''
    Validación de tipo del argumento: -d --output-directory, comprueba 
    que exita el directorio.
    '''
    if Path(path).is_dir():
        return path
    else:
        raise argparse.ArgumentTypeError(f'invalid directory path: {path!r}')

def order():
    '''
    Cada cinco ordenes generamos cuatro OrderAccepted y una OrderCancelled
    '''
    order = 1
    def made_order():
        nonlocal order
        if order <= 4:
            order += 1
            return 'OrderAccepted'
        else:
            order=1
            return 'OrderCancelled'
    return made_order

get_order = order()
get_filename = lambda date: f'orders-{datetime.strftime(date, "%Y-%m-%d-%H-%M-%S-%f")}.json'

def get_event(event_no, date=datetime.now()):
    '''
    Generador de eventos uno de cada dos eventos es de tipo 'OrderPlaced',
    el otro según los indicado en `get_order()`.
    '''
    order_type = 'OrderPlaced' if (event_no % 2) == 1 else get_order()
    order_id = str(uuid.uuid4())
    timestamp = datetime.strftime(date, "%Y-%m-%dT%H:%M:%SZ")
    return json.dumps({
        "Type": order_type,
        "Data": {
            "OrderId": order_id,
            "TimestampUtc": timestamp
        }
    })
    
def generate_events(orders, batch, interval, outdir):
    '''
    Generamos los ficheros de eventos.
    '''
    # (numero de ordenes) * (2 eventos / ordern) / (eventos / fichero) 
    #   // (floor division): Número de ficheros completos con batch eventos.
    #   % (modulo): Eventos restantes (tamaño menor que batch).
    events = orders * 2
    num_files = events // batch

    event_no = 0
    for file_no in range(num_files):
        file = []
        for _ in range(batch):
            event_no += 1
            file.append(get_event(event_no))
        filename = f'{outdir}/{get_filename(datetime.now())}'
        print(f'Generando fichero: {filename}')
        with open(filename, 'w') as f:
            f.write('\n'.join(file) + '\n')
        # Si no es el último fichero duerme interval segundos
        if file_no < num_files - 1 or file_no == (num_files - 1) and events % batch:
            print(f'Durmiendo {interval} segundo{"" if interval == 1 else "s"}')
            time.sleep(interval)

    if events % batch:
        file = []
        for _ in range(1, events % batch + 1):
            event_no += 1
            file.append(get_event(event_no))
        filename = f'{outdir}/{get_filename(datetime.now())}'
        print(f'Generando fichero: {filename}')
        with open(filename, 'w') as f:
            f.write('\n'.join(file) + '\n')

def main():
    '''
    Parseo de los argumentos.
    '''
    parser = argparse.ArgumentParser(description='Convierte fichero TSV mal formateado', add_help=False)
    parser.add_argument('-h', '--help', action='help', default=argparse.SUPPRESS,
        help='Imprime este mensaje de ayuda y sale.')
    parser.add_argument('-n', '--number-of-orders', dest='orders',
        metavar='1000000', type=int, required=True,
        help='Número de ordenes generadas (cada orden produce dos eventos)')
    parser.add_argument('-b', '--batch-size', dest='batch',
        metavar='5000', type=int, required=True,
        help='Número de eventos por archivo')
    parser.add_argument('-i', '--interval', 
        metavar='1', type=int, required=True,
        help='Intervalo en segundos entre la creación de los ficheros')
    parser.add_argument('-d', '--output-directory', 
        metavar='<local-dir>', type=is_path, required=True, dest='outdir',
        help='Directorio de salida,para guardar los ficheros generados')
    args = parser.parse_args()
    
    generate_events(args.orders, args.batch, args.interval, args.outdir)


if __name__ == '__main__':
    main()