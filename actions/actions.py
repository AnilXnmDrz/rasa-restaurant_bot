# This files contains your custom actions which can be used to run
# custom Python code.

# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions

# This is a simple example for a custom action which utters "Hello World!"


from typing import Any, Text, Dict, List
from rasa_sdk.forms import FormAction
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
import requests
from pprint import pprint
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


class ActionFormInfo(FormAction):
    def name(self) -> Text:
       
        return "restaurant_form"

    @staticmethod
    def required_slots(tracker: Tracker) -> List[Text]:
       
        return ["location", "cuisines"]
    
    def check(city_id,usr_cuisine): 
        result=''
        
        if city_id == None:
            print("city is none")
            result+="no service found at your provided location "
        if usr_cuisine == None:
            print("cuisine is none")
            result+="Either the cusine name is incorrect or not available at your city"
        else:
            result+="everything is fine"
        print("result is ",result)
        return result    
               

    def submit(
            self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any],
    ) -> List[Dict]:
        city_id = Action_zomato.getlocation(city=tracker.get_slot('location'))
        cuisines= tracker.get_slot('cuisines')
        usr_cuisine = Action_zomato.search_cusine(city_id,cuisines)
        result=ActionFormInfo.check(city_id,usr_cuisine)
        
        
        dispatcher.utter_message(template="utter_submit", res=result)
        return []
    
    

class Action_zomato(Action):

    def name(self) -> Text:
        return "action_zomato_api"

    def getlocation(city):
        #city=input("enter city")
        city_id = None
        city_url = base_url+'cities?q='+city
        print("url for location", city_url)

        r = requests.get(city_url, headers=header)
        print("r is", r)
        if r.ok:
            data = r.json()

            pprint(data)
            for result in data['location_suggestions']:
                print("availabe restaurant are {0} and id are {1}".format(
                    result['name'], result['id']))
                city_id = (result['id'])

        else:
            print("not found")

        return city_id

    def collection(city_id):

        coll_id = []
        collection_url = base_url+'collections?city_id='+str(city_id)
        print("collection url", collection_url)
        res = requests.get(collection_url, headers=header)

        if res.ok:
            data = res.json()
            # pprint(data)
            for result in data['collections']:
                print("result", result)
                coll_id.append(result['collection']['collection_id'])
        return coll_id

    def search_cusine(city_id, desired_c):
        cuisines_id = []

        cuisine_url = base_url+'cuisines?city_id='+str(city_id)
        r = requests.get(cuisine_url, headers=header)
        if r.ok:

            data = r.json()['cuisines']

            for cusine_name in desired_c:
                for wanted in data:
                    #print("outside wanted", wanted)
                    if (cusine_name).lower() == (wanted['cuisine']['cuisine_name']).lower():
                        print("wanted cuisine", wanted)
                        # matched cuisine cty id
                        cuisines_id.append(wanted['cuisine']['cuisine_id'])
                        break

        return cuisines_id

    def Search(city_id, Coll_id, cuisine_id,):
        res_dic = {}
        available_restaurant = []
        cuisines = ','.join(map(str, cuisine_id))
        collection = ','.join(map(str, Coll_id))

        search_url = base_url+'search?entity_id=' + \
            str(city_id)+'&entity_type=city&count=3&cuisines=' + \
            cuisines+'&collection_id='+collection
        r = requests.get(search_url, headers=header)
        if r.ok:
            data = r.json()['restaurants']
            count = 0
            for rest in data:
                # pprint(rest)
                if count == 6:
                    break
                else:
                    res_dic[count] = {'r_name': rest['restaurant']['name'], 'address': rest['restaurant']['location']['address'],
                                      'link': rest['restaurant']['menu_url'], 'establishment': rest['restaurant']['establishment'], 'image': rest['restaurant']['featured_image']}
                    available_restaurant.append(res_dic[count])
                    count += 1
        pprint(len(res_dic))
        return available_restaurant

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        city = tracker.get_slot('location')
        city_id = Action_zomato.getlocation(city)
        coll_id = Action_zomato.collection(city_id)
        usr_cuisine = tracker.get_slot('cuisines')

        print("user cuisne", usr_cuisine)

        cuisine_id = Action_zomato.search_cusine(city_id, usr_cuisine)
        available_res = Action_zomato.Search(city_id, coll_id, cuisine_id)

        # "utter_lc_based_result",tracker,result=available_res)
        dispatcher.utter_template(
            "utter_lc_based_result", tracker, result=available_res)
        return []
