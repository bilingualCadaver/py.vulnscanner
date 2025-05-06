## Description
This is a vulnerability scanner created in Python, be kind as this is my first project😐 This vulnerability scanner will scan for simple web-based vulnerabilities. DO NOT use this at the time of reading, its initial stages are yet to be completed.

The common-user-agents.txt file used doesn't originate from me, click [here](https://techblog.willshouse.com/2012/01/03/most-common-user-agents/) for more on the file.


## Installation

```sh
git clone https://github.com/bilingualCadaver/py.vulnscanner

cd py.vulnscanner

pip3 install -r requirements.txt
```


## Usage

```sh
python3 vulnscanner.py --help
```

```console
Usage: vulnscanner.py [OPTIONS]

Options:
  -u, --url TEXT                  URL(s) to start crawling at. This parameter
                                  can be used multiple times.  [required]
  -f, --scope-file FILE           File containing scopes, e.g. entries may be
                                  example.com or *.example.com  [required]
  -s, --scan-type [xss]
                                  Type of vulnerability to scan for
                                  [required]
  -h, --header TEXT               Headers to be sent with the request
  --random-agent BOOLEAN          Use a random user agent for each request
                                  [default: False]
  --allow-http BOOLEAN            Allow URLs communicating over HTTP to be
                                  tested; pls know what you are doing -_-
                                  [default: False]
  --max-retries INTEGER           Maximum number of retries on a URL when
                                  trying to crawl it  [default: 1]
  --backoff-factor FLOAT          Factor for exponential backoff when
                                  attempting retries  [default: 1.0]
  --max-concurrent-requests FLOAT
                                  Maximum number of concurrent requests made
                                  [default: 10]
  --time-period FLOAT             The time period for which the maximum number
                                  of requests made must not be passed;
                                  measurement is in seconds.  [default: 60]
  --help                          Show this message and exit.
```


## Disclaimer

This software is provided "as is", without warranty of any kind. Use it at your own risk. The author is not responsible for any damage or issues caused by the use of this software :P


## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE.md) file for details.
