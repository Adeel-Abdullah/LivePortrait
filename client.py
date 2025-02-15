import requests
import time

API_URL = "http://localhost:5000/predict"  # Flask app URL
STATUS_URL = "http://localhost:5000/task_status/{}"
DOWNLOAD_URL = "http://localhost:5000/download/{}"

SOURCE_IMAGE_PATH = "file.jpg"  # Update with actual source image path
DRIVING_VIDEO_PATH = "d0.mp4"  # Update with actual driving video path

def upload_files():
    """Uploads source image and driving video, then starts processing."""
    with open(SOURCE_IMAGE_PATH, "rb") as source, open(DRIVING_VIDEO_PATH, "rb") as driving:
        files = {
            "source": source,
            "driving": driving,
        }

        data = {
            "flag_normalize_lip": "true",  # Example additional argument
            "flag_relative_motion": "true",
        }

        response = requests.post(API_URL, files=files, data=data)

        if response.status_code == 200:
            data = response.json()
            task_id = data.get("task_id")
            status_url = data.get("status_url")
            print(f"✅ Task started! Check status at: {status_url}")
            return task_id
        else:
            print(f"❌ Error: {response.json()}")
            return None


def check_status(task_id):
    """Checks task status until it's completed."""
    while True:
        response = requests.get(STATUS_URL.format(task_id))
        if response.status_code == 200:
            data = response.json()
            status = data.get("status")
            if status == "COMPLETED":
                output_filename = data.get("output_file").split("/")[-1]
                return output_filename
            elif status == "FAILED":
                print(f"❌ Task failed: {data.get('error')}")
                return None
            else:
                print(f"⏳ Task status: {status}... Retrying in 5 seconds")
        else:
            print(f"❌ Failed to get task status: {response.json()}")

        time.sleep(5)  # Wait before retrying

def download_result(filename):
    """Downloads the result video."""
    response = requests.get(DOWNLOAD_URL.format(filename), stream=True)
    if response.status_code == 200:
        output_filepath = f"output_{filename}"
        with open(output_filepath, "wb") as f:
            for chunk in response.iter_content(chunk_size=1024):
                f.write(chunk)
        print(f"✅ Inference successful! Output saved as {output_filepath}")
    else:
        print(f"❌ Error downloading file: {response.json()}")

if __name__ == "__main__":
    task_id = upload_files()
    # task_id = 'cc5f33b9-c3b3-4a73-8742-e6c329b68272'
    print(task_id)
    if task_id:
        output_filename = check_status(task_id)
        if output_filename:
            download_result(output_filename)
