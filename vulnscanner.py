#!/usr/bin/env python3

from core.crawler import crawl
from urllib.parse import urlparse
import asyncio
import signal
try:
    import validators
    import click
except ImportError:
    print("[!] Error: Missing required libraries. Please pip install requirements.txt")
    exit(1)


@click.command()
@click.option('--url', '-u', type=str, required=True, multiple=True, help="URL(s) to start crawling at. This parameter can be used multiple times.")
@click.option('--scope-file', '-f', required=True, type=click.Path(exists=True, dir_okay=False, readable=True), help="File containing scopes, e.g. entries may be example.com or *.example.com")
@click.option('--scan-type', '-s', type=click.Choice(['xss'], case_sensitive=False), required=True, help="Type of vulnerability to scan for")
@click.option('--header', '-h', multiple=True, type=str, help="Headers to be sent with the request")
@click.option('--random-agent', default=False, type=bool, show_default=True, help="Use a random user agent for each request")
@click.option('--allow-http', default=False, type=bool, show_default=True, help="Allow URLs communicating over HTTP to be tested; pls know what you are doing -_-")
@click.option('--max-retries', default=1, type=int, show_default=True, help="Maximum number of retries on a URL when trying to crawl it")
@click.option('--backoff-factor', default=1.0, type=float, show_default=True, help="Factor for exponential backoff when attempting retries")
@click.option('--max-concurrent-requests', default=10, type=float, show_default=True, help='Maximum number of concurrent requests made')
@click.option('--time-period', default=60, type=float, show_default=True, help='The time period for which the maximum number of requests made must not be passed; measurement is in seconds.')
# Add the ability to have sessions
def main(url, scope_file, scan_type, header, random_agent, allow_http, max_retries, backoff_factor, max_concurrent_requests, time_period):
    if max_concurrent_requests < 1:
        raise click.BadParameter(f"[!] Error: Number of maximum concurrent requests cannot be less than 1")

    if not validators.url(url):
        raise click.BadParameter(f"[!] Error: One or more URls are invalid")

    parsed_url = urlparse(url)
    if not allow_http and parsed_url.scheme == 'http':
        raise click.BadParameter(f"[!] Error: One or more URLs are using HTTP instead of HTTPS.\nTo test URLs communicating over HTTP, append the option --allow-http.")
    
    try:
        rc = asyncio.run(crawl(url, scope_file, scan_type, header, random_agent, allow_http, max_retries, backoff_factor, max_concurrent_requests, time_period))
    except asyncio.CancelledError:
        print("[*] Aborted!")
    except KeyboardInterrupt:
        print("[*] Aborted!")
    except Exception as e:
        print(f"[!] Error: {e}")
    finally:
        print("[*] Done!")


if __name__ == "__main__":
    main()