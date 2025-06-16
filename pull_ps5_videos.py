from ppadb.client import Client as AdbClient
import os
import sys

# Common possible PS5 app download locations
PS5_PATHS = [
    "/sdcard/Movies/PS App/",
    "/sdcard/Android/data/com.scee.psxandroid/",
    "/sdcard/Android/data/com.playstation.mobilemessenger/",
    "/sdcard/PSApp/",
    "/sdcard/Download/PSApp/",
    "/sdcard/Movies/PSApp/",
    "/sdcard/Movies/",
    "/sdcard/Download/"
]

VIDEO_EXTENSIONS = [".mp4", ".mov", ".mkv", ".avi"]

def get_adb_device():
    client = AdbClient(host="127.0.0.1", port=5037)
    devices = client.devices()
    if not devices:
        print("No ADB devices found.")
        sys.exit(1)
    return devices[0]

def adb_shell_ls(device, path):
    try:
        output = device.shell(f"ls -1 '{path}'")
        print(f"DEBUG: ls output for {path}:\n{output}")
        lines = output.strip().split("\n")
        return [line for line in lines if not line.startswith('ls:') and line.strip() != '']
    except Exception as e:
        print(f"DEBUG: Exception for {path}: {e}")
        return []

def find_ps5_video_dir(device):
    for base in PS5_PATHS:
        files = adb_shell_ls(device, base)
        if files:
            for f in files:
                if any(f.lower().endswith(ext) for ext in VIDEO_EXTENSIONS):
                    return base
    return None

def list_videos(device, path):
    files = adb_shell_ls(device, path)
    return [f for f in files if any(f.lower().endswith(ext) for ext in VIDEO_EXTENSIONS)]

def pull_video(device, remote_path, local_dir):
    os.makedirs(local_dir, exist_ok=True)
    local_path = os.path.join(local_dir, os.path.basename(remote_path))
    device.pull(remote_path, local_path)
    return True, local_path

def main():
    device = get_adb_device()
    print("Searching for PS5 app video downloads on your phone...")
    video_dir = find_ps5_video_dir(device)
    if not video_dir:
        print("Could not find PS5 app video downloads directory.")
        sys.exit(1)
    print(f"Found possible video directory: {video_dir}")
    videos = list_videos(device, video_dir)
    if not videos:
        print("No video files found in the directory.")
        sys.exit(1)
    print("Videos found:")
    for idx, vid in enumerate(videos):
        print(f"{idx+1}: {vid}")
    choice = input(f"Enter the number of the video to pull (1-{len(videos)}): ")
    try:
        idx = int(choice) - 1
        if idx < 0 or idx >= len(videos):
            raise ValueError
    except ValueError:
        print("Invalid selection.")
        sys.exit(1)
    remote_path = os.path.join(video_dir, videos[idx])
    local_dir = os.path.join(os.getcwd(), "ps5_videos")
    print(f"Pulling {videos[idx]} to {local_dir} ...")
    success, local_path = pull_video(device, remote_path, local_dir)
    if success:
        print(f"Video pulled successfully: {local_path}")
    else:
        print("Failed to pull video.")

if __name__ == "__main__":
    main()
