import os
import numpy as np
import glob
import struct
from scipy.io import wavfile
from scipy.signal import stft
from scipy.signal import istft
from numpy.matlib import repmat


file_cnt = 0
SUB_PATH = './48k_MDI'
BIN_S_ORG = 765
BIN_E_ORG = 910
BIN_S = 880
BIN_E = 1025
power_ratio = []
if os.path.isdir(SUB_PATH) == False:
	os.mkdir(SUB_PATH)
for fname in glob.glob(r'./*/*.wav', recursive=False):
	print(fname)

	fs, x_speech = wavfile.read(fname)
	x_out = np.copy(x_speech)
	for ch in range(0,len(x_speech[0,:])):
		#Get STFT from waveform
		f, t, X = stft(x=x_speech[:,ch], fs=fs, window='hann', nperseg=2048, noverlap=None, nfft=2048, detrend=False, return_onesided=True, boundary='zeros', padded=True, axis=-1)
		X = X * 0.99
		X_fill = X[BIN_S_ORG:BIN_E_ORG,:]
		mdi_gain = 0.8
		#mdi_gain = np.abs(X[BIN_S,:]) / np.abs(X_fill[0,:])
		#mdi_gain = np.convolve(mdi_gain, np.ones((10,))/10, mode='same')
		#mdi_gain = repmat(mdi_gain, X_fill.shape[0],1)
		X[BIN_S:BIN_E] = np.fliplr(X_fill / np.abs(X_fill)) * np.abs(X_fill* mdi_gain) 
		t, x_tmp = istft(X, fs=fs, window='hann', nperseg=2048, noverlap=None, nfft=2048, input_onesided=True, boundary=True, time_axis=-1, freq_axis=-2)
		x_tmp = x_tmp.astype('int16')
		x_out[:,ch] = x_tmp[:x_out.shape[0]]
	
	x_out = np.clip(x_out, -32768, 32767)
	wavfile.write(fname,fs,x_out)