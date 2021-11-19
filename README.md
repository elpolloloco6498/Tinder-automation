# tinder-swiper
Tinder swiper is a program that enables you to automatically swipe on tinder. The main feature of this program is the ability to swipe based on a score that is computed for a profil. Each profil is given a score based on beauty, the program check every pictures of the profils and makes the decision to like or pass.

## How to use Tinder swiper
Using tinder swiper is pretty straight forward.
You will need to install Python on your machine.
Additionnaly you will need to install the python modules listed in the program.
Furthermore it is necessary to generate API keys for tinder and faceplusplus.

### Generating the api keys
#### API auth key tinder
Let's generate the API auth key for Tinder.
Navigate to your favorite browser and go on the tinder website, login.
Now that you are on the main page of tinder, right click, inspect element and type the following code inside the console to reveal your API authorization key.
localStorage.getItem('TinderWeb/APIToken')
#### API auth faceplusplus
Face++ is an API service that is used to rate image based on physical appearance.
Go the faceplusplus website and create an account.
Once the account is created you will have access to your keys.

Replace thoses keys in the code.

### Launching the program
python3 tinder_swiper.py

