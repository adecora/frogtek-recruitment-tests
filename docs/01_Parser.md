[Home](../README.md) \| [Siguiente (2 Generar eventos de empresas)](02_Generate_events.md)

# 1 Parser TSV mal formateado

En el primer ejercicio propuesto recibimos un fichero `tsv` con codificación `UTF16LE` que viene mal formateado.

Antes de empezar a desarrollar el parser, vamos a bichear la estructura del fichero.

```bash
# Cabecera del fichero
$ iconv -f UTF16LE -t UTF8 data/data.tsv | head -5
id      first_name      last_name       account_number  email
1       Addison Marks   196296  ornare.lectus@et.edu
2       Dakota  Garza   409025  scelerisque@Praesentluctus.edu
3       Basia   Wolfe   637720  Aliquam@nullaIntegerurna.com
4       Germaine        Campbell        826846  id.magna@viverraMaecenas.ca

# Algunas de las casuísticas que vamos a afrontar para parsear el fichero, 
# utilizamos `bat -A` para tener una visión más bonita de los caracteres no imprimibles
# (tmbn se podría usar `cat -A`)
$ iconv -f UTF16LE -t UTF8 data/data.tsv | \
sed -n -e '29,33p' -e '71p' -e '74p' -e '85,87p' -e '207p' -e '619p' | \
bat -A
───────┬─────────────────────────────────────────────────────────────────────────────────────
       │ STDIN
───────┼─────────────────────────────────────────────────────────────────────────────────────
   1   │ 28├──┤Ivory├──┤Downs├──┤133677├──┤sem@sed.ca␊
   2   │ 29├──┤Adena├──┤Hobbs␊
   3   │ Bosley├──┤656184␊
   4   │ ├──┤ac.ipsum.Phasellus@ut.net␊
   5   │ 30├──┤Laura├──┤Rivera├──┤270464├──┤nascetur.ridiculus.mus@Donecnibhenim.org␊
   6   │ 68├──┤Shelley├──┤Mccormick••••••••├──┤326352├──┤Duis.gravida@actellus.edu␊
   7   │ 71├──┤Kay\u{c8}├──┤Noel├──┤464972├──┤Aenean.massa.Integer@anteMaecenasmi.co.uk␊
   8   │ 82├──┤Jade├──┤Battle␊
   9   │ •••••├──┤531695├──┤lectus.justo@lorem.co.uk␊
  10   │ 83├──┤Nevada├──┤black├──┤504965├──┤enim.condimentum@a.net␊
  11   │ 203├──┤Deirdr\u{c8}├──┤Franco├──┤998247├──┤Fusce.mollis.Duis@urna.com␊
  12   │ 613├──┤├──┤├──┤104969├──┤dictum@Suspendisse.net␊
───────┴─────────────────────────────────────────────────────────────────────────────────────
```

Vamos a tener que afrontar columnas que contienen: caracteres especiales `(\n\t\r)`[^1], campos vacíos... el fichero [bin/parser.py](../bin/parser.py) utiliza un `regex` para capturar las filas del `tsv` mal formateadas. Actúa sobre el fichero completo o un fragmento indicado **(con posición y longitud)** (en el caso de un fragmento devuelve sólo las filas completas que encuentra) e imprime el resultado por pantalla, lo rediccionaremos a un fichero de salida.

[^1]: Python trabaja con [universal newlines](https://docs.python.org/3/glossary.html#term-universal-newlines)

El fichero [bin/test_tsv.py](../bin/test_tsv.py) valida que los ficheros generado con el **parser** puedan ser leídos correctamente por un parser estándar de [CSV](https://docs.python.org/3/library/csv.html#module-csv).

```bash
# El fichero generado va a estar en formato UTF8, lo comprobamos
$ python -c 'import sys; print(sys.getdefaultencoding())'
utf-8

$ ./bin/parser.py --help
usage: parser.py [-h] [-p POSITION] [-l LENGTH] filename

Convierte fichero TSV mal formateado

positional arguments:
  filename              Fichero TSV mal formateado (codificación=UTF16LE)

optional arguments:
  -h, --help            show this help message and exit
  -p POSITION, --position POSITION
                        Omite N caracteres desde el inicio
  -l LENGTH, --length LENGTH
                        lectura de N caracteres

$ ./bin/parser.py data/data.tsv > results/fix.tsv
$ file -i results/fix.tsv
results/fix.tsv: text/plain; charset=utf-8

$ head -5 results/fix.tsv | bat -A
───────┼─────────────────────────────────────────────────────────────────────────────────────
       │ STDIN
───────┼─────────────────────────────────────────────────────────────────────────────────────
   1   │ id├──┤first_name├──┤last_name├──┤account_number├──┤email␊
   2   │ 1├──┤'Addison'├──┤'Marks'├──┤'196296'├──┤'ornare.lectus@et.edu'␊
   3   │ 2├──┤'Dakota'├──┤'Garza'├──┤'409025'├──┤'scelerisque@Praesentluctus.edu'␊
   4   │ 3├──┤'Basia'├──┤'Wolfe'├──┤'637720'├──┤'Aliquam@nullaIntegerurna.com'␊
   5   │ 4├──┤'Germaine'├──┤'Campbell'├──┤'826846'├──┤'id.magna@viverraMaecenas.ca'␊
───────┴─────────────────────────────────────────────────────────────────────────────────────

$ ./bin/parser.py data/data.tsv --position 1200 --length 200
24       'Quincy'        'Buckner'       '676034'        'velit@nislelementum.co.uk'
25      'Lee'   'Vance' '874024'        'lorem@nonummyultriciesornare.co.uk'

$ ./bin/test_tsv.py
.
----------------------------------------------------------------------
Ran 1 test in 0.066s

OK
```

### Curiosidades

A la hora de computar la longitud del fichero original hay un desfase de dos caracteres entre el resultado `cli` y el resultado `python`.

```python
# file-len.py
with open('data/data.tsv', encoding='utf_16le') as f:
    text = f.read()
    print(len(text))
```

```bash
$ iconv -f UTF16LE -t UTF8 data/data.tsv | wc -c
53447

$ python file-test.py
53445
```

Qué pasa con esos dos caracteres? Hay dos filas **71** y **203** en las que la columna **first_name** tiene un carácter `Unicode`, que puede representarse de dos formas distintas.
Algunas letras como la "ñ" pueden representarse como único punto de código U+00F1 representación `NFC`, o como, U+006E U+0303, que es un punto de código para "n" seguido de un punto de código para 'CAREACTER ESPECIAL TILDE' representación `NFD`. Estos producen la misma salida cuando se imprimen, pero uno es una cadena de longitud 1 y el otro una cadena de longitud 2 [Unicode doc](https://docs.python.org/3/howto/unicode.html#the-string-type).


```python
# unicode-test.py
import re
import unicodedata

text = f.read()
    words = re.split('\s', text)
    print(f'{"Palabra":>8s} {"NFD":>12} {"NFC":>15s}')
    print('-'*37)
    for w in words:
        if w != unicodedata.normalize('NFD', w):
            nfd = unicodedata.normalize('NFD', w)
            print(f'{w:>8s} {ascii(w):>12} {ascii(nfd):>15s}')
w = 'ñ'
nfd = unicodedata.normalize('NFD', w)
print(f'{w:>8s} {ascii(w):>12} {ascii(nfd):>15s}')
```

```bash
$ python unicode-test.py
 Palabra          NFD             NFC
-------------------------------------
    KayÈ    'Kay\xc8'    'KayE\u0300'
 DeirdrÈ 'Deirdr\xc8' 'DeirdrE\u0300'
       ñ       '\xf1'       'n\u0303'

# Ilustramos con un ejemplo sencillo como la ñ
$ unicode 0xF1  
U+00F1 LATIN SMALL LETTER N WITH TILDE
UTF-8: c3 b1 UTF-16BE: 00f1 Decimal: &#241; Octal: \0361
ñ (Ñ)
Uppercase: 00D1
Category: Ll (Letter, Lowercase); East Asian width: N (neutral)
Unicode block: 0080..00FF; Latin-1 Supplement
Bidi: L (Left-to-Right)

Decomposition: 006E 0303


$ unicode U0303 
U+0303 COMBINING TILDE
UTF-8: cc 83 UTF-16BE: 0303 Decimal: &#771; Octal: \01403
 ̃
Category: Mn (Mark, Non-Spacing); East Asian width: A (ambiguous)
Unicode block: 0300..036F; Combining Diacritical Marks
Bidi: NSM (Non-Spacing Mark)

Combining: 230 (Above)
```

[Home](../README.md) \| [Siguiente (2 Generar eventos de empresas)](02_Generate_events.md)