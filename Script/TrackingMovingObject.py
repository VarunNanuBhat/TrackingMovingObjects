import datetime
import cv2
import pandas # For creating data frames to Log the timings and generate .csv file
from bokeh.plotting import figure, show, output_file
from bokeh.models import HoverTool, ColumnDataSource
#bokeh is for plotting the graph using data frames created by Pandas

first_frame = None
status_list = [None, None]
times = []
df = pandas.DataFrame(columns=["Start", "End"])
video = cv2.VideoCapture(0)#creating a video object using OpenCv , 0 means the source of video would be the inbuilt camera of the device.

a = 1
while True:
    a = a + 1
    check, frame = video.read() #reading the video object and storing the individual frames inside the loop
    status = 0
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) #coverting the frame to gray scale (binary image)
    gray = cv2.GaussianBlur(gray, (21, 21), 0) #converting the gray scale frame to Gaussian Blur image

#Storing the first frame in first_frame variable that will be used substract from further frames to get the objects.
    if first_frame is None:
        first_frame = gray
        continue

    delta_frame = cv2.absdiff(first_frame, gray) #substracting the subsequent gray scale frames in while loop with first_frame
    th_delta = cv2.threshold(delta_frame, 60, 255, cv2.THRESH_BINARY)[1] #thresholding the delta_frame (difference in first and current frame).If pixel value is greater than a threshold value, it is assigned one value, else it is assigned another value
    th_delta = cv2.dilate(th_delta, None, iterations=0) #dilating the thresh delta further to increse efficiency. (enlarge image to screen)
    (_ ,cnts, _) = cv2.findContours(th_delta.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE) #finding the contours of the detected object in frame and storing in the variable cnts

#looping through the contours and drawing a rectangle around the object
    for contour in cnts:
        if cv2.contourArea(contour) < 10000:
            continue
        status = 1
        (x, y, w, h) = cv2.boundingRect(contour)
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 3)

    status_list.append(status)
    status_list = status_list[-2:]
#changing the status value between 1 and 0 based on the object first enters and then leaves the frame
    if status_list[-1] == 1 and status_list[-2] == 0:
        times.append(datetime.datetime.now())
#then storing the current datetime first when the object enters the frame and then when it leaves the frame
    if status_list[-1] == 0 and status_list[-2] == 1:
        times.append(datetime.datetime.now())

    cv2.imshow('Capturing', frame) #displaying the frame in window where we will detect the objects as well

#continue the while loop until user presses ‘q’ button on keyboard.
    key = cv2.waitKey(1)
    if key == ord('q'):
        break

for i in range(0, len(times), 2):
    df = df.append({"Start": times[i], "End": times[i+1]}, ignore_index=True)

df.to_csv("Times_"+datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S")+".csv") # storing te Start and End timing into the Pandas dataframe object “df” .saving the the dataframe data into the .csv file in application folder
video.release()
cv2.destroyAllWindows()

# Code to Generate Graph using Bokeh
df["Start_string"] = df["Start"].dt.strftime("%Y-%m-%d %H:%M:%S")
df["End_string"] = df["End"].dt.strftime("%Y-%m-%d %H:%M:%S")

cds=ColumnDataSource(df)

p=figure(x_axis_type='datetime', height=100, width=500, title="Motion Graph")
p.yaxis.minor_tick_line_color=None
p.ygrid[0].ticker.desired_num_ticks=1

hover=HoverTool(tooltips=[("Start", "@Start_string"), ("End", "@End_string")])
p.add_tools(hover)

q=p.quad(left="Start", right="End", bottom=0, top=1, color="red", source=cds)
output_file("Graph"+datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S")+".html")
show(p)
# End of Code of Generating Graph
