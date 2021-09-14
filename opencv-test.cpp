

#include <opencv2/core/core.hpp>
#include <opencv2/highgui/highgui.hpp>
#include <opencv2/imgproc.hpp>
#include <opencv2/imgcodecs.hpp>
#include <opencv2/videoio.hpp>
#include <opencv2/highgui.hpp>
#include <opencv2/video.hpp>
#include <iostream>
#include<random>

using namespace cv;
using namespace std;



//return the median from given vector
int computeMedian(vector<int> elements)
{
    nth_element(elements.begin(), elements.begin() + elements.size() / 2, elements.end());
    return elements[elements.size() / 2];
}

//find the median of each pixel from the given random frames
Mat compute_median(vector<Mat> vec)
{
    Mat medianImg(vec[0].rows, vec[0].cols, CV_8UC3, cv::Scalar(0, 0, 0));
    for (int row = 0; row < vec[0].rows; row++)
    {
        for (int col = 0; col < vec[0].cols; col++)
        {
            vector<int> elements_B;
            vector<int> elements_G;
            vector<int> elements_R;
            for (int imgNumber = 0; imgNumber < vec.size(); imgNumber++)
            {
                int B = vec[imgNumber].at<Vec3b>(row, col)[0];
                int G = vec[imgNumber].at<Vec3b>(row, col)[1];
                int R = vec[imgNumber].at<Vec3b>(row, col)[2];

                elements_B.push_back(B);
                elements_G.push_back(G);
                elements_R.push_back(R);
            }
            medianImg.at<Vec3b>(row, col)[0] = computeMedian(elements_B);
            medianImg.at<Vec3b>(row, col)[1] = computeMedian(elements_G);
            medianImg.at<Vec3b>(row, col)[2] = computeMedian(elements_R);
        }
    }
    return medianImg;
}

int main(int argc, char* argv[])
{
    string path = "C:\\Users\\הודיה\\Videos\\mm.mp4";
    VideoCapture video_stream(path);
    if (!video_stream.isOpened()) {
        //error in opening the video input
        cerr << "Unable to open: " << path << endl;
        return 0;
    }
    int w = (int)video_stream.get(CAP_PROP_FRAME_WIDTH);
    default_random_engine generator;
    uniform_int_distribution<int>distribution(0, video_stream.get(CAP_PROP_FRAME_COUNT));
    vector<Mat> frames;
    Mat frame;

    //create vector of random frames for calculate the median backround
    for (int i = 0; i < 10; i++)
    {
        int fid = distribution(generator);
        video_stream.set(CAP_PROP_POS_FRAMES, fid);
        video_stream >> frame;
        if (frame.empty())
            continue;
        frames.push_back(frame);
    }
    Mat medianFrame = compute_median(frames);

    video_stream.set(CAP_PROP_POS_FRAMES, 0);
    Mat grayMedianFrame;
    Mat gray_frame;
    cvtColor(medianFrame, grayMedianFrame, COLOR_BGR2GRAY);
    string frameNumberString;
    string num_frame="-1";
    //for each frame in the video
    while (1)
    {
        video_stream >> frame;
        if (frame.empty())
            break;
        cvtColor(frame, gray_frame, COLOR_BGR2GRAY);
        Mat dframe;
        absdiff(gray_frame, grayMedianFrame, dframe);
        threshold(dframe, dframe, 30, 255, THRESH_BINARY);
        //vector of all the outlines in the background
        vector<vector<Point> > contours;
        Mat contourOutput = dframe.clone();
        findContours(contourOutput, contours, RETR_EXTERNAL, CHAIN_APPROX_SIMPLE);
        //display the number of the frame
        rectangle(frame, cv::Point(10, 2), cv::Point(70, 20), Scalar(255, 255, 255), -1);
        stringstream ss;
        ss << video_stream.get(CAP_PROP_POS_FRAMES);
        frameNumberString = ss.str();
        putText(frame, frameNumberString.c_str(), cv::Point(15, 15),FONT_HERSHEY_SIMPLEX, 0.5, cv::Scalar(0, 0, 0));
        int counter = 0;
        for (int c = 0; c < contours.size(); c++)
        {
            //limit each outline with rectangle and find the biggest (of the bicycle)
            Rect r = boundingRect(contours[c]);
            if ((r.height * r.width) > 4000)
            {
                rectangle(frame, r, Scalar(0, 0, 255));
                counter++;
            }
            if (counter == 1 && (r.height * r.width) > 47000)
            {
                //keep the frame number of the detection
                num_frame = frameNumberString;
                break;
            }
        }
        //print the warning of theft
        if (num_frame != "-1")
        {
            rectangle(frame, cv::Point(130, 2), cv::Point(750, 25), Scalar(255, 255, 255), -1);
            putText(frame, "Suspected theft - Inserted into database to verify", cv::Point(160, 20), FONT_HERSHEY_SIMPLEX, 0.7, cv::Scalar(0, 0, 255), 2);
        }
        //show the video
        imshow("frame", frame);
        //imshow("frame", dframe);
        waitKey(20);
    }
    video_stream.release();
    return 0;
}