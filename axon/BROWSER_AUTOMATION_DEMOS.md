# AXON Browser Automation - Demo Prompts & Capabilities

## What Can AXON Do with Browser Automation?

AXON can now control web browsers to perform a wide variety of tasks. Here are real-world examples with the exact prompts you can use.

---

## 🔍 Research & Information Gathering

### Demo 1: Search GitHub for Popular Projects

**User Prompt:**
> "Search GitHub for React and show me the most starred repositories"

**What AXON Will Do:**
1. Open GitHub in browser
2. Use search function
3. Type "React"
4. Sort by most stars
5. Take a screenshot
6. Close browser

**Expected Actions:**
```json
{"action": "browser_navigate", "url": "https://github.com"}
{"action": "browser_press_key", "key": "/"}
{"action": "browser_type", "selector": "#query-builder-test", "text": "React"}
{"action": "browser_press_key", "key": "Enter"}
{"action": "browser_wait", "selector": ".repo-list"}
{"action": "browser_click", "selector": "button:has-text('Sort')"}
{"action": "browser_click", "selector": "a[href*='sort=stars']"}
{"action": "browser_screenshot", "path": "axon/bob-reports/react_repos.png"}
{"action": "browser_close"}
```

---

### Demo 2: Google Search for Information

**User Prompt:**
> "Search Google for 'Python web scraping tutorial' and take a screenshot"

**What AXON Will Do:**
1. Navigate to Google
2. Type search query
3. Submit search
4. Wait for results
5. Capture screenshot

**Expected Actions:**
```json
{"action": "browser_navigate", "url": "https://www.google.com"}
{"action": "browser_type", "selector": "input[name='q']", "text": "Python web scraping tutorial"}
{"action": "browser_press_key", "key": "Enter"}
{"action": "browser_wait", "selector": "#search"}
{"action": "browser_screenshot", "path": "axon/bob-reports/google_search.png"}
{"action": "browser_close"}
```

---

### Demo 3: Check Documentation

**User Prompt:**
> "Go to Python.org and take a screenshot of the homepage"

**What AXON Will Do:**
1. Navigate to Python.org
2. Wait for page to load
3. Take screenshot
4. Close browser

**Expected Actions:**
```json
{"action": "browser_navigate", "url": "https://www.python.org"}
{"action": "browser_wait", "selector": ".main-content"}
{"action": "browser_screenshot", "path": "axon/bob-reports/python_homepage.png"}
{"action": "browser_close"}
```

---

## 📝 Form Filling & Data Entry

### Demo 4: Fill Contact Form

**User Prompt:**
> "Fill out the contact form on example.com with name 'John Doe', email 'john@example.com', and message 'Hello, this is a test'"

**What AXON Will Do:**
1. Navigate to the form page
2. Fill in name field
3. Fill in email field
4. Fill in message field
5. Submit form
6. Take confirmation screenshot

**Expected Actions:**
```json
{"action": "browser_navigate", "url": "https://example.com/contact"}
{"action": "browser_type", "selector": "#name", "text": "John Doe"}
{"action": "browser_type", "selector": "#email", "text": "john@example.com"}
{"action": "browser_type", "selector": "#message", "text": "Hello, this is a test"}
{"action": "browser_click", "selector": "button[type='submit']"}
{"action": "browser_wait", "selector": ".success-message"}
{"action": "browser_screenshot", "path": "axon/bob-reports/form_submitted.png"}
{"action": "browser_close"}
```

---

### Demo 5: Newsletter Signup

**User Prompt:**
> "Sign up for the newsletter on example.com with email test@example.com"

**What AXON Will Do:**
1. Navigate to website
2. Find email input
3. Enter email
4. Click subscribe button
5. Capture confirmation

**Expected Actions:**
```json
{"action": "browser_navigate", "url": "https://example.com"}
{"action": "browser_type", "selector": "input[type='email']", "text": "test@example.com"}
{"action": "browser_click", "selector": "button:has-text('Subscribe')"}
{"action": "browser_wait", "selector": ".confirmation"}
{"action": "browser_screenshot", "path": "axon/bob-reports/newsletter_signup.png"}
{"action": "browser_close"}
```

---

## 🛒 E-commerce & Shopping

### Demo 6: Product Search

**User Prompt:**
> "Search Amazon for 'wireless mouse' and show me the results"

**What AXON Will Do:**
1. Navigate to Amazon
2. Find search box
3. Type product name
4. Submit search
5. Take screenshot of results

**Expected Actions:**
```json
{"action": "browser_navigate", "url": "https://www.amazon.com"}
{"action": "browser_type", "selector": "#twotabsearchtextbox", "text": "wireless mouse"}
{"action": "browser_press_key", "key": "Enter"}
{"action": "browser_wait", "selector": ".s-result-list"}
{"action": "browser_screenshot", "path": "axon/bob-reports/amazon_search.png"}
{"action": "browser_close"}
```

---

### Demo 7: Price Comparison

**User Prompt:**
> "Check the price of iPhone 15 on Apple's website"

**What AXON Will Do:**
1. Navigate to Apple store
2. Search for iPhone 15
3. Navigate to product page
4. Capture pricing information

**Expected Actions:**
```json
{"action": "browser_navigate", "url": "https://www.apple.com/shop"}
{"action": "browser_click", "selector": ".search-button"}
{"action": "browser_type", "selector": "input[type='search']", "text": "iPhone 15"}
{"action": "browser_press_key", "key": "Enter"}
{"action": "browser_wait", "selector": ".product-list"}
{"action": "browser_screenshot", "path": "axon/bob-reports/iphone_price.png"}
{"action": "browser_close"}
```

---

## 📱 Social Media Interactions

### Demo 8: Check Twitter/X Trends

**User Prompt:**
> "Go to Twitter and show me what's trending"

**What AXON Will Do:**
1. Navigate to Twitter/X
2. Wait for trends section
3. Capture screenshot of trends

**Expected Actions:**
```json
{"action": "browser_navigate", "url": "https://twitter.com"}
{"action": "browser_wait", "selector": "[data-testid='trend']"}
{"action": "browser_screenshot", "path": "axon/bob-reports/twitter_trends.png"}
{"action": "browser_close"}
```

---

### Demo 9: LinkedIn Profile Check

**User Prompt:**
> "Open LinkedIn and take a screenshot of the homepage"

**What AXON Will Do:**
1. Navigate to LinkedIn
2. Wait for page load
3. Capture homepage

**Expected Actions:**
```json
{"action": "browser_navigate", "url": "https://www.linkedin.com"}
{"action": "browser_wait", "selector": ".main-content"}
{"action": "browser_screenshot", "path": "axon/bob-reports/linkedin_home.png"}
{"action": "browser_close"}
```

---

## 📰 News & Content

### Demo 10: Read Latest News

**User Prompt:**
> "Go to BBC News and show me the top headlines"

**What AXON Will Do:**
1. Navigate to BBC News
2. Wait for headlines to load
3. Take screenshot

**Expected Actions:**
```json
{"action": "browser_navigate", "url": "https://www.bbc.com/news"}
{"action": "browser_wait", "selector": ".top-stories"}
{"action": "browser_screenshot", "path": "axon/bob-reports/bbc_headlines.png"}
{"action": "browser_close"}
```

---

### Demo 11: Check Weather

**User Prompt:**
> "Check the weather forecast on weather.com for New York"

**What AXON Will Do:**
1. Navigate to weather.com
2. Search for New York
3. View forecast
4. Capture screenshot

**Expected Actions:**
```json
{"action": "browser_navigate", "url": "https://weather.com"}
{"action": "browser_type", "selector": "input[name='search']", "text": "New York"}
{"action": "browser_press_key", "key": "Enter"}
{"action": "browser_wait", "selector": ".forecast"}
{"action": "browser_screenshot", "path": "axon/bob-reports/ny_weather.png"}
{"action": "browser_close"}
```

---

## 🎓 Education & Learning

### Demo 12: Course Search

**User Prompt:**
> "Search Coursera for Python courses"

**What AXON Will Do:**
1. Navigate to Coursera
2. Search for Python courses
3. Show results

**Expected Actions:**
```json
{"action": "browser_navigate", "url": "https://www.coursera.org"}
{"action": "browser_type", "selector": "input[placeholder='What do you want to learn?']", "text": "Python"}
{"action": "browser_press_key", "key": "Enter"}
{"action": "browser_wait", "selector": ".course-list"}
{"action": "browser_screenshot", "path": "axon/bob-reports/python_courses.png"}
{"action": "browser_close"}
```

---

### Demo 13: Wikipedia Research

**User Prompt:**
> "Look up 'Artificial Intelligence' on Wikipedia and take a screenshot"

**What AXON Will Do:**
1. Navigate to Wikipedia
2. Search for topic
3. Open article
4. Capture page

**Expected Actions:**
```json
{"action": "browser_navigate", "url": "https://en.wikipedia.org"}
{"action": "browser_type", "selector": "#searchInput", "text": "Artificial Intelligence"}
{"action": "browser_press_key", "key": "Enter"}
{"action": "browser_wait", "selector": "#content"}
{"action": "browser_screenshot", "path": "axon/bob-reports/ai_wikipedia.png"}
{"action": "browser_close"}
```

---

## 💼 Professional Tasks

### Demo 14: Job Search

**User Prompt:**
> "Search Indeed for 'Software Engineer' jobs in San Francisco"

**What AXON Will Do:**
1. Navigate to Indeed
2. Enter job title
3. Enter location
4. Search
5. Show results

**Expected Actions:**
```json
{"action": "browser_navigate", "url": "https://www.indeed.com"}
{"action": "browser_type", "selector": "#text-input-what", "text": "Software Engineer"}
{"action": "browser_type", "selector": "#text-input-where", "text": "San Francisco"}
{"action": "browser_click", "selector": "button[type='submit']"}
{"action": "browser_wait", "selector": ".job-list"}
{"action": "browser_screenshot", "path": "axon/bob-reports/job_search.png"}
{"action": "browser_close"}
```

---

### Demo 15: Stock Price Check

**User Prompt:**
> "Check Tesla stock price on Yahoo Finance"

**What AXON Will Do:**
1. Navigate to Yahoo Finance
2. Search for TSLA
3. View stock details
4. Capture screenshot

**Expected Actions:**
```json
{"action": "browser_navigate", "url": "https://finance.yahoo.com"}
{"action": "browser_type", "selector": "#yfin-usr-qry", "text": "TSLA"}
{"action": "browser_press_key", "key": "Enter"}
{"action": "browser_wait", "selector": ".quote-header"}
{"action": "browser_screenshot", "path": "axon/bob-reports/tesla_stock.png"}
{"action": "browser_close"}
```

---

## 🎨 Creative & Media

### Demo 16: Image Search

**User Prompt:**
> "Search Google Images for 'sunset beach'"

**What AXON Will Do:**
1. Navigate to Google Images
2. Search for images
3. Show results

**Expected Actions:**
```json
{"action": "browser_navigate", "url": "https://images.google.com"}
{"action": "browser_type", "selector": "input[name='q']", "text": "sunset beach"}
{"action": "browser_press_key", "key": "Enter"}
{"action": "browser_wait", "selector": "#search"}
{"action": "browser_screenshot", "path": "axon/bob-reports/sunset_images.png"}
{"action": "browser_close"}
```

---

### Demo 17: YouTube Search

**User Prompt:**
> "Search YouTube for 'Python tutorial for beginners'"

**What AXON Will Do:**
1. Navigate to YouTube
2. Search for videos
3. Show results

**Expected Actions:**
```json
{"action": "browser_navigate", "url": "https://www.youtube.com"}
{"action": "browser_type", "selector": "input#search", "text": "Python tutorial for beginners"}
{"action": "browser_press_key", "key": "Enter"}
{"action": "browser_wait", "selector": "#contents"}
{"action": "browser_screenshot", "path": "axon/bob-reports/youtube_search.png"}
{"action": "browser_close"}
```

---

## 🔧 Technical & Development

### Demo 18: Stack Overflow Search

**User Prompt:**
> "Search Stack Overflow for 'Python async await'"

**What AXON Will Do:**
1. Navigate to Stack Overflow
2. Search for question
3. Show results

**Expected Actions:**
```json
{"action": "browser_navigate", "url": "https://stackoverflow.com"}
{"action": "browser_type", "selector": "input[name='q']", "text": "Python async await"}
{"action": "browser_press_key", "key": "Enter"}
{"action": "browser_wait", "selector": ".search-results"}
{"action": "browser_screenshot", "path": "axon/bob-reports/stackoverflow_search.png"}
{"action": "browser_close"}
```

---

### Demo 19: NPM Package Search

**User Prompt:**
> "Search NPM for 'react router' package"

**What AXON Will Do:**
1. Navigate to npmjs.com
2. Search for package
3. Show package details

**Expected Actions:**
```json
{"action": "browser_navigate", "url": "https://www.npmjs.com"}
{"action": "browser_type", "selector": "input[type='search']", "text": "react router"}
{"action": "browser_press_key", "key": "Enter"}
{"action": "browser_wait", "selector": ".search-results"}
{"action": "browser_screenshot", "path": "axon/bob-reports/npm_search.png"}
{"action": "browser_close"}
```

---

### Demo 20: GitHub Repository Info

**User Prompt:**
> "Go to the React GitHub repository and show me the README"

**What AXON Will Do:**
1. Navigate to React repo
2. Wait for README to load
3. Capture screenshot

**Expected Actions:**
```json
{"action": "browser_navigate", "url": "https://github.com/facebook/react"}
{"action": "browser_wait", "selector": "#readme"}
{"action": "browser_screenshot", "path": "axon/bob-reports/react_readme.png"}
{"action": "browser_close"}
```

---

## 🎯 Complex Multi-Step Tasks

### Demo 21: Research and Compare

**User Prompt:**
> "Compare Python and JavaScript by searching for both on Google and taking screenshots"

**What AXON Will Do:**
1. Search for Python
2. Take screenshot
3. Search for JavaScript
4. Take screenshot
5. Close browser

**Expected Actions:**
```json
{"action": "browser_navigate", "url": "https://www.google.com"}
{"action": "browser_type", "selector": "input[name='q']", "text": "Python programming"}
{"action": "browser_press_key", "key": "Enter"}
{"action": "browser_wait", "selector": "#search"}
{"action": "browser_screenshot", "path": "axon/bob-reports/python_search.png"}
{"action": "browser_navigate", "url": "https://www.google.com"}
{"action": "browser_type", "selector": "input[name='q']", "text": "JavaScript programming"}
{"action": "browser_press_key", "key": "Enter"}
{"action": "browser_wait", "selector": "#search"}
{"action": "browser_screenshot", "path": "axon/bob-reports/javascript_search.png"}
{"action": "browser_close"}
```

---

## 💡 Tips for Best Results

### Good Prompts:
✅ "Search GitHub for React repositories"
✅ "Fill out the contact form with my details"
✅ "Check the weather on weather.com"
✅ "Search Google for Python tutorials"

### Prompts to Avoid:
❌ "Do something on the internet" (too vague)
❌ "Login to my account" (requires credentials)
❌ "Download this file" (file downloads not yet supported)
❌ "Open 10 tabs" (single tab only currently)

---

## 🚀 Capabilities Summary

AXON can:
- ✅ Navigate to any website
- ✅ Search for information
- ✅ Fill out forms
- ✅ Click buttons and links
- ✅ Type text into fields
- ✅ Take screenshots
- ✅ Wait for content to load
- ✅ Extract text from pages
- ✅ Perform multi-step workflows

AXON cannot (yet):
- ❌ Handle authentication/login
- ❌ Download files
- ❌ Upload files
- ❌ Work with multiple tabs
- ❌ Handle CAPTCHAs
- ❌ Execute JavaScript directly

---

## 📝 How to Use

Simply tell AXON what you want to do in natural language:

**Examples:**
- "Search for X on Y website"
- "Go to Z website and take a screenshot"
- "Fill out the form on W website with these details"
- "Check the price of X on Y store"
- "Look up X on Wikipedia"

AXON will understand your intent and execute the appropriate browser actions!

---

**Last Updated:** 2026-05-17  
**Status:** ✅ Production Ready  
**Total Demo Scenarios:** 21+