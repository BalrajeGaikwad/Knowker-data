import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import signal
import os
import pandas as pd
from scipy.fft import fft
import pywt
import librosa
import argparse
# from find_f0 import calculate_fundamental_frequency
from scipy.signal import find_peaks
# Example usage
if __name__ == "__main__":
    # Initialize the Parser
    parser = argparse.ArgumentParser(description='Process Single File for Whisper Speechtotext.')
    parser.add_argument('-i', '--input', type=str, required=True)
    args = parser.parse_args()

    

    # Replace 'your_audio_file.wav' with the actual filename of your audio file    
    # audio_file = '/home/sumasoft/Downloads/15/57_mic1.wav'
    # path = '/home/sumasoft/Downloads/54/'
    path = args.input
    out_dir = os.path.join(path,'results','fft')
    os.makedirs(out_dir,exist_ok=True)


    # Define the column names
    columns = ['filename','s1_f0', 's2_f0', 's3_f0', 's4_f0', 's1_M', 's2_M', 's3_M', 's4_M']
    import csv
    # Create the CSV file and write the header
    csv_filename = os.path.join(path,'results','F0_Analysis.csv')
    with open(csv_filename, mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=columns)
        writer.writeheader()


    files = os.listdir(path)
    files = [filename for filename in files if filename.endswith('.csv')]
    # import pdb; pdb.set_trace()
    # Sort the list of filenames in numerical order
    files.sort(key=lambda x: int(os.path.splitext(x)[0].split('_')[0]))
    for file in files:
        vibration_file = os.path.join(path,file)
        if vibration_file.endswith('.csv') and not vibration_file.endswith('max_amplitude_frequency_results.csv'):
            # Define the column names you want to use
            column_names = ['s1_x', 's1_y', 's1_z',
                                  's2_x', 's2_y', 's2_z',
                                  's3_x', 's3_y', 's3_z',
                                  's4_x', 's4_y', 's4_z']  # Replace with your desired column names
            # import pdb; pdb.set_trace()
            data = pd.read_csv(vibration_file, names=column_names, index_col=False,delimiter=',')
            
            # ##<Continuous Wavelet Transform>-------------------------
            # # # Choose a wavelet and its parameters
            # wavelet = 'morl'  # Morlet wavelet is a common choice
            # scales = np.arange(1, 128)  # Adjust the range of scales as needed
            
            # fig, axs = plt.subplots(4, 3)
            # pos = [(0,0),(0,1),(0,2),(1,0),(1,1),(1,2),(2,0),(2,1),(2,2),(3,0),(3,1),(3,2)]
            # for cnt,column_name in enumerate(column_names):
            #     i,j = pos[cnt]

            #     # Perform the CWT
            #     coeffs, freqs = pywt.cwt(data[column_name], scales, wavelet)
            #     axs[i,j].imshow(np.abs(coeffs), extent=[0, len(data), min(freqs), max(freqs)], cmap='inferno', aspect='auto')
            # # Show colorbar
            # fig.colorbar(axs[-1, -1].imshow(np.abs(coeffs), cmap='inferno', aspect='auto'), ax=axs, label='Magnitude')
            # # plt.show()
            # plt.savefig(os.path.join(out_dir,finew_datale.split('.')[0] +'.png'))
            # ##<\Continuous Wavelet Transform>-------------------------
            
            # # ##<\Fast Fourier  Transform>-------------------------
            # fig, axs = plt.subplots(4, 3)
            # pos = [(0,0),(0,1),(0,2),(1,0),(1,1),(1,2),(2,0),(2,1),(2,2),(3,0),(3,1),(3,2)]
            # for cnt,column_name in enumerate(column_names):
            #     i,j = pos[cnt]
            #     # Perform FFT on the x-axis data
            #     sample_rate = 128  # Adjust to your actual sample rate
            #     fft_result_x = np.fft.fft(data[column_name])
            #     frequencies = np.fft.fftfreq(len(fft_result_x), 1.0 / sample_rate)
            #     magnitude_x = np.abs(fft_result_x)                
            #     # # Plot the frequency domain representation
            #     axs[i,j].plot(frequencies, magnitude_x)
            # # plt.show()
            # plt.savefig(os.path.join(out_dir,file.split('.')[0] +'.png'))
            # # ##<\Fast Fourier  Transform>-------------------------

            # ##<\Fast Fourier  Transform>-------------------------
            # fig, axs = plt.subplots(4, 3)
            # pos = [(0,0),(0,1),(0,2),(1,0),(1,1),(1,2),(2,0),(2,1),(2,2),(3,0),(3,1),(3,2)]
            # for cnt,column_name in enumerate(column_names):
            #     i,j = pos[cnt]
            #     # Perform FFT on the x-axis data
            #     sample_rate = 128  # Adjust to your actual sample rate
            #     fft_result_x = np.abs(np.fft.fft(data[column_name]))
            #     _len = int(len(fft_result_x)/2)
            #     t = np.linspace(0,sample_rate,_len)
            #     # frequencies = np.fft.fftfreq(len(fft_result_x), 1.0 / sample_rate)
            #     # magnitude_x = np.abs(fft_result_x)                
            #     # # Plot the frequency domain representation
            #     axs[i,j].plot(t, fft_result_x[:_len])
            # ##<\Fast Fourier  Transform>-------------------------
            sensor_F0 = []
            sensor_F0_MAG = []
            fig, axs = plt.subplots(4,1)
            pos = [(0,0),(1,0),(2,0),(3,0)]
            column_names = [('s1_x', 's1_y', 's1_z'),
                                  ('s2_x', 's2_y', 's2_z'),
                                  ('s3_x', 's3_y', 's3_z'),
                                  ('s4_x', 's4_y', 's4_z')] 
            for cnt,column_name in enumerate(column_names):
                col1,col2,col3 = column_name
                new_data = np.sqrt(np.square(data[col1]) + np.square(data[col2])+ np.square(data[col3]))
                sign = np.sign(data[col1]) * np.sign(data[col2]) *np.sign(data[col3])
                arr = np.array([(data[col1]),(data[col2]),(data[col3])])
                sign_idx = np.argmax(np.array([abs(data[col1]),abs(data[col2]),abs(data[col3])]),axis=0)

                sign = [np.sign(arr[idx,cnt]) for cnt,idx in enumerate(sign_idx)]
                # import pdb; pdb.set_trace()

                new_data = new_data *sign
                # new_data = new_data[50:]
                # import pdb; pdb.set_trace()
                i,j = pos[cnt]
                # Perform FFT on the x-axis data
                sample_rate = 8000  # Adjust to your actual sample rate
                fft_result_x = np.abs(np.fft.fft(new_data))
                _len = int(len(fft_result_x)/2)
                t = np.linspace(0,sample_rate,_len)                
                
                ##Calculate F0 from function
                # F0 = calculate_fundamental_frequency(new_data,sample_rate)

                # Compute FFT
                N = len(new_data)  # Number of samples
                fft_values = np.fft.fft(new_data)
                fft_magnitude = np.abs(fft_values)[:N // 2]  # Single-sided magnitude spectrum
                frequencies = np.fft.fftfreq(N, 1 / sample_rate)[:N // 2]  # Frequencies corresponding to FFT
                # Find peaks in the magnitude spectrum
                peaks, _ = find_peaks(fft_magnitude,prominence=1)  # Find all peaks
                peak_frequencies = frequencies[peaks]  # Frequencies of the peaks
                peak_magnitudes = fft_magnitude[peaks]  # Magnitudes of the peaks

                # Sort peaks by magnitude to determine the fundamental frequency
                sorted_indices = np.argsort(peak_magnitudes)[::-1]  # Sort indices by descending magnitude
                sorted_peak_frequencies = peak_frequencies[sorted_indices]  # Frequencies sorted by magnitude

                # Fundamental frequency is the first (highest magnitude) peak
                fundamental_frequency = sorted_peak_frequencies[0]
                
                # # Display results
                # print(f"Fundamental Frequency: {fundamental_frequency:.2f} Hz")


                # frequencies = np.fft.fftfreq(len(fft_result_x), 1.0 / sample_rate)
                # magnitude_x = np.abs(fft_result_x)                
                # import pdb; pdb.set_trace()
                # # Plot the frequency domain representation
                # axs[i].plot(t[50:], fft_result_x[50:_len])
                # axs[i].plot(t, fft_result_x[:_len])
                # axs[i].plot(frequencies[50:], fft_magnitude[50:])
                axs[i].plot(frequencies, fft_magnitude)
                axs[i].scatter([fundamental_frequency],
                            [fft_magnitude[np.abs(frequencies - fundamental_frequency).argmin()],
                            ],
                            color="red", label="Fundamental & Harmonics", zorder=5)
                sensor_F0.append(fundamental_frequency)
                sensor_F0_MAG.append(fft_magnitude[np.abs(frequencies - fundamental_frequency).argmin()])
                




                


                # plt.plot(new_data,'m')
                # plt.plot(data[col1],'r')
                # plt.plot(data[col2],'g')
                # plt.plot(data[col3],'b')
                # plt.show()
                # import pdb; pdb.set_trace()

                
            # plt.show()
            plt.savefig(os.path.join(out_dir,file.split('.')[0] +'.png'))
            # row = []
            # row.extend([file])
            # row.extend(sensor_F0)
            # row.extend(sensor_F0_MAG)
            # print(row)
            # row = [file,sensor_F0,sensor_F0_MAG]
            row = {
                'filename': file,
                's1_f0': sensor_F0[0],  # Example: Random frequency
                's2_f0': sensor_F0[1],
                's3_f0': sensor_F0[2],
                's4_f0': sensor_F0[3],
                's1_M': sensor_F0_MAG[0],
                's2_M': sensor_F0_MAG[1],
                's3_M': sensor_F0_MAG[2],
                's4_M': sensor_F0_MAG[3],
            }
            with open(csv_filename, mode='a', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=columns)
                writer.writerow(row)
    
    # import pdb; pdb.set_trace()
    plt.close('all')
    df = pd.read_csv(csv_filename, names=columns,skiprows=1, index_col=False,delimiter=',')
    plt.plot(list(df['s1_f0']));  plt.title('sensor1 Fundamental Frequency');  plt.savefig(os.path.join(out_dir,'sensor1 F0 Analysis')); plt.close()
    plt.plot(list(df['s2_f0']));  plt.title('sensor2 Fundamental Frequency');  plt.savefig(os.path.join(out_dir,'sensor2 F0 Analysis')); plt.close()
    plt.plot(list(df['s3_f0']));  plt.title('sensor3 Fundamental Frequency');  plt.savefig(os.path.join(out_dir,'sensor3 F0 Analysis')); plt.close()
    plt.plot(list(df['s4_f0']));  plt.title('sensor4 Fundamental Frequency');  plt.savefig(os.path.join(out_dir,'sensor4 F0 Analysis')); plt.close()
    
    

            
            
            # ##<\Fast Fourier  Transform>-------------------------



            # # ##<\Fast Fourier  Transform>-------------------------
            # fig, axs = plt.subplots(4, 1)
            # fig.suptitle(f'{file}', fontsize=16)  # Set the figure title

            # pos = [(0,0),(0,1),(0,2),(1,0),(1,1),(1,2),(2,0),(2,1),(2,2),(3,0),(3,1),(3,2)]
            # for cnt,column_name in enumerate(column_names):
            #     if column_name.endswith('y'):
            #         i,j = pos[cnt]
            #         # Perform FFT on the x-axis data
            #         sample_rate = 128  # Adjust to your actual sample rate
            #         fft_result_x = np.fft.fft(data[column_name])
            #         frequencies = np.fft.fftfreq(len(fft_result_x), 1.0 / sample_rate)
            #         magnitude_x = np.abs(fft_result_x)                
            #         # # Plot the frequency domain representation
            #         axs[i].plot(frequencies, magnitude_x)
            # # plt.title(f"{file}")
            # plt.show()
            # # ##<\Fast Fourier  Transform>-------------------------





            # # f_s = 50.0 # Hz
            # # f = 1.0 # Hz
            # # time = np.arange(0.0, 3.0, 1/f_s)
            # # x = 5 * np.sin(2 * np.pi * f * time) + 2 * np.sin(10 * 2 * np.pi * f * time)
            # # fft_x = np.fft.fft(x)



            # f_s = 1000.0 # Hz
            # fft_x = np.fft.fft(data['s2_x'])
            # n = len(fft_x)
            # freq = np.fft.fftfreq(n, 1/f_s)

            # # plt.plot(np.abs(fft_x))
            # # plt.show()

            # fft_x_shifted = np.fft.fftshift(fft_x)
            # freq_shifted = np.fft.fftshift(freq)



            # # plt.plot(freq_shifted, np.abs(fft_x_shifted))
            # # plt.xlabel("Frequency (Hz)")
            # # plt.show()



            # half_n = int(np.ceil(n/2.0))
            # fft_x_half = (2.0 / n) * fft_x[:half_n]
            # freq_half = freq[:half_n]


            # plt.plot(freq_half, np.abs(fft_x_half))
            # plt.xlabel("Frequency (Hz)")
            # plt.ylabel("Amplitude")

            # plt.show()
     

     

     



            # # Preprocess the data - Apply a low-pass filter
            # def butter_lowpass(cutoff, fs, order=5):
            #     nyquist = 0.5 * fs
            #     normal_cutoff = cutoff / nyquist
            #     b, a = signal.butter(order, normal_cutoff, btype='low', analog=False)
            #     return b, a
            # sample_rate = 1000  # Adjust to your actual sample rate
            # cutoff_frequency = 50  # Adjust the cutoff frequency as needed
            # order = 5

            # # butter_lowpass = butter_lowpass(cutoff_frequency, sample_rate)
            # # # Design a Butterworth low-pass filter
            # # sos = signal.butter(order, cutoff_frequency, btype='low', output='sos')


            # # data['x'] = signal.sosfilt(sos, data['s2_x'])
            # # data['y'] = signal.sosfilt(sos, data['s2_y'])
            # # data['z'] = signal.sosfilt(sos, data['s2_z'])

            # # Analyze the data
            # mean_x = data['s2_x'].mean()
            # std_x = data['s2_x'].std()

            # # Frequency analysis - Fast Fourier Transform (FFT)
            # f, Pxx_x = signal.periodogram(data['s2_x'], fs=sample_rate)

            # # Visualize the FFT results
            # plt.figure()
            # plt.semilogy(f, np.sqrt(Pxx_x))
            # plt.xlabel('Frequency [Hz]')
            # plt.ylabel('Spectral Density')
            # plt.show()

            # # Compute the spectrogram
            # frequencies, times, Sxx = signal.spectrogram(data['s2_x'], fs=sample_rate)



            # # Create a spectrogram plot
            # plt.figure(figsize=(10, 6))
            # plt.pcolormesh(times, frequencies, 10 * np.log10(Sxx), shading='auto', cmap='inferno')
            # plt.title('Spectrogram-Like Plot')
            # plt.xlabel('Time (s)')
            # plt.ylabel('Frequency (Hz)')
            # plt.colorbar(label='Power/Frequency (dB/Hz)')
            # plt.ylim(0, 100)  # Adjust the frequency range as needed
            # plt.show()


            # y, sr = librosa.load('15_mic1.wav')
            # # Compute MFCCs
            # # mfccs = librosa.feature.mfcc(y=np.asarray(data['s2_x']).astype('float32'), sr=sample_rate, n_mfcc=13)
            # mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)

            # # Visualize MFCCs
            # plt.figure(figsize=(10, 6))
            # librosa.display.specshow(mfccs, x_axis='time')
            # plt.colorbar()
            # plt.title('MFCCs')
            # plt.xlabel('Time')
            # plt.ylabel('MFCC Coefficients')
            # plt.show()


            # # # Interpret the results and take further actions as needed