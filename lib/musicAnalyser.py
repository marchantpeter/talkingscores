__author__ = 'PMarchant'

import json
import math
import pprint
import logging, logging.handlers, logging.config
from music21 import *

logger = logging.getLogger("TSScore")

class MusicAnalyser:
    score = None
    analyse_parts = []

    def __init__(self):
        print("hello - I'm a MusicAnalyser...")
        

    def setScore(self, sc):
        if not self.score == None: # it still gets called twice - I don't know why!
            print ("score already added...")
            return

        self.score = sc
        part_index = 0
        self.analyse_parts = []
        for p in self.score.parts:
            #print (p.flat.notes.secondsMap)
            self.analyse_parts.append(AnalysePart())
            self.analyse_parts[part_index].setPart(p)
            part_index = part_index + 1
        
        print("\n ### \n")
        print("added all the parts")
        for ap in self.analyse_parts:
            print ("len interval dictionary = " + str(len(ap.interval_dictionary)))
        
    
    def count_pitches(self):
        print("counting pitches")


class AnalyseIndex:

    def __init__(self, ei):
        #print("hello - I'm an AnalyseIndex...")
        self.event_index = ei
        self.event_type = '' # n c r

        self.chord_interval_index = [-1, -1] 
        self.chord_pitches_index = [-1, -1]
        self.chord_name_index = ['', -1]
        
        self.pitch_number_index = [-1, -1]
        self.pitch_name_index = ['', -1]
        self.interval_index = [-1, -1]

        self.rhythm_note_index = [-1, -1]
        self.rhythm_chord_index = [-1, -1]
        self.rhythm_rest_index = [-1, -1]

class AnalysePart:
    
    def __init__(self):
        print("hello - I'm an AnalysePart...")
        self.analyse_indexes = []
        
        self.pitches = [0] * 128
        self.pitch_list = []
        self.pitch_name_dictionary = {}
        self.interval_dictionary = {}
        self.rhythm_note_dictionary = {}
        self.rhythm_rest_dictionary = {}
        self.rhythm_chord_dictionary = {}

        self.chord_pitches_list = [] # each unique chord
        self.chord_pitches_dictionary = {} # index of each chord occurrence
        self.chord_intervals_list = []
        self.chord_intervals_dictionary = {}
        self.chord_common_name_dictionary = {}

        self.count_pitches = []
        self.count_pitch_names = []
        self.count_intervals = []
        self.count_chord_pitches = []
        self.count_chord_intervals = []
        self.count_chord_common_names = []
        self.count_rhythm_note = []
        self.count_rhythm_rest = []
        self.count_rhythm_chord = []

        self.note_duration = 0
        self.note_count = 0
        self.rest_duration = 0
        self.rest_count = 0
        self.chord_duration = 0
        self.chord_count = 0

        self.part = None


    def find_chord(self, chord):
        chord_index=0
        find = sorted(p.midi for p in chord.pitches)
        for c in self.chord_pitches_list:
            if c==find:
                return chord_index
            chord_index += 1
        return -1
    
    def find_chord_intervals(self, chord_intervals):
        chord_index=0
        for c in self.chord_intervals_list:
            if c==chord_intervals:
                return chord_index
            chord_index += 1
        return -1
    
    def make_chord_intervals(self, chord):
        p1 = chord.pitches[0].midi
        pitches = sorted(p.midi for p in chord.pitches)
        intervals = [p-p1 for p in pitches]
        return intervals
        


    def setPart(self, p):
        self.part = p
        print("I'm setting a part...")
        print (p)

        for i in range(128):
            self.pitch_list.append([])

        event_index = 0
        last_note_pitch = -1
        for n in self.part.flat.notesAndRests:
            ai = AnalyseIndex(event_index)
            if n.isRest:
                ai.event_type = 'r'
                
                d = n.duration.quarterLength
                if self.rhythm_rest_dictionary.get(d) == None:
                    self.rhythm_rest_dictionary[d] = [event_index]
                else:
                    self.rhythm_rest_dictionary[d].append(event_index)
                ai.rhythm_rest_index = [self.rhythm_rest_dictionary.get(d), len(self.rhythm_rest_dictionary.get(d))-1]
                
                last_note_pitch = -1
                self.rest_duration += d
                self.rest_count += 1
            elif n.isChord:
                ai.event_type = 'c'
                
                d = n.duration.quarterLength
                if self.rhythm_chord_dictionary.get(d) == None:
                    self.rhythm_chord_dictionary[d] = [event_index]
                else:
                    self.rhythm_chord_dictionary[d].append(event_index)
                ai.rhythm_chord_dictionary = [self.rhythm_chord_dictionary.get(d), len(self.rhythm_chord_dictionary.get(d))-1]
                
                index = self.find_chord(n)
                if index == -1:
                    self.chord_pitches_list.append(sorted(p.midi for p in n.pitches))
                    index = len(self.chord_pitches_list)-1
                    self.chord_pitches_dictionary[index] = [event_index]
                else:
                    self.chord_pitches_dictionary[index].append(event_index)
                ai.chord_pitches_index = [index, len(self.chord_pitches_dictionary.get(index))-1]
                
                chord_intervals = self.make_chord_intervals(n)
                index = self.find_chord_intervals(chord_intervals)
                if index == -1:
                    self.chord_intervals_list.append(chord_intervals)
                    index = len(self.chord_intervals_list)-1
                    self.chord_intervals_dictionary[index] = [event_index]
                else:
                    self.chord_intervals_dictionary[index].append(event_index)
                ai.chord_interval_index = [index, len(self.chord_intervals_dictionary.get(index))-1]
                
                common_name = n.commonName
                #music21 describes eg A, D, E as a quatral trichord - ie E, A, D are perfect fourths...
                if chord_intervals == [0, 5, 7]:
                    common_name = "Suspended 4th"
                elif chord_intervals == [0, 2, 7]:
                    common_name = "Suspended 2nd"
                if self.chord_common_name_dictionary.get(common_name) == None:
                    self.chord_common_name_dictionary[common_name] = [event_index]
                else:
                    self.chord_common_name_dictionary[common_name].append(event_index)
                ai.chord_name_index = [common_name, len(self.chord_common_name_dictionary.get(common_name))-1]
                
                self.chord_duration += d
                self.chord_count += 1
            elif not n.isChord:
                ai.event_type = 'n'
                
                self.pitches[n.pitch.midi] += 1
                self.pitch_list[n.pitch.midi].append(event_index)
                ai.pitch_number_index = [n.pitch.midi, len(self.pitch_list[n.pitch.midi])-1]
                
                if self.pitch_name_dictionary.get(n.pitch.name) == None:
                    self.pitch_name_dictionary[n.pitch.name] = [event_index]
                else:
                    self.pitch_name_dictionary[n.pitch.name].append(event_index)
                ai.pitch_name_index = [n.pitch.name, len(self.pitch_name_dictionary[n.pitch.name])-1]
                
                if (last_note_pitch>-1):
                    interval = n.pitch.midi-last_note_pitch
                    if self.interval_dictionary.get(interval) == None:
                        self.interval_dictionary[interval] = [event_index]
                    else:
                        self.interval_dictionary[interval].append(event_index)
                    ai.interval_index = [interval, len(self.interval_dictionary.get(interval))-1]
                
                d = n.duration.quarterLength
                if self.rhythm_note_dictionary.get(d) == None:
                    self.rhythm_note_dictionary[d] = [event_index]
                else:
                    self.rhythm_note_dictionary[d].append(event_index)
                ai.rhythm_note_dictionary = [self.rhythm_note_dictionary.get(d), len(self.rhythm_note_dictionary.get(d))-1]
                
                last_note_pitch = n.pitch.midi
                self.note_duration += d
                self.note_count += 1
            
            self.analyse_indexes.append(ai)
            event_index = event_index + 1 

        #for i in range (128):
            #if self.pitches[i]>0:
                #print("i = " + str(i) + " - " + str(self.pitches[i]))
                #print(self.pitch_list[i])

        #print(self.rhythm_note_dictionary)

        print("\n ### after \n")
        print("note count = " + str(self.note_count))
        print("note duration = " + str(self.note_duration))
        print("rest count = " + str(self.rest_count))
        print("rest duration = " + str(self.rest_duration))
        print("chord count = " + str(self.chord_count))
        print("chord duration = " + str(self.chord_duration))

        print ("\n ### \n")

        #print(self.chord_intervals_list)
        #print(self.chord_intervals_dictionary)

        print (self.chord_common_name_dictionary)
 
        #make lists of index and totals then sort by totals for eg most common pitch / rhythm etc
        #lists
        self.count_pitches = self.count_list(self.pitch_list)
        print(self.count_pitches)
        #dictionaries
        self.count_pitch_names = self.count_dictionary(self.pitch_name_dictionary)
        self.count_intervals = self.count_dictionary(self.interval_dictionary)
        self.count_chord_common_names = self.count_dictionary(self.chord_common_name_dictionary)
        self.count_rhythm_note = self.count_dictionary(self.rhythm_note_dictionary)
        self.count_rhythm_rest = self.count_dictionary(self.rhythm_rest_dictionary)
        self.count_rhythm_chord = self.count_dictionary(self.rhythm_chord_dictionary)
        #dictionaries with list indexes as keys
        self.count_chord_pitches = self.count_dictionary(self.chord_pitches_dictionary)
        self.count_chord_intervals = self.count_dictionary(self.chord_intervals_dictionary)
        
        #self.count_pitches = self.count_list(self.pitch_list)


    def sort_count_list(self, e):
        return e[1]

    def count_dictionary(self, d):
        sorted_list = []
        for k, v in d.items():
            sorted_list.append([k, len(v)])
        sorted_list.sort(reverse=True, key=self.sort_count_list)
        return sorted_list

    def count_list(self, l):
        sorted_list = []
        i = 0
        for item in l:
            if len(item)>0:
                sorted_list.append([i, len(item)])
            i += 1
        sorted_list.sort(reverse=True, key=self.sort_count_list)
        return sorted_list


    #get keys in order of items in list - for w in sorted(self.chord_common_name_dictionary, key=self.sort_count_dictionary, reverse=True):
    def sort_count_dictionary(self, e):
        return len(e)




