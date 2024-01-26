# usage python floor_plan_analyser.py plan.txt or python3 floor_plan_analyser.py plan.txt

from dataclasses import dataclass, field
from re import finditer, search
from typing import Dict, List
import sys

# Class to represent a segment of a row in the floor plan
# Manages row number, start column and end start column of segment
@dataclass
class RowPieces():
    r_no : int
    c_start : int
    c_end : int

# Class to represent a space (room) in the floor plan
# Manages space with furniture count, list of rows and flag indicator
@dataclass
class Space():
    name : str = 'default_space'
    furn_count : Dict[str, int] = field(default_factory = dict)
    segments : List[RowPieces] = field(default_factory = list)
    complete : bool = False

# read plan from file
def read_floor_plan(file_path):
    with open(file_path) as f:
        data = f.read()
    return data

# Analyze the floor plan to identify spaces and count furniture
def analyze_floor_plan(data, furn_types):
    workspaces = [] # Temporary list to hold spaces being analyzed
    rooms = [] # List to hold the final spaces (rooms)
    rows = data.split('\n')
    rows.pop(0) # We don't need first row

    for idx, row_data in enumerate(rows):
        # Identify segments in the row from /|+- to next |+-
        found_segments = list(finditer(r'[^/\\|+-]+', row_data))
        row_segments = [RowPieces(idx, segment.start(), segment.end()) for segment in found_segments]
        for space in workspaces:
            for segment in row_segments:
                # Check if the segment overlaps with the last segment in the space
                if max(space.segments[-1].c_start, segment.c_start) < min(space.segments[-1].c_end, segment.c_end):
                    space.segments.append(segment)
                    row_segments.remove(segment)
                    break
            else:
                # Process a completed space
                space_text = ''.join([rows[s.r_no][s.c_start:s.c_end] for s in space.segments])
                room_name_search = search(r'\([\w\s]+\)', space_text)
                if room_name_search:
                    space.name = room_name_search[0][1:-1]
                    space.furn_count = {f: space_text.count(f) for f in furn_types}
                    rooms.append(space)
                space.complete = True
         # Wa take only completed spaces
        workspaces = [space for space in workspaces if not space.complete]
        for segment in row_segments:
            # Create a new space for each unprocessed segment
            new_space = Space()
            new_space.segments.append(segment)
            workspaces.append(new_space)
    return rooms

def print_floor_plan_results(rooms):
    # Calculate total counts of each furniture type
    total_counts = {f: 0 for f in 'WPSC'}
    for room in rooms:
        for f, count in room.furn_count.items():
            total_counts[f] += count

    # Print the total counts in the desired format
    print("total:")
    print(', '.join([f'{k}: {total_counts[k]}' for k in 'WPSC']))

    # Sort rooms alphabetically by name
    sorted_rooms = sorted(rooms, key=lambda x: x.name)

    # Print the furniture counts for each room in the desired format
    for room in sorted_rooms:
        print(f"{room.name}:")
        print(', '.join([f'{k}: {room.furn_count.get(k, 0)}' for k in 'WPSC']))

if __name__ == "__main__":
     # Check for correct command line arguments
    if len(sys.argv) != 2:
        print("Usage: python floor_plan_analyser_v2.py <path_to_floor_plan>")
        sys.exit(1)

    file_path = sys.argv[1]
    data = read_floor_plan(file_path)
    rooms = analyze_floor_plan(data, furn_types='CPSW')
    print_floor_plan_results(rooms)
