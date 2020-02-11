import os
import soundfile as sf
import random as rand
import numpy as np
import librosa
import glob
#import sys
#import json
#from pydub import AudioSegment

#Global Parameters   
Angles = ["_0","_20","_40","_60","_80","_100","_120","_140","_160","_180"] #소리의 각도(폴더명)

Samplerate = 48000
SNR_List = [1, 0.5, 0.25] #거리
Dist_Name = {1 : '5m', 0.5 :'10m', 0.25 : '20m'}

RAND_SEED = 5
TOTAL_TIME = 180 #총 DB 길이
INTERF_PERCENT = 0.2 #간섭음 Mixing 빈도
ZP_LEN = 0.2 #목표 음성의 20% 내 random 

def main():
    
    Interf_Path = "../DB3_Aroom/sony_A10/interf/"              #방해소리경로
    Speech_Path = "../DB3_Aroom/sony_A10/speech/"              #사람소리경로
    Drone_Path = "../DB1_drone/sony_A10/"             #드론소리경로
    Mix_Path = "../simdata/simdata_"+"S"+str(RAND_SEED)+"T"+str(TOTAL_TIME)+"/"  #합친소리경로

    if os.path.isdir(Mix_Path) == False:
        os.mkdir(Mix_Path)
        os.mkdir(Mix_Path+'/clean')
        os.mkdir(Mix_Path+'/noise')
        os.mkdir(Mix_Path+'/mix')

    DisturbSound = []
    HumanSound = []
    DronSound = []
    
    for dir_path, dir_name, file_name in os.walk(Interf_Path):    # 방해소리 종류(폴더명)
        DisturbSound.append(dir_name)
    
    for dir_path, dir_name, file_name in os.walk(Speech_Path):    # 사람소리 종류(폴더명)
        HumanSound.append(dir_name)

    for dir_path, dir_name, file_name in os.walk(Drone_Path):   # 드론소리 종류(폴더명)
        DronSound.append(dir_name)

    rand.seed( RAND_SEED )

    if not os.path.exists(Mix_Path):
        os.makedirs(Mix_Path)

    times = 0
    while (True):

        if times >= TOTAL_TIME:
            print("Time = " + str(TOTAL_TIME) + "sec")
            break

        random_percent = rand.random()
        
        if random_percent >= INTERF_PERCENT:
            
            for Angle in Angles:
              
                for Gain in SNR_List:

                    # 사람소리, 드론소리 중에 한가지를 랜덤선택
                    speech_class = rand.sample(HumanSound[0],1)
                    drone_class = rand.sample(DronSound[0],1)

                    # 사람소리의 각도중 랜덤선택
                    speech_angle = Angle
       
                    # 사람소리, 드론소리가 담긴 폴더의 wav파일중 한가지 선택
                    Speech_file_list = os.listdir(Speech_Path+speech_class[0]+"/"+speech_class[0]+speech_angle)
                    Speech_file = [file for file in Speech_file_list if file.endswith(".wav")]
                    
                    speech_name = rand.sample(Speech_file,1)

                    Drone_file_list = os.listdir(Drone_Path+drone_class[0])
                    Drone_file = [file for file in Drone_file_list if file.endswith(".wav")]
                    drone_name = rand.sample(Drone_file,1)

                    #선택된 wav파일 load
                    x_target, fs = sf.read(Speech_Path+speech_class[0]+"/"+speech_class[0]+speech_angle+"/"+speech_name[0])
                    x_drone, fs = sf.read(Drone_Path+drone_class[0]+"/"+drone_name[0])
            
                    #x_target 좌우 random zero padding
                    rp_zp_s = rand.randrange(0,int(x_target.shape[0]*ZP_LEN))
                    rp_zp_e = rand.randrange(0,int(x_target.shape[0]*ZP_LEN))
                    x_zp_s = np.zeros((rp_zp_s,x_target.shape[1]))
                    x_zp_e = np.zeros((rp_zp_e,x_target.shape[1]))
                    x_concat = np.concatenate((x_zp_s, x_target, x_zp_e),axis=0)
                    x_target = x_concat

                    #드론소리의 랜덤부분과 합친소리를 합치고 파일생성
                    randomslice = rand.randrange(0,x_drone.shape[0]-x_target.shape[0])
                    x_target = x_target * Gain
                    x_drone = x_drone[randomslice:randomslice+x_target.shape[0],:]
                    x_mix = x_target + x_drone
                    
                    #File Write
                    sf.write(Mix_Path+"clean/{}_{}_{}_{}_{}.wav".format(Dist_Name[Gain],speech_class[0],speech_name[0][:-4],speech_angle[1:],drone_name[0][:-4]),x_target,Samplerate,"PCM_16")
                    sf.write(Mix_Path+"noise/{}_{}_{}_{}_{}.wav".format(Dist_Name[Gain],speech_class[0],speech_name[0][:-4],speech_angle[1:],drone_name[0][:-4]),x_mix-x_target,Samplerate,"PCM_16")
                    sf.write(Mix_Path+"mix/{}_{}_{}_{}_{}.wav".format(Dist_Name[Gain],speech_class[0],speech_name[0][:-4],speech_angle[1:],drone_name[0][:-4]),x_mix,Samplerate,"PCM_16")

                    time = np.arange(len(x_mix))/float(Samplerate)
                    times += time[-1]

        else:

            for Angle in Angles:
                for Gain in SNR_List: 
        
                    #방해소리, 사람소리, 드론소리 중에 한가지를 랜덤선택
                    random_Interf = rand.sample(DisturbSound[0],1)
                    speech_class = rand.sample(HumanSound[0],1)
                    drone_class = rand.sample(DronSound[0],1)

                    #방해소리, 사람소리의 각도중 랜덤선택        
                    random_InterfA = rand.sample(Angles,1)
                    speech_angle = Angle
        
                    #방해소리, 사람소리, 드론소리가 담긴 폴더의 wav파일중 한가지 선택
                    DS_file_list = os.listdir(Interf_Path+random_Interf[0]+"/"+random_Interf[0]+random_InterfA[0])
                    DS_file = [file for file in DS_file_list if file.endswith(".wav")]
                        
                    random_InterfN = rand.sample(DS_file,1)

                    Speech_file_list = os.listdir(Speech_Path+speech_class[0]+"/"+speech_class[0]+speech_angle)
                    Speech_file = [file for file in Speech_file_list if file.endswith(".wav")]
                        
                    speech_name = rand.sample(Speech_file,1)

                    Drone_file_list = os.listdir(Drone_Path+drone_class[0])
                    Drone_file = [file for file in Drone_file_list if file.endswith(".wav")]
                    drone_name = rand.sample(Drone_file,1)

                    #선택된 wav파일 load
                    x_interf, fs = sf.read(Interf_Path+random_Interf[0]+"/"+random_Interf[0]+random_InterfA[0]+"/"+random_InterfN[0])
                    x_target, fs = sf.read(Speech_Path+speech_class[0]+"/"+speech_class[0]+speech_angle+"/"+speech_name[0])
                    x_drone, fs = sf.read(Drone_Path+drone_class[0]+"/"+drone_name[0])
                    
                    #x_target 좌우 random zero padding
                    rp_zp_s = rand.randrange(0,int(x_target.shape[0]*ZP_LEN))
                    rp_zp_e = rand.randrange(0,int(x_target.shape[0]*ZP_LEN))
                    x_zp_s = np.zeros((rp_zp_s,x_target.shape[1]))
                    x_zp_e = np.zeros((rp_zp_e,x_target.shape[1]))
                    x_concat = np.concatenate((x_zp_s, x_target, x_zp_e),axis=0)
                    x_target = x_concat

                    #방해소리와 사람소리를 합치고 파일생성
                    if x_interf.shape[0] >= x_target.shape[0]:
                        x_long = x_interf * random_percent
                        x_short = x_target * Gain
                    else:
                        x_long = x_target * Gain
                        x_short = x_interf * random_percent
                    
                    x_zeros = np.zeros(x_short.shape)
                    x_concat = np.concatenate((x_zeros,x_long,x_zeros),axis=0)
                    x_sd = np.copy(x_concat)
                    rp = rand.randrange(x_short.shape[0],x_concat.shape[0]-x_short.shape[0])
                    x_sd[rp:rp+x_short.shape[0],:] =  x_concat[rp:rp+x_short.shape[0],:] + x_short

                    if x_interf.shape[0] >= x_target.shape[0]:
                        x_target_rev = x_sd - x_concat
                    else:
                        x_target_rev = x_concat

                    if np.max(np.abs(x_sd)) > 1.0:
                        x_sd /= np.max(np.abs(x_sd))
                        x_target_rev /= np.max(np.abs(x_sd))
                    #드론소리의 랜덤부분과 합친소리를 합치고 파일생성 
                    # print(len(x_drone) - len(x_com))
                    # import pdb; pdb.set_trace()
                    randomslice2 = rand.randrange(0,x_drone.shape[0]-x_sd.shape[0])
                    x_drone = x_drone[randomslice2:randomslice2+x_sd.shape[0],:]
                    x_mix = x_sd + x_drone

                    #File Write
                    sf.write(Mix_Path+"clean/{}_{}_{}_{}_{}.wav".format(Dist_Name[Gain],speech_class[0],speech_name[0][:-4],speech_angle[1:],drone_name[0][:-4]),x_target_rev,Samplerate,"PCM_16")
                    sf.write(Mix_Path+"noise/{}_{}_{}_{}_{}.wav".format(Dist_Name[Gain],speech_class[0],speech_name[0][:-4],speech_angle[1:],drone_name[0][:-4]),x_mix-x_target_rev,Samplerate,"PCM_16")
                    sf.write(Mix_Path+"mix/{}_{}_{}_{}_{}.wav".format(Dist_Name[Gain],speech_class[0],speech_name[0][:-4],speech_angle[1:],drone_name[0][:-4]),x_mix,Samplerate,"PCM_16")

                    time = np.arange(len(x_mix))/float(Samplerate)
                    times += time[-1]

if __name__ == '__main__':
    main()