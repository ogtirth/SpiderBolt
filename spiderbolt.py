import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from collections import defaultdict
from threading import Lock, Thread
from queue import Queue
from colorama import Fore, Style, init
from datetime import datetime
import random
import os

init(autoreset=True)

visited_lock = Lock()

def art():                         
    art = f"""{Fore.RED}  
                         
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
    """
    print(art)

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

def scrape(url, domain, user_agents, visited, html_links, other_links, request_queue):
    try:
        user_agent = random.choice(user_agents)
        headers = {"User-Agent": user_agent}
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, "html.parser")
            for a_tag in soup.find_all("a", href=True):
                full_url = urljoin(url, a_tag["href"])
                if dsame(full_url, domain):
                    with visited_lock:
                        if full_url not in visited:
                            visited.add(full_url)
                            request_queue.put(full_url)
                            if full_url.endswith((".html", ".php", ".asp", ".aspx", "/")):
                                html_links.add(full_url)
                            else:
                                other_links.add(full_url)
                            print(f"{Fore.GREEN}{full_url}{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}Error scraping {url}: {e}{Style.RESET_ALL}")

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

    try:
        with open("user-agents.txt", "r") as f:
            user_agents = [ua.strip() for ua in f.readlines()]
    except FileNotFoundError:
        print(f"{Fore.RED}Error: 'user-agents.txt' file not found. Please provide a valid file :/{Style.RESET_ALL}")
        return

    visited = set()
    html_links = set()
    other_links = set()
    request_queue = Queue()

    request_queue.put(url)
    visited.add(url)

    print(f"{Fore.YELLOW}\n[Scraping links...]\n{Style.RESET_ALL}")
    threads = []

    def worker():
        while not request_queue.empty():
            current_url = request_queue.get()
            scrape(current_url, domain, user_agents, visited, html_links, other_links, request_queue)
            request_queue.task_done()

    for _ in range(num_threads):
        thread = Thread(target=worker)
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()

    domain_name = dname(url)
    output_file = f"{domain_name}.txt"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    html_grouped = lpath(html_links)
    other_grouped = lpath(other_links)

    with open(output_file, "w") as f:

        f.write(f"Scraping Timestamp: {timestamp}\n")
        f.write(f"Target URL: {url}\n")
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

if __name__ == "__main__":
    main()
