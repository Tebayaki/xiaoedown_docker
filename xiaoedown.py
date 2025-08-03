import os
import re
import sys
import shutil
import requests
import subprocess
from concurrent.futures import ThreadPoolExecutor
from Crypto.Cipher import AES
from pathlib import Path

# Function to download the M3U8 file
def download_m3u8(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        base_name = os.path.basename(url).split('?')[0]  # Remove query params if any
        dir_name = base_name.replace('.m3u8', '')
        os.makedirs(dir_name, exist_ok=True)
        os.chdir(dir_name)
        m3u8_path = Path(base_name)
        with open(m3u8_path, 'wb') as f:
            f.write(response.content)
        return base_name
    except Exception as e:
        raise Exception(f"Failed to download M3U8 file: {e}")

# Function to parse M3U8 file and extract key URL and TS URLs
def get_urls(prefix, filename):
    try:
        with open(filename, 'rb') as f:
            data = f.read()

        # Extract TS URLs first
        ts_url_matches = re.findall(rb'.+\.ts.*', data)
        if not ts_url_matches:
            raise Exception("Failed to match TS URLs")
        ts_urls = [prefix + match.decode('utf-8') for match in ts_url_matches]

        # Check if file is encrypted
        key_url_match = re.search(rb'AES-128,URI="(.*?)"', data)
        if key_url_match:
            # Handle encrypted content
            key_url = key_url_match.group(1).decode('utf-8')
            response = requests.get(key_url, timeout=10)
            response.raise_for_status()
            with open('key', 'wb') as f:
                f.write(response.content)
            with open('key', 'rb') as f:
                key = f.read()
        else:
            # Handle unencrypted content
            key = None

        return key, ts_urls
    except Exception as e:
        raise Exception(f"Error parsing M3U8 or downloading key: {e}")

# Also need to modify download_and_decrypt_ts function to handle unencrypted content
def download_and_decrypt_ts(task_data):
    num, url, key = task_data
    filename = f"{num}.ts"
    try:
        # Download TS file
        print(f"Downloading {num} {url}")
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.content

        if key:  # Only decrypt if we have a key
            # Decrypt TS file (AES-128 CBC with IV of 16 zeros)
            cipher = AES.new(key, AES.MODE_CBC, iv=b'\x00' * 16)
            data = cipher.decrypt(data)
            
            # Remove padding (PKCS5/PKCS7)
            padding_len = data[-1]
            if padding_len <= 16:
                data = data[:-padding_len]

        with open(filename, 'wb') as f:
            f.write(data)
        return num, url, filename, None
    except Exception as e:
        return num, url, filename, e

# Function to download and decrypt all TS files concurrently
def download_chunks(key, urls):
    tasks = [(i, url, key) for i, url in enumerate(urls)]
    print(f"Total segments: {len(urls)}")
    
    with ThreadPoolExecutor(max_workers=10) as executor:
        results = list(executor.map(download_and_decrypt_ts, tasks))
    
    for num, url, filename, error in results:
        if error:
            raise Exception(f"Failed to download or decrypt {url}: {error}")
    
    return len(urls)

# Function to merge TS files using FFmpeg
def merge_file(count, output):
    try:
        files = [f"{i}.ts" for i in range(count)]
        concat_str = '|'.join(files)
        cmd = ['ffmpeg', '-i', f'concat:{concat_str}', '-c', 'copy', output, '-y']
        print(f"Running: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True)
        print(result.stdout)
        if result.returncode != 0:
            raise Exception(f"FFmpeg error: {result.stderr}")
    except Exception as e:
        raise Exception(f"Failed to merge files: {e}")

# Function to extract URL prefix
def get_prefix(url):
    return url[:url.rfind('/') + 1]

def main(url, new_name):
    # Parse command-line arguments
    # parser = argparse.ArgumentParser(description="Download and merge M3U8 files.")
    # parser.add_argument('-u', '--url', required=True, help="M3U8 URL")
    # parser.add_argument('-n', '--name', default='', help="New name for the output file")
    # args = parser.parse_args()

    # url = args.url
    # new_name = args.name

    # Validate M3U8 URL
    if not re.search(r'm3u8($|\?.*)', url):
        print("Please enter a valid M3U8 URL")
        sys.exit(1)
    
    if not new_name:
        print("Please specify output file name")

    # Store original directory
    original_dir = os.getcwd()

    try:
        # 1. Download M3U8 file
        filename = download_m3u8(url)

        # 2. Parse M3U8 to get key and TS URLs
        key, ts_urls = get_urls(get_prefix(url), filename)

        # 3. Download and decrypt TS segments concurrently
        count = download_chunks(key, ts_urls)

        # 4. Merge TS files
        output_dir = os.path.join(original_dir, 'output')
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, new_name)
        merge_file(count, output_path)

        # 5. Rename and cleanup
        os.chdir(original_dir)
        shutil.rmtree(os.path.basename(url).split('.m3u8')[0])
        print(f"Successfully created {new_name}")

    except Exception as e:
        print(f"Error: {e}")
        os.chdir(original_dir)
        sys.exit(1)
