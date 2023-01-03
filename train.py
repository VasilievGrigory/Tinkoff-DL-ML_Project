import argparse
import numpy as np
import os
import pathlib
from normalizer import normalize_text
from tqdm import tqdm

def save_all_texts(files, plag1, plag2):
    '''
    Запомним все тексты из представленных обучающих директорий для дальнейшего использования для BERT
    '''

    texts = []
    # Все полученные директории
    dirs = [files, plag1, plag2]
    lens_dirs = {dir: 0 for dir in dirs}
    # Проходимся по всем тестовым данным, преобразуем
    for dir in dirs:
        count = 0
        for file in tqdm(os.listdir(dir)):
            filename = os.fsdecode(file)
            if filename.endswith(".py"):
                with open(os.path.join(dir, filename), 'r', encoding='utf8') as f:
                    texts.append(normalize_text(f.read()))
                    count += 1
        lens_dirs[dir] = count
                    

    
    # Сохраним все тестовые данные в временную директорию
    p = pathlib.Path("train/")
    p.mkdir(parents=True, exist_ok=True)
    i_global = 0
    for dir in dirs:
        for i in range(lens_dirs[dir]):
            fn = f'{i+1} ' + dir
            filepath = p / fn
            with filepath.open("w", encoding ="utf-8") as f:
                f.write(texts[i_global])
                i_global += 1

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Файлы для просмотра сходства')
    parser.add_argument('files_to_train', type=str, help='Файлы оригиналы для обучения')
    parser.add_argument('plagiat1_files_to_train', type=str, help='Файл c плагиатом 1 для обучения')
    parser.add_argument('plagiat2_files_to_train', type=str, help='Файл с плагиатом 2 для обучения')
    args = parser.parse_args()
    save_all_texts(args.files_to_train, args.plagiat1_files_to_train, args.plagiat2_files_to_train)