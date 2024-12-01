# SpiderBolt
**SpiderBolt** is a fast and efficient Python web scraping script that extracts links from websites using multi-threading and random user agents. It categorizes links into HTML and other types, groups them by paths, and saves them in an organized file. Customizable settings ensure flexibility for various scraping needs.

## Features  
- 🌟 **Multi-threading:** Handles up to 500 threads for fast and efficient web scraping.
- 🌐 **Custom User Agents:** Mimics real browsers using random user-agent headers to avoid detection.    
- 📊 **Link Categorization:** Automatically categorizes links into HTML and other types, grouping them by paths for easy analysis.
- 🛠️ **Customizable Settings:** Adjust the number of threads and tweak other settings to suit your scraping needs.  

## Installation  
1. Clone the repository:  
   ```bash
   git clone https://github.com/ogtirth/SpiderBolt.git
   cd SpiderBolt
   ```
2. Install the required dependencies:  
   ```bash
   pip install -r requirements.txt
   ```
3. Make sure to add a \`user-agents.txt\` file with a list of user agents (one per line) in the project directory.  

## Usage  
Run the script:  
```bash
python spiderbolt.py
```

Follow the on-screen prompts to:  
1. Enter the domain to scrape links.  
2. Specify the number of threads you want.    

The script will handle the rest, providing you with real-time status updates for each request.

