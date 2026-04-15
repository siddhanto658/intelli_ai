import eel
from command import takecommand, speak


def _safe_index_from_voice():
    spoken_value = takecommand()
    try:
        return int(spoken_value) - 1
    except (TypeError, ValueError):
        return None

# Initialize an empty list to store tasks
tasks = []
@eel.expose
# Function to add a task
def add_task():
        
        eel.DisplayMessage("Please tell the Title of your task!")
        speak("Please tell the Title of your task!")
        title = takecommand()
        
        eel.DisplayMessage("Please tell the Description of your task!")
        speak("Please tell the Description of your task!")
        description = takecommand()
        tasks.append({"title": title, "description": description})
        print("Task added successfully!")
        
        eel.DisplayMessage("Task added successfully!")
        speak("Task added successfully!")
# add_task()
# Function to view all tasks
def view_task():
        if tasks:
            print("Tasks:")
            for idx, task in enumerate(tasks, start=1):
                print(f"{idx}. Title: {task['title']}, Description: {task['description']}")
                eel.DisplayMessage(f"Title: {task['title']}, Description: {task['description']}")
                speak(f"Title: {task['title']}, Description: {task['description']}")
            
        else:
            print("No tasks available.")
            eel.DisplayMessage("No task availiable")
            speak("No task availiable")
# view_task()

# Function to update a task
def update_task():
        view_task()
        if tasks:  
            eel.DisplayMessage("Please tell the index of your task!")
            speak("Please tell the index of your task!")
            task_index = _safe_index_from_voice()
            if task_index is None:
                eel.DisplayMessage("Invalid task index.")
                speak("Invalid task index.")
                return
            if 0 <= task_index < len(tasks):
                eel.DisplayMessage("Please tell the new title of your task!")
                speak("Please tell the new title of your task!")
                new_title = takecommand()
                eel.DisplayMessage("Please tell the new description of your task!")
                speak("Please tell the new description of your task!")
                new_description = takecommand()
                if new_title:
                    tasks[task_index]['title'] = new_title
                if new_description:
                    tasks[task_index]['description'] = new_description
                print("Task updated successfully!")
                eel.DisplayMessage("Task updated successfully!")
                speak("Task updated successfully!")
            else:
                print("Invalid task index.")
                eel.DisplayMessage("Invalid task index.")
                speak("Invalid task index.")
        else:
            print("No tasks available.")
            eel.DisplayMessage("No tasks availiable.")
            speak("No tasks available.")
# update_task()
# Function to delete a task
def delete_task():
        view_task()
        if tasks:
            print("Please tell the index number of the task to delete!")
            eel.DisplayMessage("Please tell the index number of the task to delete!")
            speak("Please tell the index number of the task to delete!")
            task_index = _safe_index_from_voice()
            if task_index is None:
                eel.DisplayMessage("Invalid task index.")
                speak("Invalid task index.")
                return
            if 0 <= task_index < len(tasks):
                deleted_task = tasks.pop(task_index)
                print(f"Task '{deleted_task['title']}' deleted successfully!")
                eel.DisplayMessage(f"Task '{deleted_task['title']}' deleted successfully!")
                speak("Task deleted successfully!")
            else:
                print("Invalid task index.")
                eel.DisplayMessage("Invalid task index.")
                speak("Invalid task index.")
        else:
            print("No tasks available.")
            eel.DisplayMessage("No tasks availiable.")
            speak("No tasks available.")
# delete_task()
# Main loop
# while True:
#     print("\nInteractive Task Manager")
#     print("1. Add Task")
#     print("2. View Tasks")
#     print("3. Update Task")
#     print("4. Delete Task")
#     print("5. Exit")
    
#     speak("Please select an option (1-5)!")
#     choice = int(takecommand())
    
#     if choice == "1":
#         add_task()
#     elif choice == "2":
#         view_tasks()
#     elif choice == "3":
#         update_task()
#     elif choice == "4":
#         delete_task()
#     elif choice == "5":
#         print("Exiting the Task Manager. Goodbye!")
#         speak("Exiting the Task Manager. Goodbye!")
#         break
#     else:
#         print("Invalid choice. Please select a valid option (1-5).")
#         speak("Invalid choice. Please select a valid option (1-5).")
