import requests
import json
import ipaddress

# 3rd party imports
from fastapi import FastAPI, Request

# Local impors
from ip_ranges import ICELANDIC_IP_RANGE

print(ICELANDIC_IP_RANGE)

def get_current_endpoint_data_json():
    """ Fetches the episode list from the RÚV api """
    req = requests.get('https://api.ruv.is/api/programs/program/30762/all')

    # Return no data if request failed
    if not req or req.status_code != 200:
        return None

    return req.json()


def get_all_clips(search_word=None, is_icelandic_ip=False):
    """ 
    Iterates over episode/clip data, returning them in a new format.

    Provides a searchable string for finding content specific clips,
    as well as altering the media URL based on IP address bool.
    """
    json_data = get_current_endpoint_data_json()
    #json_data = json.load(open('endpoint.json')) #local json file test

    # Return empty list if request to API failed
    if not json_data:
        return [{"data":{}}]

    cleaned_data = []
    for episode in json_data['episodes']:
        # Only return year-month for the date
        episode_data = {
            "year-month": '-'.join(episode['firstrun'].split(' ')[0].split('-')[0:2]),
        }

        # Get all the clips associated with the episode, filtering if requested
        episode_clips = []
        for clip in episode['clips']:
            # Skips adding if search word is set and doesn't match title, slug
            if search_word is not None and \
                    search_word.lower() not in clip['text'].lower() and \
                    search_word.lower() not in clip['slug'].lower():
                continue

            # Set the url, and check if Icelandic
            episode_url = episode['file'] 
            if not is_icelandic_ip:
                episode_url = episode['file'].replace('opid', 'lokad')

            episode_clips.append({
                "title": clip['text'],
                "slug": clip['slug'],
                "url": episode_url,
                "time": clip['time'],
                "date": episode['firstrun'].split(' ')[0] # Remove time from date
            })
        
        if len(episode_clips) > 0:
            episode_data['clips'] = episode_clips
            cleaned_data.append(episode_data)

    return [{"data": cleaned_data}]


# Define internal network pattern of IP, simple start of IP lookup, since we will always know
INTERNAL_NETWORK_RANGE = '192.168.'

def is_ip_internal(ip_addr):
    """
    Returns if the IP address given is a local dev or inhouse address.
    """
    return ('127.0.0.1' == ip_addr or 'localhost' == ip_addr or INTERNAL_NETWORK_RANGE in ip_addr)


def get_is_host_icelandic_ip(ip_addr):
    """
    Takes the provided IP address, compares the 
    root of it to the list of icelandic addresses.
    """

    if not ip_addr:
        return False

    if is_ip_internal(ip_addr):
        return True

    first_16_of_ip = '.'.join(ip_addr.split('.')[0:2])

    # Match the first 16-bits of IP to Icelandic ranges
    for addr_range in ICELANDIC_IP_RANGE:
        # If found, dive deeper into subnet range
        if first_16_of_ip in addr_range:
            for ip in ipaddress.IPv4Network(addr_range):
                if str(ip) == ip_addr:
                    return True

    return False


# FastAPI endpoints
app = FastAPI()

@app.get("/clips")
def read_root():
    """ Returns all clips, with IP-address as outside Iceland, for safety """
    clips = get_all_clips()
    return clips

@app.get("/clips/{search_word}")
def get_clips_search_word(search_word: str, request: Request):
    """ 
    Returns clips based on search word and hosts location.

    Searchable by words:
    * /clips/covid
    * /clips/rúv
    * /clips/Katrín
    * /clips/eftir
    """
    is_ip_icelandic = get_is_host_icelandic_ip(request.client.host) if request.client.host else False
    
    # Uncommend to try different IP addresses

    #is_ip_icelandic = get_is_host_icelandic_ip('31.209.207.234') #Siminn
    #is_ip_icelandic = get_is_host_icelandic_ip('31.209.207.234') #Síminn
    #is_ip_icelandic = get_is_host_icelandic_ip('185.153.177.15') #Mexico - TEFINCOM S.A.
    #is_ip_icelandic = get_is_host_icelandic_ip('194.110.84.111') #Finland
    #is_ip_icelandic = get_is_host_icelandic_ip('101.36.115.123') # Random

    return get_all_clips(search_word, is_ip_icelandic)