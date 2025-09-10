# YTLofi - YouTube Playlist to Lofi Video Generator

A comprehensive toolkit for creating long-form background videos perfect for study, work, or relaxation sessions. Combines YouTube playlist audio with looping animations to generate professional lofi-style content.

## 🎯 Features

- **YouTube Playlist Processing**: Download and stitch audio from entire playlists
- **Animation Looping**: Loop video animations to match audio duration
- **Video Cropping**: Crop videos to remove unwanted edges or watermarks
- **Image-Based Videos**: Create videos from static images with audio
- **Duration Analysis**: Calculate total duration of audio collections
- **Flexible Output**: Multiple format support and quality options

## 📁 Project Structure

```
ytlofi/
├── video_generator.py          # Main video generation script
├── mp3_duration_counter.py     # Audio duration analysis tool
├── create_image_audio_videos.py # Image + audio video creator
└── README.md                   # This file
```

## 🛠️ Dependencies

### Required Software
- **FFmpeg**: Video/audio processing
  - macOS: `brew install ffmpeg`
  - Ubuntu: `sudo apt install ffmpeg`
  - Windows: Download from [ffmpeg.org](https://ffmpeg.org/download.html)

### Python Packages
```bash
pip install yt-dlp mutagen ffmpeg-python
```

## 🚀 Quick Start

### 1. Basic Video Generation
```bash
python video_generator.py animation.mp4 "https://youtube.com/playlist?list=..."
```

### 2. Custom Output and Settings
```bash
python video_generator.py loop.gif "https://youtube.com/playlist?list=..." \
  -o study_video.mp4 \
  --bitrate 256k \
  --time-limit 60
```

### 3. Video Cropping
```bash
python video_generator.py animation.mp4 "https://youtube.com/playlist?list=..." \
  --crop-right 55 \
  --crop-bottom 55
```

## 📖 Detailed Usage

### Video Generator (`video_generator.py`)

The main script that combines YouTube playlist audio with looping animations.

**Workflow:**
1. Downloads playlist audio using yt-dlp
2. Stitches audio tracks into one continuous file
3. Optionally crops animation video
4. Loops animation to match audio duration
5. Combines looped video with audio

**Arguments:**
- `animation`: Path to animation file (MP4 recommended)
- `playlist_url`: YouTube playlist URL
- `-o, --output`: Output filename (default: lofi_video.mp4)
- `--bitrate`: Audio bitrate (default: 192k)
- `--max-retries`: Download retry attempts (default: 3)
- `--crop-right`: Pixels to crop from right edge
- `--crop-bottom`: Pixels to crop from bottom edge
- `--time-limit`: Stop downloading at X minutes (0 = no limit)
- `--keep-temp`: Keep temporary files for debugging

**Examples:**
```bash
# Basic usage
python video_generator.py my_animation.mp4 "https://youtube.com/playlist?list=PLx..."

# High quality with cropping
python video_generator.py bg.mov "https://youtube.com/playlist?list=PLx..." \
  --bitrate 320k \
  --crop-right 100 \
  --crop-bottom 50

# Time-limited download (1 hour of content)
python video_generator.py loop.gif "https://youtube.com/playlist?list=PLx..." \
  --time-limit 60 \
  -o "1hour_study.mp4"
```

### Duration Counter (`mp3_duration_counter.py`)

Analyzes MP3 collections to calculate total listening time.

**Usage:**
```bash
# Analyze current directory
python mp3_duration_counter.py

# Analyze specific folder
python mp3_duration_counter.py /path/to/music/folder
```

**Output:**
- Individual file durations
- Total collection time
- Average track length
- File processing status

### Image Video Creator (`create_image_audio_videos.py`)

Creates multiple videos from image collections paired with unique audio sequences.

**Usage:**
```bash
python create_image_audio_videos.py <image_folder> <mp3_folder> <time_limit_minutes> [output_folder]
```

**Features:**
- Each image gets paired with unique audio sequences
- No song reuse across videos
- Automatic duration matching
- Support for multiple image formats (JPG, PNG, WebP, etc.)
- Support for multiple audio formats (MP3, WAV, FLAC, M4A)

**Example:**
```bash
python create_image_audio_videos.py ./backgrounds ./music 120 ./output
```

## 🎨 Supported Formats

### Video/Animation Input
- MP4 (recommended for best performance)
- MOV, AVI, GIF
- Most FFmpeg-supported formats

### Audio Input
- MP3 (primary)
- WAV, FLAC, M4A

### Image Input
- JPG, JPEG, PNG
- BMP, TIFF, WebP

## ⚙️ Advanced Configuration

### Performance Optimization
- Use MP4 animations for fastest processing (stream copy)
- Higher bitrates (256k-320k) for better audio quality
- Consider video resolution vs. file size tradeoffs

### Quality Settings
```bash
# High quality output
--bitrate 320k

# Balanced quality/size
--bitrate 192k  # default

# Smaller file size
--bitrate 128k
```

### Troubleshooting
- Use `--keep-temp` to debug intermediate files
- Check FFmpeg installation: `ffmpeg -version`
- Verify yt-dlp functionality: `yt-dlp --version`

## 🔧 Technical Details

### Video Processing Pipeline
1. **Audio Download**: yt-dlp extracts audio from YouTube
2. **Audio Stitching**: FFmpeg concatenates tracks
3. **Duration Analysis**: FFprobe measures total length
4. **Video Looping**: FFmpeg loops animation to match audio
5. **Final Merge**: FFmpeg combines video and audio streams

### Optimization Features
- Stream copying for compatible MP4 inputs
- Automatic fallback to re-encoding when needed
- Temporary file management for large operations
- Error handling and retry mechanisms

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test with various input formats
5. Submit a pull request

## 📝 License

This project is open source. Please respect YouTube's terms of service when downloading content.

## 🐛 Known Issues

- Large playlists may take significant time to download
- Some videos may require re-encoding (slower processing)
- Internet connection affects download reliability

## 💡 Tips

- Use shorter animations (10-30 seconds) for better looping
- Test with small playlists first
- Keep animations at reasonable resolutions (1080p max)
- Consider using time limits for very large playlists

---

**Created for educational and personal use. Please respect content creators' rights and YouTube's terms of service.**
