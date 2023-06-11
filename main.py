#Import
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

# Memuat model yang telah disimpan sebelumnya
model = load_model('model.h5')

# Load data
data = pd.read_csv('Gabungan1.csv')

# Pisahkan fitur (Ingredients) dan label (Potensial Allergies, Potensial Diseases, Halal/Haram)
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

# Inisialisasi LabelEncoder
label_encoder_allergies = LabelEncoder()
y_encoded_allergies = label_encoder_allergies.fit_transform(y_allergies)

label_encoder_diseases = LabelEncoder()
y_encoded_diseases = label_encoder_diseases.fit_transform(y_diseases)

label_encoder_halal = LabelEncoder()
y_encoded_halal = label_encoder_halal.fit_transform(y_halal)

# Membuat DataFrame baru untuk hasil preprocessing
preprocessed_data = pd.DataFrame({
    'Features': X,
    'Labels_Allergies': y_encoded_allergies,
    'Labels_Diseases': y_encoded_diseases,
    'Labels_Halal': y_encoded_halal
})

@app.route('/process_input', methods=["GET", "POST"])
def process_input():
# Memeriksa otorisasi token user
    #auth_token = request.headers.get('Authorization')
    #if auth_token != 'YOUR_AUTH_TOKEN':
        #return 'Unauthorized', 401

# Mengambil input dari body request dalam format JSON
    data = request.get_json()
    user_text = data.get('text')

# Lakukan proses machine learning pada user_text
#Process the Input
    # Memisahkan input teks berdasarkan koma
    input_texts = user_text.split(",")

    # Menginisialisasi variabel untuk hasil prediksi
    allergies_output = []
    diseases_output = []
    halal_output = []

    # Lakukan prediksi untuk user_text
    for text in input_texts:
      # Preprocessing teks
      input_sequence = tokenizer.texts_to_sequences([text.strip()])
      input_padded = pad_sequences(input_sequence, maxlen=max_length)

      # Lakukan prediksi menggunakan model
      y_pred_allergies, y_pred_diseases, y_pred_halal = model.predict(input_padded)

      # Mengembalikan label prediksi menjadi bentuk aslinya
      label_prediksi_allergies = label_encoder_allergies.inverse_transform(np.argmax(y_pred_allergies, axis=1))
      label_prediksi_diseases = label_encoder_diseases.inverse_transform(np.argmax(y_pred_diseases, axis=1))
      label_prediksi_halal = label_encoder_halal.inverse_transform(np.argmax(y_pred_halal, axis=1))

      # Menggabungkan output dari beberapa teks
      allergies_output.extend(label_prediksi_allergies)
      diseases_output.extend(label_prediksi_diseases)
      halal_output.extend(label_prediksi_halal)

    # Gabungkan hasil prediksi dari beberapa teks
    combined_allergies_output = ' '.join(allergies_output) if allergies_output else ""
    combined_diseases_output = ' '.join(diseases_output) if diseases_output else ""
    combined_halal_output = ' '.join(halal_output) if halal_output else ""

    # Memeriksa hasil prediksi untuk membuat response
    if combined_allergies_output and "No Potential Allergies Detected" in allergies_output and len(allergies_output) > 1:
        non_no_allergies_output = [output for output in allergies_output if output != "No Potential Allergies Detected"]
        if non_no_allergies_output:
          final_allergies_output = ", ".join(non_no_allergies_output)
        else:
          final_allergies_output = "No Potential Allergies Detected"
    else:
      final_allergies_output = "Sorry we can't detect it"


    if combined_diseases_output and "No Potential Diseases Detected" in diseases_output and len(diseases_output) > 1:
        non_no_diseases_output = [output for output in diseases_output if output != "No Potential Diseases Detected"]
        if non_no_diseases_output:
          final_diseases_output = ", ".join(non_no_diseases_output)
        else:
          final_diseases_output = "No Potential Diseases Detected"
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

# Membuat response
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