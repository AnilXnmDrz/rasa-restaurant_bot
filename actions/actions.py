

from pprint import pprint
from typing import Any, Dict, List, Text, Union
import json
import requests
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

from rasa_sdk.events import SlotSet,EventType

base_url = "https://developers.zomato.com/api/v2.1/"
Key = "80a29f13bb2f0f227731b2a1999f4360"
header = {"User-agent": "curl/7.43.0",
          "Accept": "application/json", "user_key": Key}


'''class ActionGreetUser(Action):
    """
    Greet user for the first time he has opened the bot windows
    """

    def name(self) -> Text:
        return "action_greet_user"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        dispatcher.utter_message(text="hi, im here to help you find restaurant.")
        return []'''





'''class ActionCheckGeo(Action):
    def name(self) -> Text:
        return "action_check_geo"

    def run(
        self,
        dispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        URL = "https://geocode.search.hereapi.com/v1/geocode"
       
        location=tracker.get_slot('Location')
       
        geo_api_key = 'NrB2Ixxvzqi4FKGuN0ezYXVqP_kczfr6Yf362CEBGxg' 
        PARAMS = {'apikey':geo_api_key,'q':location[4:]} 

        # sending get request and saving the response as response object 
        city,latitude,longitude=None,None,None
        r = requests.get(url = URL, params = PARAMS) 
        data = r.json()
        print(data)
        if data:
            city=data['items'][0]['address']['city']
            latitude = data['items'][0]['position']['lat']
            longitude = data['items'][0]['position']['lng']
            print(latitude,longitude,city)
        else:
             dispatcher.utter_message(text="no service available at this location")

        return[SlotSet("City",city),SlotSet("Latitude",city),SlotSet("Longitude",city)]'''
      

class Action_zomato(Action):

    def name(self) -> Text:
        return "action_zomato_api"

    def Search(city_id, Coll_id, cuisine_id,):
        res_dic = {}
        available_restaurant = []
        cuisines =cuisine_id# ','.join(map(str, cuisine_id))
        collection =','.join(map(str, Coll_id))

        search_url = base_url+'search?entity_id=' + \
            str(city_id)+'&entity_type=city&count=3&cuisines=' + \
            str(cuisines)+'&collection_id='+str(collection)
        r = requests.get(search_url, headers=header)
        if r.ok:
            data = r.json()['restaurants']
            count = 0
            for rest in data:
                # pprint(rest)
                if count == 6:
                    break
                else:
                    res_dic[count] = {'name': rest['restaurant']['name'], 'address': rest['restaurant']['location']['address'],
                                      'link': rest['restaurant']['menu_url'], 'establishment': rest['restaurant']['establishment'], 'image': rest['restaurant']['featured_image']}
                    available_restaurant.append(res_dic[count])
                    #print(available_restaurant[count])
                    count += 1
        #available_restaurant=res_dic
        pprint(len(res_dic))
        return available_restaurant

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
   
        city_id=tracker.get_slot('City')
        coll_id=tracker.get_slot('Collection')
        cuisine_id=tracker.get_slot('Cuisines')
        available_res = Action_zomato.Search(city_id, coll_id, cuisine_id)
        print("passed result of restaurant",available_res[0])   
        rname1=available_res[0]['name']
        rname2=available_res[0]['name']
        rname3=available_res[0]['name']
        rname4=available_res[0]['name']
        rname5=available_res[0]['name']
        link1=available_res[0]['link']
        link2=available_res[0]['link']
        link3=available_res[0]['link']
        link4=available_res[0]['link']
        link5=available_res[0]['link']
        
                 
        dispatcher.utter_message(template="utter_lc_based_result",name1=rname1,link1=link1,name2=rname2,link2=link2,name3=rname3,link3=link3,name4=rname4,link4=link4,name5=rname5,link5=link5)
     
        return []


class GetCityid(Action):
    def name(self) -> Text:
        return "action_validate_city"

    def getcityid(city):
        #city=input("enter city")
        city_id = None
        city_url = base_url+'cities?q='+city
        print("url for location", city_url)

        r = requests.get(city_url, headers=header)
        print("r is", r)
        if r.ok and r.json()['location_suggestions']:
            data = r.json()

            pprint(data)
            for result in data['location_suggestions']:
                print("availabe restaurant are {0} and id are {1}".format(
                    result['name'], result['id']))
                city_id = (result['id'])
                break

        else:
            print("not found")
            

        return city_id
    def collection(city_id):
    
        coll_id = []
        collection_url = base_url+'collections?city_id='+str(city_id)
        print("collection url", collection_url)
        res = requests.get(collection_url, headers=header)
        data = res.json()
        if res.ok and "collections" in data.keys():
            
            # pprint(data)
            for result in data['collections']:
                print("result", result)
                coll_id.append(result['collection']['collection_id'])
        return coll_id    
        
    def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        data=tracker.latest_message.get('text')
        
        city = data[5:]#tracker.get_slot('Location')
        city_id = GetCityid.getcityid(city)
        coll_id =GetCityid.collection(city_id)

        if city_id== None or coll_id==[]:
            dispatcher.utter_message(template="utter_change_location")
            return []
        
        else:
            dispatcher.utter_message(template="utter_ask_Cuisine")
            return[SlotSet('City',city_id),SlotSet('Collection',coll_id)]    


class GetCusineid(Action):
    def name(self) -> Text:
        return "action_validate_cuisine"
    def search_cusine(city_id, desired_c):
        cuisines_id = None
        cuisine_name=desired_c
        cuisine_url = base_url+'cuisines?city_id='+str(city_id)
        r = requests.get(cuisine_url, headers=header)
        if r.ok:
            d=json.loads(r.text)
            data = d['cuisines']

            
            for wanted in data:
                    #print("outside wanted", wanted)
                if (cuisine_name).lower() == (wanted['cuisine']['cuisine_name']).lower():
                    print("wanted cuisine matched")
                    #matched cuisine cty id
                    cuisines_id=(wanted['cuisine']['cuisine_id'])
                    break

        return cuisines_id 
    def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        data=tracker.latest_message.get('text')   
        usr_cuisine = data[4:]#tracker.get_slot('Cuisines')

        city_id=tracker.get_slot('City')
        print("user cuisne", usr_cuisine)

        cuisine_id = GetCusineid.search_cusine(city_id, usr_cuisine)
        print("cuisine id",cuisine_id)
        if cuisine_id == None:
            dispatcher.utter_message(template="utter_change_cuisine")
            return []
        else:
            dispatcher.utter_message(template="action_zomato_api")
            return [SlotSet("Cuisines",cuisine_id)]        

class ActionShowUrl(Action):
    """
    Greet user for the first time he has opened the bot windows
    """

    def name(self) -> Text:
        return "action_show_url"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        url=tracker.get_slot('url')
        dispatcher.utter_message(template="utter_display_url",link=url)
        return []
        