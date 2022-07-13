# Punctuation Restoration using Transformer Models

This repository is an extension of the paper [*Punctuation Restoration using Transformer Models for High-and Low-Resource Languages*](https://aclanthology.org/2020.wnut-1.18/) accepted at the EMNLP workshop [W-NUT 2020](http://noisy-text.github.io/2020/).


## Data

#### Datasets
TedTalk datasets are provided in `data` directory.


## Model Architecture
We fine-tune a Transformer architecture based language model (e.g., BERT) for the punctuation restoration task.
Transformer encoder is followed by a bidirectional LSTM and linear layer that predicts target punctuation token at
each sequence position.
![](./assets/model_architectue.png)


## Dependencies
Install PyTorch following instructions from [PyTorch website](https://pytorch.org/get-started/locally/). Remaining
dependencies can be installed with the following command
```bash
pip install -r requirements.txt
```


## Training
To train punctuation restoration model with optimal parameter settings for English run the following command
```
bash src/run-train.sh
```

#### Target models for finetuning
```
bert-base-uncased
```


## Inference
You can run inference on unprocessed text file to produce punctuated text using `inference` module. Note that if the 
text already contains punctuation they are removed before inference. 

Example script for English:
```bash
bash src/run-inference.sh
```


## Test
Trained models can be tested on processed data using `test` module to prepare result.

For example, to test the best preforming English model run following command
```bash
bash run-test.py
```
