import re
import requests
from lxml import etree


XSRF_TOKEN = "eyJpdiI6Ik5aaTNxMVdjQmo5OWFmRXVvRkU1NEE9PSIsInZhbHVlIjoiXC9scUFYbEk1SkIwNmQzNjdrSGIzWXk0UVBjZ0ZQMHdXVzVsTTlYWk5CZU9DRWlwN05JbEd1OTRMNUgrS3M5K28iLCJtYWMiOiJlZTUyMjhhN2IyMWI3ODMxYzM2NmEzMGM3ZWY0OWNlZmY4NmM4MTRkOWFiODgwNjU0ODI1OWI1NTEzYzIwNTAxIn0" # XSRF-TOKEN cookie
laravel_session = "eyJpdiI6IjNSWXRsVXdLcVlBNGF5b2YxRjZyeVE9PSIsInZhbHVlIjoia0phdmZkbGFDTktnd1RRblwvR293V0EyVk40bUJLdnlCeVZUSTBUbmdQR0EydW9idWliR1FMaHY1Ukdrb0JnQW8iLCJtYWMiOiJjYWI5MjAzMDM4MjdmZjJiNmViYjE0YjYyNjllOTc1YzZjMmUwZjE2Y2Y3NDM0NzlhOWI1N2ZjM2UyYjVhMWZkIn0" # laravel_session cookie

'''
404: Exception Handling Not Found :(

NOTE:
DO NOT use the logout button on website. Instead, clear the site cookies manually to log out.
If you use logout from website, cookies will become invalid.
'''

# ===================================================================

def parse_info(res):
    f = re.findall(">(.*?)<\/td>", res.text)
    info_parsed = {}
    for i in range(0, len(f), 3):
        info_parsed[f[i].lower().replace(' ', '_')] = f[i+2]
    return info_parsed

def sharer_pw_dl(url, forced_login=False):
    client = requests.Session()
    
    client.cookies.update({
        "XSRF-TOKEN": XSRF_TOKEN,
        "laravel_session": laravel_session
    })
    
    res = client.get(url)
    token = re.findall("_token\s=\s'(.*?)'", res.text)
    
    ddl_btn = etree.HTML(res.content).xpath("//button[@id='btndirect']")

    info_parsed = parse_info(res)
    info_parsed['error'] = True
    info_parsed['src_url'] = url
    info_parsed['link_type'] = 'login' # direct/login
    info_parsed['forced_login'] = forced_login
    
    headers = {
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'x-requested-with': 'XMLHttpRequest'
    }
    
    data = {
        '_token': token
    }
    
    if len(ddl_btn):
        info_parsed['link_type'] = 'direct'
    if not forced_login:
        data['nl'] = 1
    
    try: 
        res = client.post(url+'/dl', headers=headers, data=data).json()
    except:
        return info_parsed
    
    if 'url' in res and res['url']:
        info_parsed['error'] = False
        info_parsed['gdrive_link'] = res['url']
    
    if len(ddl_btn) and not forced_login and not 'url' in info_parsed:
        # retry download via login
        return sharer_pw_dl(url, forced_login=True)
    
    return info_parsed

# ===================================================================

#ut = sharer_pw_dl(url)
#print(out)

# ===================================================================

'''
SAMPLE OUTPUT:
{
    file_name: xxx, 
    type: video/x-matroska, 
    size: 880.6MB, 
    added_on: 2022-02-04, 
    error: False, 
    link_type: direct/login
    forced_login: False (True when script retries download via login if non-login dl fails for any reason)
    src_url: https://sharer.pw/file/xxxxxxxx, 
    gdrive_link: https://drive.google.com/...
}
'''
