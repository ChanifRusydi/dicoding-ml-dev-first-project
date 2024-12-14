import json

import tensorflow as tf
import numpy as np
import urllib
from keras.preprocessing.text import  Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences


def solution_C4():
    data_url = 'https://github.com/dicodingacademy/assets/raw/main/Simulation/machine_learning/sarcasm.json'
    urllib.request.urlretrieve(data_url, 'sarcasm.json')
    with open('sarcasm.json', 'r') as f:
        dataset=json.load(f)
    
    # DO NOT CHANGE THIS CODE
    # Make sure you used all of these parameters or test may fail
    vocab_size = 1000
    embedding_dim = 16
    max_length = 120
    trunc_type = 'post'
    padding_type = 'post'
    oov_tok = "<OOV>"
    training_size = 20000

    sentences = []
    labels = []
    # YOUR CODE HERE
    for item in dataset:
        sentences.append(item['headline'])
        labels.append(item['is_sarcastic'])

    print(sentences[:5])
    print(labels[:5])
    # Fit your tokenizer with training data
    tokenizer = Tokenizer(num_words=vocab_size,oov_token=oov_tok)  # YOUR CODE HERE
    tokenizer.fit_on_texts(sentences)
    training_sentence=tokenizer.texts_to_sequences(sentences[:training_size])
    training_padded=pad_sequences(training_sentence,maxlen=max_length,truncating=trunc_type,padding=padding_type,value=0)

    testing_sentence=tokenizer.texts_to_sequences(sentences[training_size:])
    testing_padded=pad_sequences(testing_sentence,maxlen=max_length,truncating=trunc_type,padding=padding_type,value=0)
    
    training_labels=np.array(labels[:training_size])
    testing_labels=np.array(labels[training_size:])
    
    print(training_padded.shape)
    print(testing_padded.shape)
    print(training_labels.shape)
    print(testing_labels.shape)

    # model = tf.keras.Sequential([
    #     tf.keras.layers.Embedding(vocab_size, embedding_dim, input_length=max_length),
    #     tf.keras.layers.Bidirectional(tf.keras.layers.LSTM(32, return_sequences=True)),
    #     tf.keras.layers.Bidirectional(tf.keras.layers.LSTM(32)),
    #     tf.keras.layers.Dense(24, activation='relu'),
    #     # YOUR CODE HERE. DO not change the last layer or test may fail
    #     tf.keras.layers.Dense(1, activation='sigmoid')
    # ])
    # model.compile(loss='binary_crossentropy',optimizer='adam',metrics=['accuracy'])
    # model.fit(training_padded,training_labels,epochs=1,validation_data=(testing_padded,testing_labels))   
    # return model


# The code below is to save your model as a .h5 file.
# It will be saved automatically in your Submission folder.
if __name__ == '__main__':
    # DO NOT CHANGE THIS CODE
    model = solution_C4()
    model.save("model_C4.h5")