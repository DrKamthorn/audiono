import streamlit as st
import tensorflow as tf
import matplotlib.pyplot as plt
import numpy as np
from scipy.io.wavfile import write
import util_functions as ufs
import time

# Setting config option for deployment
st.set_page_config(initial_sidebar_state="collapsed")
st.set_option('deprecation.showPyplotGlobalUse', False)
st.title('')
st.subheader('ปรับลดเสียงรบกวนในไฟล์บันทึก')

# UI design

nav_choice = st.sidebar.radio('Navigation', ['.'], index=0)

_param_dict = {}  # Used for getting plot related information
_path_to_model = 'utils/models/auto_encoders_for_noise_removal_production.h5'  # Path to pre-trained model
_targe_file = 'utils/outputs/preds.wav'  # target file for storing model.output

if nav_choice == '.':
    #st.image('utils/images/header.jpg', width=450)

    st.info('Upload ไฟล์เสียง')
    audio_sample = st.file_uploader('ไฟล์ที่เลือก', ['wav'])  # Get audio sample as an input from users
    if audio_sample:
        try:
            prog = st.progress(0)
            model = ufs.load_model(_path_to_model)  # call to the utility module to cache the model
            audio = tf.audio.decode_wav(audio_sample.read(), desired_channels=1)
            # decoding audio waveform by using  tf.audio.decode_wav as a mono sound wave
            _param_dict.update({'audio_sample': audio.audio})
            flag = 1
            for i in range(100):
                time.sleep(0.001)
                prog.progress(i + 1)
            st.info('Uploaded ไฟล์บันทึก')
            st.audio(audio_sample)
            with st.spinner('Wait for it...'):
                time.sleep(1)
                preds = model.predict(tf.expand_dims(audio.audio, 0))  # using this EagerTensor to suppress te noie
                preds = tf.reshape(preds, (-1, 1))
                _param_dict.update({'predicted_outcomes': preds})
                preds = np.array(preds)
                write(_targe_file, 44100, preds)  # writing the output file to play
            st.success('Audio after noise removal')
            st.audio(_targe_file)

            # Visual Representation of model's prediction using sync plots

            prediction_stats = st.checkbox('ภาพความถี่ของเสียงที่คาด')
            noise_rem = st.checkbox('ภาพความถี่ของเสียงที่ปรับลดแล้ว')
            if noise_rem:
                fig, axes = plt.subplots(2, 1, figsize=(10, 6))
                axes[0].plot(np.arange(len(_param_dict['audio_sample'])), _param_dict['audio_sample'], c='r')
                axes[0].set_title('Original')
                axes[1].plot(np.arange(len(_param_dict['predicted_outcomes'])), _param_dict['predicted_outcomes'],
                             c='b')
                axes[1].set_title('Denoised')
                st.pyplot()

            if prediction_stats:
                plt.figure(figsize=(10, 6))
                plt.plot(np.arange(len(_param_dict['audio_sample'])), _param_dict['audio_sample'], c='r',
                         label='Original')
                plt.plot(np.arange(len(_param_dict['predicted_outcomes'])), _param_dict['predicted_outcomes'], c='b',
                         label='Denoised')
                plt.legend()
                st.pyplot()

        except Exception as e:
            print(e, type(e))
