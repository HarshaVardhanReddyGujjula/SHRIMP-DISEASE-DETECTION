import sys


try:
    import cv2
except ImportError:
    cv2 = None

try:
    import numpy as np
except ImportError:
    np = None


if cv2 is None or np is None:
    missing = []
    if cv2 is None:
        missing.append("opencv-python")
    if np is None:
        missing.append("numpy")

    print("ERROR: Missing required packages:", ", ".join(missing))
    print("Run: pip install opencv-python numpy")
    sys.exit(1)



def analyze_frame(frame):
    """
    Detect white spots in center region (ROI)
    """

    h, w, _ = frame.shape

    
    y1, y2 = h // 4, 3 * h // 4
    x1, x2 = w // 4, 3 * w // 4
    roi = frame[y1:y2, x1:x2]

    
    hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)

    
    lower_white = np.array([0, 0, 180], dtype=np.uint8)
    upper_white = np.array([180, 60, 255], dtype=np.uint8)

   
    mask = cv2.inRange(hsv, lower_white, upper_white)

    
    white_ratio = np.count_nonzero(mask) / mask.size

    
    threshold = 0.15
    diseased = white_ratio > threshold

    return diseased, white_ratio, (x1, y1, x2, y2), mask



def main():

    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("ERROR: Could not open camera. Trying another index...")
        cap = cv2.VideoCapture(1)

    if not cap.isOpened():
        print("ERROR: Failed to open any camera.")
        return

    print("SUCCESS: Camera opened. Press 'q' to quit.")

    while True:
        ret, frame = cap.read()

        if not ret:
            print("ERROR: Failed to grab frame.")
            break

        
        diseased, white_ratio, (x1, y1, x2, y2), mask = analyze_frame(frame)

        
        cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)

        
        if diseased:
            status_text = "POSSIBLY DISEASED"
            color = (0, 0, 255)
        else:
            status_text = "LIKELY HEALTHY"
            color = (0, 255, 0)

        
        cv2.putText(frame,
                    f"Status: {status_text}",
                    (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    color,
                    2,
                    cv2.LINE_AA)

        
        cv2.putText(frame,
                    f"White ratio: {white_ratio * 100:.1f}%",
                    (10, 60),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (255, 255, 255),
                    2,
                    cv2.LINE_AA)

        
        cv2.imshow("Shrimp Detection", frame)
        cv2.imshow("White Mask (Debug)", mask)

        # Exit on 'q'
        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            break

    
    cap.release()
    cv2.destroyAllWindows()



if __name__ == "__main__":
    main()q