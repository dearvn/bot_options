Close this repo

```bash
git clone https://github.com/dearvn/bot_options.git
```

Open backend folder of this project by PyCharm and create an venv enviroment

![Alt text](https://github.com/dearvn/bot_options/raw/main/step1.png?raw=true "step1")


```bash
cd bot_options/backend
```

## Installation to test on local not use docker
```bash

# Create an isolated Python virtual environment
pip3 install virtualenv
virtualenv ./virtualenv --python=$(which python3)

# Activate the virtualenv
# IMPORTANT: it needs to be activated every time before you run
. virtualenv/bin/activate

# Install Python requirements
pip install -r requirements.txt

Go to parent folder
# Install
pip install -e ./app
```
