import pyopenms
from pyopenms import *
from scipy.spatial.distance import euclidean
from fastdtw import fastdtw
from operator import itemgetter

#Remove line breaks from plain text data
def remove_breaks(lines):
    for index in range(len(lines)):
        line = lines[index]
        if line[-1] == "\n":
            lines[index] = line[0:-1]
    return(lines)

#Combines several spectra (separated by time) into a single overall spectrum for that experiment
def sum_spectra(spectra):
    summed_peaks = {}
    for spectrum in spectra:
        mz, intensity = spectrum.get_peaks()
        for i in range(len(mz)):
            current_mz = mz[i]
            current_intensity = intensity[i]
            #This accounts for duplicate peak entries with the same m/z value (and adds their intensities together)
            if current_mz in summed_peaks:
                summed_peaks[current_mz] += current_intensity
            else:
                summed_peaks[current_mz] = current_intensity
    return(summed_peaks)

#Returns a dictionary of peaks obtained by subtracting the peaks of the unbound spectrum (Ub) away from the peaks of the bound spectrum (Ub + either C, O, or T)
def get_difference(bound, unbound):
    bound_peaks = {}
    unbound_peaks = {}
    difference_peaks = {}
    for mz, intensity in bound.items():
        if mz in bound_peaks:
            bound_peaks[mz] += intensity
        else:
            bound_peaks[mz] = intensity
    for mz, intensity in unbound.items():
        if mz in unbound_peaks:
            unbound_peaks[mz] += intensity
        else:
            unbound_peaks[mz] = intensity
    #The values in both spectra are normalized by dividing by the maximum value, so the maximum intensity is set to 1
    bound_max = max(bound_peaks.values())
    unbound_max = max(unbound_peaks.values())
    for mz, i in bound_peaks.items():
        difference_peaks[mz] = i / bound_max
    for mz, i in unbound_peaks.items():
        if mz in difference_peaks:
            difference_peaks[mz] -= i / unbound_max
        else:
            difference_peaks[mz] = -i / unbound_max
    return(difference_peaks)

#Finds the closest peak (in the theoretical spectrum) for a given peak in the difference spectrum
def find_closest(peak):
    #If the m/z of the given peak is lower than any in the theoretical spectrum, return the peak with the lowest m/z in the theoretical spectrum
    if peak[0] < theoretical[0][0]:
        return(theoretical[0])
    #If the m/z of the given peak is higher than any in the theoretical spectrum, return the peak with the highest m/z in the theoretical spectrum
    elif peak[0] > theoretical[-1][0]:
        return(theoretical[-1])
    else:
        left = 0
        right = 0
        index = 0
        #Find the closest peak on either side of the given peak
        while left == 0 :
            current = theoretical[index]
            if current[0] == peak[0]:
                return(current)
            elif current[0] > peak[0]:
                right = current
                left = theoretical[index - 1]
            index += 1
        #Return the peak on the side that is closer to the one given
        left_closer = peak[0] - left[0] < right[0] - peak[0]
        if left_closer:
            return(left)
        else:
            return(right)

#Open the file with the unbound spectra and read the contents
unbound_file = open("ub_1_1.xy", "r")
unbound_lines = unbound_file.readlines()
unbound_file.close()
unbound_lines = remove_breaks(unbound_lines)
#Create an experiment to store the unbound data
unbound_exp = pyopenms.MSExperiment()
unbound_spectrum = MSSpectrum()
unbound_mz = []
unbound_intensity =[]
#Process each line of the text file and store the data in the lists
for line in unbound_lines:
    current_mz, current_intensity = line.split()
    #Accuracy of m/z values is standardised at 1dp as this is the lowest accuracy encountered among xy files we used
    unbound_mz.append(round(float(current_mz),1))
    unbound_intensity.append(float(current_intensity))
#Update the experiment with the data, then store it in a file
unbound_spectrum.set_peaks([unbound_mz, unbound_intensity])
unbound_exp.setSpectra([unbound_spectrum])
pyopenms.MzMLFile().store("unbound.mzML", unbound_exp)

#Open the file with the bound spectra and read the contents
bound_file = open("o_1_1.xy", "r")
bound_lines = bound_file.readlines()
bound_file.close()
bound_lines = remove_breaks(bound_lines)
#Create an experiment to store the bound data
bound_exp = pyopenms.MSExperiment()
bound_spectrum = MSSpectrum()
bound_mz = []
bound_intensity =[]
#Process each line of the text file and store the data in the lists
for line in bound_lines:
    current_mz, current_intensity = line.split()
    #Accuracy of m/z values is standardised at 1dp as this is the lowest accuracy encountered among xy files we used
    bound_mz.append(round(float(current_mz),1))
    bound_intensity.append(float(current_intensity))
#Update the experiment with the data, then store it in a file
bound_spectrum.set_peaks([bound_mz, bound_intensity])
bound_exp.setSpectra([bound_spectrum])
pyopenms.MzMLFile().store("bound.mzML", bound_exp)

#Import the two mzML files into experiments, and retrieve a single spectrum for each
bound = MSExperiment()
MzMLFile().load("bound.mzML", bound)
bound_spectrum = sum_spectra(bound.getSpectra())
unbound = MSExperiment()
MzMLFile().load("unbound.mzML", unbound)
unbound_spectrum = sum_spectra(unbound.getSpectra())

#In theory, subtracting the unbound spectrum from the bound spectrum should return the effects of the binding with the platin
binding_effect = get_difference(bound_spectrum, unbound_spectrum)

#Convert the string representation of Ubiquitin into an amino acid sequence object
ubiquitin = AASequence.fromString("MQIFVKTLTGKTITLEVEPSDTIENVKAKIQDKEGIPPDQQRLIFAGKQLEDGRTLSDYNIQKESTLHLVLRLRGG")
tsg = TheoreticalSpectrumGenerator()
spectrum = MSSpectrum()
#Initialise parameters object and set the values for parameters
#To change which parameters are set to true (false is default), specific lines can be commented out and vice versa
parameters = Param()
parameters.setValue(b"add_isotopes", b"true", "")
#parameters.setValue(b"add_losses", b"true", "")
parameters.setValue(b"add_b_ions", b"true", "")
parameters.setValue(b"add_y_ions", b"true", "")
parameters.setValue(b"add_a_ions", b"true", "")
parameters.setValue(b"add_c_ions", b"true", "")
parameters.setValue(b"add_x_ions", b"true", "")
parameters.setValue(b"add_z_ions", b"true", "")
#parameters.setValue(b"add_precursor_peaks", b"true", "")
#parameters.setValue(b"add_all_precursor_charges", b"true", "")
#parameters.setValue(b"add_first_prefix_ion", b"true", "")
parameters.setValue(b"add_metainfo", b"true", "")
tsg.setParameters(parameters)
#Generate the theoretical spectrum of Ubiquitin
tsg.getSpectrum(spectrum, ubiquitin, 1, 2)

#Stores the peaks of the difference spectrum in a list of [m/z, i] items
difference = []
for mz, i in binding_effect.items():
    if i < 0:
        difference.append([mz,-i])

#The theoretical spectrum is converted from a pair of lists to a single list of [m/z, i] items
theoretical = []
for i in range(len(spectrum.get_peaks()[0])):
    current_mz = spectrum.get_peaks()[0][i]
    current_intensity = spectrum.get_peaks()[1][i]
    theoretical.append([current_mz, current_intensity])

len_t = len(theoretical)
#Sort the difference spectrum by intensity values from largest to smallest
filtered_difference = sorted(difference, key=itemgetter(1), reverse=True)
#To make the DTW calculation less computationally intensive, only the n peaks with the highest intensity values are used (where n is the number of peaks in the theoretical spectrum)
if len_t < len(filtered_difference):
    filtered_difference = filtered_difference[:len_t]
len_fd = len(filtered_difference)

#The distance between the two lists of peaks, and path through the DTW matrix are calculated
distance, path = fastdtw(filtered_difference, theoretical)
#The DTW distance is normalised by dividing by the sum of the lengths of the two input series'
#This 'sum of the two lengths' value was chosen as it is proportional to the length of the diagonal path that the DTW algorithm must find across the DTW matrix
norm_distance = distance / (len_t + len_fd)

#The number of peaks was further reduced such that only peaks with large enough intensities were considered as meaningful indicaitons of binding sites
significant_peaks = filtered_difference[:100]

#Create a list of pairs of peaks matching each peak from significant_peaks to it's closest counterpart in the theoretical spectrum
matched_peaks = []
for peak in significant_peaks:
    theo_peak = find_closest(peak)
    matched_peaks.append([peak, theo_peak])

#For each pair of matched peaks, their m/z and intensity is added to a dictionary
matching_significance = {}
for match in matched_peaks:
    match_mz = match[1][0]
    match_i = match[0][1]
    #Multiple signigicant peaks may be matched to the same theoretical peak if that theoretical peak is the closest peak to multiple experimental peaks, in which case their intensities are added together
    #These sums of intensities are reffered to as the 'significance' of the theoretical peak which was matched
    if match_mz not in matching_significance.keys():
        matching_significance[match_mz] = match_i
    else:
        matching_significance[match_mz] += match_i

#For each peak identified in the matching_significance above, the ion of that peak is identified from the original TheoreticalSpectrumGenerator spectrum
fragments = []
for ion, peak in zip(spectrum.getStringDataArrays()[0], spectrum):
    for peak_mz, peak_sig in matching_significance.items():
        if peak.getMZ() == peak_mz:
            fragments.append([ion, peak_mz, peak_sig])
#These fragments (which represent potential binding sites) are sorted from most significant to least
fragments = sorted(fragments, key=itemgetter(2), reverse=True)

#The results are printed out, including the fragment type, location, and charge (e.g. y15++), the m/z of that fragment, and the fragments significance as a potential binding site
print("Ion\t\tm/z\t\t\tRelative Significance")
for fragment in fragments:
    if len(fragment[0]) < 5:
        print(fragment[0], "\t\t", fragment[1], "\t", fragment[2], sep="")
    else:
        print(fragment[0], "\t", fragment[1], "\t", fragment[2], sep="")