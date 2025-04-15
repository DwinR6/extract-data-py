import os

def rename_files_in_directory(directory, old_text, new_text):
    try:
        for filename in os.listdir(directory):
            if filename.endswith(".mp3"):
                new_filename = filename.replace(old_text, new_text)
                old_file_path = os.path.join(directory, filename)
                new_file_path = os.path.join(directory, new_filename)
                
                if old_file_path != new_file_path:
                    os.rename(old_file_path, new_file_path)
                    print(f'Renamed: "{filename}" to "{new_filename}"')
                else:
                    print(f'No changes made to: "{filename}"')
    except Exception as e:
        print(f"An error occurred: {e}")

def main():
    directory = r"C:\Users\E_noe\Music\Aniceto Molina"  # Usa tu ruta aquí como raw string
    old_text = "spotifydown.com"
    new_text = input(f"Enter the text to replace '{old_text}' with: ").strip()
    
    if os.path.exists(directory) and os.path.isdir(directory):
        rename_files_in_directory(directory, old_text, new_text)
    else:
        print("The specified directory does not exist or is not valid.")

if __name__ == "__main__":
    main()
