import os
import soundfile as sf
import random as rand
import numpy as np
import librosa
import glob
#import sys
#import json
#from pydub import AudioSegment

def main():
    
    Interf_Path = "../sony/Aroom/interf/"              #방해소리경로
    Speech_Path = "../sony/Aroom/speech/"              #사람소리경로
    Drone_Path = "../sony/Drone/"             #드론소리경로
    Mix_Path = "../sony/mix_test/"  #합친소리경로

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
   
    Angles = ["_0","_20","_40","_60","_80","_100","_120","_140","_160","_180"] #소리의 각도(폴더명)

    Samplerate = 48000
    SNR_List = [1, 0.5, 0.25] #거리
    Dist_Name = {1 : '5m', 0.5 :'10m', 0.25 : '20m'}

    Random_seed = 3
    times = 0
    end_time = 10
    percent = 0.05

    rand.seed( Random_seed )

    if not os.path.exists(Mix_Path):
        os.makedirs(Mix_Path)

    while (True):

        if times >= end_time:
            print("Time = " + str(end_time) + "sec")
            break

        random_percent = rand.random()
        
        if random_percent >= percent:
            
            for Angle in Angles:
              
                for Gain in SNR_List:

                    # 사람소리, 드론소리 중에 한가지를 랜덤선택
                    speech_class = rand.sample(HumanSound[0],1)
                    drone_class = rand.sample(DronSound[0],1)

                    # 사람소리의 각도중 랜덤선택
                    speech_angle = Angle
       
                    # 사람소리, 드론소리가 담긴 폴더의 wav파일중 한가지 선택
                    Speech_file_list = os.listdir(Speech_Path+speech_class[0]+"/"+speech_class[0]+str(speech_angle))
                    Speech_file = [file for file in Speech_file_list if file.endswith(".wav")]
                    
                    speech_name = rand.sample(Speech_file,1)

                    Drone_file_list = os.listdir(Drone_Path+drone_class[0])
                    Drone_file = [file for file in Drone_file_list if file.endswith(".wav")]
                    drone_name = rand.sample(Drone_file,1)

                    #선택된 wav파일 load
                    x_target, fs = sf.read(Speech_Path+speech_class[0]+"/"+speech_class[0]+str(speech_angle)+"/"+speech_name[0])
                    x_drone, fs = sf.read(Drone_Path+drone_class[0]+"/"+drone_name[0])
            
                    #드론소리의 랜덤부분과 합친소리를 합치고 파일생성
                    randomslice = rand.randrange(0,len(x_drone[:,0])-len(x_target[:,0]))
                    x_target = x_target * Gain
                    x_drone = x_drone[randomslice:randomslice+len(x_target[:,0]),:]
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
                    DS_file_list = os.listdir(Interf_Path+random_Interf[0]+"/"+random_Interf[0]+str(random_InterfA))
                    DS_file = [file for file in DS_file_list if file.endswith(".wav")]
                        
                    random_InterfN = rand.sample(DS_file,1)

                    Speech_file_list = os.listdir(Speech_Path+speech_class[0]+"/"+speech_class[0]+str(speech_angle))
                    Speech_file = [file for file in Speech_file_list if file.endswith(".wav")]
                        
                    speech_name = rand.sample(Speech_file,1)

                    Drone_file_list = os.listdir(Drone_Path+drone_class[0])
                    Drone_file = [file for file in Drone_file_list if file.endswith(".wav")]
                    drone_name = rand.sample(Drone_file,1)

                    #선택된 wav파일 load
                    x_interf, fs = sf.read(Interf_Path+random_Interf[0]+"/"+random_Interf[0]+str(random_InterfA)+"/"+random_InterfN[0])
                    x_target, fs = sf.read(Speech_Path+speech_class[0]+"/"+speech_class[0]+str(speech_angle)+"/"+speech_name[0])
                    x_drone, fs = sf.read(Drone_Path+drone_class[0]+"/"+str(drone_name)+".wav")
                    
                    #방해소리와 사람소리를 합치고 파일생성
                    if len(x_interf[:,0]) >= len(x_target[:,0]):
                        x_long = x_interf
                        x_short = x_target
                        gain_long = random_percent
                        gain_short = Gain
                    else:
                        x_long = x_target
                        x_short = x_interf
                        gain_long = Gain
                        gain_short = random_percent
                    
                    x_zeros = np.zeros((len(x_short[:,0]), len(x_short[:,0])))
                    x_concat = np.concatenate((x_zeros,x_long,x_zeros),axis=1)
                    rp = rand.randrange(len(x_short[:,0]),len(x_concat[:,0])-len(x_short[:,0]))
                    
                    x_mix =  gain_long * x_concat[:,rp:rp+len(x_short[:,0])] + gain_short * x_short
                    if np.max(np.abs(x_mix)) > 1.0:
                        x_mix = x_mix / np.max(np.abs(x_mix))
                    
                    #드론소리의 랜덤부분과 합친소리를 합치고 파일생성 
                    # print(len(x_drone) - len(x_com))
                    # import pdb; pdb.set_trace()
                    randomslice2 = rand.randrange(0,len(x_drone[:,0])-len(x_mix[:,0]))
                    x_drone = x_drone[randomslice2:randomslice2+len(x_mix[:,0]),:]
                    x_mix = x_mix + x_drone

                    #File Write
                    sf.write(Mix_Path+"clean/{}_{}_{}_{}_{}.wav".format(Dist_Name[Gain],speech_class[0],speech_name[0][:-4],speech_angle[1:],drone_name[0][:-4]),x_target*Gain,Samplerate,"PCM_16")
                    sf.write(Mix_Path+"noise/{}_{}_{}_{}_{}.wav".format(Dist_Name[Gain],speech_class[0],speech_name[0][:-4],speech_angle[1:],drone_name[0][:-4]),x_mix-x_target*Gain,Samplerate,"PCM_16")
                    sf.write(Mix_Path+"mix/{}_{}_{}_{}_{}.wav".format(Dist_Name[Gain],speech_class[0],speech_name[0][:-4],speech_angle[1:],drone_name[0][:-4]),x_mix,Samplerate,"PCM_16")

                    time = np.arange(len(x_mix))/float(Samplerate)
                    times += time[-1]
        
if __name__ == '__main__':
    main()