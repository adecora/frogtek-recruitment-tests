#!/usr/bin/env python
import argparse
import re

# Creamos los grupos de captura, para generar el patrón
DELIMITER='\t'
ID = r'(?P<ID>\d{1,4})'
FIRST_NAME = r'(?P<FIRST_NAME>[\w\s]+)?'
LAST_NAME = r'(?P<LAST_NAME>[\w\s-]+)?'
ACCOUNT = r'(?P<ACCOUNT>[\d\s/-]*)'
EMAIL = r'(?P<EMAIL>[\w\s\.-]*@\w*\.\w{2,3}(?:\.\w{2})?\s?)\n'
pattern = re.compile(DELIMITER.join([ID, FIRST_NAME, LAST_NAME, ACCOUNT, EMAIL]))

# Formato de salida de los campos formateados.
#   - ID: Número de fila, se representa como número, los campos vienen bien formateados
#   - FIRST_NAME: Nombre, dado que los campos pueden tener caracteres especiales (e.g. `\t`, `\r`, `\n`) 
#       se utiliza formato de representación para escaparlos.
#   - LAST_NAME: Apellido, dado que los campos pueden tener caracteres especiales (e.g. `\t`, `\r`, `\n`) 
#       se utiliza formato de representación para escaparlos.
#   - ACCOUNT: Cuenta, casi la totalidad son cuentas de 6 dígitos numéricas, pero alguna de la cuentas
#       utilizan otros formatos:
#                           454-586
#                           437/680
#                           168-722
#                           865-008
#                           357-130
#                           1181-61
#                           93128
#                           75182
#       Para mantener la cohenrencia se utiliza el formato de representación de cadenas.
#   - EMAIL: Email, se utiliza el formato de representación de cadenas para mantener la coherencia
#       aunque no sea necesario escapar caracteres especiales.
#
#   ** Las columnas FIRST_NAME y LAST_NAME vienen vacías en algún caso, se representan como cadena
#       vacía ''.
formats = [int, repr, repr, repr, repr]

def parse_bad_tsv(csv_file, formats, position, length):
    '''
    Parseamos el fichero TSV mal formado y los mandamos a stdout, 
    para que pueda ser redireccionado desde cli
    '''
    if position is None or position == 0:
       # Si la lectura comienza desde el principio, leemos las cabeceras y actualizamos length
       # en caso que sea necesario
       header = csv_file.readline().strip()
       if length is not None:
           length = length - csv_file.tell()
       print(header)
    
    text = csv_file.read()

    # Creamos el slice de la porción del texto que vamos a pasear.
    s = slice(position, length if length is None else length + position)    
    text = text[s]
    
    for r in pattern.finditer(text):
        # Leemos los grupos de captura (ID, FIRST_NAME, LAST_NAME, ACCOUNT, EMAIL)
        # Parseamos los grupos de captura vacios None a cadena vacía '' solo
        # ocurre en FIRST_NAME y LAST_NAME pero comprobamos todas las columnas por comodidad
        # Aplicamos el formato correcto TSV para imprimir el resultado por stdout.
        row = r.groups()
        row = ['' if r is None else r for r in row]
        row = [func(val.strip()) for func, val in zip(formats, row)]
        print(*row, sep=DELIMITER)     

def main():
    '''
    Hacemos un parseo de los argumentos sin muchas florituras.
    '''
    parser = argparse.ArgumentParser(description='Convierte fichero TSV mal formateado')
    parser.add_argument(dest='filename', type=argparse.FileType('r', encoding='utf_16le'),
        help='Fichero TSV mal formateado (codificación=UTF16LE)')
    parser.add_argument('-p', '--position', type=int,
        help='Omite N caracteres desde el inicio')
    parser.add_argument('-l', '--length', type=int,
        help='lectura de N caracteres')
    args = parser.parse_args()
    parse_bad_tsv(args.filename, formats, args.position, args.length)


if __name__ == '__main__':
    main()