#!/usr/bin/env python3
"""
MP3 Duration Counter Script
Calculates the total length of all MP3 files in a specified folder.
"""

import os
import sys
import glob
from mutagen.mp3 import MP3
from mutagen.id3 import ID3NoHeaderError

def get_mp3_duration(file_path):
    """Get duration of a single MP3 file in seconds."""
    try:
        audio = MP3(file_path)
        return audio.info.length
    except (ID3NoHeaderError, Exception) as e:
        print(f"Error reading {file_path}: {e}")
        return 0

def format_duration(seconds):
    """Convert seconds to hours:minutes:seconds format."""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    
    if hours > 0:
        return f"{hours}:{minutes:02d}:{secs:02d}"
    else:
        return f"{minutes}:{secs:02d}"

def count_mp3_durations(folder_path="."):
    """Count total duration of all MP3 files in the specified folder."""
    # Get all MP3 files in the folder
    mp3_pattern = os.path.join(folder_path, "*.mp3")
    mp3_files = glob.glob(mp3_pattern)
    
    if not mp3_files:
        print(f"No MP3 files found in {folder_path}")
        return
    
    total_duration = 0
    file_count = 0
    
    print(f"Found {len(mp3_files)} MP3 files in {folder_path}")
    print("Analyzing files...")
    print("-" * 50)
    
    for file_path in sorted(mp3_files):
        filename = os.path.basename(file_path)
        duration = get_mp3_duration(file_path)
        
        if duration > 0:
            total_duration += duration
            file_count += 1
            print(f"{filename:<50} {format_duration(duration)}")
        else:
            print(f"{filename:<50} ERROR")
    
    print("-" * 50)
    print(f"Successfully processed: {file_count} files")
    print(f"Total duration: {format_duration(total_duration)}")
    print(f"Average duration: {format_duration(total_duration / file_count if file_count > 0 else 0)}")

def main():
    """Main function to handle command line arguments."""
    folder_path = "."
    
    if len(sys.argv) > 1:
        folder_path = sys.argv[1]
    
    if not os.path.exists(folder_path):
        print(f"Error: Folder '{folder_path}' does not exist.")
        sys.exit(1)
    
    if not os.path.isdir(folder_path):
        print(f"Error: '{folder_path}' is not a directory.")
        sys.exit(1)
    
    print(f"MP3 Duration Counter")
    print(f"Analyzing folder: {os.path.abspath(folder_path)}")
    print("=" * 60)
    
    count_mp3_durations(folder_path)

if __name__ == "__main__":
    main()