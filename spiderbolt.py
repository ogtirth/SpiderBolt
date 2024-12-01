import argparse
import asyncio
import aiohttp
from aiohttp.client_exceptions import ClientError
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from collections import defaultdict
from datetime import datetime
from queue import Queue
from colorama import Fore, Style, init
from tqdm import tqdm
import os
import random

init(autoreset=True)

def art():
    print(f"""{Fore.RED}   
                         
                                                                                          ██
                                                                                        ██
███████ ██████  ██ ██████  ███████ ██████      ██████   ██████  ██      ████████      ██
██      ██   ██ ██ ██   ██ ██      ██   ██     ██   ██ ██    ██ ██         ██       ██
███████ ██████  ██ ██   ██ █████   ██████      ██████  ██    ██ ██         ██       ███████
     ██ ██      ██ ██   ██ ██      ██   ██     ██   ██ ██    ██ ██         ██            ██
███████ ██      ██ ██████  ███████ ██   ██     ██████   ██████  ███████    ██          ██
                                                                                     ██
                                                                                   ██
                                                         
                                                           - Just A Link Scraper by ogtirth ;)
    {Style.RESET_ALL}
    """)

def dname(url):
    parsed_url = urlparse(url)
    return parsed_url.netloc or parsed_url.path.replace("/", "_")

def dsame(url, domain):
    return urlparse(url).netloc == domain

def lpath(links):
    grouped_links = defaultdict(list)
    for link in links:
        parsed = urlparse(link)
        path = parsed.path.split("/")[1] if "/" in parsed.path and parsed.path != "/" else "root"
        grouped_links[path].append(link)
    return grouped_links

async def scrape(url, session, domain, visited, queue, html_links, other_links):
    if url in visited:
        return
    visited.add(url)
    try:
        async with session.get(url) as response:
            if response.status != 200:
                return
            html = await response.text()
            soup = BeautifulSoup(html, "html.parser")
            for a_tag in soup.find_all("a", href=True):
                full_url = urljoin(url, a_tag["href"])
                if dsame(full_url, domain) and full_url not in visited:
                    queue.put(full_url)
                    if full_url.endswith((".html", ".php", ".asp", ".aspx", "/")):
                        html_links.add(full_url)
                    else:
                        other_links.add(full_url)
                    print(f"{Fore.GREEN}{full_url}{Style.RESET_ALL}")
    except (ClientError, asyncio.TimeoutError) as e:
        print(f"{Fore.RED}Error fetching {url}: {e}{Style.RESET_ALL}")

async def crawl(start_url, depth, user_agents, max_threads, output_file):
    domain = urlparse(start_url).netloc
    visited = set()
    queue = Queue()
    queue.put(start_url)
    visited.add(start_url)
    html_links = set()
    other_links = set()
    user_agent = {"User-Agent": random.choice(user_agents)}

    async with aiohttp.ClientSession(headers=user_agent) as session:
        for _ in range(depth):
            tasks = []
            for _ in tqdm(range(queue.qsize()), desc=f"{Fore.YELLOW}Crawling Depth {_ + 1}{Style.RESET_ALL}"):
                url = queue.get()
                tasks.append(scrape(url, session, domain, visited, queue, html_links, other_links))
                if len(tasks) >= max_threads:
                    await asyncio.gather(*tasks)
                    tasks = []
            if tasks:
                await asyncio.gather(*tasks)

    html_grouped = lpath(html_links)
    other_grouped = lpath(other_links)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open(output_file, "w") as f:
        f.write(f"Scraping Timestamp: {timestamp}\n")
        f.write(f"Target URL: {start_url}\n")
        f.write("=" * 80 + "\n\n")
        f.write("########## HTML LINKS BY PATH ##########\n\n")
        for path, links in html_grouped.items():
            f.write(f"===== {path.upper()} =====\n")
            for link in links:
                f.write(link + "\n")
            f.write("\n")
        f.write("########## OTHER LINKS BY PATH ##########\n\n")
        for path, links in other_grouped.items():
            f.write(f"===== {path.upper()} =====\n")
            for link in links:
                f.write(link + "\n")
            f.write("\n")

    print(f"{Fore.CYAN}\n" + "=" * 80 + f"{Style.RESET_ALL}")
    print(f"{Fore.GREEN}Scraping completed. {len(html_links)} HTML links and {len(other_links)} other links saved to {output_file}.{Style.RESET_ALL}")
    print(f"{Fore.CYAN}" + "=" * 80 + f"{Style.RESET_ALL}")

def main():
    os.system("cls" if os.name == "nt" else "clear")
    art()

    url = input(f"{Fore.BLUE}Enter the website link to scrape ;) {Style.RESET_ALL}").strip()
    domain = urlparse(url).netloc
    while True:
        try:
            num_threads = int(input(f"{Fore.BLUE}How many threads do you want to use?: {Style.RESET_ALL}").strip())
            if num_threads <= 0 or num_threads > 500:
                raise ValueError("Threads must be between 1 and 500 :) ")
            break
        except ValueError as e:
            print(f"{Fore.RED}Invalid input:/ {e}{Style.RESET_ALL}")

    while True:
        try:
            depth = int(input(f"{Fore.BLUE}Enter the crawl depth: {Style.RESET_ALL}").strip())
            if depth <= 0:
                raise ValueError("Depth must be greater than 0")
            break
        except ValueError as e:
            print(f"{Fore.RED}Invalid input:/ {e}{Style.RESET_ALL}")

    try:
        with open("user-agents.txt", "r") as f:
            user_agents = [ua.strip() for ua in f.readlines()]
    except FileNotFoundError:
        print(f"{Fore.RED}Error: 'user-agents.txt' file not found. Please provide a valid file :/{Style.RESET_ALL}")
        return

    domain_name = dname(url)
    output_file = f"{domain_name}.txt"

    asyncio.run(crawl(
        start_url=url,
        depth=depth,
        user_agents=user_agents,
        max_threads=num_threads,
        output_file=output_file
    ))

if __name__ == "__main__":
    main()
