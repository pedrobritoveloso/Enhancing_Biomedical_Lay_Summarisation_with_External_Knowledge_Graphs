import os
import dgl
import pickle
import sqlite3
import torch

from constants import *
from os.path import join
from metamaplite import MetaMapLite  # Changed to pymetamaplite
from sqlitedict import SqliteDict
from utils import create_dir_if_not_exist

# Main Functions
def umls_search_concepts(sents, prune=False, filtered_types = MM_TYPES):
    create_dir_if_not_exist(CACHE_DIR)
    search_results, cache_used, api_called = [], 0, 0
    sqlitedict = SqliteDict(UMLS_CONCEPTS_SQLITE, autocommit=True)
    
    # Initialize MetaMapLite instead of MetaMap
    METAMAP = MetaMapLite()

    for sent_idx, sent in enumerate(sents):
        # Use MetaMapLite API
        api_called += 1
        
        if not prune:
            # Extract concepts using pymetamaplite's extract_concepts method
            raw_concepts, error = METAMAP.extract_concepts([sent])
        else:
            # For prune=True, specify additional parameters as per pymetamaplite's API
            raw_concepts, error = METAMAP.extract_concepts(
                [sent],
                word_sense_disambiguation=True,  # Enable word sense disambiguation
                filter_by_type=filtered_types,   # Optionally filter concepts by semantic types
                prune_concepts=True,             # If you want to prune based on certain criteria
            )

        # Handle error if extraction fails
        if error is None:
            sqlitedict[sent] = raw_concepts
        else:
            raise Exception(f"Error extracting concepts: {error}")

        # Processing raw concepts
        processed_concepts = []
        for concept in raw_concepts:
            should_skip = False
            # Semantic Types
            semtypes = set(concept['semtypes'])  # Adjust based on pymetamaplite's output
            if len(semtypes.intersection(filtered_types)) == 0:
                continue  # Skip if the concept does not match the filtered types
            semtypes = list(semtypes); semtypes.sort()

            # Offset Locations
            pos_info = concept['pos_info']  # Adjust based on pymetamaplite's output
            pos_info = pos_info.replace(';', ',')
            pos_info = pos_info.replace('[', '')
            pos_info = pos_info.replace(']', '')
            pos_infos = pos_info.split(',')

            for pos_info in pos_infos:
                try:
                    start, length = [int(a) for a in pos_info.split('/')]
                except:
                    print('Skipped', pos_info)
                    start = 0
                    length = 0
                    continue
                
                start_char = start - 1
                end_char = start + length - 1

                # Heuristics Rules
                concept_text = sent[start_char:end_char]
                if concept_text == 'A': continue
                if concept_text == 'to': continue

                # Update processed_concepts
                processed_concepts.append({
                    'cui': concept['cui'], 'semtypes': semtypes,
                    'start_char': start_char, 'end_char': end_char,
                    "score": concept['score'], "preferred_name": concept['preferred_name'],
                    "trigger": concept['trigger']
                })

        search_results.append({
            'sent_idx': sent_idx, 'concepts': processed_concepts
        })
    
    sqlitedict.close()
    return search_results, {'cache_used': cache_used, 'api_called': api_called}
