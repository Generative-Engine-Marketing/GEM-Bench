from .prompts import *
from .ChatHistory import ChatHistory
from .API import OpenAIAPI
from .Products import Products
from .Topics import Topics
import random, re


class Advertiser:
    def __init__(self, product_list_path: str, topic_list_path: str, mode:str='control', ad_freq:float=1.0, demographics:str='', verbose:bool=False):
        self.oai_api = OpenAIAPI()
        self.mode = mode
        self.system_prompt = ''
        self.products = Products(product_list_path, verbose=verbose)
        self.topics = Topics(topic_list_path, verbose=verbose)
        self.chat_history = ChatHistory()
        self.personality = ''
        self.profile = demographics
        self.verbose = verbose
        self.ad_freq = ad_freq
        self.product = {'name': None, 'url': None, 'desc': None}
        self.topic = None
        
        # Initialize mode-specific prompts, different prompting strategies
        if mode == 'interest-based':
            self.initializer = SYS_INTEREST
            self.initializer_desc = SYS_INTEREST_DESC
        elif mode == 'chatbot-centric':
            self.initializer = SYS_CHATBOT_CENTRIC_INTEREST
            self.initializer_desc = SYS_CHATBOT_CENTRIC_INTEREST_DESC
        elif mode == 'user-centric':
            self.initializer = SYS_USER_CENTRIC_INTEREST
            self.initializer_desc = SYS_USER_CENTRIC_INTEREST_DESC
        elif mode == 'influencer':
            self.initializer = SYS_INFLUENCER_INTEREST
            self.initializer_desc = SYS_INFLUENCER_INTEREST_DESC
        else:
            self.initializer = 'You are a helpful assistant.'
            self.system_prompt = self.initializer
            self.mode = 'control'
            
    def parse(self, prompt:str):
        
        if self.mode == 'control':
            self.set_sys_prompt()
            self.chat_history.add_message(role='system', content=self.system_prompt)
            self.chat_history.add_message(role='user', content=prompt)
            return None
        
        profile = self.profile
        topic = self.topics.find_topic(prompt)
        if topic:
            product = self.products.assign_relevant_product(prompt, topic, profile)
            if self.verbose: print('product: ', product)
            idx = self.products()[topic]['names'].index(product)
            product = {'name': self.products()[topic]['names'][idx], 'url': self.products()[topic]['urls'][idx], 'desc': None}
            try:
                product['desc'] = self.products()[topic]['descs'][idx]
            except Exception:
                product['desc'] = None
        else:
            product = {'name': None, 'url': None, 'desc': None}
        self.product = product
        self.topic = topic
        

        self.set_sys_prompt(self.product, profile)
        self.chat_history.add_message(role='system', content=self.system_prompt)
        self.chat_history.add_message(role='user', content=prompt)
        if self.verbose: print(self.chat_history())
        return self.product

    def set_sys_prompt(self, product=None, profile=None):
        kwargs = {}
        if product:
            kwargs['product'] = product['name']
            kwargs['url'] = product['url']
            kwargs['desc'] = product['desc']
            kwargs['personality'] = self.personality
            kwargs['profile'] = profile
        if self.mode == 'control' or random.random() > self.ad_freq or not product:
            self.system_prompt = 'You are a helpful assistant.'
        elif profile:
            if product['desc']:
                self.system_prompt = self.initializer_desc.format(**kwargs)
            else:
                self.system_prompt = self.initializer.format(**kwargs)
        else:
            if product['desc']:
                self.system_prompt = SYS_INTEREST_DESC.format(**kwargs)
            else:
                self.system_prompt = SYS_INTEREST.format(**kwargs)

    def check_relevance(self, new_prompt:str, product:dict):
        kwargs = {'product': product['name'], 'desc': product['desc'], 'prompt': new_prompt}
        message, _ = self.oai_api.handle_response(SYS_CHECK_RELEVANCE, USER_CHECK_RELEVANCE.format(**kwargs))
        match = 10
        numbers = re.findall(r'\d+', message)
        if len(numbers) > 0:
            match = int(numbers[0])
        if int(match) > 4:
            return True
        else:
            print('LOW RELEVANCE: {}'.format(message))
            return False

    def change_ad_frequency(self, freq):
        self.ad_freq = freq
