"""
Author: Tzvi puchinsky
"""
import utilFunction as util
import javaScript_functions as js
from print_colors import bcolors
import os
import sys


def run_main_discourse(filename='19.txt.xml', parsed_xml_path='Input/xmlParse'):
    util.parse_xml_to_sub_file(filename)
    parsed_xml_path = os.path.join(parsed_xml_path, filename[:-8])
    for parsed_file in os.listdir(parsed_xml_path):
        full_path = os.path.join(parsed_xml_path, parsed_file[:-4])
        print(bcolors.OKBLUE + 'Processing File:{0}'.format(parsed_file) + bcolors.ENDC)
        if util.run_presentation(full_path) is not False:
            path_for_js = os.path.join('Output', parsed_file[:-4] + '_strip_output.txt')
            nucleus_text = js.find_nucleus_text(path_for_js)
            write_nucleus_results(parsed_file[:-4] + '_nucleusText.txt', nucleus_text)
        else:
            print(bcolors.FAIL + '[Main] Skipping file: ' + parsed_file + bcolors.ENDC)


def write_nucleus_results(file_name, data, output_Folder='Output/Nucleus'):
    # Check if dir exists
    if not os.path.exists(output_Folder):
        os.mkdir(output_Folder)
    # Write results to file
    with open(os.path.join(output_Folder, file_name), mode='w') as outputFile:
        outputFile.write(data)


def loop_folder(inputFolder='Input/xml_part1'):
    counter = 1
    files_processed = skip_files_processed()
    numOfFiles = len(os.listdir(inputFolder))
    for filename in os.listdir(inputFolder):
        if filename[:-8] in files_processed:
            continue
        print(bcolors.OKBLUE + 'Filename: {0} | Progress:{1}/{2}'.format(filename, counter, numOfFiles) + bcolors.ENDC)
        run_main_discourse(filename)
        counter += 1


def skip_files_processed(outputFolder='Output'):
    files_list = list()
    files = os.listdir(outputFolder)
    for file_name in files:
        if not os.path.isdir(os.path.join(outputFolder, file_name)):
            number = file_name.split('_')[0]
            files_list.append(number)
    return files_list
# #Testing
# run_main_discourse('19.txt.xml')


if __name__ == '__main__':
    # Testing
    print('Args: ' + str(sys.argv))
    print('Abs path: ' + os.path.abspath(sys.argv[0]))
    print('Working dir: ' + os.path.dirname(sys.argv[0]))
    os.chdir(os.path.dirname(sys.argv[0]))
    print('Processing: ' + sys.argv[1])
    run_main_discourse(sys.argv[1])
    # run_main_discourse('64.txt.xml')
    # loop_folder()
