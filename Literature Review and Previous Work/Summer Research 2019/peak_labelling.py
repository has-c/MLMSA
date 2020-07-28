from operator import itemgetter
import matplotlib.pyplot as plt

#Remove line breaks from plain text data
def remove_breaks(lines):
    for index in range(len(lines)):
        line = lines[index]
        if line[-1] == "\n":
            lines[index] = line[0:-1]
    return(lines)

#Returns local maxima from a list of peaks
def get_maxima(peaks):
    maxima = []
    appendable = True
    for i in range(len(peaks)):
        peak = peaks[i]
        #Only significant (intensity > 5% of the max intensity) peaks are considered
        if peak[1] > 0.05 and appendable:
            maximum = True
            #The left and right bounds denote a group of 40 peaks surrounding the peak being examined
            left_bound = max(0, i - 20)
            right_bound = min(len(peaks), i + 20)
            for j in range(left_bound, right_bound):
                comparison_peak = peaks[j]
                #If any peaks withing the group are higher than the peak being examined, it is not considered a local maximum
                if comparison_peak[1] > peak[1]:
                    maximum = False
            if maximum:
                maxima.append(peak)
                #Once a local maxima has been found, no further peaks are considered until a sufficiently small peak (intensity <= 1% of the max intensity) occurs
                #This is to prevent small fluctuations in the data from causing many local maxima to be found within the same overall peak
                appendable = False
        elif peak[1] <= 0.01:
            appendable = True
    return(maxima)

#Open the file with the spectra and read the contents
input_file = open("o_1_1.xy", "r")
input_lines = input_file.readlines()
input_file.close()
input_lines = remove_breaks(input_lines)

#Initialise a dictionary to store the peaks
peaks_dict = {}
#Process each line of the text file and store the data in the dictionary
for line in input_lines:
    current_mz, current_intensity = line.split()
    current_mz = float(current_mz)
    current_intensity = float(current_intensity)
    #This if statement accounts for instances where multiple peaks with the same m/z are present (usually separated by time)
    if current_mz in peaks_dict.keys():
        peaks_dict[current_mz] += current_intensity
    else:
        peaks_dict[current_mz] = current_intensity

#Once duplicate m/z values have had their intensities summed, storing the peaks in a list allows easier access
peaks_list = []
#The intensity value of each peak is divided by the maximum intensity value, to normalise the data with the max at i = 1
max_i = max(peaks_dict.values())
for mz, intensity in peaks_dict.items():
    peaks_list.append([mz, intensity / max_i])

#To reduce the number of peaks needed to represent the meaningful features in the data, the list of peaks is filtered to a list of local maxima
local_maxima = get_maxima(peaks_list)

#Known molecular masses are initialised
#ub_mass is the mass of Ubiquitin
ub_mass = 8565
#ox_mass refers to the mass of Pt + the mass of the Oxaliplatin C6H14N2 ligand (a.k.a. the overall mass of Oxaliplatin once bound)
ox_mass = 195 + 114.18
ub_peaks = []
#ubo_peaks are peaks where Ubiquitin and Oxaliplatin are both present (where binding has occured)
ubo_peaks = []

#Possible peaks which would result from a molecule with charges between 1 and 20 are examined
for charge in range(1,20):
    #MOC stands for Mass Over Charge
    ub_moc = ub_mass / charge
    ubo_moc = (ub_mass + ox_mass) / charge
    ub_peak = [0, 0]
    #If any peaks in the local maxima list are sufficiently close to the predicted m/z, the one with the highest intensity is selected as the match
    for peak in local_maxima:
        if peak[0] >= ub_moc - 1 and peak[0] <= ub_moc + 1:
            if ub_peak[1] < peak[1]:
                ub_peak = peak
    #If a match is found, it is added to our list of Ubiquitin peaks, along with its associated charge
    if ub_peak != [0, 0]:
        ub_peaks.append([ub_peak, charge])
        #Once a Ubiquitin peak is found, a smiliar process is repeated to find it's associated Ubiquitin + Oxaliplatin peak (the first adduct)
        ubo_peak = [0, 0]
        for peak in local_maxima:
            if peak[0] >= ubo_moc - 1 and peak[0] <= ubo_moc + 1:
                if ubo_peak[1] < peak[1]:
                    ubo_peak = peak
        if ubo_peak != [0,0]:
            ubo_peaks.append([ubo_peak, charge])

#Colours used for visualisation are initialised
colours = ['g','y','m','b','k','r','c','#f05e23']
#Each of the detected peaks is displayed using the matplotlib library
for i in range(0,len(ub_peaks),1):
    item = ub_peaks[i][0]
    plt.vlines(item[0],0,item[1],colors=colours[i],label='Ub (charge = ' + str(ub_peaks[i][1]) + ')')
    item = ubo_peaks[i][0]
    plt.vlines(item[0],0,item[1],colors=colours[i],linestyles='dashed',label='Ub + O')
plt.legend()
plt.show()