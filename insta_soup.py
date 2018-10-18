import requests
import json
import sys
import os
from bs4 import BeautifulSoup

# Take Instagram username from command line argument 
username = sys.argv[1]

# Make a folder to store the photos
path = os.getcwd() + '/' + username + '_insta'
print('Creating directory: %s' % path)
os.makedirs(path)
os.chdir(path)

# Prepare variables for request
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
url = 'https://www.instagram.com/' + username
response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.text, 'lxml')

# Parse the first page html and get the script that contain first few photos, and parse into json
script = soup.find('script', text=lambda t: t.startswith('window._sharedData'))
photo_json = script.text.split(' = ', 1)[1].rstrip(';')
data = json.loads(photo_json)

# Dig the json file to get key value for further scrapping
profile_id = data['entry_data']['ProfilePage'][0]['graphql']['user']['id']
has_next_page = data['entry_data']['ProfilePage'][0]['graphql']['user']['edge_owner_to_timeline_media']['page_info']['has_next_page']
end_cursor = data['entry_data']['ProfilePage'][0]['graphql']['user']['edge_owner_to_timeline_media']['page_info']['end_cursor']

print(end_cursor)

# Get the profile pic url and download it
profile_pic_url = data['entry_data']['ProfilePage'][0]['graphql']['user']['profile_pic_url_hd']
with open('profile.jpg', 'wb') as handle:
    response = requests.get(profile_pic_url, stream=True)
    for block in response.iter_content(1024):
        if not block:
            break
        handle.write(block)

# for index, photo in enumerate(data['entry_data']['ProfilePage'][0]['graphql']['user']['edge_owner_to_timeline_media']['edges']):
#     # photo_url = photo['node']['thumbnail_resources'][4]['src']
#     photo_url = photo['node']['display_url']
#     filename = 'photo_' + str(index) + '.jpg'
#     with open(filename, 'wb') as handle:
#         response = requests.get(photo_url, stream=True)
#         for block in response.iter_content(1024):
#             if not block:
#                 break
#             handle.write(block)

# Loop through the available photos to get their post url, then request them
for index, post in enumerate(data['entry_data']['ProfilePage'][0]['graphql']['user']['edge_owner_to_timeline_media']['edges']):
    post_url = 'https://www.instagram.com/p/' + post['node']['shortcode']
    small_response = requests.get(post_url, headers=headers)
    small_soup = BeautifulSoup(small_response.text, 'lxml')

    # Get their script containing photo url and parse into json
    small_script = small_soup.find('script', text=lambda t: t.startswith('window._sharedData'))
    post_json = small_script.text.split(' = ', 1)[1].rstrip(';')
    small_data = json.loads(post_json)

    # If that post contain multiple photos
    if small_data['entry_data']['PostPage'][0]['graphql']['shortcode_media']['__typename'] == 'GraphSidecar':
        # Loop through 
        for small_index, photo in enumerate(small_data['entry_data']['PostPage'][0]['graphql']['shortcode_media']['edge_sidecar_to_children']['edges']):
            if photo['node']['__typename'] == 'GraphImage':
                photo_url = photo['node']['display_url']
                print(photo_url)
                filename = 'photo_' + str(index) + '_' + str(small_index) + '.jpg'
                with open(filename, 'wb') as handle:
                    small_response = requests.get(photo_url, stream=True)
                    for block in small_response.iter_content(1024):
                        if not block:
                            break
                        handle.write(block)
            else:
                video_url = photo['node']['video_url']
                print(video_url)
                filename = 'video_' + str(index) + '_' + str(small_index) + '.mp4'
                with open(filename, 'wb') as handle:
                    small_response = requests.get(video_url, stream=True)
                    for block in small_response.iter_content(1024):
                        if not block:
                            break
                        handle.write(block)
    elif small_data['entry_data']['PostPage'][0]['graphql']['shortcode_media']['__typename'] == 'GraphImage':
        photo_url = small_data['entry_data']['PostPage'][0]['graphql']['shortcode_media']['display_url']
        print(photo_url)
        filename = 'photo_' + str(index) + '.jpg'
        with open(filename, 'wb') as handle:
            small_response = requests.get(photo_url, stream=True)
            for block in small_response.iter_content(1024):
                if not block:
                    break
                handle.write(block)
    else:
        video_url = small_data['entry_data']['PostPage'][0]['graphql']['shortcode_media']['video_url']
        print(video_url)
        filename = 'video_' + str(index) + '.mp4'
        with open(filename, 'wb') as handle:
            small_response = requests.get(video_url, stream=True)
            for block in small_response.iter_content(1024):
                if not block:
                    break
                handle.write(block)



print('Happy scraping!')