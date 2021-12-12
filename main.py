from datetime import datetime
import face_recognition
import cv2
import numpy as np
from livenessmodel import get_liveness_model
from common import get_users
import pandas as pd

font = cv2.FONT_HERSHEY_DUPLEX

# Get the liveness network
model = get_liveness_model()

# load weights into new model
model.load_weights("model/model.h5")
print("Loaded model from disk")

# Read the users data and create face encodings
known_names, known_encods = get_users()

video_capture = cv2.VideoCapture(0)
video_capture.set(3, 640)
video_capture.set(4, 480)

# Initialize some variables
face_locations = []
face_encodings = []
face_names = []
process_this_frame = True
input_vid = []
sheet1 = []
sheet2 = []

img_counter = 0

now = datetime.now()

        # dd/mm/YY H:M:S
dt_string = now.strftime("%d/%m/%Y %H:%M:%S")


while True:
    # Grab a single frame of video
    if len(input_vid) < 24:

        ret, frame = video_capture.read()

        liveimg = cv2.resize(frame, (100,100))
        liveimg = cv2.cvtColor(liveimg, cv2.COLOR_BGR2GRAY)
        input_vid.append(liveimg)
    else:
        ret, frame = video_capture.read()

        #date and time
        now = datetime.now()

        # dd/mm/YY H:M:S
        dt_string = now.strftime("%d/%m/%Y %H:%M:%S")

        liveimg = cv2.resize(frame, (100,100))
        liveimg = cv2.cvtColor(liveimg, cv2.COLOR_BGR2GRAY)
        input_vid.append(liveimg)
        inp = np.array([input_vid[-24:]])
        inp = inp/255
        inp = inp.reshape(1,24,100,100,1)
        pred = model.predict(inp)
        input_vid = input_vid[-25:]

        if pred[0][0]> .80:

            # Resize frame of video to 1/4 size for faster face recognition processing
            small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

            # Only process every other frame of video to save time
            if process_this_frame:
                # Find all the faces and face encodings in the current frame of video
                face_locations = face_recognition.face_locations(small_frame)
                face_encodings = face_recognition.face_encodings(small_frame, face_locations)
                name = "Unknown"
                face_names = []
                for face_encoding in face_encodings:
                    for ii in range(len(known_encods)):
                        # See if the face is a match for the known face(s)
                        match = face_recognition.compare_faces([known_encods[ii]], face_encoding)

                        if match[0]:
                            name = known_names[ii]

                    face_names.append(name)

            process_this_frame = not process_this_frame

            unlock = False
            for n in face_names:

                if n != 'Unknown':
                    unlock = True

            # Display the results
            for (top, right, bottom, left), name in zip(face_locations, face_names):
                # Scale back up face locations since the frame we detected in was scaled to 1/4 size
                top *= 4
                right *= 4
                bottom *= 4
                left *= 4

                # Draw a box around the face
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

                # Draw a label with a name below the face
                cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)

                cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)
                if unlock:
                    cv2.putText(frame, 'RECOGNIZED', (frame.shape[1] // 2, frame.shape[0] // 2), font, 1.0,
                                (255, 255, 255), 1)
                    cv2.putText(frame, 'Click "I" to Check-in and "O" key to Check-Out', (frame.shape[0] // 2, 50 // 1), font, 1.0,
                                (0, 255, 0), 1)
                    k = cv2.waitKey(1)
                    if k % 256 == 32:
                        # SPACE pressed
                        if name not in sheet1:
                            img_name = "opencv_frame_{}.png".format(img_counter)
                            cv2.imwrite(img_name, frame)
                            print("{} written!".format(img_name))
                            img_counter += 1

                            sheet1.append(name)
                            sheet1.append(dt_string)


                        else:
                            print("Marked present already")

                    elif k % 256 == 27:
                        # ESC pressed
                        print("Escape hit, closing...")
                        # print(sheet)
                        # video_captur oe.release()
                        # cv2.destroyAllWindows()
                        lst1 = [sheet1[x:x + 2] for x in range(0, len(sheet1), 2)]
                        lst2 = [sheet2[x:x + 2] for x in range(0, len(sheet2), 2)]
                        # print(lst)
                        print(lst2)
                        df1 = pd.DataFrame(lst1, columns=['Name', 'In Time'])
                        df2 = pd.DataFrame(lst2, columns = ['Name', 'Out Time'])
                        df = pd.merge(df1, df2, on="Name")
                        print(df.head)
                        df.to_csv("attendance.csv", encoding='utf-8', index=False)
                        exit()
                    if cv2.waitKey(1) & 0xFF == ord('o'):
                        if name not in sheet2:
                            img_name = "opencv_frame_{}.png".format(img_counter)
                            cv2.imwrite(img_name, frame)
                            print("{} written!".format(img_name))
                            img_counter += 1

                            sheet2.append(name)
                            sheet2.append(dt_string)
                            print(sheet2)

                else:
                    cv2.putText(frame, 'NOT RECOGNISED', (frame.shape[1] // 2, frame.shape[0] // 2), font, 1.0,
                                (255, 255, 255), 1)
        else:
            cv2.putText(frame, 'WARNING!', (frame.shape[1] // 2, frame.shape[0] // 2), font, 1.0, (255, 255, 255), 1)
        # Display the liveness score in top left corner
        cv2.putText(frame, str(pred[0][0]), (20, 20), font, 1.0, (255, 255, 0), 1)
        # Display the resulting image
        cv2.imshow('Video', frame)

        # Hit 'q' on the keyboard to quit!
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

# Release handle to the webcam
video_capture.release()
cv2.destroyAllWindows()