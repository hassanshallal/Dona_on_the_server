from __future__ import absolute_import, division, print_function

import numpy as np
from numpy import argmax

from sklearn.preprocessing import LabelEncoder
from sklearn.preprocessing import OneHotEncoder
from sklearn.metrics import confusion_matrix, accuracy_score

import tensorflow as tf

import matplotlib.pyplot as plt
import json
import pickle
import datetime
import time
from os import system

import torch
from infersent import InferSent
import nltk
nltk.download('punkt')
# globals

# Load


def load_data_aware_embed():
    actions = pickle.load(open("modified_actions", "rb"))
    reactions = pickle.load(open("modified_reactions", "rb"))
    actions_embeddings = pickle.load(open("actions_embeddings", "rb"))
    reactions_embeddings = pickle.load(open("reactions_embeddings", "rb"))
    awareness = pickle.load(open("awareness", "rb"))
    awareness_resp = pickle.load(open("awareness_resp", "rb"))
    print('Data loaded')
    print(len(actions), len(reactions), actions_embeddings.shape,
          reactions_embeddings.shape, len(awareness), len(awareness_resp))
    return actions, reactions, actions_embeddings, reactions_embeddings, awareness, awareness_resp

# encode awareness or awareness_resp
def encode(target):
    values = np.array(target)
    label_encoder = LabelEncoder()
    integer_encoded = label_encoder.fit_transform(values)
    values = values.reshape(len(values), 1)
    onehot_encoder = OneHotEncoder(sparse=False)
    onehot_encoded = onehot_encoder.fit_transform(values)
    return label_encoder, integer_encoded, onehot_encoded


# Alright, we will setup infersent encoder here
# 1) Load our pre-trained model (in encoder/):
V = 2
MODEL_PATH = 'infersent_encoder/infersent%s.pkl' % V
params_model = {'bsize': 64, 'word_emb_dim': 300, 'enc_lstm_dim': 2048,
                'pool_type': 'max', 'dpout_model': 0.0, 'version': V}
W2V_PATH = 'fastText/crawl-300d-2M.vec'


class Awareness:
    def __init__(self):
        self.actions, self.reactions, self.actions_embeddings, self.reactions_embeddings, self.awareness, self.awareness_resp = load_data_aware_embed()

        # Get one-hot and label encoders for both awareness and awareness_resp
        self.label_encoder_awareness, self.integer_encoded_awareness, self.onehot_encoded_awareness = encode(
            self.awareness)
        self.label_encoder_awareness_resp, self.integer_encoded_awareness_resp, self.onehot_encoded_awareness_resp = encode(
            self.awareness_resp)

        # Load the models for predicting either awareness or awareness_resp
        self.model_query = tf.keras.models.load_model(
            './assets/awareness_model_infersent_version0.h5')
        print("model_query is loaded!")

        self.model_response = tf.keras.models.load_model(
            './assets/awareness_resp_model_infersent_version0.h5')
        print("model_response is loaded!")

        # Infersent embedder
        self.infersent = InferSent(params_model)
        self.infersent.load_state_dict(torch.load(MODEL_PATH))
        self.infersent.set_w2v_path(W2V_PATH)
        self.infersent.build_vocab(
            self.actions + self.reactions, tokenize=True)
        print("infersent embedder is prepared!")

    def embed_normalize_sent(self, query):
        query_embed = self.infersent.encode([query], tokenize=True)
        query_embed = torch.tensor(query_embed)
        query_embed = query_embed / query_embed.norm(dim=1)[:, None]
        query_embed = query_embed.numpy()
        return query_embed

    def get_awareness_query(self, query):
        query_embed = self.embed_normalize_sent(query)
        query_class = np.argmax(
            self.model_query.predict([query_embed]), axis=1)
        query_awareness_class = self.label_encoder_awareness.inverse_transform(
            query_class).tolist()[0]
        return query_awareness_class

    def get_awareness_response(self, response):
        response_embed = self.embed_normalize_sent(response)
        response_class = np.argmax(
            self.model_response.predict([response_embed]), axis=1)
        response_awareness_class = self.label_encoder_awareness_resp.inverse_transform(
            response_class).tolist()[0]
        return response_awareness_class

    def get_most_similar(self, query):
        query_embed = self.embed_normalize_sent(query)
        dot_product = np.dot(self.actions_embeddings, query_embed.T)
        max_index = np.argmax(dot_product)
        return max_index, dot_product[max_index][0]
