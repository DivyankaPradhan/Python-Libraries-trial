import cv2
import mediapipe as mp
import math
import time

cap = cv2.VideoCapture(0)

mpHands = mp.solutions.hands
hands = mpHands.Hands(
    max_num_hands=1,
    min_detection_confidence=0.75,
    min_tracking_confidence=0.75
)

draw = mp.solutions.drawing_utils

canvas = None

prev_x = None
prev_y = None
drawing = False

brush_color = (0,255,0)
brush_size = 6

colors = {
    "red":(0,0,255),
    "green":(0,255,0),
    "blue":(255,0,0),
    "yellow":(0,255,255),
    "white":(255,255,255),
    "black":(0,0,0)
}

buttons = [
    ("red",(10,10,60,60)),
    ("green",(80,10,130,60)),
    ("blue",(150,10,200,60)),
    ("yellow",(220,10,270,60)),
    ("eraser",(290,10,360,60)),
    ("clear",(380,10,460,60))
]

prev_time = time.time()

while True:

    success, frame = cap.read()

    if not success:
        break

    frame = cv2.flip(frame,1)

    if canvas is None:
        canvas = frame.copy()
        canvas[:] = 0

    rgb = cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)

    result = hands.process(rgb)

    h,w,_ = frame.shape

    current = time.time()
    fps = 1/(current-prev_time)
    prev_time = current
    if result.multi_hand_landmarks:

        hand = result.multi_hand_landmarks[0]

        draw.draw_landmarks(
            frame,
            hand,
            mpHands.HAND_CONNECTIONS
        )

        lm = hand.landmark

        index = lm[8]
        thumb = lm[4]
        middle = lm[12]

        ix = int(index.x * w)
        iy = int(index.y * h)

        tx = int(thumb.x * w)
        ty = int(thumb.y * h)

        mx = int(middle.x * w)
        my = int(middle.y * h)

        cv2.circle(frame,(ix,iy),8,(0,0,255),-1)
        cv2.circle(frame,(tx,ty),8,(255,0,0),-1)

        pinch_distance = math.hypot(ix-tx, iy-ty)

        if pinch_distance < 35:
            drawing = True
        else:
            drawing = False

        if drawing:

            if prev_x is None:
                prev_x = ix
                prev_y = iy

            smooth_x = int(prev_x * 0.7 + ix * 0.3)
            smooth_y = int(prev_y * 0.7 + iy * 0.3)

            cv2.line(
                canvas,
                (prev_x, prev_y),
                (smooth_x, smooth_y),
                brush_color,
                brush_size
            )

            prev_x = smooth_x
            prev_y = smooth_y

        else:

            prev_x = None
            prev_y = None
        for name, box in buttons:

            x1, y1, x2, y2 = box

            if name == "eraser":
                cv2.rectangle(frame, (x1, y1), (x2, y2), (200, 200, 200), -1)
                cv2.putText(frame, "ERASE", (x1+3, y1+32),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,0), 2)

            elif name == "clear":
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0,0,255), -1)
                cv2.putText(frame, "CLEAR", (x1+2, y1+32),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 2)

            else:
                cv2.rectangle(frame, (x1, y1), (x2, y2), colors[name], -1)

            if x1 < ix < x2 and y1 < iy < y2:

                if pinch_distance < 35:

                    if name == "eraser":
                        brush_color = colors["black"]

                    elif name == "clear":
                        canvas[:] = 0

                    else:
                        brush_color = colors[name]

                    time.sleep(0.2)

        frame = cv2.add(frame, canvas)

        cv2.putText(
            frame,
            f"FPS : {int(fps)}",
            (10, h-20),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255,255,255),
            2
        )

        cv2.putText(
            frame,
            "Pinch = Draw",
            (w-180, h-20),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255,255,255),
            2
        )
    if result.multi_hand_landmarks:

        fingers = []

        finger_tips = [4, 8, 12, 16, 20]

        fingers.append(1 if lm[4].x < lm[3].x else 0)

        for tip in finger_tips[1:]:
            if lm[tip].y < lm[tip-2].y:
                fingers.append(1)
            else:
                fingers.append(0)

        if fingers == [1,1,1,1,1]:

            cv2.putText(
                frame,
                "CLEARING...",
                (180, h//2),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0,0,255),
                3
            )

            canvas[:] = 0

            prev_x = None
            prev_y = None

            time.sleep(0.4)

    key = cv2.waitKey(1) & 0xFF

    if key == ord("s"):

        filename = f"drawing_{int(time.time())}.png"

        cv2.imwrite(filename, canvas)

        print("Saved:", filename)

    elif key == ord("+") or key == ord("="):

        brush_size = min(40, brush_size + 1)

    elif key == ord("-"):

        brush_size = max(1, brush_size - 1)

    elif key == ord("r"):

        brush_color = colors["red"]

    elif key == ord("g"):

        brush_color = colors["green"]

    elif key == ord("b"):

        brush_color = colors["blue"]

    elif key == ord("y"):

        brush_color = colors["yellow"]

    elif key == ord("e"):

        brush_color = colors["black"]

    cv2.putText(
        frame,
        f"Brush Size : {brush_size}",
        (10, h-50),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (255,255,255),
        2
    )

    cv2.imshow("AI Air Drawing", frame)

    if key == ord("q"):
        break
cap.release()
cv2.destroyAllWindows()                            
    

