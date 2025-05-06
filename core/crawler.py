import asyncio
import aiofiles
import aiohttp
from aiolimiter import AsyncLimiter
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urldefrag, urlparse, parse_qs
import validators
from core.xss.scanner import scan


async def is_valid_location(netloc):
    if netloc.startswith("*."):
        netloc = netloc[2:]
    
    if ':' in netloc:
        location, port = netloc.split(':', 1)
        return (validators.domain(location) or validators.ipv4(location)) and (port.isdigit() and validators.between(int(port), min=0, max=65535))
    else:
        return validators.domain(netloc) or validators.ipv4(netloc)

async def read_scope_file(scope_file):
    scopes = []

    try:
        async with aiofiles.open(scope_file, 'r') as f:
            async for line in f:
                line = line.strip()
                if await is_valid_location(line):
                    scopes.append(line)
                else:
                    print(f"Invalid entry within {scope_file}: {line}")
    except Exception as e:
        print(f"An error occurred while reading '{scope_file}': {e}")
        return None
    
    return scopes

async def is_in_scope(url, scope):
    parsed_url = urlparse(url)
    netloc = parsed_url.netloc
    _, port = netloc.split(':', 1) if ':' in netloc else (netloc, None)

    for s in scope:
        if s.startswith("*."):
            base_domain = s[2:]
            if netloc == base_domain or netloc.endswith("." + base_domain):
                return True
        elif s == netloc:
            return True
    
    return False

async def valid_href(href):
    if len(href) == 0:
        return False

    allowed_schemes = ['http', 'https']
    parsed_url = urlparse(href)

    if parsed_url.scheme and parsed_url.scheme not in allowed_schemes:
        return False

    if parsed_url.scheme and not parsed_url.netloc:
        return False
    
    if href.startswith("tel+"):
        return False

    return True

async def http_retry(url, retries, backoff_factor):
    attempted = 0
    while attempted < retries:
        try:
            print("Retrying...")
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=(5, 10)) as response:
                    response.raise_for_status()
                    return response
        except aiohttp.ClientError as e:
            print(f"An error occurred: {e}")
            attempted += 1
            sleep_time = backoff_factor * (2 ** retries)
            await asyncio.sleep(sleep_time)

    return None

async def fetch_n_parse(url, session, limiter, allow_http, retries, backoff_factor, scope, visited):
    async with limiter:
        try:
            parsed_url = urlparse(url)
            if parsed_url.query:
                url = url.replace(f'?{parsed_url.query}', '')
                params = parse_qs(parsed_url.query)

            async with session.get(url, params=params) as resp:
                resp.raise_for_status()
                html = await resp.text()
                soup = BeautifulSoup(html, "html.parser")
                
                links = []
                for a in soup.find_all("a", href=True):
                    if not await valid_href(a['href']):
                        continue

                    next_url = urljoin(url, a.get("href"))
                    next_url, _ = urldefrag(next_url)
                    
                    if not await is_in_scope(next_url, scope) or next_url in visited:
                        continue

                    parsed_next_url = urlparse(next_url)
                    if not allow_http and parsed_next_url.scheme == "http":
                        continue

                    links.append(next_url)

                return html, links
        except aiohttp.ClientError as e:
            print(f"Failed to fetch {url}: {e}")
            return None, []
        

async def get_random_agents():
    try:
        async with aiofiles.open("data/common-user-agents.txt", 'r') as f:
            agents = [line.strip() for line in f]
    except Exception as e:
        print(f"An error occurred while reading 'user-agents.txt': {e}")
        return None
    
    return agents

async def startup(scope, scope_file, urls, random_agents):
    scope = await read_scope_file(scope_file)
    if scope is None:
        return 1
    
    for url in urls:
        url, _ = urldefrag(url)
        if not await is_in_scope(url, scope):
            print(f"URL given is not in scope: {url}")
            return None
    
    if random_agents:
        random_agents = await get_random_agents()

    return scope, random_agents

async def crawl(urls, scope_file, scan_type, headers, random_agent, allow_http, retries, backoff_factor, max_concurrent_requests, time_period):
    limiter = AsyncLimiter(max_rate=max_concurrent_requests, time_period=time_period)
    to_visit = set(urls)
    visited = set()

    rc = await startup(scope_file, urls, random_agent)
    if rc == 1:
        return 1

    sessions = {}
    async with asyncio.TaskGroup() as tg:
        while to_visit:
            for url in list(to_visit):
                if url not in visited:
                    visited.add(url)
                    to_visit.remove(url)

                    parsed_url = urlparse(url)
                    netloc = parsed_url.netloc
                    if netloc not in sessions:
                        sessions[netloc] = aiohttp.ClientSession(headers=headers)

                    session = sessions[netloc]
                    tg.create_task(fetch_n_parse(url, session, limiter, allow_http, retries, backoff_factor, scope, visited))

            results = await tg

            for html, links in results:
                if links:
                    to_visit.update(set(links) - visited)
                
    for session in sessions.values():
        await session.close()
    
    if scan_type == 'xxs':
        # await scan(visited)
        pass


    return visited
