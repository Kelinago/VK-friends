# VK-friends

# Getting started

```
git clone https://github.com/Kelinago/VK-friends
```

### Prerequisites

After cloning please run 

```
pip install -r requirements.txt
```

Then paste your VK application's settings

```
    ...
    "APP_ID": "YOUR_APP_ID",
    "APP_CODE": "YOUR_APP_ENCRYPTED_KEY",
    ...
```
If you want to use it not on localhost you should also configure redirect uris in config.json and templates/index.html

### Running

```
export FLASK_APP=app.py
flask run
```
