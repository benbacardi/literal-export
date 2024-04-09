# literal-export

Script to export data from [Literal](https://literal.club) to make up for shortcomings in their official exporter.

## Requirements

The script requires Python 3.10 and the [`requests`](https://requests.readthedocs.io) library.

## Usage

Run the script with `python literal-export.py`. It will prompt you for your Literal email and password.

Currently, the only export supported is your book review ratings. By default, they will be printed to stdout in CSV format:

```csv
$ python literal-export.py
Enter the email address for your Literal account: example@example.com
Enter the password for your Literal account:
Title,Author,Rating,Date,Comment
Words of Radiance,Brandon Sanderson,5,2024-04-04T23:33:31.284Z,
The Way of Kings,Brandon Sanderson,5,2024-03-21T06:19:07.523Z,
Warbreaker,Brandon Sanderson,4,2024-02-23T23:47:18.066Z,
Bringing Columbia Home,"Jonathan H. Ward, Michael D. Leinbach",5,2024-01-13T23:43:21.383Z,
```

### Options

The following options are supported:

* `-e, --email`: Provide your Literal account email instead of prompting for it.
* `-p, --password`: Provide your Literal account password instead of prompting for it.
* `-f, --format`: Export format, one of either `csv` or `json`. Defaults to `csv`.
* --outfile`: The filename to save the data to. Defaults to printing to stdout.
