#!/usr/bin/env python3
"""
Image-Audio Video Generator

Creates videos by combining images with stitched MP3 audio tracks.
Each image gets paired with a unique sequence of MP3 files up to the specified time limit.

Usage:
    python create_image_audio_videos.py <image_folder> <mp3_folder> <time_limit_minutes> [output_folder]

Example:
    python create_image_audio_videos.py ./images ./music 120 ./output
"""

import os
import sys
import random
import argparse
import tempfile
from pathlib import Path
try:
    import ffmpeg
except ImportError:
    print("Error: ffmpeg-python library not found.")
    print("Please install it with: pip install ffmpeg-python")
    sys.exit(1)


def get_supported_files(folder, extensions):
    """Get all supported files from a folder."""
    folder = Path(folder)
    if not folder.exists():
        raise ValueError(f"Folder does not exist: {folder}")
    
    files = []
    for ext in extensions:
        files.extend(folder.glob(f"*.{ext}"))
        files.extend(folder.glob(f"*.{ext.upper()}"))
    
    return sorted(files)


def get_audio_duration(audio_file):
    """Get audio duration using ffmpeg-python."""
    try:
        probe = ffmpeg.probe(str(audio_file))
        duration = float(probe['format']['duration'])
        return duration
    except Exception as e:
        print(f"Warning: Could not get duration for {audio_file}: {e}")
        return 0


def create_audio_sequence(available_files, target_duration_seconds, used_songs, temp_dir):
    """Create an audio sequence using only unused songs and return temp file path."""
    # Filter out already used songs
    unused_files = [f for f in available_files if str(f) not in used_songs]
    
    if not unused_files:
        print("Warning: No unused songs available for this video.")
        return None
    
    audio_segments = []
    current_duration = 0
    files_for_this_video = unused_files.copy()
    songs_used_in_this_video = set()
    
    while current_duration < target_duration_seconds and files_for_this_video:
        # Randomly select an MP3 file
        mp3_file = random.choice(files_for_this_video)
        
        try:
            audio_duration = get_audio_duration(mp3_file)
            if audio_duration <= 0:
                files_for_this_video.remove(mp3_file)
                continue
            
            # If adding this clip would exceed target, truncate it
            if current_duration + audio_duration > target_duration_seconds:
                remaining_time = target_duration_seconds - current_duration
                audio_segments.append({
                    'file': str(mp3_file),
                    'start': 0,
                    'duration': remaining_time
                })
                current_duration = target_duration_seconds
                # Mark this song as used
                songs_used_in_this_video.add(str(mp3_file))
                break
            else:
                audio_segments.append({
                    'file': str(mp3_file),
                    'start': 0,
                    'duration': audio_duration
                })
                current_duration += audio_duration
                # Mark this song as used
                songs_used_in_this_video.add(str(mp3_file))
                # Remove the file from available files for this sequence
                files_for_this_video.remove(mp3_file)
                
        except Exception as e:
            print(f"Warning: Could not process {mp3_file}: {e}")
            if mp3_file in files_for_this_video:
                files_for_this_video.remove(mp3_file)
            continue
    
    # Add all songs used in this video to the global used songs set
    used_songs.update(songs_used_in_this_video)
    
    if not audio_segments:
        return None
    
    # Create concatenated audio file using ffmpeg-python
    output_audio = temp_dir / f"audio_sequence_{random.randint(1000, 9999)}.mp3"
    
    try:
        if len(audio_segments) == 1:
            # Single file, just copy with potential trimming
            segment = audio_segments[0]
            stream = ffmpeg.input(segment['file'])
            if segment['duration'] < get_audio_duration(segment['file']):
                stream = stream.filter('atrim', start=segment['start'], duration=segment['duration'])
            stream = ffmpeg.output(stream, str(output_audio), acodec='copy')
            ffmpeg.run(stream, overwrite_output=True, quiet=True)
        else:
            # Multiple files, need to concatenate
            inputs = []
            for i, segment in enumerate(audio_segments):
                stream = ffmpeg.input(segment['file'])
                # Trim if needed
                if segment['duration'] < get_audio_duration(segment['file']):
                    stream = stream.filter('atrim', start=segment['start'], duration=segment['duration'])
                inputs.append(stream)
            
            # Concatenate all inputs
            joined = ffmpeg.concat(*inputs, v=0, a=1)
            output = ffmpeg.output(joined, str(output_audio), acodec='mp3')
            ffmpeg.run(output, overwrite_output=True, quiet=True)
        
        return str(output_audio)
    except Exception as e:
        print(f"Error creating audio sequence: {e}")
        return None


def create_video(image_path, audio_file, output_path, target_duration_seconds):
    """Create a video with image and audio using ffmpeg-python."""
    try:
        # Create video input (looped image)
        video_input = ffmpeg.input(str(image_path), loop=1, framerate=1)
        
        if audio_file:
            # Create audio input
            audio_input = ffmpeg.input(audio_file)
            
            # Combine video and audio
            output = ffmpeg.output(
                video_input, audio_input,
                str(output_path),
                vcodec='libx264',
                acodec='aac',
                pix_fmt='yuv420p',
                shortest=None  # Stop when shortest input ends
            )
        else:
            # Create video with just image (no audio)
            output = ffmpeg.output(
                video_input,
                str(output_path),
                vcodec='libx264',
                pix_fmt='yuv420p',
                t=target_duration_seconds
            )
        
        ffmpeg.run(output, overwrite_output=True, quiet=True)
        return True
        
    except Exception as e:
        print(f"Error creating video for {image_path}: {e}")
        return False


def check_ffmpeg():
    """Check if ffmpeg is available (ffmpeg-python will handle this)."""
    try:
        # Test if we can run a simple ffmpeg command
        test_stream = ffmpeg.input('pipe:', f='lavfi', t=0.1)
        test_output = ffmpeg.output(test_stream, 'pipe:', f='null')
        ffmpeg.run(test_output, pipe_stdout=True, pipe_stderr=True, quiet=True)
        return True
    except Exception:
        print("Error: ffmpeg is required but not found or not working.")
        print("Please install ffmpeg: https://ffmpeg.org/download.html")
        return False


def main():
    parser = argparse.ArgumentParser(description='Create videos from images and MP3 files')
    parser.add_argument('image_folder', help='Folder containing image files')
    parser.add_argument('mp3_folder', help='Folder containing MP3 files')
    parser.add_argument('time_limit', type=int, help='Time limit in minutes')
    parser.add_argument('output_folder', nargs='?', default='./output', 
                       help='Output folder (default: ./output)')
    
    args = parser.parse_args()
    
    # Check if ffmpeg is available
    # if not check_ffmpeg():
    #     return 1
    
    # Validate inputs
    image_folder = Path(args.image_folder)
    mp3_folder = Path(args.mp3_folder)
    output_folder = Path(args.output_folder)
    time_limit_seconds = args.time_limit * 60
    
    if not image_folder.exists():
        print(f"Error: Image folder does not exist: {image_folder}")
        return 1
        
    if not mp3_folder.exists():
        print(f"Error: MP3 folder does not exist: {mp3_folder}")
        return 1
    
    # Create output folder if it doesn't exist
    output_folder.mkdir(parents=True, exist_ok=True)
    
    # Get image and MP3 files
    try:
        image_extensions = ['jpg', 'jpeg', 'png', 'bmp', 'tiff', 'webp']
        mp3_extensions = ['mp3', 'wav', 'flac', 'm4a']
        
        image_files = get_supported_files(image_folder, image_extensions)
        mp3_files = get_supported_files(mp3_folder, mp3_extensions)
        
        if not image_files:
            print(f"Error: No supported image files found in {image_folder}")
            return 1
            
        if not mp3_files:
            print(f"Error: No supported audio files found in {mp3_folder}")
            return 1
            
        print(f"Found {len(image_files)} images and {len(mp3_files)} audio files")
        print(f"Creating videos with {args.time_limit} minutes duration each")
        
    except Exception as e:
        print(f"Error scanning folders: {e}")
        return 1
    
    # Track individual songs used to ensure no song is used twice
    used_songs = set()
    
    # Calculate if we have enough songs for all videos
    total_songs_needed = 0
    for image_path in image_files:
        # Estimate songs needed per video (rough calculation)
        # Assuming average song length of 3-4 minutes
        estimated_songs_per_video = max(1, time_limit_seconds // 180)  # 3 minutes average
        total_songs_needed += estimated_songs_per_video
    
    if total_songs_needed > len(mp3_files):
        print(f"Warning: May not have enough unique songs for all videos.")
        print(f"Estimated songs needed: {total_songs_needed}, Available: {len(mp3_files)}")
        print(f"Some videos may have shorter durations or reuse songs.")
    
    # Create temporary directory for intermediate files
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Process each image
        successful = 0
        for i, image_path in enumerate(image_files, 1):
            print(f"\nProcessing image {i}/{len(image_files)}: {image_path.name}")
            
            # Create audio sequence using only unused songs
            audio_file = create_audio_sequence(mp3_files, time_limit_seconds, used_songs, temp_path)
            
            if not audio_file:
                print(f"Warning: Could not create audio sequence for {image_path.name}")
                continue
            
            # Create output filename
            output_filename = f"{image_path.stem}_video.mp4"
            output_path = output_folder / output_filename
            
            # Create video
            print(f"Creating video: {output_filename}")
            if create_video(image_path, audio_file, output_path, time_limit_seconds):
                successful += 1
                print(f"✅ Successfully created: {output_path}")
            else:
                print(f"❌ Failed to create video for: {image_path.name}")
    
        print(f"\n🎬 Process complete! Successfully created {successful}/{len(image_files)} videos")
        print(f"📁 Output folder: {output_folder.absolute()}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())