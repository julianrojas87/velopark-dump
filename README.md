# velopark-dump
Python script to download Velopark's parkings of a certain region ([NIS code](https://en.wikipedia.org/wiki/NIS_code)) into a CSV file.

## ⚠️ Disclaimer
This script creates an export of the parking data with only a subset of the properties available in the original data source, [published by Velopark](https://velopark.ilabt.imec.be/data/catalog) on the Web. This is due to having some property values as lists of objects, which in turn have multiple properties, as in the case for example of [`vp:allows`](http://velopark.ilabt.imec.be/openvelopark/vocabulary#https://velopark.ilabt.imec.be/openvelopark/vocabulary#allows). Such property value lists cannot be easily included in a simple CSV row and would need to be somehow encoded. Therefore they are not included in this export. As requested, the [`schema:openingHoursSpecification`](https://schema.org/openingHoursSpecification) has been included.

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
