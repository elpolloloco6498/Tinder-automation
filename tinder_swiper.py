from numpy import mat
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests
import re
from PIL import Image
import imagehash
from io import BytesIO
from random import randint
from random import random
import time
import json

class TinderSwiper:
    def __init__(self):
        self.api_tinder_auth = "your tinder auth key"
        self.faceplusplus_api_key = "your face++ key"
        self.aceplusplus_api_secret = "your face++ secret"
        self.faceplusplus_api_url = "https://api-us.faceplusplus.com/facepp/v3/detect"
        self.tinder_api_likes_url = "https://api.gotinder.com/v2/fast-match/teasers"
        self.tinder_api_recs_url = "https://api.gotinder.com/user/recs"
        self.min_score_swipe = 35
        self.nb_profil_liked = 0
        self.nb_profil_swiped = 0

    def rand_sleep(self) -> None:
        nb = randint(1,6)
        #print(f"sleeping for {nb}s")
        time.sleep(nb)

    def swipe_left(self, profil):
        r = requests.get(f"https://api.gotinder.com/pass/{profil['_id']}", headers={"X-Auth-Token": self.api_tinder_auth})
        if r.status_code == 200:
            print("PASS")
        else:
            print("Failure could not pass the profil")

    def swipe_right(self, profil)->None:
        r = requests.get(f"https://api.gotinder.com/like/{profil['_id']}", headers={"X-Auth-Token": self.api_tinder_auth})
        if r.status_code == 200:
            match = r.json()["match"]
            self.nb_profil_liked += 1
            print("LIKE")
            if match: print("It's a match !")
        else:
            print("Failure could not like profil")

    def get_url_pictures_from_profile_likes(self):
        #this function computes a hash for each profile picture of the likes canvas.
        r = requests.get("https://api.gotinder.com/v2/fast-match/teasers", headers={"X-Auth-Token": self.api_tinder_auth})
        print(r)
        if r.status_code == 200:
            print("success request likes")
            list_profils = r.json()["data"]["results"]
            profils_preview_url_list = [profil["user"]["photos"][0]["url"] for profil in list_profils]
            return profils_preview_url_list
        else:
            print("failure request likes")
            return None
    
    def get_image_hash_from_url(self, url):
        r = requests.get(url)
        hash = imagehash.average_hash(Image.open(BytesIO(r.content))) 
        #print(hash)
        return hash

    def get_hashlist_from_profils_likes(self):
        urls = self.get_url_pictures_from_profile_likes()
        hashs = [self.get_image_hash_from_url(url) for url in urls]
        return hashs

    def profil_in_likes(self, url, hashs_profils)->bool:
        eps = 5
        image_hash = self.get_image_hash_from_url(url)
        for preview_image_hash in hashs_profils:
            if preview_image_hash - image_hash < eps:
                print("It's a match !")
                return True
        return False

    def swipe_like_profils(self, profil, hashs_profils)->None:
        url = self.get_url_profil_pic(profil)
        if self.profil_in_likes(url, hashs_profils):
            print("This profil is in likes")
            self.swipe_right(profil)
        else:
            print("This profil is not in likes")
    
    def swipe_random(self, profil)->None:
        if random() < 0.8:
            self.swipe_right(profil)
        else:
            self.swipe_left(profil)
    
    def get_beauty_score_from_img_url(self, url)->float:
        params = {"image_url": url, "api_key": self.faceplusplus_api_key, "api_secret": self.aceplusplus_api_secret, "return_attributes": "beauty"}
        data = requests.post(self.faceplusplus_api_url, params=params).json()
        if data["faces"]:
            beauty_score = data["faces"][0]["attributes"]["beauty"]["female_score"]
        else:
            beauty_score = 0
        return beauty_score

    def get_score_profil(self, urls)->float:
        #computes the score of a profil
        score = 0
        for url_img in urls:
            score += self.get_beauty_score_from_img_url(url_img)
        final_score = score/len(urls)
        return final_score
    
    def swipe_based_on_score(self, profil)->None:
        urls = self.get_urls_profil_images(profil)
        score = self.get_score_profil(urls)
        print(f"score : {score}")
        if score > self.min_score_swipe:
            self.swipe_right(profil)
        else:
            self.swipe_left(profil)

    def swipe(self, profil, only_likes=False, swipe_ai = False, hashs_profils_likes=None) -> None:
        if only_likes:
            url = self.get_url_profil_pic(profil)
            self.swipe_like_profils(profil, hashs_profils_likes)
        elif swipe_ai:
            self.swipe_based_on_score(profil)
        else:
            self.swipe_random()
        self.nb_profil_swiped += 1
        self.rand_sleep()

    def get_recs(self):
        r = requests.get(self.tinder_api_recs_url, headers={"X-Auth-Token": self.api_tinder_auth})
        if r.status_code == 200:
            profils = r.json()["results"]
            return profils
        else:
            return None

    def get_urls_profil_images(self, profil):
        urls = list()
        for pic in profil["photos"]:
            urls.append(pic["processedFiles"][0]["url"])
        return urls
    
    def get_url_profil_pic(self, profil):
        return self.get_urls_profil_images(profil)[0]

    def run(self, only_likes=False, swipe_ai=False, iter=1):
        hash_urls_profils_like = self.get_hashlist_from_profils_likes()
        for i in range(iter):
            print(f"Recommandation set : nb {i}\n")
            profils = self.get_recs() #update recommandations
            for profil in profils:
                self.display(profil)
                self.swipe(profil, only_likes=only_likes, swipe_ai=swipe_ai, hashs_profils_likes=hash_urls_profils_like)
                print("\n")
        print(f"nb profil liked : {self.nb_profil_liked}")
        print(f"nb profil passed : {self.nb_profil_swiped-self.nb_profil_liked}")

    def display(self, profil):
        print(f"name : {profil['name']}")
        print(f"distance : {profil['distance_mi']*1.6} km")
        print(f"pic : {self.get_url_profil_pic(profil)}")

#TODO create launch mode options for script

tinder = TinderSwiper()
tinder.run(swipe_ai=True, iter=2)

