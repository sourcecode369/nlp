# -*- coding: utf-8 -*-
"""HuggingFace nlp library - Tutorial.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1LartYbCd33ZY2NlLNbfrJTTnGv3WAQTX

### Installation
"""

!pip install nlp

"""### List Datasets"""

import nlp

datasets = nlp.list_datasets()
metrics = nlp.list_metrics()

print(f"🤩 Currently {len(datasets)} datasets are available on HuggingFace AWS bucket: \n" 
      + '\n'.join(dataset.id for dataset in datasets) + '\n')
print(f"🤩 Currently {len(metrics)} metrics are available on HuggingFace AWS bucket: \n" 
      + '\n'.join(metric.id for metric in metrics))

"""## Loading a dataset

### Load Dataset
"""

import nlp

mnli = nlp.load_dataset(path='glue', name='mnli', split='train[:10%]')

"""## Whats in a dataset object

### Features and columns
"""

print(mnli.shape)
print(mnli.num_columns)
print(mnli.num_rows)
print(len(mnli))
print(mnli.column_names)
print(mnli.features)

dataset = mnli
print(dataset.features['label'].num_classes)
print(dataset.features['label'].names)

"""### Metadata"""

print(dataset.split)
print(dataset.description)
print(dataset.homepage)
print(dataset.license)

"""### Cache Files and Memory Usage"""

print(dataset.cache_files)

from nlp import total_allocated_bytes
print('Number of bytes allocated on the drive is: ', dataset.nbytes)
print('Comparison: ', total_allocated_bytes())

dataset.cleanup_cache_files()

"""### Getting Rows, Slices, Batches and Columns"""

dataset[:3]

dataset[[1,3,5]]

dataset['premise'][:10]

"""### Working with Other Data Types"""

dataset.column_names

dataset.set_format(type='torch', columns=['label'])

dataset.column_names

dataset[0:3]

dataset[0]

print(dataset.format)
dataset.reset_format()
print(dataset.format)

"""## Processing data in a Dataset

### sorting the dataset
"""

print(dataset['label'][:5])
sorted_dataset = dataset.sort('label')
print(sorted_dataset['label'][:5])

sorted_dataset['label'][-10:]

"""### Shuffling the dataset"""

shuffled_dataset = sorted_dataset.shuffle(seed=2020)

shuffled_dataset['label'][:10]

"""### Filtering rows"""

dataset.select([0,10])

print(len(dataset.filter(lambda x : x['label']==0)))
print(len(dataset.filter(lambda x : x['label']==1)))
print(len(dataset.filter(lambda x : x['label']==2)))

"""### Splitting the dataset in train and test split"""

dataset.train_test_split(test_size=0.1)

"""### processing data with `map`"""

small_dataset = dataset.select(range(10))
small_dataset

len(small_dataset)

# small_dataset.map(lambda example: print(example['label']), verbose=False)

dataset.column_names

def add_prefix(example):
    example['premise'] = "premise: " + example['premise']
    return example

updated_dataset = small_dataset.map(add_prefix)
updated_dataset['premise'][:5]

updated_dataset = small_dataset.map(lambda example: {'premise': 'My sentence: ' + example['premise']})
updated_dataset['premise'][:5]

"""### Remove columns"""

updated_dataset = small_dataset.map(lambda example: {'new_sentence': example['premise']}, remove_columns=['premise'])

"""### Using row indices"""

updated_dataset = small_dataset.map(lambda example, idx: {'new_premise':f'{idx}  '+ example['premise']}, with_indices=True)

"""### Processing data in batches"""

!pip install transformers

from transformers import BertTokenizerFast
tokenizer = BertTokenizerFast.from_pretrained('bert-base-cased')

encoded_dataset = dataset.map(lambda examples: tokenizer(examples['premise']), batched=True)

encoded_dataset.column_names

print(encoded_dataset[:2])

"""### Augmentation of datasets"""

def chunk_examples(examples):
    chunks = []
    for sentence in examples['premise']:
        chunks += [sentence[i:i+50] for i in range(0,len(sentence),50)]
    return {'chunks':chunks}

chunked_dataset = dataset.map(chunk_examples, batched=True, remove_columns=dataset.column_names)
chunked_dataset

chunked_dataset[:10]

print(chunked_dataset.num_rows)
print(dataset.num_rows)

from transformers import pipeline
from random import randint

fillmask = pipeline('fill-mask')
mask_token = fillmask.tokenizer.mask_token 
smaller_dataset = dataset.filter(lambda e, i: i< 100, with_indices=True)

def augment_data(examples):
    outputs = []
    for sentence in examples['premise']:
        words = sentence.split(' ')
        K = randint(1, len(words)-1)
        masked_sentence = " ".join(words[:K]  + [mask_token] + words[K+1:])
        predictions = fillmask(masked_sentence)
        augmented_sequences = [predictions[i]['sequence']for i in range(3)]
        outputs += [sentence] + augmented_sequences
        return {'data': outputs}

augmented_dataset = smaller_dataset.map(augment_data, batched=True, remove_columns=dataset.column_names, batch_size=8)

len(augmented_dataset)

augmented_dataset[:9]['data']

"""### Processing several splits at once"""

dataset = nlp.load_dataset('glue', 'mnli')

dataset.map(lambda examples: tokenizer(examples['premise']), batched=True)