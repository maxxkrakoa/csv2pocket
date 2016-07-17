# csv2pocket

A simple tool for taking a CSV file and importing it to Pocket

## CSV format

The input rows in the CSV file can either contain 1, 2, or 3 items.

```shell
<url>
<url>,<title>
<url>,<title>,<tags>
```

*tags* is itself a comma separated list of tags - make sure to enclose it in
quotes to escape the commas.

See file `test.csv` for an example.

## Running

### Example

```shell
csv2pocket.py test.csv
```

### All command line options

```shell
usage: csv2pocket.py [-h] csv_file_name

A simple tool for taking a CSV file and importing it to Pocket

positional arguments:
  csv_file_name  the CSV file to read from

optional arguments:
  -h, --help     show this help message and exit
```

## Releases

### 1.0.1

-   Use bulk add to prevent rate limiting. Requires re-authentication to get
`Modify` permissions.

### 1.0.0

-   Initial release.

## TODO

-   Check that url exists before adding
