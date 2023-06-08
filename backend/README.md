Close this repo

```bash
cd bot_options
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
