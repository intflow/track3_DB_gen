import os
import numpy as np
import glob
import webrtcvad
import struct
from scipy.io import wavfile

#VAD 
vad = webrtcvad.Vad()

# set aggressiveness from 0 to 3
vad.set_mode(3)

sample_rate = 48000
samples_per_window = 480
bytes_per_sample = 2

#name of sim data folder
DB_NAME = 'simdata_S5T18000'
VAD_PATH = '../simdata/'+DB_NAME+'/vad/'

if os.path.isdir(VAD_PATH) == False:
	os.mkdir(VAD_PATH)

file_cnt = 0
power_ratio = []
for fname in glob.glob(r'../simdata/'+DB_NAME+'/clean/*.wav', recursive=False):
	print(fname)

	fs, x_speech = wavfile.read(fname)

	#Get filename
	fname = fname.replace('\\','/')
	fname_name = fname.split('/')[-1][:-4]

	#Prepare writing vad label
	ftxt = open(VAD_PATH+fname_name+'.txt','w')

	##Add Last signals
	#x_speech = np.concatenate((x_speech,x_tail),axis=0)

	#Compare Power between L/R
	x_speech_L = x_speech[:,0]
	x_speech_R = x_speech[:,1]
	xcomp = np.mean(x_speech_L) - np.mean(x_speech_R)
	
	if xcomp > 0: #Left larger
		x_speech = x_speech_L
	else:
		x_speech = x_speech_R
	x_tlen = int(len(x_speech) / samples_per_window)

	raw_samples = struct.pack("%dh" % len(x_speech), * x_speech)
		
	subfile_num = 0
	is_init = True
	vad_tot = np.zeros((x_tlen,1))

	t_s = 0
	t_e = 0
	subfrm_cnt = 0
	for start in np.arange(0, len(x_speech), samples_per_window):
		stop = min(start + samples_per_window, len(x_speech))
		if (stop - start) < samples_per_window:
			break

		is_speech = vad.is_speech(raw_samples[start * bytes_per_sample: stop * bytes_per_sample], sample_rate=sample_rate)
		if (is_speech == True):
			#print(cnt)
			if is_init:
				if subfile_num == 0:
					t_s = start
					#ftxt.write(str(t_s) + ' ' +str(t_e) + ',')
				t_e = stop

				is_init = False
				subfrm_cnt = 0
				subfile_num += 1
			else:
				t_e = stop
				subfrm_cnt += 1
		else:
			is_init = True
			#vad_tot[cnt]=1
		#cnt += 1
	ftxt.write(str(t_s) + ' ' +str(t_e))
	ftxt.close()