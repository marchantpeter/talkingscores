__author__ = 'PMarchant'

import json
import math
import pprint
import logging, logging.handlers, logging.config
from music21 import *

logger = logging.getLogger("TSScore")

class AnalyseIndex:

    def __init__(self, ei):
        self.event_index = ei
        self.event_type = '' # n c r

        #[the particular eg chord_interval_index, the occurance of that particular event in eg AnalysePart.chord_pitches_dictionary]
        self.chord_interval_index = [-1, -1] 
        self.chord_pitches_index = [-1, -1]
        self.chord_name_index = ['', -1]
        
        self.pitch_number_index = [-1, -1]
        self.pitch_name_index = ['', -1]
        self.interval_index = [-1, -1]
        #possibly only needs one rhythm index
        self.rhythm_note_index = [-1, -1]
        self.rhythm_chord_index = [-1, -1]
        self.rhythm_rest_index = [-1, -1]
    
    def print_info(self):
        print("EventIndex..." + str(self.event_index) + " - type " + self.event_type)
        if (self.event_type=='n'):
            print(self.pitch_name_index + self.pitch_number_index + self.interval_index)
            print ("rhythm " + str(self.rhythm_note_index))
        elif (self.event_type=='c'):
            print(self.chord_pitches_index + self.chord_interval_index + self.chord_name_index)
            print ("rhythm " + str(self.rhythm_chord_index))
        elif (self.event_type=='r'):
            print("rhythm " + str(self.rhythm_rest_index))
        

class AnalyseSection:
    def __init__(self):
        self.analyse_indexes = [] # all the notes etc in the section
        self.section_start_event_indexes = [] # the event indexes where this section occurs
        
    def print_info(self):
        print("section length = " + str(len(self.analyse_indexes)))
        #for ai in self.analyse_indexes:
            #ai.print_info

class MusicAnalyser:
    score = None
    analyse_parts = []
    summary = ""
    repetition_right_hand = ""
    repetition_left_hand = ""

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
        
        self.repetition_left_hand = self.analyse_parts[1].describe_repetition()
        self.repetition_right_hand = self.analyse_parts[0].describe_repetition()

        self.summary_left_hand = self.analyse_parts[1].describe_summary()
        self.summary_right_hand = self.analyse_parts[0].describe_summary()


    def count_pitches(self):
        print("counting pitches")

class AnalysePart:

    _position_map = {
        0: 'near the start',
        1: 'before the middle',
        2: 'after the middle',
        3: 'near the end'
    }

    _DURATION_MAP = {
        4.0: 'semibreves',
        3.0: 'dotted minims',
        2.0: 'minims',
        1.5: 'dotted crotchets',
        1.0: 'crotchets',
        0.75: 'dotted quavers',
        0.5: 'quavers',
        0.375: 'dotted semi-quavers',
        0.25: 'semi-quavers',
        0.1875: 'dotted demi-semi-quavers',
        0.125: 'demi-semi-quavers',
        0.09375: 'dotted hemi-demi-semi-quavers',
        0.0625: 'hemi-demi-semi-quavers',
        'zero': 'grace notes',
    }
    
    def compare_sections(self, s1:AnalyseSection, s2:AnalyseSection, compare_type): 
        to_return = True
        if (len(s1.analyse_indexes)!=len(s2.analyse_indexes)):
            to_return=False
        else:
            for i in range(len(s1.analyse_indexes)):
                if (compare_type==0 and self.compare_indexes(s1.analyse_indexes[i], s2.analyse_indexes[i])==False):
                    to_return=False
                    break
                elif(compare_type==1 and self.compare_indexes_rhythm(s1.analyse_indexes[i], s2.analyse_indexes[i])==False):
                    to_return=False
                    break
                elif(compare_type==2 and self.compare_indexes_intervals(s1.analyse_indexes[i], s2.analyse_indexes[i])==False):
                    to_return=False
                    break
        return to_return

    #one might have a chord or play a note in octaves - and this will say the intervals don't match - even if they kind of do...
    def compare_indexes_intervals(self, ai1:AnalyseIndex, ai2:AnalyseIndex):
        to_return = True
        if not (ai1.event_type==ai2.event_type):
            to_return = False
        elif(ai1.event_type=='n'):
            if(ai1.interval_index[0]!=ai2.interval_index[0]):
                to_return = False
        
        return to_return

    #rest durations must match.  Chords / single notes are interchangeable - but their durations must match
    def compare_indexes_rhythm(self, ai1:AnalyseIndex, ai2:AnalyseIndex):
        to_return = True
        if (ai1.event_type=='r' and not ai2.event_type=='r'):
            to_return = False
        elif ( (ai1.event_type=='n' or ai1.event_type=='c') and ai2.event_type=='r'):
            to_return = False
        elif ( (ai1.rhythm_chord_index[0]!=ai2.rhythm_chord_index[0])):
            to_return = False
        elif ( (ai1.rhythm_note_index[0]!=ai2.rhythm_note_index[0])):
            to_return = False
        elif ( (ai1.rhythm_rest_index[0]!=ai2.rhythm_rest_index[0])):
            to_return = False

        return to_return
        

    def compare_indexes(self, ai1:AnalyseIndex, ai2:AnalyseIndex):
        to_return = True
        if not (ai1.event_type==ai2.event_type):
            to_return = False
        elif (ai1.event_type=='n'):
            if (ai1.rhythm_note_index[0]!=ai2.rhythm_note_index[0]) :
                to_return = False
            if (ai1.pitch_number_index[0]!=ai2.pitch_number_index[0]) :
                to_return = False
        elif (ai1.event_type=='c'):
            if (ai1.rhythm_chord_index[0]!=ai2.rhythm_chord_index[0]):
                to_return = False
            if (ai1.chord_pitches_index[0]!=ai2.chord_pitches_index[0]):
                to_return = False
        elif (ai1.event_type=='r'):
            if (ai1.rhythm_rest_index[0]!=ai2.rhythm_rest_index[0]):
                to_return = False
        return to_return

    def __init__(self):
        print("hello - I'm an AnalysePart...")
        self.analyse_indexes = []
        self.analyse_indexes_list = []
        self.analyse_indexes_dictionary = {}
        self.measure_indexes = {} # a dictionary instead of a list because there might be a pickup bar
        
        self.measure_analyse_indexes_list = [] # each element is a list of AnalyseIndex
        self.measure_analyse_indexes_dictionary = {} # index of each measure occurrence
        self.measure_analyse_indexes_all = {} # the index of every measure within measure_analyse_indexes_list
        self.measure_groups_list = [] # [ [[1, 4], [9, 12]], [[7, 8], [15, 16]] ]
        self.repeated_measures_not_in_groups_dictionary = {} # measure index, list of repetition

        self.measure_rhythm_analyse_indexes_list = [] # each element is a list of AnalyseIndex
        self.measure_rhythm_analyse_indexes_dictionary = {} # index of each measure occurrence
        self.measure_rhythm_analyse_indexes_all = {} # the index of every measure within measure_analyse_indexes_list
        self.measure_rhythm_not_full_match_all = [] # [[1, 3, 6], [2, 4]]
        self.measure_rhythm_not_full_match_groups_list = [] # [ [[1, 4], [9, 12]], [[7, 8], [15, 16]] ]
        self.repeated_rhythm_measures_not_full_match_not_in_groups_dictionary = {} # measure index, list of repetition
        
        self.measure_intervals_analyse_indexes_list = [] # each element is a list of AnalyseIndex
        self.measure_intervals_analyse_indexes_dictionary = {} # index of each measure occurrence
        self.measure_intervals_analyse_indexes_all = {} # the index of every measure within measure_analyse_indexes_list
        self.measure_intervals_not_full_match_all = []
        self.measure_intervals_not_full_match_groups_list = [] # [ [[1, 4], [9, 12]], [[7, 8], [15, 16]] ]
        self.repeated_intervals_measures_not_full_match_not_in_groups_dictionary = {} # measure index, list of repetition
        
        self.pitches = [0] * 128
        self.pitch_list = []
        self.pitch_name_dictionary = {}
        self.interval_dictionary = {}
        self.rhythm_note_dictionary = {}
        self.rhythm_rest_dictionary = {}
        self.rhythm_chord_dictionary = {}
        self.count_accidentals_in_measures = {}

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
        self.accidental_count = 0 # displayed accidentals ie not in the key signature
        self.possible_accidental_count = 0 # each note - on its own or part of a chord
        
        self.part = None

    #if a section doesn't contain any consecutive notes - then it doesn't contain any intervals...
    #all the interval indexes will be -1 so compare_sections will think it is a match for intervals!
    def does_section_contain_intervals(self, section:AnalyseSection):
        for ai in section.analyse_indexes:
            if (ai.interval_index[0]>-1):
                return True
        return False

    #compare_type - 0 = all, 1=rhythm, 2=intervals
    def find_section(self, section_to_find:AnalyseSection, sections_to_search, compare_type):
        i = 0
        for s in sections_to_search:
            if self.compare_sections(s, section_to_find, compare_type):
                return i
            i += 1
        return -1

    def find_analyse_index(self, ai):
        ai_index = 0
        for a in self.analyse_indexes_list:
            if self.compare_indexes(ai, self.analyse_indexes[ai_index]):
                return ai_index
            ai_index += 1
        return -1

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
    
    def when_is_measure_next_used(self, measure_index):
        mia = self.measure_analyse_indexes_dictionary[self.measure_analyse_indexes_all[measure_index][0]]
        if len(mia)-1>self.measure_analyse_indexes_all[measure_index][1]:
            return mia[self.measure_analyse_indexes_all[measure_index][1]+1] 
        else:
            return -1

    def are_measures_in(self, group_list, current_measure_index, check_measure_index):
        for group in group_list:
            if current_measure_index in group and check_measure_index in group:
                return True
        return False 
        
        
    def is_measure_used_at(self, current_measure_index, check_measure_index):
        if not check_measure_index in self.measure_analyse_indexes_all:
            return False
        else:    
            if (self.measure_analyse_indexes_all[current_measure_index][0]==self.measure_analyse_indexes_all[check_measure_index][0]):
                return True
            else:
                return False

    def find_measure_group(self, mg, to_list):
        mg_index=0
        mg_index = 0
        for measure_groups in to_list:
            for group in measure_groups:
                if mg==group:
                    return mg_index
            mg_index += 1
        return -1

    def calculate_rhythm_measures_not_full_match(self):
        for measure_indexes in self.measure_rhythm_analyse_indexes_dictionary.values():
            if len(measure_indexes)>1: # the rhythm of this measure is used more than once
                measures=[]
                for measure_index in measure_indexes:
                    if (len(self.measure_analyse_indexes_dictionary[self.measure_analyse_indexes_all[measure_index][0]])==1):
                        measures.append(measure_index)               
                if len(measures)>1:
                    self.measure_rhythm_not_full_match_all.append(measures)

    def calculate_intervals_measures_not_full_match(self):
        for measure_indexes in self.measure_intervals_analyse_indexes_dictionary.values():
            if len(measure_indexes)>1: # the intervals of this measure is used more than once
                measures=[]
                for measure_index in measure_indexes:
                    if (len(self.measure_analyse_indexes_dictionary[self.measure_analyse_indexes_all[measure_index][0]])==1):
                        measures.append(measure_index)               
                if len(measures)>1:
                    self.measure_intervals_not_full_match_all.append(measures)

    def calculate_repeated_measures_not_in_groups2(self, measures_list, groups_list, output_dictionary):
        for measure_indexes in measures_list:
            if len(measure_indexes)>1: # the measure is used more than once
                measures=[]
                for measure_index in measure_indexes:
                    if not self.in_measure_groups(measure_index, groups_list):
                        measures.append(measure_index)
                
                if len(measures)>1:
                    output_dictionary[measures[0]] = measures[1:]


    def calculate_repeated_measures_not_in_groups(self):
        for measure_indexes in self.measure_analyse_indexes_dictionary.values():
            if len(measure_indexes)>1: # the measure is used more than once
                measures=[]
                for measure_index in measure_indexes:
                    if not self.in_measure_groups(measure_index, self.measure_groups_list):
                        measures.append(measure_index)
                
                if len(measures)>1:
                    self.repeated_measures_not_in_groups_dictionary[measures[0]] = measures[1:]

    def in_measure_groups(self, measure_index, groups_list):
        for mgl in groups_list:
            for mg in mgl:
                if measure_index>=mg[0] and measure_index<=mg[1]:
                    return True
        return False

    #TODO - improve so it the first measure in the group can be used more than once
    def calculate_groups(self, from_list, to_list):
        next_used_at = 1
        group_size = 1
        gap = 1
        skip=0
        print("calcuating measure gruops - not full match")
        for measures in from_list:
            for index, measure in enumerate(measures):
                if (index<len(measures)-1):
                    next_used_at = measures[index+1]
                    gap = next_used_at - measure
                    if gap>1:
                        group_size=1
                        while (self.are_measures_in(from_list, measure + group_size, measure + group_size + gap) and group_size<gap):
                            group_size+=1
                        
                        group_size-=1
                            
                        if (group_size>0):
                            measure_group = [measure, measure + group_size]
                            measure_group_index = self.find_measure_group(measure_group, to_list)
                            if (measure_group_index==-1): #ie need to add 1st and 2nd occurance.  When you come to 2nd and 3rd occurance - the 2nd occurance will already have been added.  Does it this way to avoid not adding the final occurance
                                to_list.append([measure_group])
                                to_list[len(to_list)-1].append([measure + gap, measure + gap + group_size])
                            else:
                                to_list[measure_group_index].append([measure + gap, measure + gap + group_size])
                        
                            skip=group_size #not great as it overlooks possible smaller gruops within large groups eg it will find 1 t 8 being used at 9 to 16 but miss 1 to 4 being used at 17 to 20.


    #TODO - improve so it the first measure in the group can be used more than once
    def calculate_measure_groups(self):
        next_used_at = 1
        group_size = 1
        gap = 1
        skip=0
        print("calculating measure groups")
        for look_at_measure in self.measure_analyse_indexes_all:
            if (skip>0):
                skip-=1
                continue

            next_used_at = self.when_is_measure_next_used(look_at_measure)
            if next_used_at>-1:
                gap = next_used_at - look_at_measure
                if gap>1:
                    group_size=1
                    while (self.is_measure_used_at(look_at_measure + group_size, look_at_measure + group_size + gap) and group_size<gap):
                        group_size+=1
                    
                    group_size-=1
                        
                    if (group_size>0):
                        measure_group = [look_at_measure, look_at_measure + group_size]
                        measure_group_index = self.find_measure_group(measure_group, self.measure_groups_list)
                        if (measure_group_index==-1): #ie need to add 1st and 2nd occurance.  When you come to 2nd and 3rd occurance - the 2nd occurance will already have been added.  Does it this way to avoid not adding the final occurance
                            self.measure_groups_list.append([measure_group])
                            self.measure_groups_list[len(self.measure_groups_list)-1].append([look_at_measure + gap, look_at_measure + gap + group_size])
                        else:
                            self.measure_groups_list[measure_group_index].append([look_at_measure + gap, look_at_measure + gap + group_size])
                    
                        skip=group_size #not great as it overlooks possible smaller gruops within large groups eg it will find 1 t 8 being used at 9 to 16 but miss 1 to 4 being used at 17 to 20.

    def describe_repetition_percentage(self, percent):
        if percent>99:
            return "all"
        elif percent>85:
            return "almost all"
        elif percent>50:
            return "over half"
        else:
            return ""

    #return a list with commas and an in the right place
    #eg [1,4,6] = "1, 4 and 6"
    def comma_and_list(self, l):
        output = ""
        for index, v in enumerate(l):
            if index==len(l)-1 and index>0:
                    output += " and "
            elif index<len(l)-1 and index>0:
                output += ", "  
            output += str(v)
        return output

    def describe_distribution(self, count_in_measures, total):
        distribution = ""

        measure_percents = {}
        for k, c in count_in_measures.items():
            if c>0:
                measure_percents[k] = (c/total)*100        
        sorted_percent = dict(sorted(measure_percents.items(), reverse=True, key=lambda item: item[1]))
        
        ms=[]
        to_pop = [] #can't pop during for loop
        for m,p in sorted_percent.items():
            if p>20:
                ms.append(m)
                to_pop.append(m)
        percent_remaining = 100
        for tp in to_pop:
            percent_remaining -= measure_percents[tp]
            measure_percents.pop(tp)

        if len(ms)>0:
            distribution += " mostly in bar"
            if len(ms)>1:
                distribution += "s"
            distribution += " "
            distribution += self.comma_and_list(ms)
            
        if len(measure_percents)>0:
            if not distribution=="":
                distribution += " and "
            dist = {0:0, 1:0, 2:0, 3:0}
            for index, mp in measure_percents.items():
                if (index>len(count_in_measures)*0.75):
                    dist[3]+=(mp/percent_remaining)*100
                elif (index>len(count_in_measures)*0.5):
                    dist[2]+=(mp/percent_remaining)*100
                elif (index>len(count_in_measures)*0.25):
                    dist[1]+=(mp/percent_remaining)*100
                else:
                    dist[0]+=(mp/percent_remaining)*100
            sorted_dist = sorted(dist.items(), reverse=True, key=lambda item: item[1])
            positions = " "
            if sorted_dist[0][1]>50:
                positions += self._position_map[sorted_dist[0][0]]
            elif sorted_dist[0][1] + sorted_dist[1][1]>70:
                positions += self._position_map[sorted_dist[0][0]] + " and " + self._position_map[sorted_dist[1][0]]
            else:
                positions += str(len(measure_percents)) + " bars throughout"
            
            distribution += positions + "."

        return distribution

    #eg notes or chords as a percentage of events
    def describe_percentage(self, percent):
        if percent>99:
            return "all"
        elif percent>90:
            return "almost all"
        elif percent>75:
            return "mostly"
        elif percent>45:
            return "lots of"
        elif percent>30:
            return "some"
        elif percent>10:
            return "a few"
        elif percent>1:
            return "very few"
        else:
            return ""

    #an event that is uncommon - like accidentals - so the descriptions weighted differently
    def describe_percentage_uncommon(self, percent):
        if percent>5:
            return "many"
        elif percent>2:
            return "a lot of"
        elif percent>1:
            return "quite a few"
        elif percent>0.5:
            return "a few"
        else:
            return "some"

    def describe_count_list(self, count_list, total):
        description = ""
        for index, count_item in enumerate(count_list):
            if count_item[1]/total>0.98:
                description += "all " + str(count_item[0]) + ", "
            elif count_item[1]/total>0.90:
                description += "almost all " + str(count_item[0]) + ", "
            elif count_item[1]/total>0.6:
                description += "mostly " + str(count_item[0]) + ", "
            elif count_item[1]/total>0.3:
                description += "some " + str(count_item[0]) + ", "
        
        description = self.replace_end_with(description, ", ", "")
        
        return description


    def describe_summary(self):
        print("describing summary...")
        summary = ""
        event_count = self.chord_count + self.note_count + self.rest_count
        event_duration = self.chord_duration + self.note_duration + self.rest_duration

        #lower weighting to number of items than to duration - ie 1 bar of semiquavers vs 8 bars of minims!
        percent_dictionary = {}
        percent_dictionary["chords"] =  ((self.chord_count/event_count*50) + (self.chord_duration/event_duration*150)) / 2
        percent_dictionary["individual notes"] =  ((self.note_count/event_count*50) + (self.note_duration/event_duration*150)) / 2
        percent_dictionary["rests"] =  ((self.rest_count/event_count*50) + (self.rest_duration/event_duration*150)) / 2
        
        for k,v in sorted(percent_dictionary.items(), key=lambda item: item[1], reverse=True):
            if v>1:
                summary+=self.describe_percentage(v) + " " + k
                if k=="chords":
                    describe_count = self.describe_count_list(self.count_chord_common_names, self.chord_count)
                    if describe_count!="":
                        describe_count+=", "
                    describe_count += self.describe_count_list(self.count_rhythm_chord, self.chord_count)
                    if describe_count!="":
                        summary+=" (" + describe_count + ")"
                elif k=="individual notes":
                    describe_count = ""
                    temp = self.describe_count_list(self.count_rhythm_note, self.note_count)
                    if temp!="":
                        describe_count += temp + ", "

                    temp = self.describe_count_list(self.count_pitch_names, self.note_count)
                    if temp!="":
                        describe_count += temp + ", "


                    describe_count += self.describe_count_list(self.count_intervals, self.note_count)
                    describe_count = self.replace_end_with(describe_count, ", ", "")
        
                    if describe_count!="":
                        summary+=" (" + describe_count + ")"
                elif k=="rests":
                    describe_count = self.describe_count_list(self.count_rhythm_rest, self.rest_count)
                    if describe_count!="":
                        summary+=" (" + describe_count + ")"
                summary+=", "  
        
        #describe the number of accidentals and where they mostly occur
        if self.accidental_count>1:
            accidental_percent = (self.accidental_count/self.possible_accidental_count)*100
            summary+=self.describe_percentage_uncommon(accidental_percent) + " accidentals."
            summary+=self.describe_distribution(self.count_accidentals_in_measures, self.accidental_count)

        summary = self.replace_end_with(summary, ", ", ".  ")
        return summary

    def replace_end_with(self, original:str, remove:str, add:str):
        to_return = original
        if original.endswith(remove):
            to_return = original[0:original.rfind(remove)]
            to_return += add
        return to_return

    def describe_repetition(self):
        repetition = ""
        if len(self.measure_groups_list)>0:
            for group in self.measure_groups_list:
                group_repetition_percent = ((group[0][1]-group[0][0])*len(group)/len(self.measure_indexes))*100
                if group_repetition_percent>50:
                    if (group[0][1]-group[0][0]==1): # x and y or x to y.
                        repetition+="Bars " + str(group[0][0]) + " and " + str(group[0][1])
                    else:
                        repetition+="Bars " + str(group[0][0]) + " to " + str(group[0][1])
                    repetition += " are used "
                    repetition += self.describe_repetition_percentage(group_repetition_percent)
                    repetition += " of the way through.  "
                else:
                    if (group[0][1]-group[0][0]==1): # x and y or x to y.
                        repetition+="Bars " + str(group[0][0]) + " and " + str(group[0][1])
                    else:
                        repetition+="Bars " + str(group[0][0]) + " to " + str(group[0][1])
                    repetition+= " are used at "
                    for index, ms in enumerate(group[1:]):
                        if index==len(group)-2 and index>0:
                            repetition += " and "
                        elif index<len(group)-1 and index>0:
                            repetition += ", "  
                        repetition+= str(ms[0])
                    repetition += ".  "
            
        for key, ms in self.repeated_measures_not_in_groups_dictionary.items():
            repetition += "Bar " + str(key) + " is used at "
            for index, m in enumerate(ms):
                if index==len(ms)-1 and index>0:
                    repetition += " and "
                elif index<len(ms)-1 and index>0:
                    repetition += ", "
                repetition+=str(m)
            repetition += ".  "

        if repetition == "":
            repetition+="There are no repeated bars...  "

        #rhythm
        rhythm_repetition = ""
        if len(self.measure_rhythm_not_full_match_groups_list)>0:
            for group in self.measure_rhythm_not_full_match_groups_list:
                if (group[0][1]-group[0][0]==1): # x and y or x to y.
                    rhythm_repetition+="The rhythm in bars " + str(group[0][0]) + " and " + str(group[0][1])
                else:
                    rhythm_repetition+="The rhythm in bars " + str(group[0][0]) + " to " + str(group[0][1])
                rhythm_repetition+= " are used at "
                for index, ms in enumerate(group[1:]):
                    if index==len(group)-1 and index>0:
                        rhythm_repetition += " and "
                    elif index<len(group)-1 and index>0:
                        rhythm_repetition += ", "
                    
                    rhythm_repetition += str(ms[0])
                rhythm_repetition += ".  "

        for key, ms in self.repeated_rhythm_measures_not_full_match_not_in_groups_dictionary.items():
            rhythm_repetition += "The rhythm in bar " + str(key) + " is used at "
            for index, m in enumerate(ms):
                if index==len(ms)-1 and index>0:
                    rhythm_repetition += " and "
                elif index<len(ms)-1 and index>0:
                    rhythm_repetition += ", "
                rhythm_repetition+=str(m)
            rhythm_repetition += ".  "
        
        if rhythm_repetition=="":
            rhythm_repetition = "There are no bars with just the same rhythm...  "

        repetition += rhythm_repetition

        #intervals
        interval_repetition = ""
        if len(self.measure_intervals_not_full_match_groups_list)>0:
            for group in self.measure_intervals_not_full_match_groups_list:
                if (group[0][1]-group[0][0]==1): # x and y or x to y.
                    interval_repetition+="The intervals in bars " + str(group[0][0]) + " and " + str(group[0][1])
                else:
                    interval_repetition+="The intervals in bars " + str(group[0][0]) + " to " + str(group[0][1])
                interval_repetition+= " are used at "
                for index, ms in enumerate(group[1:]):
                    if index==len(group)-1 and index>0:
                        interval_repetition += " and "
                    elif index<len(group)-1 and index>0:
                        interval_repetition += ", "
                    
                    interval_repetition += str(ms[0])
                interval_repetition += ".  "

        for key, ms in self.repeated_intervals_measures_not_full_match_not_in_groups_dictionary.items():
            interval_repetition += "The intervals in bar " + str(key) + " are used at "
            for index, m in enumerate(ms):
                if index==len(ms)-1 and index>0:
                    interval_repetition += " and "
                elif index<len(ms)-1 and index>0:
                    interval_repetition += ", "
                interval_repetition+=str(m)
            interval_repetition += ".  "
        
        if interval_repetition=="":
            interval_repetition = "There are no bars with just the same intervals...  "

        repetition += interval_repetition

        return repetition

    def setPart(self, p):
        self.part = p
        print("I'm setting a part...")
        print (p)

        for i in range(128):
            self.pitch_list.append([])

        event_index = 0
        last_note_pitch = -1
        current_measure=-1
        measure_analyse_indexes = AnalyseSection()
        measure_accidentals = 0
        for n in self.part.flat.notesAndRests:
            if (n.measureNumber>current_measure):
                self.measure_indexes[n.measureNumber] = event_index
                current_measure = n.measureNumber
                if (len(measure_analyse_indexes.analyse_indexes)>0): #first time through will be empty
                    self.count_accidentals_in_measures[current_measure-1] = measure_accidentals
                    measure_accidentals = 0

                    index = self.find_section(measure_analyse_indexes, self.measure_analyse_indexes_list, 0)
                    if index == -1:
                        self.measure_analyse_indexes_list.append(measure_analyse_indexes)
                        index = len(self.measure_analyse_indexes_list)-1
                        self.measure_analyse_indexes_dictionary[index] = [current_measure-1]
                        self.measure_analyse_indexes_all[current_measure-1] = [index, 0]
                    else:
                        self.measure_analyse_indexes_dictionary[index].append(current_measure-1)
                        self.measure_analyse_indexes_all[current_measure-1] = [index, len(self.measure_analyse_indexes_dictionary[index])-1]
                    
                    #measures with matching rhythm
                    index = self.find_section(measure_analyse_indexes, self.measure_rhythm_analyse_indexes_list, 1)
                    if index == -1:
                        self.measure_rhythm_analyse_indexes_list.append(measure_analyse_indexes)
                        index = len(self.measure_rhythm_analyse_indexes_list)-1
                        self.measure_rhythm_analyse_indexes_dictionary[index] = [current_measure-1]
                        self.measure_rhythm_analyse_indexes_all[current_measure-1] = [index, 0]
                    else:
                        self.measure_rhythm_analyse_indexes_dictionary[index].append(current_measure-1)
                        self.measure_rhythm_analyse_indexes_all[current_measure-1] = [index, len(self.measure_rhythm_analyse_indexes_dictionary[index])-1]
                    
                    #measures with matching intervals
                    if (self.does_section_contain_intervals(measure_analyse_indexes)):
                        index = self.find_section(measure_analyse_indexes, self.measure_intervals_analyse_indexes_list, 2)
                        if index == -1:
                            self.measure_intervals_analyse_indexes_list.append(measure_analyse_indexes)
                            index = len(self.measure_intervals_analyse_indexes_list)-1
                            self.measure_intervals_analyse_indexes_dictionary[index] = [current_measure-1]
                            self.measure_intervals_analyse_indexes_all[current_measure-1] = [index, 0]
                        else:
                            self.measure_intervals_analyse_indexes_dictionary[index].append(current_measure-1)
                            self.measure_intervals_analyse_indexes_all[current_measure-1] = [index, len(self.measure_intervals_analyse_indexes_dictionary[index])-1]
                        
                    measure_analyse_indexes = AnalyseSection()
                    last_note_pitch=-1 # reset interval comparison for each measure

            ai = AnalyseIndex(event_index)
            if n.isRest:
                ai.event_type = 'r'
                
                d = n.duration.quarterLength
                if self.rhythm_rest_dictionary.get(d) == None:
                    self.rhythm_rest_dictionary[d] = [event_index]
                else:
                    self.rhythm_rest_dictionary[d].append(event_index)
                ai.rhythm_rest_index = [d, len(self.rhythm_rest_dictionary.get(d))-1]
                
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
                ai.rhythm_chord_index = [d, len(self.rhythm_chord_dictionary.get(d))-1]
                
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
                
                #count accidentals in the chord
                for p in n.pitches:
                    if p.accidental is not None and p.accidental.displayStatus == True:
                        measure_accidentals += 1
                        self.accidental_count += 1
                        print("chord accidental displayed")
                self.possible_accidental_count += len(n.pitches)

                self.chord_duration += d
                self.chord_count += 1
            elif n.isChord == False:
                ai.event_type = 'n'
                
                if n.pitch.accidental is not None and n.pitch.accidental.displayStatus == True:
                    measure_accidentals += 1
                    self.accidental_count += 1
                    print("it has an accidental " + str(n.pitch) + " and display = " + str(n.pitch.accidental.displayStatus))
                self.possible_accidental_count += 1
                
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
                
                d = n.duration.quarterLength #numeric value
                if self.rhythm_note_dictionary.get(d) == None:
                    self.rhythm_note_dictionary[d] = [event_index]
                else:
                    self.rhythm_note_dictionary[d].append(event_index)
                ai.rhythm_note_index = [d, len(self.rhythm_note_dictionary.get(d))-1]
                
                last_note_pitch = n.pitch.midi
                self.note_duration += d
                self.note_count += 1
            
            index = self.find_analyse_index(ai)
            if index == -1:
                self.analyse_indexes_list.append(ai)
                index = len(self.analyse_indexes_list)-1
                self.analyse_indexes_dictionary[index] = [event_index]
            else:
                self.analyse_indexes_dictionary[index].append(event_index)
            

            self.analyse_indexes.append(ai)
            measure_analyse_indexes.analyse_indexes.append(ai)
            event_index = event_index + 1 

        #add last measure
        if (len(measure_analyse_indexes.analyse_indexes)>0):
            self.count_accidentals_in_measures[current_measure-1] = measure_accidentals
            
            index = self.find_section(measure_analyse_indexes, self.measure_analyse_indexes_list, 0)
            print ("adding last measure " + str(len(measure_analyse_indexes.analyse_indexes)) + " and index = " + str(index) + " and current measure = " + str(current_measure) )
            if index == -1:
                self.measure_analyse_indexes_list.append(measure_analyse_indexes)
                index = len(self.measure_analyse_indexes_list)-1
                self.measure_analyse_indexes_dictionary[index] = [current_measure]
                self.measure_analyse_indexes_all[current_measure] = [index, 0]
            else:
                self.measure_analyse_indexes_dictionary[index].append(current_measure)
                self.measure_analyse_indexes_all[current_measure] = [index, len(self.measure_analyse_indexes_dictionary[index])-1]
        
            #measures with matching rhythm
            index = self.find_section(measure_analyse_indexes, self.measure_rhythm_analyse_indexes_list, 1)
            if index == -1:
                self.measure_rhythm_analyse_indexes_list.append(measure_analyse_indexes)
                index = len(self.measure_rhythm_analyse_indexes_list)-1
                self.measure_rhythm_analyse_indexes_dictionary[index] = [current_measure]
                self.measure_rhythm_analyse_indexes_all[current_measure] = [index, 0]
            else:
                self.measure_rhythm_analyse_indexes_dictionary[index].append(current_measure)
                self.measure_rhythm_analyse_indexes_all[current_measure] = [index, len(self.measure_rhythm_analyse_indexes_dictionary[index])-1]
            
            #measures with matching intervals
            if (self.does_section_contain_intervals(measure_analyse_indexes)):
                index = self.find_section(measure_analyse_indexes, self.measure_intervals_analyse_indexes_list, 2)
                if index == -1:
                    self.measure_intervals_analyse_indexes_list.append(measure_analyse_indexes)
                    index = len(self.measure_intervals_analyse_indexes_list)-1
                    self.measure_intervals_analyse_indexes_dictionary[index] = [current_measure]
                    self.measure_intervals_analyse_indexes_all[current_measure] = [index, 0]
                else:
                    self.measure_intervals_analyse_indexes_dictionary[index].append(current_measure)
                    self.measure_intervals_analyse_indexes_all[current_measure] = [index, len(self.measure_intervals_analyse_indexes_dictionary[index])-1]
                
        for i in range (19):
            self.analyse_indexes[i].print_info()
            #print(self.compare_indexes(self.analyse_indexes[0], self.analyse_indexes[i]))
            

        print ("rhythm chord dictionary")
        print(self.rhythm_chord_dictionary)
        print ("rhythm note dictionary")
        print(self.rhythm_note_dictionary)
        print ("rhythm rest dictionary")
        print(self.rhythm_rest_dictionary)

        print ("measure_analyse_indexes_dictionary")
        print(self.measure_analyse_indexes_dictionary)

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

        print("\nmeasure analysis diectionary...")
        print (self.measure_analyse_indexes_dictionary)
        print("end of measure analysis...")
        
        print("\nmeasure_analyse_indexes_all...")
        print (self.measure_analyse_indexes_all)
        print("end of measure_analyse_indexes_all...")
        
        self.calculate_measure_groups()
        print("\nmeasure_groups_list...")
        print (self.measure_groups_list)
        print("end of measure_groups_list...")
        
        self.calculate_repeated_measures_not_in_groups()
        print("\nrepeated measures not in groups...")
        print (self.repeated_measures_not_in_groups_dictionary)
        
        print("\nrhythm measures dictionary...")
        print (self.measure_rhythm_analyse_indexes_dictionary)
        
        print("\nintervals measures dictionary...")
        print (self.measure_intervals_analyse_indexes_dictionary)
        
        print("\nmeasure intervals analyse indexes list...")
        print (self.measure_intervals_analyse_indexes_list)
        

        self.calculate_rhythm_measures_not_full_match()
        print("\nrhythm measures not full match...")
        print (self.measure_rhythm_not_full_match_all)

        self.calculate_groups(self.measure_rhythm_not_full_match_all, self.measure_rhythm_not_full_match_groups_list)
        print("\nrhythm groups not full match...")
        print (self.measure_rhythm_not_full_match_groups_list)
        self.calculate_repeated_measures_not_in_groups2(self.measure_rhythm_not_full_match_all, self.measure_rhythm_not_full_match_groups_list, self.repeated_rhythm_measures_not_full_match_not_in_groups_dictionary)
        print(self.repeated_rhythm_measures_not_full_match_not_in_groups_dictionary)

        self.calculate_intervals_measures_not_full_match()
        print("\nintervals measures not full match...")
        print (self.measure_intervals_not_full_match_all)
        self.calculate_repeated_measures_not_in_groups2(self.measure_intervals_not_full_match_all, self.measure_intervals_not_full_match_groups_list, self.repeated_intervals_measures_not_full_match_not_in_groups_dictionary)
        print (self.repeated_intervals_measures_not_full_match_not_in_groups_dictionary)


        self.calculate_groups(self.measure_intervals_not_full_match_all, self.measure_intervals_not_full_match_groups_list)
        print("\nintervals groups not full match...")
        print (self.measure_intervals_not_full_match_groups_list)

        print("\nmeasure rhythm analysis diectionary...")
        print (self.measure_rhythm_analyse_indexes_dictionary)
        
        print("\nmeasure intervals analysis diectionary...")
        print (self.measure_intervals_analyse_indexes_dictionary)
        
        
        print("\nchord common name diectionary...")
        print (self.chord_common_name_dictionary)
 
        #make lists of index and totals then sort by totals for eg most common pitch / rhythm etc
        #lists
        self.count_pitches = self.count_list(self.pitch_list)
        print("\nPitches count...")
        print(self.count_pitches)
        
        print("\nAccidentals in measures count")
        print(self.count_accidentals_in_measures)
        print("Possible accidentals = " + str(self.possible_accidental_count))
        print("accidentals count = " + str(self.accidental_count) + "\n") 

        print(self.count_accidentals_in_measures)
        #dictionaries
        self.count_pitch_names = self.count_dictionary(self.pitch_name_dictionary)
        print (self.count_pitch_names)
        self.count_intervals = self.count_dictionary(self.interval_dictionary)
        self.count_chord_common_names = self.count_dictionary(self.chord_common_name_dictionary)
        
        self.count_rhythm_note = self.count_dictionary(self.rhythm_note_dictionary)
        self.count_rhythm_rest = self.count_dictionary(self.rhythm_rest_dictionary)
        self.count_rhythm_chord = self.count_dictionary(self.rhythm_chord_dictionary)
        print ("\ncount_rhythm_note = ")
        print(self.count_rhythm_note)
        self.rename_count_list_keys(self.count_rhythm_note, self._DURATION_MAP)
        self.rename_count_list_keys(self.count_rhythm_rest, self._DURATION_MAP)
        self.rename_count_list_keys(self.count_rhythm_chord, self._DURATION_MAP)
        print ("\nand now count_rhythm_note = ")
        print(self.count_rhythm_note)
        
        #dictionaries with list indexes as keys
        self.count_chord_pitches = self.count_dictionary(self.chord_pitches_dictionary)
        self.count_chord_intervals = self.count_dictionary(self.chord_intervals_dictionary)
        
        #self.count_pitches = self.count_list(self.pitch_list)

    def rename_count_list_keys(self, count_list, key_names):
        for item in count_list:
            if item[0] in key_names:
                item[0] = key_names.get(item[0])

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



