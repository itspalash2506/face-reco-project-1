import cv2
import numpy as np
import os
import imutils
from datetime import datetime, timedelta
from dotenv import load_dotenv
from supabase import create_client, Client
from notification_service import send_whatsapp_notification

load_dotenv()

supabase_url = os.getenv('SUPABASE_URL')
supabase_key = os.getenv('SUPABASE_ANON_KEY')
supabase: Client = create_client(supabase_url, supabase_key)

size = 4
haar_file = 'haarcascade_frontalface_default.xml'
datasets = 'images'
print('Training the model...')

notification_cooldown = {}

(images, labels, names, id) = ([], [], {}, 0)
for (subdirs, dirs, files) in os.walk(datasets):
    for subdir in dirs:
        names[id] = subdir
        subjectpath = os.path.join(datasets, subdir)
        for filename in os.listdir(subjectpath):
            path = os.path.join(subjectpath, filename)
            label = id
            images.append(cv2.imread(path, 0))  
            labels.append(int(label))
        id += 1
(width, height) = (130, 100)
images = np.array(images, dtype=np.uint8)
labels = np.array(labels, dtype=np.int32)  
model = cv2.face.LBPHFaceRecognizer_create()
model.train(images, labels)
face_cascade = cv2.CascadeClassifier(haar_file)
webcam = cv2.VideoCapture(0)
cnt = 0
while True:
    _, im = webcam.read()
    # imgPath = urllib.request.urlopen(url)
    # imgNp = numpy.array(bytearray(imgPath.read()), dtype=numpy.uint8)
    # im = cv2.imdecode(imgNp, -1)
    im = imutils.resize(im, width=1000)
    gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)
    for (x, y, w, h) in faces:
        cv2.rectangle(im, (x, y), (x + w, y + h), (255, 255, 0), 2)
        face = gray[y:y + h, x:x + w]
        face_resize = cv2.resize(face, (width, height))
        prediction = model.predict(face_resize)
        cv2.rectangle(im, (x, y), (x + w, y + h), (0, 255, 0), 3)
        if prediction[1] < 800:
            detected_name = names[prediction[0]]
            cv2.putText(im, '%s - %.0f' % (detected_name, prediction[1]),
                        (x-10, y-10), cv2.FONT_HERSHEY_PLAIN, 1, (255, 255, 255))
            print(detected_name)
            cnt = 0

            current_time = datetime.now()
            should_notify = True

            if detected_name in notification_cooldown:
                last_notification_time = notification_cooldown[detected_name]
                if current_time - last_notification_time < timedelta(minutes=5):
                    should_notify = False

            if should_notify:
                try:
                    result = supabase.table('persons').select('*').eq('name', detected_name).execute()

                    if result.data and len(result.data) > 0:
                        person_data = result.data[0]
                        phone_number = person_data.get('phone_number')
                        email = person_data.get('email')

                        if phone_number and email:
                            notification_sent = send_whatsapp_notification(
                                phone_number,
                                detected_name,
                                email
                            )

                            if notification_sent:
                                supabase.table('persons').update({
                                    'last_detected_at': current_time.isoformat(),
                                    'notification_sent': True
                                }).eq('name', detected_name).execute()

                                notification_cooldown[detected_name] = current_time
                                print(f"WhatsApp notification sent for {detected_name}")
                            else:
                                print(f"Failed to send notification for {detected_name}")
                        else:
                            print(f"Missing contact details for {detected_name}")
                    else:
                        print(f"No database record found for {detected_name}")

                except Exception as e:
                    print(f"Error sending notification: {str(e)}")
        else:
            cnt += 1
            cv2.putText(im, 'Unknown', (x-10, y-10), cv2.FONT_HERSHEY_PLAIN, 1, (0, 255, 0))
            if cnt > 100:
                print("Unknown Person")
                cv2.imwrite("unknown.jpg", im)
                cnt = 0
    cv2.imshow('Face Recognition', im)
    key = cv2.waitKey(10)
    if key == 27:  # Press 'Esc' to exit
        break
webcam.release()
cv2.destroyAllWindows()