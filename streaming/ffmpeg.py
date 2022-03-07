import cv2
import numpy as np
import subprocess

# TODO: add multiple stream sources
# in_stream = 'rtsp://wowzaec2demo.streamlock.net/vod/mp4:BigBuckBunny_115k.mov'
input_stream = '../resources/raw_videos/360demo.mp4'


def create_stream(in_stream):
    # Read video width, height and framerate using OpenCV (use it if you don't know the size of the video frames).
    cap = cv2.VideoCapture(in_stream)

    framerate = cap.get(30)  # frame rate

    # Get resolution of input video
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # Release VideoCapture - it was used just for getting video resolution
    cap.release()

    command = ['ffmpeg',
               # '-rtsp_flags', 'listen',  # The "listening" feature is not working (probably because the stream is from the web)
               # '-rtsp_transport', 'tcp',  # Force TCP (for testing)
               '-max_delay', '30000000',  # 30 seconds (sometimes needed because the stream is from the web).
               '-i', in_stream,
               '-f', 'image2pipe',
               '-pix_fmt', 'bgr24',
               '-vcodec', 'rawvideo', '-an', '-']

    # Open sub-process that gets in_stream as input and uses stdout as an output PIPE.
    p1 = subprocess.Popen(command, stdout=subprocess.PIPE)
    return p1, width, height


def main():
    p1, width, height = create_stream(input_stream)
    while True:
        # read width*height*3 bytes from stdout (1 frame)
        raw_frame = p1.stdout.read(width * height * 3)

        if len(raw_frame) != (width * height * 3):
            print('Error reading frame!!!')  # Break the loop in case of an error (too few bytes were read).
            break

        # Convert the bytes read into a NumPy array, and reshape it to video frame dimensions
        frame = np.fromstring(raw_frame, np.uint8)
        frame = frame.reshape((height, width, 3))

        # Show video frame
        cv2.imshow('image', frame)
        cv2.waitKey(1)

    # Wait one more second and terminate the sub-process
    try:
        p1.wait(1)
    except sp.TimeoutExpired:
        p1.terminate()

    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
