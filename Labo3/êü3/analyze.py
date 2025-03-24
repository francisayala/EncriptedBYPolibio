from re import sub, finditer
from math import gcd
from typing import Tuple, List, MutableSet, Dict
from sklearn.preprocessing import LabelEncoder
import numpy as np
import pandas as pd


ALPHABET = 'абвгдежзийклмнопрстуфхцчшщъыьэюя'


def preprocess(text: str) -> Tuple[str, List[int]]:
    punct_removed = sub(r'[\)\(\.,\?!\[\]:;\-/ё"]', ' ', text.replace('ё', 'е'))
    splitted_by_space = punct_removed.split()
    text = (''.join(splitted_by_space)).lower()
    lens = [len(x) for x in splitted_by_space]
    return text, lens



def get_ic(
        preprocessed_text: str,
        mu_range: Tuple[int, int]
    ) -> Dict[int,float]:
    result = {}
    encoder = LabelEncoder()
    encoded = encoder.fit_transform(list(preprocessed_text))
    for mu in range(*mu_range):
        reshaped = [[] for _ in range(mu)]
        for i in range(len(encoded) // mu * mu):
            reshaped[i % mu].append(encoded[i])
        reshaped = np.array(reshaped)
        average_ic = 0
        for i in range(mu):
            _, counts = np.unique(reshaped[i], return_counts=True)
            average_ic += np.sum(counts * (counts - 1)) / (len(reshaped[i]) * (len(reshaped[i]) - 1))
        result[mu] = average_ic / mu
    return result


class FrequencyDictionary:
    def __init__(self, path: str) -> None:
        self.freq = pd.read_csv(path, sep='\t')
        self.freq.sort_values(by='Freq(ipm)', ascending=False, inplace=True)
        self.freq['Lemma'] = self.freq['Lemma'].apply(lambda word: word.replace('ё', 'e').lower())
        self.__fast_set = set(self.freq['Lemma'])
        
    def get_n_letters_words(self, n: int) -> List[str]:
        return list(
                filter(
                    lambda word: len(word) == n and '-' not in word and "'" not in word, 
                    self.freq['Lemma']
                )
            )
    
    def get_top_n(self, n: int, min_size: int = 4) -> List[int]:
        return list(
                filter(
                    lambda word: len(word) >= min_size, 
                    self.freq['Lemma']
                )
            )[:n]
    
    def __contains__(self, item: str) -> bool:
        return item in self.__fast_set

    
def decode(key: str, chipher: str) -> str:
    alphabet = {chr(ord('а') + i): i for i in range(ord('я') - ord('а') + 1)}
    inversed_alphabet = {value: key for key, value in alphabet.items()}
    repeat_times = len(chipher) // len(key) + (1 if len(chipher) % len(key) != 0 else 0)
    repeated_key = (key * repeat_times)[:len(chipher)]
    digital_chipher = np.array([alphabet[c] for c in chipher])
    digital_key = np.array([alphabet[c] for c in repeated_key])
    digital_result = (digital_chipher - digital_key) % len(alphabet)
    return ''.join([inversed_alphabet[d] for d in digital_result])


def key_search(
        preprocessed_text: str, 
        frequency_dictionary: FrequencyDictionary,
        key_size: int,
        check_size: int
    ) -> Dict[str,int]:
    key_scores = {}
    top_n = frequency_dictionary.get_top_n(check_size)
    for potential_key in frequency_dictionary.get_n_letters_words(key_size):
        try:
            open_text = decode(potential_key, preprocessed_text)
            count = 0
            for word in top_n:
                count += 1 if word in open_text else 0
            key_scores[potential_key] = count
        except:
            pass
    return key_scores


def restore_from_split(text: str, lens: List[int]) -> str:
    assert len(text) == sum(lens)
    result = []
    last_index = 0
    for count in lens:
        result.append(text[last_index:last_index + count])
        last_index += count
    return ' '.join(result)


def auto_decode(
        text: str, 
        key_size_range: Tuple[int, int]
    ) -> Tuple[str, str]:
    frequency_dictionary = FrequencyDictionary('freqrnc2011.csv')
    preprocessed, split_lens = preprocess(text)
    ics = get_ic(preprocessed, key_size_range)
    best_mu = [x[0] for x in sorted(ics.items(), key=lambda x: -x[1])[:3]]
    all_keys_scores = {}
    for mu in best_mu:
        keys_scores = key_search(preprocessed, frequency_dictionary, mu, 1000)
        all_keys_scores.update(keys_scores)
    key = sorted(all_keys_scores.items(), key=lambda x: -x[1])[0][0]
    return key, restore_from_split(decode(key, preprocessed), split_lens)
