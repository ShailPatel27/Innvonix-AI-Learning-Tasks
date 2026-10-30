from fastapi import BackgroundTasks, FastAPI

app = FastAPI()

notifications = []


def save_notification(email: str, message: str):
    notifications.append({"email": email, "message": message})


@app.post("/notify/{email}")
def send_notification(email: str, background_tasks: BackgroundTasks):
    background_tasks.add_task(save_notification, email, "Your task is complete.")
    return {"message": "Notification queued"}


@app.get("/notifications")
def list_notifications():
    return notifications
