def create_beauty_pass(input_file, output_file):
    try:
        with open(input_file, 'r', encoding='utf-8') as infile:
            # Read the content of the file
            content = infile.read()
            
            # Replace occurrences of 'q', 'r', and 's' with a space
            modified_content = content.replace('q', ' ').replace('r', ' ').replace('s', ' ')
            
        # Save the modified content to a new file
        with open(output_file, 'w', encoding='utf-8') as outfile:
            outfile.write(modified_content)
        
        print(f"Beauty pass completed successfully. Output saved to {output_file}")
    except Exception as e:
        print(f"An error occurred: {e}")

# Example usage
create_beauty_pass("input.txt", "beauty_pass_output.txt")
