import argparse
import numpy as np
import os
from Levenshtein import distance as lev
from normalizer import normalize_text
from tqdm import tqdm

def parse_files(input):
    with open(input, 'r') as f:
        temp = f.read().split('\n')
    files = []
    for file in temp:
        files += file.split(' ')[:2]
    return files

def lev_distance(input, out):
    files = parse_files(input)
    ans = []
    texts = []
    for i in range(0, len(files) - 1, 2):
        file_1 = files[i]
        file_2 = files[i + 1]
        with open(file_1, 'r', encoding="utf8") as original:
            with open(file_2, 'r', encoding="utf8") as plagiat:
                a = normalize_text(original.read())
                b = normalize_text(plagiat.read())
                texts.append(a)
                texts.append(b)
                ans.append(1 - lev(a, b) / max(len(a), len(b)))
    return ans, texts

def fit_model(test_texts):
    texts = []
    dir = 'train'
    # Проверим, есть ли вообще нужна директория
    if dir not in os.listdir(): 
        print('Не был запущен скрипт train.py, нет обучающей директории.')
        return -1

    # Чтобы быстрее работал алгоритм, не требующий модельки
    from sentence_transformers import SentenceTransformer
    from sklearn.metrics.pairwise import cosine_similarity

    # Проходимся по директории текстов для обучения
    for file in tqdm(os.listdir(dir)):
        filename = os.fsdecode(file)
        if filename.endswith(".py"):
            with open(os.path.join(dir, filename), 'r', encoding='utf8') as f:
                texts.append(normalize_text(f.read()))
    texts += test_texts
    model = SentenceTransformer('bert-base-nli-mean-tokens')
    sentence_embeddings = model.encode(texts)
    scores = np.zeros((sentence_embeddings.shape[0], sentence_embeddings.shape[0]))
    for i in range(sentence_embeddings.shape[0]):
        scores[i, :] = cosine_similarity(
            [sentence_embeddings[i]],
            sentence_embeddings
        )[0]
    scores = scores[-len(test_texts):][-len(test_texts):]
    cos_dists = []
    for i in range(0, len(test_texts), 2):
        cos_dists.append(scores[i][i+1])
    
    return cos_dists


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Файлы для просмотра сходства')
    parser.add_argument('files_to_check', type=str, help='Входной файл с названиями скриптов')
    parser.add_argument('outfile', type=str, help='Файл для записи результатов')
    parser.add_argument('--model', type=int, default=0, help='Нужно ли использовать модель BERT(по умолчанию - нет), введите 1, если требуется модель')
    args = parser.parse_args()
    lev_dists, test_texts = lev_distance(args.files_to_check, args.outfile)

    if args.model == 1:
        cos_dists = fit_model(test_texts)
        if cos_dists == -1:
            with open(args.outfile, 'w') as f:
                f.write('Bad request!')
        else:
            # Усредняем полученные результаты косинусного расстояния и расстояния Левенштейна.
            with open(args.outfile, 'w') as f:
                for lev, cos in zip(lev_dists, cos_dists):
                    f.write(f'{(lev + cos) / 2}\n')

    else:
        with open(args.outfile, 'w') as f:
            for lev in lev_dists:
                f.write(f'{lev}\n')