# -*- coding: utf-8 -*-
"""app2.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1-0MPmL5xDy-DcYlu6or8ERKoIgO6Bu8M
"""

import pandas as pd
import numpy as np
import tensorflow as tf
import os
from tensorflow import keras
from sklearn.preprocessing import LabelEncoder
from keras.preprocessing.text import Tokenizer
from keras.models import Model
from keras.models import load_model
from tensorflow.keras.preprocessing.sequence import pad_sequences
from flask import Flask, request, jsonify

app = Flask(__name__)

# Loads a previously saved model
model = load_model('safebite.h5')

# Load data
data = pd.read_csv('safebite.csv')

# Separate features (Ingredients) and labels (Potential Allergies, Potential Diseases, Halal/Haram)
X = data['Ingredients']
y_allergies = data['Potential Allergies']
y_diseases = data['Potential Diseases']
y_halal = data['Halal/Haram']

# Preprocessing teks
tokenizer = Tokenizer()
tokenizer.fit_on_texts(X)
X_sequences = tokenizer.texts_to_sequences(X)
X_padded = pad_sequences(X_sequences)
vocab_size = len(tokenizer.word_index) + 1
embedding_dim = 100
max_length = X_padded.shape[1]

# Initializing LabelEncoder
label_encoder_allergies = LabelEncoder()
y_encoded_allergies = label_encoder_allergies.fit_transform(y_allergies)

label_encoder_diseases = LabelEncoder()
y_encoded_diseases = label_encoder_diseases.fit_transform(y_diseases)

label_encoder_halal = LabelEncoder()
y_encoded_halal = label_encoder_halal.fit_transform(y_halal)

# Create a new DataFrame for preprocessing results
preprocessed_data = pd.DataFrame({
    'Features': X,
    'Labels_Allergies': y_encoded_allergies,
    'Labels_Diseases': y_encoded_diseases,
    'Labels_Halal': y_encoded_halal
})

@app.route('/process_input', methods=['POST'])
def process_input():
# Check user token authorization
    #auth_token = request.headers.get('Authorization')
    #if auth_token != 'YOUR_AUTH_TOKEN':
    #    return 'Unauthorized', 401

# Takes input from the body of the request in JSON format
    data = request.get_json()
    user_text = data.get('text')

#Process the Input
    # Separates text input by commas
    input_texts = user_text.split(",")

    # Initialize variables for predictive results
    allergies_output = []
    diseases_output = []
    halal_output = []

    # Make predictions for user_text
    for text in input_texts:
      # Preprocessing text
      input_sequence = tokenizer.texts_to_sequences([text.strip()])
      input_padded = pad_sequences(input_sequence, maxlen=max_length)

      # Make predictions using models
      y_pred_allergies, y_pred_diseases, y_pred_halal = model.predict(input_padded)

      # Returns the predicted label to its original form
      label_prediksi_allergies = label_encoder_allergies.inverse_transform(np.argmax(y_pred_allergies, axis=1))
      label_prediksi_diseases = label_encoder_diseases.inverse_transform(np.argmax(y_pred_diseases, axis=1))
      label_prediksi_halal = label_encoder_halal.inverse_transform(np.argmax(y_pred_halal, axis=1))

      # Combines the output of multiple texts
      allergies_output.extend(label_prediksi_allergies)
      diseases_output.extend(label_prediksi_diseases)
      halal_output.extend(label_prediksi_halal)


    # Combine prediction results from multiple texts
    combined_allergies_output = ' '.join(allergies_output) if allergies_output else ""
    combined_diseases_output = ' '.join(diseases_output) if diseases_output else ""
    combined_halal_output = ' '.join(halal_output) if halal_output else ""

    # Examine the prediction results to create a response
    if combined_allergies_output and "No" in allergies_output and len(allergies_output) > 1:
        non_no_allergies_output = [output for output in allergies_output if output != "No"]
        if non_no_allergies_output:
          final_allergies_output = ", ".join(non_no_allergies_output)
        else:
          final_allergies_output = "No"
    else:
      final_allergies_output = "Sorry we can't detect it"


    if combined_diseases_output and "No" in diseases_output and len(diseases_output) > 1:
        non_no_diseases_output = [output for output in diseases_output if output != "No"]
        if non_no_diseases_output:
          final_diseases_output = ", ".join(non_no_diseases_output)
        else:
          final_diseases_output = "No"
    else:
      final_diseases_output = "Sorry we can't detect it"


    if final_allergies_output == "Sorry we can't detect it" and final_diseases_output == "Sorry we can't detect it":
      final_halal_output = "Sorry we can't detect it"
    else:
      if combined_halal_output:
        if "Haram" in halal_output:
            final_halal_output = "Haram"
        else:
            final_halal_output = "Halal"
      else:
        final_halal_output = "Sorry we can't detect it"


# Create responses
    response = {
        'status': 'success',
        'result': {
            'Data':  user_text,
            'Allergies Prediction': final_allergies_output,
            'Diseases Prediction': final_diseases_output,
            'Halal/Haram Prediction': final_halal_output
        }
    }

    return response

if __name__ == '__main__':
    app.run()
