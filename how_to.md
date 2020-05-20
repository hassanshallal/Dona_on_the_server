#### There are two parts: 
1. Creating an environment.
2. Running training and inference.

==========================================================================

#### Creating an environment
                      
1. Please open a terminal and make sure the current directory is /Volumes/external/algoromida/algoChat/Dona_2.0/deployment

2. On the terminal, type the following:
```bash
sudo apt install python3.7 python3-venv python3.7-venv python3.7-dev

python3.7 -m venv deploy
source deploy/bin/activate 
python3.7 -m pip install -r requirements.txt

pip install --pre torch torchvision -f https://download.pytorch.org/whl/nightly/cu101/torch_nightly.html
```
Please note that installing the packages in the requirements.txt may take sometime.

In order to deactivate the environment:
```bash
deactivate
```

3. Run corpora.py in order to download the stopwords using nltk.download(). After running this script, please wait for a few seconds for the nltk.download() window to open. Navigate to corpora and select stopwords and hit download. On the terminal:
```bash
python3 corpora.py
```

5. Download Spacy model used for preprocessing and cleaning.
```bash
python3 -m spacy download en_core_web_md
```
