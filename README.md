# YOLO-Salamander-Tracker
Using YOLO (You Only Look Once) to detect objects.


run the backend with:
cd backend
./start.bat

run the frontend with:
cd frontend
npm run dev

uploading + viewing videos:
upload a video in the frontend window, the bounding box video will be sent to backend/outputs, but will also be shown in the frontend's window after it is finished- the outputs and inputs folder is gitignored so it won't be visible to you until you upload a video!


Reflection:

Yolo vs Real World

YOLO did better when things in the video weren’t consistent. In our clips, the salamanders were moving over rocky/uneven backgrounds, lighting would change a bit, and sometimes they overlapped each other. YOLO was still able to pick them out in most of those cases, even when they weren’t super clear or were partially hidden.

Color masking, on the other hand, would probably only work well if everything was really controlled. Like if the tank background was a solid, consistent color and the lighting never changed. In that kind of setup, masking would actually be faster and simpler than YOLO. But once things get messy or unpredictable, it would break down pretty quickly.

YOLO is more flexible and works in real-world conditions, while color masking is better for simple, controlled environments.

What We Would Build Next

If we had more time, we’d probably work on improving tracking consistency so IDs stay the same even when salamanders leave the frame or cross paths. We also talked about adding a heatmap overlay so you can actually see movement patterns visually instead of just numbers.

We focused on getting the full pipeline working end-to-end first (upload → processing → tracking → results), so we kept it simple and didn’t add extra features that could break things.
