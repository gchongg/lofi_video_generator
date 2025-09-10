#!/usr/bin/env python3
"""
Automated Video Generator for Lofi Content

Combines an animation loop with audio from YouTube playlists to create
long-form background videos perfect for study/work sessions.

Workflow:
1. Downloads playlist audio using existing playlist_to_mp3.py
2. Stitches audio tracks using existing stitch_mp3.py  
3. Crops animation video if requested (optional)
4. Loops animation video to match audio duration
5. Combines looped video with audio using ffmpeg
"""

import argparse
import subprocess
import sys
import tempfile
from pathlib import Path
import shutil
import json

def run_command(cmd, description=""):
    """Run a command and handle errors gracefully"""
    print(f"🔧 {description}")
    print(f"   Running: {' '.join(str(x) for x in cmd)}")
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"❌ Failed: {description}")
        print(f"   Error: {result.stderr}")
        return False
    
    if result.stdout.strip():
        print(f"   Output: {result.stdout.strip()}")
    
    return True

def download_playlist_audio(playlist_url, temp_dir, max_retries=3, time_limit_minutes=0):
    """Download playlist audio using playlist_to_mp3.py"""
    script_path = Path(__file__).parent / "playlist_to_mp3.py"
    audio_dir = temp_dir / "audio"
    
    cmd = [
        sys.executable, str(script_path),
        playlist_url,
        "-o", str(audio_dir),
        "--max-retries", str(max_retries)
    ]
    
    # Add time limit if specified
    if time_limit_minutes > 0:
        cmd.extend(["--time-limit", str(time_limit_minutes)])
    
    success = run_command(cmd, "Downloading playlist audio")
    
    if success:
        # Find the playlist directory (should be the only subdirectory in audio_dir)
        playlist_dirs = [d for d in audio_dir.iterdir() if d.is_dir()]
        if playlist_dirs:
            return playlist_dirs[0]  # Return path to playlist folder
    
    return None

def stitch_audio(audio_folder, output_audio_path, bitrate="192k"):
    """Stitch MP3 files using stitch_mp3.py"""
    script_path = Path(__file__).parent / "stitch_mp3.py"
    
    cmd = [
        sys.executable, str(script_path),
        str(audio_folder),
        "-o", str(output_audio_path),
        "--bitrate", bitrate
    ]
    
    return run_command(cmd, "Stitching audio files")

def get_audio_duration(audio_path):
    """Get duration of audio file in seconds using ffprobe"""
    cmd = [
        "ffprobe", "-v", "quiet", "-show_entries", 
        "format=duration", "-of", "default=noprint_wrappers=1:nokey=1",
        str(audio_path)
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        try:
            return float(result.stdout.strip())
        except ValueError:
            pass
    
    return None

def get_video_dimensions(infile):
    """Get width and height of the input video using ffprobe."""
    cmd = [
        "ffprobe", "-v", "error",
        "-select_streams", "v:0",
        "-show_entries", "stream=width,height",
        "-of", "json", str(infile)
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    info = json.loads(result.stdout)
    width = info["streams"][0]["width"]
    height = info["streams"][0]["height"]
    return width, height

def crop_video(infile, outfile, crop_right=55, crop_bottom=55):
    """Crop crop_right and crop_bottom pixels from the video."""
    width, height = get_video_dimensions(infile)
    new_width = width - crop_right
    new_height = height - crop_bottom

    cmd = [
        "ffmpeg", "-y",
        "-i", str(infile),
        "-vf", f"crop={new_width}:{new_height}:0:0",
        "-c:v", "libx264",
        "-crf", "18",
        "-preset", "veryfast",
        "-c:a", "copy",
        str(outfile)
    ]
    return run_command(cmd, f"Cropping video ({crop_right}px right, {crop_bottom}px bottom)")

def loop_animation(animation_path, duration_seconds, output_path):
    """Loop animation video to match audio duration"""
    # Check if input is already MP4 with compatible codec
    input_ext = Path(animation_path).suffix.lower()
    
    if input_ext == '.mp4':
        # For MP4 inputs, try stream copy first for faster processing
        cmd = [
            "ffmpeg", "-y",  # overwrite output
            "-stream_loop", "-1",          # infinite loop
            "-i", str(animation_path),     # input animation
            "-t", str(int(duration_seconds)), # duration in seconds
            "-c:v", "copy",                # copy video stream (fast)
            "-an",                         # no audio
            str(output_path)
        ]
        
        # Try stream copy first
        if run_command(cmd, f"Looping MP4 animation for {int(duration_seconds)} seconds (fast mode)"):
            return True
        
        print("   Stream copy failed, falling back to re-encoding...")
    
    # Fallback or non-MP4 input: re-encode with optimization
    cmd = [
        "ffmpeg", "-y",  # overwrite output
        "-stream_loop", "-1",          # infinite loop
        "-i", str(animation_path),     # input animation
        "-t", str(int(duration_seconds)), # duration in seconds
        "-c:v", "libx264",             # video codec
        "-preset", "fast",             # faster encoding for loops
        "-crf", "20",                  # slightly better quality for MP4
        "-pix_fmt", "yuv420p",         # compatibility
        "-movflags", "+faststart",     # optimize for streaming
        "-an",                         # no audio
        str(output_path)
    ]
    
    return run_command(cmd, f"Looping animation for {int(duration_seconds)} seconds")

def combine_video_audio(video_path, audio_path, output_path):
    """Combine video and audio using ffmpeg"""
    cmd = [
        "ffmpeg", "-y",  # overwrite output
        "-i", str(video_path),         # input video
        "-i", str(audio_path),         # input audio
        "-c:v", "copy",                # copy video stream (no re-encode)
        "-c:a", "aac",                 # encode audio to AAC
        "-b:a", "192k",                # audio bitrate
        "-shortest",                   # match shortest stream duration
        str(output_path)
    ]
    
    return run_command(cmd, "Combining video and audio")

def check_dependencies():
    """Check if required tools are available"""
    tools = ["ffmpeg", "ffprobe"]
    missing = []
    
    for tool in tools:
        if not shutil.which(tool):
            missing.append(tool)
    
    if missing:
        print(f"❌ Missing required tools: {', '.join(missing)}")
        print("   Please install ffmpeg: https://ffmpeg.org/download.html")
        return False
    
    # Check if yt-dlp is available
    try:
        import yt_dlp
    except ImportError:
        print("❌ Missing yt-dlp. Install with: pip install yt-dlp")
        return False
    
    return True

def main():
    parser = argparse.ArgumentParser(
        description="Generate lofi videos by combining animation with YouTube playlist audio",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python video_generator.py my_animation.mp4 "https://youtube.com/playlist?list=..." 
  python video_generator.py loop.gif "https://youtube.com/playlist?list=..." -o study_video.mp4
  python video_generator.py bg.mov "https://youtube.com/playlist?list=..." --bitrate 256k
  python video_generator.py animation.mp4 "https://youtube.com/playlist?list=..." --crop-right 55 --crop-bottom 55
  python video_generator.py animation.mp4 "https://youtube.com/playlist?list=..." --time-limit 60
        """
    )
    
    parser.add_argument("animation", 
                       help="Path to your animation file (MP4 recommended for best performance)")
    parser.add_argument("playlist_url", 
                       help="YouTube playlist URL")
    parser.add_argument("-o", "--output", default="lofi_video.mp4",
                       help="Output video filename (default: lofi_video.mp4)")
    parser.add_argument("--bitrate", default="192k",
                       help="Audio bitrate (default: 192k)")
    parser.add_argument("--max-retries", type=int, default=3,
                       help="Max download retries (default: 3)")
    parser.add_argument("--keep-temp", action="store_true",
                       help="Keep temporary files for debugging")
    parser.add_argument("--crop-right", type=int, default=0,
                       help="Pixels to crop from right edge (default: 0)")
    parser.add_argument("--crop-bottom", type=int, default=0,
                       help="Pixels to crop from bottom edge (default: 0)")
    parser.add_argument("--time-limit", type=int, default=0,
                       help="Stop downloading when total duration reaches this many minutes (default: 0 = no limit)")
    
    args = parser.parse_args()
    
    # Validate inputs
    animation_path = Path(args.animation).resolve()
    if not animation_path.exists():
        print(f"❌ Animation file not found: {animation_path}")
        sys.exit(1)
    
    output_path = Path(args.output).resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    print(f"🎬 Starting video generation...")
    print(f"   Animation: {animation_path.name}")
    print(f"   Playlist: {args.playlist_url}")
    print(f"   Output: {output_path}")
    if args.time_limit > 0:
        print(f"   Time limit: {args.time_limit} minutes")
    
    # Use temporary directory for intermediate files
    with tempfile.TemporaryDirectory() as temp_dir_str:
        temp_dir = Path(temp_dir_str)
        
        # Step 1: Download playlist audio
        print("\n📥 Step 1: Downloading playlist audio...")
        playlist_folder = download_playlist_audio(
            args.playlist_url, temp_dir, args.max_retries, args.time_limit
        )
        
        if not playlist_folder:
            print("❌ Failed to download playlist audio")
            sys.exit(1)
        
        # Step 2: Stitch audio files
        print("\n🔗 Step 2: Stitching audio files...")
        stitched_audio = temp_dir / "stitched_audio.mp3"
        
        if not stitch_audio(playlist_folder, stitched_audio, args.bitrate):
            print("❌ Failed to stitch audio files")
            sys.exit(1)
        
        # Step 3: Get audio duration
        print("\n⏱️  Step 3: Analyzing audio duration...")
        audio_duration = get_audio_duration(stitched_audio)
        
        if not audio_duration:
            print("❌ Failed to get audio duration")
            sys.exit(1)
        
        print(f"   Audio duration: {audio_duration:.1f} seconds ({audio_duration/60:.1f} minutes)")
        
        # Step 4: Crop animation if requested
        print("\n✂️  Step 4: Cropping animation...")
        if args.crop_right > 0 or args.crop_bottom > 0:
            cropped_video = temp_dir / "cropped_animation.mp4"
            
            if not crop_video(animation_path, cropped_video, args.crop_right, args.crop_bottom):
                print("❌ Failed to crop animation")
                sys.exit(1)
            
            animation_to_loop = cropped_video
        else:
            print("   Skipping cropping (no crop values specified)")
            animation_to_loop = animation_path
        
        # Step 5: Loop animation to match audio duration
        print("\n🔄 Step 5: Looping animation...")
        looped_video = temp_dir / "looped_animation.mp4"
        
        if not loop_animation(animation_to_loop, audio_duration, looped_video):
            print("❌ Failed to loop animation")
            sys.exit(1)
        
        # Step 6: Combine video and audio
        print("\n🎵 Step 6: Combining video and audio...")
        
        if not combine_video_audio(looped_video, stitched_audio, output_path):
            print("❌ Failed to combine video and audio")
            sys.exit(1)
        
        # Keep temp files if requested
        if args.keep_temp:
            debug_dir = output_path.parent / f"{output_path.stem}_temp"
            shutil.copytree(temp_dir, debug_dir)
            print(f"🔍 Temporary files saved to: {debug_dir}")
    
    print(f"\n✅ Video generation complete!")
    print(f"   Output: {output_path}")
    print(f"   Duration: {audio_duration/60:.1f} minutes")
    
    # Show file size
    size_mb = output_path.stat().st_size / (1024 * 1024)
    print(f"   File size: {size_mb:.1f} MB")

if __name__ == "__main__":
    main()