import re
import torch
import csv

import argparse
from model import DeepPunctuation
from config import *

parser = argparse.ArgumentParser(description='Punctuation restoration inference on text file')
parser.add_argument('--cuda', default=True, type=lambda x: (str(x).lower() == 'true'), help='use cuda if available')
parser.add_argument('--pretrained-model', default='bert-base-uncased', type=str, help='pretrained language model')
parser.add_argument('--lstm-dim', default=-1, type=int,
                    help='hidden dimension in LSTM layer, if -1 is set equal to hidden dimension in language model')
parser.add_argument('--user-input', default='test_en.txt', type=str, help='path to inference file')
parser.add_argument('--weight-path', default='out/weights.pt', type=str, help='model weight path')
parser.add_argument('--sequence-length', default=256, type=int,
                    help='sequence length to use when preparing dataset (default 256)')
parser.add_argument('--out-file', default='data/inference-result.txt', type=str, help='output file location')

args = parser.parse_args()

# tokenizer
tokenizer = MODELS[args.pretrained_model][1].from_pretrained(args.pretrained_model)
token_style = MODELS[args.pretrained_model][3]

# logs
model_save_path = args.weight_path

# Model
device = torch.device('cuda' if (args.cuda and torch.cuda.is_available()) else 'cpu')
deep_punctuation = DeepPunctuation(args.pretrained_model, freeze_bert=False, lstm_dim=args.lstm_dim)
deep_punctuation.to(device)


def infer_nothing(word):
    return word


def to_titlecase(word):
    return word.title()


def inference():
    print('Loading model for inference')
    deep_punctuation.load_state_dict(torch.load(model_save_path, map_location=device))
    deep_punctuation.eval()
    print('Done')

    with open(args.user_input, 'r', encoding='utf-8') as f:
        csv_reader = csv.DictReader(f)

        count = 0
        for row in csv_reader:
            line = row['01_nb']
            line = re.sub(r"[,:\-–.!;?]", '', line)
            words_original_case = line.split()
            words = line.lower().split()

            word_pos = 0
            sequence_len = args.sequence_length
            result = ""
            decode_idx = 0
            punctuation_map = {0: '', 1: ',', 2: '.', 3: '', 4: '.', 5: ','}
            function_map = {0: infer_nothing, 1: infer_nothing, 2: infer_nothing, 3: to_titlecase, 4: to_titlecase,
                            5: to_titlecase}

            while word_pos < len(words):
                x = [TOKEN_IDX[token_style]['START_SEQ']]
                y_mask = [0]

                while len(x) < sequence_len and word_pos < len(words):
                    tokens = tokenizer.tokenize(words[word_pos])
                    if len(tokens) + len(x) >= sequence_len:
                        break
                    else:
                        for i in range(len(tokens) - 1):
                            x.append(tokenizer.convert_tokens_to_ids(tokens[i]))
                            y_mask.append(0)
                        x.append(tokenizer.convert_tokens_to_ids(tokens[-1]))
                        y_mask.append(1)
                        word_pos += 1

                x.append(TOKEN_IDX[token_style]['END_SEQ'])
                y_mask.append(0)

                if len(x) < sequence_len:
                    x = x + [TOKEN_IDX[token_style]['PAD'] for _ in range(sequence_len - len(x))]
                    y_mask = y_mask + [0 for _ in range(sequence_len - len(y_mask))]
                attn_mask = [1 if token != TOKEN_IDX[token_style]['PAD'] else 0 for token in x]

                x = torch.tensor(x).reshape(1, -1)
                y_mask = torch.tensor(y_mask)
                attn_mask = torch.tensor(attn_mask).reshape(1, -1)
                x, attn_mask, y_mask = x.to(device), attn_mask.to(device), y_mask.to(device)

                with torch.no_grad():
                    y_predict = deep_punctuation(x, attn_mask)
                    y_predict = y_predict.view(-1, y_predict.shape[2])
                    y_predict = torch.argmax(y_predict, dim=1).view(-1)

                for i in range(y_mask.shape[0]):
                    if y_mask[i] == 1:
                        identified_class = y_predict[i].item()
                        target_punctuation = punctuation_map[identified_class]
                        target_word = words_original_case[decode_idx]
                        transform_function = function_map[identified_class]
                        result += transform_function(target_word) + target_punctuation + ' '
                        decode_idx += 1

            print(f'Storing punctuated text - {count}')
            count += 1
            with open(args.out_file, 'a', encoding='utf-8') as f:
                f.write(line + ",")
                f.write("\"" + result + "\"")
                f.write("\n")


if __name__ == '__main__':
    inference()
