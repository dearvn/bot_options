Close this repo

```bash
git clone https://github.com/dearvn/bot_options.git
```

# Create refresh token of TDA

## STEP 1
Open backend folder of this project by PyCharm and create an venv enviroment

![Alt text](https://github.com/dearvn/bot_options/raw/main/step1.png?raw=true "step1")


## STEP 2
PyCharm will create venv automaticly

![Alt text](https://github.com/dearvn/bot_options/raw/main/step2.png?raw=true "step2")


## STEP 3
Go to backend folder and active environment
```bash
cd bot_options/backend
```

```bash
. ./venv/bin/activate
```

![Alt text](https://github.com/dearvn/bot_options/raw/main/step3.png?raw=true "step3")

## STEP 4
Install app

```bash
pip install -e ./app
```

![Alt text](https://github.com/dearvn/bot_options/raw/main/step4.png?raw=true "step4")


## STEP 5
Go to app folder and download chromedriver(please choose a version of chromedriver compatible with Chrome browser)
and save to worker folder

https://chromedriver.chromium.org/downloads

```bash
cd app
```

![Alt text](https://github.com/dearvn/bot_options/raw/main/step5.png?raw=true "step5")


## STEP 6
Change value param in file: worker/token.php

![Alt text](https://github.com/dearvn/bot_options/raw/main/step6.png?raw=true "step6")


## STEP 7
Run script and input user name and password on TDA and follow step on TDA to complete get token

```bash
python -m worker.token
```

![Alt text](https://github.com/dearvn/bot_options/raw/main/step7.png?raw=true "step7")


