import os
from collections import defaultdict
from datetime import datetime


def find_duplicate_files(target_directory):
    """
    Scans the given directory and groups files by a composite key of (name, size).
    """
    # Dictionary to store files: {(filename, size): [list_of_absolute_paths]}
    files_manifest = defaultdict(list)

    print(f"Scanning directory: {target_directory}...")
    print("This might take a moment depending on the number of files...\n")

    # Walk through all directories and files
    for root, _, files in os.walk(target_directory):
        for filename in files:
            full_path = os.path.join(root, filename)
            try:
                # Get file size in bytes
                file_size = os.path.getsize(full_path)
                # Group by both filename and size
                files_manifest[(filename, file_size)].append(full_path)
            except (OSError, PermissionError):
                # Skip files that can't be accessed (e.g., system files)
                continue

    # Filter out keys that only have one file (no duplicates)
    duplicates = {key: paths for key, paths in files_manifest.items() if len(paths) > 1}
    return duplicates


def display_paginated_results(duplicates, page_size=10):
    """
    Displays the found duplicates in a clean, paginated format.
    """
    if not duplicates:
        print("No duplicate files (same name and size) were found.")
        return

    total_duplicates = len(duplicates)
    print(f"Found {total_duplicates} unique sets of duplicate files.\n")

    current_count = 0

    for (filename, size), paths in duplicates.items():
        current_count += 1

        # Format size for readability (KB/MB)
        size_str = f"{size / 1024:.2f} KB" if size < 1048576 else f"{size / (1024 * 1024):.2f} MB"

        print(f"[{current_count}] Duplicate Group: '{filename}' ({size_str})")
        for path in paths:
            try:
                mtime = os.path.getmtime(path)
                timestamp = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M:%S")
            except (OSError, PermissionError):
                timestamp = "Unavailable"

            print(f"  -> {path}")
            print(f"     Size: {size_str} | Last modified: {timestamp}")
        print("-" * 50)


def delete_duplicate_files(duplicates):
    """Allows user to select and delete specific duplicate files with confirmation."""
    if not duplicates:
        print("No duplicate files were found to delete.")
        return

    proceed = input(
        "\nDelete duplicate files? Type 'yes' to proceed: ").strip().lower()
    if proceed not in {"yes", "y"}:
        print("Deletion cancelled.")
        return

    for (filename, size), paths in duplicates.items():
        print(f"\n{'='*60}")
        print(f"Duplicate group: '{filename}' ({len(paths)} files)")
        print(f"{'='*60}")

        # Build list with timestamps and sizes
        file_list = []
        for idx, path in enumerate(paths, 1):
            try:
                file_size = os.path.getsize(path)
                size_str = f"{file_size / 1024:.2f} KB" if file_size < 1048576 else f"{file_size / (1024 * 1024):.2f} MB"
                mtime = os.path.getmtime(path)
                timestamp = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M:%S")
            except (OSError, PermissionError):
                size_str = "Unknown"
                timestamp = "Unavailable"
            file_list.append((idx, path, timestamp, size_str))

        # Display all files with numbered options
        for idx, path, timestamp, size_str in file_list:
            print(f"[{idx}] {path}")
            print(f"    Size: {size_str} | Last modified: {timestamp}")

        print(f"\n[0] Skip this group")
        print(f"[*] Delete multiple files (comma-separated, e.g., 1,3)")

        selection = input("\nSelect file(s) to delete (enter number or numbers): ").strip()

        if selection == "0" or selection == "":
            print("Skipped this group.")
            continue

        # Parse selection
        try:
            if "," in selection:
                selected_indices = [int(x.strip()) for x in selection.split(",")]
            else:
                selected_indices = [int(selection)]
        except ValueError:
            print("Invalid input. Skipped this group.")
            continue

        # Validate indices
        if not all(1 <= idx <= len(paths) for idx in selected_indices):
            print("Invalid selection. Skipped this group.")
            continue

        # Show confirmation for selected files
        files_to_delete = [paths[idx - 1] for idx in selected_indices]
        print(f"\nYou selected {len(files_to_delete)} file(s) for deletion:")
        for file_path in files_to_delete:
            try:
                file_size = os.path.getsize(file_path)
                size_str = f"{file_size / 1024:.2f} KB" if file_size < 1048576 else f"{file_size / (1024 * 1024):.2f} MB"
            except (OSError, PermissionError):
                size_str = "Unknown"
            print(f"  - {file_path} ({size_str})")

        final_confirm = input("\nType 'yes' to confirm deletion: ").strip().lower()
        if final_confirm not in {"yes", "y"}:
            print("Deletion cancelled for this group.")
            continue

        # Delete selected files
        for file_path in files_to_delete:
            try:
                file_size = os.path.getsize(file_path)
                size_str = f"{file_size / 1024:.2f} KB" if file_size < 1048576 else f"{file_size / (1024 * 1024):.2f} MB"
                os.remove(file_path)
                print(f"✓ Deleted: {file_path} ({size_str})")
            except (OSError, PermissionError) as error:
                print(f"✗ Failed to delete {file_path}: {error}")
            except Exception as e:
                print(f"✗ Error getting size for {file_path}: {e}")
                try:
                    os.remove(file_path)
                    print(f"✓ Deleted: {file_path}")
                except (OSError, PermissionError) as error:
                    print(f"✗ Failed to delete {file_path}: {error}")


if __name__ == "__main__":
    # Input path selection
    # For a local system: enter a standard path like 'C:\\Users\\Username\\Documents' or '/home/user/documents'
    # For a remote system: Ensure the network drive is mounted locally (e.g., 'Z:\\' or '/mnt/share')

    user_path = input("Enter the absolute directory path to scan: ").strip()

    if os.path.exists(user_path) and os.path.isdir(user_path):
        duplicate_dict = find_duplicate_files(user_path)
        display_paginated_results(duplicate_dict, page_size=10)
        delete_duplicate_files(duplicate_dict)
    else:
        print("Error: The path provided does not exist or is not a valid directory.")