def write(file_path, content):
    try:
        with open(file_path, 'w') as file:
            file.write(content)
        print("File written successfully.")
    except Exception as e:
        print(f"An error occurred: {e}")

