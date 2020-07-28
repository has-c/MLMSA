import pyopenms
from pyopenms import *
from scipy.spatial.distance import euclidean
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
def find_closest(peak,theoretical):
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
