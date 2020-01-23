import os
import numpy as np
import glob
import webrtcvad
import struct
from scipy.io import wavfile

#VAD 
vad = webrtcvad.Vad()

# set aggressiveness from 0 to 3
vad.set_mode(1)

sample_rate = 48000
samples_per_window = 1440
bytes_per_sample = 2
min_len_frm = 15
energy_thr = 100


#Tail noise to correct VAD bug
fs, x_tail = wavfile.read('tail_noise.wav')

file_cnt = 0
power_ratio = []
for fname in glob.glob(r'./*.wav', recursive=False):
	print(fname)
	SUB_PATH = './'+fname[:-4]
	if os.path.isdir(SUB_PATH) == False:
		os.mkdir(SUB_PATH)
		
	fs, x_speech = wavfile.read(fname)

	#Add Last signals
	x_speech = np.concatenate((x_speech,x_tail),axis=0)

	#Compare Power between L/R
	x_speech_L = x_speech[:,0]
	x_speech_R = x_speech[:,1]
	xcomp = np.mean(x_speech_L) - np.mean(x_speech_R)
	
	if xcomp > 0: #Left larger
		x_speech = x_speech_L
	else:
		x_speech = x_speech_R
	
	x_tlen = int(len(x_speech) / samples_per_window)
	
	fname = fname.replace('\\','/')
	fname_name = fname.split('/')[-1][:-4]

	raw_samples = struct.pack("%dh" % len(x_speech), * x_speech)
	
	
	subfile_num = 0
	is_init = True
	vad_tot = np.zeros((x_tlen,1))
	for start in np.arange(0, len(x_speech), samples_per_window):
		stop = min(start + samples_per_window, len(x_speech))
		if (stop - start) < samples_per_window:
			break

		is_speech = vad.is_speech(raw_samples[start * bytes_per_sample: stop * bytes_per_sample], sample_rate=sample_rate)
		if (is_speech == True):
			#print(cnt)
			if is_init:
				if subfile_num > 0:
					if subfrm_cnt > min_len_frm and np.mean(np.abs(speech)) > energy_thr:
						subfile = SUB_PATH + '/' + str(subfile_num) + '.wav'
						wavfile.write(subfile, sample_rate, speech)
					else:
						subfile_num -= 1
					
				speech_stereo = np.stack((x_speech_L[start:stop], x_speech_R[start:stop]))
				speech = np.copy(speech_stereo.T)
				is_init = False
				subfrm_cnt = 0
				subfile_num += 1
			else:
				speech_stereo = np.stack((x_speech_L[start:stop], x_speech_R[start:stop]))			  
				speech = np.concatenate((speech, speech_stereo.T), axis=0)
				subfrm_cnt += 1
		else:
			is_init = True
			#vad_tot[cnt]=1
		#cnt += 1