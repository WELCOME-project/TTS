import time
import logging as log
import numpy as np

import torch
from scipy.io import wavfile

import sys
sys.path.append('/text2speech_folder')  # folder where GST_Tacotron2 and MelGAN projects are located

from hyper_parameters import tacotron_params
from training import load_model
from text import text_to_sequence

from melgan.model.generator import Generator
from melgan.utils.hparams import load_hparam


# Override warn function in warnings to mute it
def warn(*args, **kwargs):
    pass

import warnings
warnings.warn = warn


class T2SPipelineConfiguration:

    def __init__(self, map_location='cpu', random_seed=1234):
        self.map_location = map_location
        self.random_seed = random_seed


class T2SPipeline:

    def __init__(self, tacotron_model_path : str, vocoder_model_path : str, config : T2SPipelineConfiguration):

        torch.manual_seed(config.random_seed)

        self.tacotron_model = self.__init_tacotron(tacotron_model_path, config.map_location)
        self.vocoder_model = self.__init_vocoder(vocoder_model_path)

    def __init_tacotron(self, tacotron_model_path, map_location):

        temp_model = torch.load(tacotron_model_path, map_location=map_location)
        state_dict = temp_model['state_dict']

        # load trained tacotron 2 model:
        hparams = tacotron_params

        model = load_model(hparams)
        model.load_state_dict(state_dict)
        _ = model.eval()

        return model

    def __init_vocoder(self, vocoder_model_path):

        # load pre trained MelGAN model for mel2audio:
        temp_model = torch.load(vocoder_model_path, map_location='cpu')

        model = Generator(80)  # Number of mel channels
        model.load_state_dict(temp_model['model_g'])
        model.eval(inference=False)

        return model

    def _preprocess(self, text, device):

        sequence = np.array(text_to_sequence(text, ['english_cleaners']))[None, :]
        sequence = torch.from_numpy(sequence).to(device=device, dtype=torch.int64)
        log.info("Input text sequence pre-processed successfully...")

        return sequence

    def _text2mel(self, sequence, scores):

        # set the GST scores you desire for speaking style:
        gst_head_scores = np.array(scores)
        gst_scores = torch.from_numpy(gst_head_scores)
        gst_scores = torch.autograd.Variable(gst_scores).float()


        # text2mel:
        t1 = time.time()
        with torch.no_grad():
            mel_outputs, mel_outputs_postnet, _, alignments = self.tacotron_model.inference(sequence, gst_scores)
        elapsed = time.time() - t1
        log.info('Time elapsed in transforming text to mel has been {} seconds.'.format(elapsed))

        return mel_outputs_postnet

    def _mel2wav(self, sequence):

        # mel2wav inference:
        t2 = time.time()
        with torch.no_grad():
            result = self.vocoder_model.inference(sequence)

        audio = result.data.cpu().detach().numpy()

        elapsed_melgan = time.time() - t2
        log.info('Time elapsed in transforming mel to wav has been {} seconds.'.format(elapsed_melgan))

        return audio

    def process(self, text, output_destination, scores=[0.58, 0.12, 0.3], device='cpu'):

        sequence = self._preprocess(text, device)

        mel_sequence = self._text2mel(sequence, scores)

        audio = self._mel2wav(mel_sequence)

        wavfile.write(output_destination, 22050, audio)
