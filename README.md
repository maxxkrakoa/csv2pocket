# csv2pocket

A simple tool for taking a CSV file and importing it to Pocket

## CSV format

The input rows in the CSV file can either contain 1, 2, or 3 items.

```
<url>
<url>,<title>
<url>,<title>,<tags>
```

*tags* is itself a comma separated list of tags - make sure to enclose it in
quotes to escape the commas.

See file `test.csv` for an example.
