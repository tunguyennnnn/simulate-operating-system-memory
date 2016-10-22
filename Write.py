def write_to_output_file(output):
    file = open("output.txt", "a")
    file.write(output)
    file.close()
    print output
