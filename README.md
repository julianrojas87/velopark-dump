# velopark-dump
Python script to download Velopark's parkings of a certain region ([NIS code](https://en.wikipedia.org/wiki/NIS_code)) into a CSV file.

## Install it

This script uses the [`rdflib`](https://github.com/RDFLib/rdflib) library and its plugin to read JSON-LD [`rdflib-jsonld`](https://github.com/RDFLib/rdflib-jsonld). Install them as follows:

```bash
pip install rdflib
pip install rdflib-jsonld
```

## Use it

Execute the script with the NIS code of the region from which you want to download the parkings. For example to get all the parkings in the regions of East Flanders do:

```bash
python velopark_dump.py 40000
```
