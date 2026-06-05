import requests, re, sys

url = sys.argv[1]
r = requests.get(url, allow_redirects=True)
print('Status:', r.status_code)
print('Final URL:', r.url)

# Try to find download button
match = re.search(r'class="[^"]*download_link[^"]*"[^>]*href="([^"]+)"', r.text)
if match:
    print('Download link:', match.group(1))
else:
    # Try common patterns for mediafire
    match = re.search(r'id="downloadButton"[^>]*href="([^"]+)"', r.text)
    if match:
        print('Download link:', match.group(1))
    else:
        # Look for any .rar or .zip download
        match = re.search(r'href="([^"]+\.(rar|zip))"', r.text)
        if match:
            print('Download link:', match.group(1))
        else:
            print('No download link found')
            # Debug: save HTML
            with open(r'C:\Users\alerrandro\AppData\Local\Temp\opencode\mediafire.html', 'w', encoding='utf-8') as f:
                f.write(r.text[:20000])
            print('Page saved for inspection')
