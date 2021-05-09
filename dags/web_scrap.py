from bs4 import BeautifulSoup
from requests import get
import pandas as pd


def test_connection():
    '''
    Testing the connection to the webpage
    '''
    headers = ({'User-Agent':
                'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36'})
    #Sample rentals.ca website
    rentals = "https://rentals.ca/toronto?p=2"
    response = get(rentals, headers=headers)
    #200 is a good response
    print("we are getting response of:", response)

    return headers

def scrapping_rentals_ca(pagenum = 2):

    headers = test_connection()

    #Initialize the final dict for return
    dic = {'name':[], 'price': [], 'latitude': [], 'longitude': [], 'url': [], 'location': [], 'room_type': []}
    k=1
    new_url=""
    #Initialize the link
    initial_link = 'https://rentals.ca/toronto?p='
    #Go to the specificied link page and get the housing info
    for idx in range(pagenum):
        link = initial_link + str(idx+1)
        response = get(link, headers=headers)
        html_soup = BeautifulSoup(response.text, 'html.parser')

        all_script = html_soup.find_all('script')

        json_list = []
        for item in all_script:
            if str(item).startswith('''<script type="applic'''):
                json_list.append(str(item))
        
        #For each webpage, save its info in a temp list and then add to dictionary
        for item in json_list:
            i = 1
            j = 1
            temp_room_type = []
            temp_price = []
            temp_name = []
            for words in item.split('\n'):
                if words.strip()[:6] == '''"name"''':
                    if i == 1:
                        temp_name.append(words.strip()[7:-1].strip().strip('\"'))
                        i += 1
                    elif i == 2:
                        dic['location'].append(''.join(e for e in words.strip()[7:-1] if e.isalnum()))
                        i += 1
                    else:
                        temp_room_type.append(words.strip()[7:-1].strip().strip('\"'))
                        
                if words.strip()[:7] == '''"price"''':
                    temp_price.append(float(words.strip()[8:].strip()[:-1]))
                if words.strip()[:10] == '''"latitude"''':
                    dic['latitude'].append(float(words.strip()[11:].strip()[:-1]))
                if words.strip()[:11] == '''"longitude"''':
                    dic['longitude'].append(float(words.strip()[12:].strip()[:-1]))
                if words.strip()[:5] == '''"url"''' and j == 1:
                    dic['url'].append(words.strip()[6:-1].strip().strip('\"'))
                    j += 1
            if len(temp_room_type) == 0 and len(temp_price) == 0:
                if len(temp_name) != 0:
                    temp_name.pop()
            else:
                dic['name'].append(temp_name)
                dic['room_type'].append(temp_room_type)
                dic['price'].append(temp_price)
                #print("Iteration {}, dictionary length now is {}".format(idx, [len(x) for x in dic.values()]))
                
            if len(dic['url'])!=0 and dic['url'][-1]!=new_url:
                sub_name=dic['name'][-1]
                print(sub_name)
                new_url=dic['url'][-1]
                print(new_url)

                #Extract from new_url
                sub_response = get(new_url, headers=headers)

                sub_html_soup = BeautifulSoup(sub_response.text, 'html.parser')

                sub_all_script = sub_html_soup.find_all('script')

                sub_json_list = []
                for sub_item in sub_all_script:
                    if str(sub_item).startswith('''<script type="text/javascript"'''):
                        sub_json_list.append(str(sub_item))
                
                #Features, amentities, utilities
                start=sub_json_list[1].find("raw_amenities")
                end=sub_json_list[1].find("categories")

                sub_feature=sub_json_list[1][start:end]

                first_split=sub_feature.split('"name": ')
                second_split=[x.split(', "slug"')[0] for x in first_split]
                sub_feature_info=[x for x in second_split if x not in ['"Building Features"','"Unit Features"','"Utilities"']][1:]

                feature_df=pd.DataFrame(sub_feature_info,columns = ['Features'] )
                sub_feature_info=pd.get_dummies(feature_df['Features']).max(axis=0).to_frame().T
                sub_feature_info['name'] = sub_name 
                sub_feature_info['url'] = new_url 
                
                #Extract unit info: room_type, price,Bedroom, Bathroom
                start_unit=sub_json_list[1].find("units")
                end_unit=sub_json_list[1].find("photos")
                unit_info=sub_json_list[1][start_unit:end_unit]
                
                unit_split=unit_info.split(', ')
    
                beds=[]
                baths=[]

                for item in unit_split:
                    if str(item).startswith('''"beds":'''):
                        beds.append(str(item)[8:])
                for item in unit_split:
                    if str(item).startswith('''"baths":'''):
                        baths.append(str(item)[9:])
                        
                sub_feature_info['"bedroom_num"'] = str(beds)[1:-1]
                sub_feature_info['"bathroom_num"'] = str(baths)[1:-1] 
                
                if k == 1:
                    final_sub_feature=sub_feature_info
                    k += 1
                else:
                    frames = [final_sub_feature, sub_feature_info]
                    final_sub_feature=pd.concat(frames)

    print(dic, final_sub_feature)

    return dic,final_sub_feature

