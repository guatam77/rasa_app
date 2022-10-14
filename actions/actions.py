# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions
# This is a simple example for a custom action which utters "Hello World!"
from typing import Any, Text, Dict, List
from rasa_sdk.types import DomainDict
from rasa_sdk import Action, Tracker,FormValidationAction
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet,UserUttered
import datetime
import re
import json
import requests
from datetime import date, timedelta
import yaml
from yaml.loader import SafeLoader
class ActionHelloWorld(Action):

    def name(self) -> Text:
        return "action_greet"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        dispatcher.utter_message(response="utter_greet")
        

class Actionemail(Action):

    def name(self) -> Text:
        return "action_email"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        pat = "^[a-zA-Z0-9-_.]+@[a-zA-Z0-9]+\.[a-z]{1,3}$"
        email = tracker.get_slot('validate_email')
        intent = tracker.latest_message['intent']
        if intent['name'] != 'email':
            dispatcher.utter_message(text="Please enter valid email")
        elif not re.match(pat,email):
            dispatcher.utter_message(text="Please enter valid email")
        else:
            dispatcher.utter_message(response="utter_email")
        return [SlotSet('city',None),SlotSet('month',None),SlotSet('start_date',None),SlotSet('end_date',None),SlotSet('hotel',None)]    

class ValidateHotelEnquiryForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_hotel_enquiry_form" 
    # def validate_country(
    #     self,
    #     slot_value: Any,
    #     dispatcher: CollectingDispatcher,
    #     tracker: Tracker,
    #     domain: DomainDict,
    # ) -> Dict[Text, Any]:
    #     guest_country = tracker.get_slot('country')
    #     intent = tracker.latest_message['intent']
    #     print("guest country .." , guest_country)
    #     print("after 1st return")
    #     if len(guest_country) == 0:
    #         dispatcher.utter_message(text="Please enter your country name ")
    #         return {'country':None}     
    #     elif intent['name'] != 'guest_country':
    #         dispatcher.utter_message(text=" will you please write correct country name ? ")
    #         return {'country':None}
    #     else:
    #         return {'country':slot_value}
    def validate_city(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        res = []
        cityname = tracker.get_slot('city')
        en = tracker.latest_message['entities']
        print(en)
        intent = tracker.latest_message['intent']
        if intent['name'] != 'location':
            dispatcher.utter_message(text="😑 Please enter valid city name !")
            return {"city": None}
        elif cityname == None:
            dispatcher.utter_message(text="👉 sorry , I didn't get it. Please enter valid city name !")
            return {"city": None}
        elif en[0]['entity'] != 'city':
            dispatcher.utter_message(text="👉 sorry , I didn't get it.Please enter valid city name !")
            return {"city": None}
        elif len(en) == 0:
            dispatcher.utter_message(text="🥺 Please enter valid city name !")
            return {"city": None}
        elif cityname in res:
            dispatcher.utter_message(text=" 🥺 Please enter city name not country !  ")
            return {"city": None}
        else:
            return {"city": slot_value}
    def validate_month(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        intent = tracker.latest_message['intent']
        entities = tracker.latest_message['entities']
        print(entities,"month")
        months_arr = ['january', 'february', 'march', 'april', 'may', 'june', 'july','august', 'september', 'october', 'november', 'december','jan','feb','mar','aug','sept','nov','dec']
        months=tracker.get_slot('month')
        today = datetime.datetime.now()
        # month_number = datetime.datetime.strptime(months[:3], "%b").month
        if intent['name'] != 'dates':
            dispatcher.utter_message(text="please enter valid date")
            return {"month": None}
        elif months.lower() not in months_arr:
           dispatcher.utter_message(text="please enter valid month")
           return {"month": None}
        else:
            return {"month": slot_value}
        
    def validate_end_date(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        end_date = tracker.get_slot('end_date')
        intent = tracker.latest_message['intent']
        entities = tracker.latest_message['entities']
        print(entities,"month")
        if intent['name'] != 'dates':
            dispatcher.utter_message(text="please enter valid checkout date")
            return {"end_date": None}
        elif int(end_date) > 31:
            dispatcher.utter_message(text="please enter valid check out date")
            return {"end_date": None}
        else:
            return {"end_date": slot_value}

    def validate_start_date(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        today = datetime.datetime.now()
        intent = tracker.latest_message['intent']
        if len(slot_value) == 0:
            dispatcher.utter_message(text="please enter valid input")
            return {"start_date": None}
        entities = tracker.latest_message['entities']
        print(entities)
        start_date = tracker.get_slot('start_date')
        months=tracker.get_slot('month')
        month_number = datetime.datetime.strptime(months[:3], "%b").month
        if int(start_date) > 31:
            dispatcher.utter_message(text="please enter valid  check in date")
            return {"start_date": None}
       
        elif int(start_date) < today.day and month_number == today.month:
            dispatcher.utter_message(text="please enter future check in date")
            return {"start_date": None}  
        else:
            print(slot_value,"**** start date")
            return {"start_date": slot_value}  


class Actionsearch(Action):

    def name(self) -> Text:
        return "action_show_search"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        guestcountry = []
        hotel = dict()
        today = datetime.datetime.now()
        country_name = []
        iso = []
        city_id = []
        months = tracker.get_slot('month')
       
        checkin_date = '0' + str(tracker.get_slot('start_date')) if int(tracker.get_slot('start_date')) < 10 else tracker.get_slot('start_date')
        checkout_date = '0' + str(tracker.get_slot('end_date')) if int(tracker.get_slot('end_date')) < 10 else tracker.get_slot('end_date')
        month_number = datetime.datetime.strptime(months[:3], "%b").month
        travel_month = '0' + str(month_number) if month_number < 10 else month_number
        current_month = int(datetime.datetime.now().strftime("%m"))
        current_year = int(datetime.datetime.now().strftime("%Y"))
        travel_year = 1 + current_year if int(travel_month) <  current_month else current_year
        location = tracker.get_slot('city')
        print(months,checkin_date,checkout_date,location)

        #  below code to find country name from given city name by user

        f = open('city.json')
        country_data = json.load(f)
        temp = country_data['data']
        for i in temp:
            if location.title() in i['cities']:
                cntry = i['country']
                country_name.append(cntry)
        f.close()
        print(country_name[0])

        #  below code is to find country iso_code 
        
        f = open('country.json')
        data = json.load(f)
        for k, v in data.items():
            if k == country_name[0].lower():
                iso.append(v)
            # if k == country.lower():
            #     guestcountry.append(v)
        iso_code = iso[0].lower()
        f.close()
        #  @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ booking.com cred @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

        with open('creds.yml') as f:
            creds = yaml.load(f, Loader=SafeLoader)
            username = creds['booking_creds'][0]['Username']
            password = creds['booking_creds'][1]['Password']

        payload = {'countries':iso_code}
        def fetchCities():
            req = requests.get("https://distribution-xml.booking.com/2.9/json/cities?languages=en", auth=(username, password),params=payload)
            print(req.status_code)
            if req.status_code == 200:
                raw_data = req.json()
                for i in raw_data['result']:
                    if location == i['name']:
                        city_id.append(i['city_id'])
            else:
                dispatcher.utter_message(text="Invalid city name. Will you please repeat")

            return city_id
        city_id = fetchCities()
        print(city_id)
        details = {
            'checkin':str(travel_year) + "-" + str(travel_month) + "-" + checkin_date,
            'checkout':str(travel_year) + "-" + str(travel_month) + "-" + checkout_date,
            'room1' : 'A,A',
            'city_ids' : city_id[0],
            'extras': 'hotel_details',
            'guest_country': "in"
            }
        
        hotel_detail = requests.get('https://distribution-xml.booking.com/2.9/json/hotelAvailability',auth=(username, password),params = details )
        if hotel_detail.status_code == 200:
            data = hotel_detail.json()
            for i in data['result']:
                # print(i['hotel_name'])
                # print(i['price'])
                # print(i['hotel_id'])
                # print(i['stars'])
                # print(i['address'])
                hotel['hotel_name'] = i['hotel_name']
                hotel['price'] = i['price']
            
                output = {
                    "attachment":{
                        "type": "template",
                        "payload": {
                            "template_type": "generic",
                            "elements": [
                                {
                                    "title": hotel,
                                    "buttons":[
                                        {
                                            "type":"postback",
                                            "title": "view more",
                                            
                                        }
                                    ]
                                }
                            ]
                        }
                    }
                }
            dispatcher.utter_message(json_message=output)
        else:
            dispatcher.utter_message(text="Invalid response from request 2")
        return []

# class Actionweekend(Action):

#     def name(self) -> Text:
#         return "action_next_weekend"

#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
#         en = tracker.latest_message['text']
#         print(en)
#         today = date.today()
#         start = today - timedelta(days=today.weekday())
#         saturday = start + timedelta(days=5)
#         sunday = start + timedelta(days=6)
#         start_str = json.dumps(start, default=str)
#         sat_str = json.dumps(saturday,default=str)
#         sun_str = json.dumps(sunday,default=str)
#         month_str = json.dumps(today.month,default=str)
#         sd = tracker.get_slot("start_date")
#         dispatcher.utter_message(response="utter_search")
#         return [SlotSet('month',month_str),SlotSet('start_date',sat_str),SlotSet('end_date',sun_str)]       
       
    
    # def validate_month(
    #     self,
    #     slot_value: Any,
    #     dispatcher: CollectingDispatcher,
    #     tracker: Tracker,
    #     domain: DomainDict,
    # ) -> Dict[Text, Any]:
    #     """Validate cuisine value."""
       
    #     return {"month": slot_value}

    

   
