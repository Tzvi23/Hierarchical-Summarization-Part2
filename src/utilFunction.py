import os
import shutil
from Discourse_Segmenter import do_segment
from Discourse_Parser import do_parse
import xml.etree.ElementTree as ET
from print_colors import bcolors
import re


"""
This functions take the file as input.
Thank splits by \n and adds to all the lines that without dot at the end a dot
for further processing.
Counts length of each sentences and if its more thatn max_length stores the index of the sent
and removes it.
Than rewrites to the input file.
"""


def read_file(filename):
    with open(os.path.join('Input', filename + '.txt')) as inputFile:
        file_read = inputFile.read()
    return file_read


def read_file_fullPath(fullPath):
    with open(fullPath + '.txt') as inputFile:
        file_read = inputFile.read()
    return file_read


def line_only_numbers(line):
    test_line = re.sub('[^a-zA-z0-9]', '', line)
    if test_line.isdigit():
        return True
    else:
        return False


def remove_long_sentences(original_text, max_length=600):
    split_text = original_text.split('\n')
    indexes = list()
    # Find indexes for sentences longer than max length
    for index in range(len(split_text)):
        # # Add dot at the end if not exists
        if not split_text[index].strip().endswith('.'):
            split_text[index] = split_text[index] + '.'
        # # Changes the first letter to capital letter
        # # TODO check if needed - if possible REMOVE!
        # if not split_text[index][0].isupper():
        #     temp_sent = list(split_text[index])
        #     temp_sent[0] = temp_sent[0].upper()
        #     split_text[index] = "".join(temp_sent)
        # Stores index if over max_length
        if len(split_text[index]) > max_length or len(split_text[index]) == 1:
            indexes.append(index)
        # Check if line contains only numbers and should be removed
        if line_only_numbers(split_text[index]) and index not in indexes:
            indexes.append(index)
    # Remove sentences found
    for pointer in reversed(indexes):
        print '[!!] Sent removed : {}'.format(split_text[pointer])
        del split_text[pointer]
    # Rejoin the list back to one text
    return '\n'.join(split_text)


def write_processed_file(filename, updated_text):
    with open(os.path.join('Input', filename + '.txt'), 'w') as outputFile:
        outputFile.write(updated_text)


def write_processed_file_full_path(fullPath, updated_text):
    with open(fullPath + '.txt', 'w') as outputFile:
        outputFile.write(updated_text)


def processFile(file_name):
    # file_name = '17cut'
    # text = remove_long_sentences(read_file(file_name))  # prev version
    text = remove_long_sentences(read_file_fullPath(file_name))
    # write_processed_file(file_name, text)  # prev version
    write_processed_file_full_path(file_name, text)
    print('Processed text: \n' + text)


def start_segmenter(file_path):
    if not do_segment(file_path):
        return False
    return True


def start_parser():
    try:
        if do_parse("tmp.edu") is False:
            return False
        return True
    except UnicodeEncodeError:
        print(bcolors.FAIL + 'Encode ERROR' + bcolors.ENDC)
        return False


def discourse_file(file_name, base_folder_path='Input'):
    print(bcolors.OKGREEN + 'Starting Pre-process of input file\n' + bcolors.ENDC)
    processFile(file_name)
    print(bcolors.OKGREEN + 'Starting Segmenter\n' + bcolors.ENDC)
    # file_path = os.path.join(base_folder_path, file_name + '.txt')  # prev version
    file_path = file_name + '.txt'
    if not start_segmenter(file_path):
        create_and_copy_output_fail(file_name, 'SEG')
        print(bcolors.FAIL + 'Segmenter failed due to max attempts' + bcolors.ENDC)
        return 'S'  # Indication that segmenter failed due to max attempts
    print(bcolors.OKGREEN + 'Starting Parser \n' + bcolors.ENDC)
    if start_parser() is False:
        print(bcolors.FAIL + 'Parsing failed due to file length' + bcolors.ENDC)
        return 'P'  # Indication that parsing failed due to file length


def create_and_copy_output(file_name, output_folder='Output'):
    # Copy Data to the new outputFile
    shutil.copy('tmp_doc.dis', os.path.join(output_folder, file_name.split('/')[3] + '_output.txt'))
    with open(os.path.join(output_folder, file_name.split('/')[3] + '_output.txt'), 'r') as original_output_file:
        data = original_output_file.read()
        data = data.replace('\n', '')
    with open(os.path.join(output_folder, file_name.split('/')[3] + '_strip_output.txt'), 'w') as updated_output_file:
        updated_output_file.write(data)
    print('Done!')


def create_and_copy_output_fail(file_name, reason, output_folder='Output'):
    with open(os.path.join(output_folder, file_name.split('/')[3] + '_output_FAILED_' + reason + '.txt'), 'w') as updated_output_file:
        updated_output_file.write('Failed due to file length')
    with open(os.path.join(output_folder, file_name.split('/')[3] + '_strip_output_FAILED_' + reason + '.txt'), 'w') as updated_output_file:
        updated_output_file.write('Failed due to file length')
    print('Done!')


def run_presentation(filename='17cut'):
    res = discourse_file(filename)
    if res != 'P' and res != 'S':
        create_and_copy_output(filename)
        # webbrowser.open('Demo/Rhetorical Parser Interface.html')
        return True
    elif res == 'P':
        create_and_copy_output_fail(filename, 'PARSE')
        return False
    elif res == 'S':
        return False


# region XML
# ==== Xml Functions ====
def read_xml_file(filename, target_dir=os.path.join('Input', 'xml_part1')):
    parsed_dict = dict()
    current_tag = 'non_section'  # base tag
    last_index = -1
    sent = False
    parsed_dict[current_tag] = list()

    tree = ET.parse(os.path.join(target_dir, filename))
    root = tree.getroot()
    for elem in root:
        if elem.tag == 'S':
            # parsed_dict[current_tag].append(elem.text) previous_version
            if len(parsed_dict[current_tag]) == 0:
                sent = True
                parsed_dict[current_tag].append(elem.text)
                last_index += 1
            elif not elem.text.endswith('.') and sent is True:
                parsed_dict[current_tag][last_index] = parsed_dict[current_tag][last_index] + elem.text
            elif not elem.text.endswith('.') and sent is False:
                sent = True
                last_index += 1
                parsed_dict[current_tag].append(elem.text + ' ')
            elif sent is True:
                sent = False
                parsed_dict[current_tag][last_index] = parsed_dict[current_tag][last_index] + elem.text
            else:
                sent = False
                last_index += 1
                parsed_dict[current_tag].append(elem.text)
            print(elem.text)
        elif elem.tag == 'section':
            current_tag = elem.attrib['name']
            last_index = -1
            parsed_dict[current_tag] = list()
            print(elem.attrib['name'])
        elif elem.tag == 'OneItem':
            # parsed_dict[current_tag].append(elem.text)
            if len(parsed_dict[current_tag]) == 0:
                sent = True
                parsed_dict[current_tag].append(elem.text + ' ')
                last_index += 1
            # elif not elem.text.endswith('.'):
            #     parsed_dict[current_tag][last_index] = parsed_dict[current_tag][last_index] + elem.text
            elif elem.text.endswith('.') and sent is False:
                last_index += 1
                parsed_dict[current_tag].append(elem.text + ' ')
            else:
                sent = True
                last_index += 1
                parsed_dict[current_tag].append(elem.text + ' ')
            print(elem.text)
        for subelem in elem:
            # parsed_dict[current_tag].append(subelem.text)
            if subelem.tag == 'S':
                # parsed_dict[current_tag].append(elem.text) previous_version
                if len(parsed_dict[current_tag]) == 0:
                    sent = True
                    parsed_dict[current_tag].append(subelem.text)
                    last_index += 1
                elif not subelem.text.endswith('.') and sent is True:
                    parsed_dict[current_tag][last_index] = parsed_dict[current_tag][last_index] + subelem.text
                elif not subelem.text.endswith('.') and sent is False:
                    sent = True
                    last_index += 1
                    parsed_dict[current_tag].append(subelem.text + ' ')
                elif sent is True:
                    sent = False
                    parsed_dict[current_tag][last_index] = parsed_dict[current_tag][last_index] + subelem.text
                else:
                    sent = False
                    last_index += 1
                    parsed_dict[current_tag].append(subelem.text)
                print(subelem.text)
            elif subelem.tag == 'OneItem':
                # parsed_dict[current_tag].append(elem.text)
                if len(parsed_dict[current_tag]) == 0:
                    sent = True
                    parsed_dict[current_tag].append(subelem.text + ' ')
                    last_index += 1
                # elif not elem.text.endswith('.'):
                #     parsed_dict[current_tag][last_index] = parsed_dict[current_tag][last_index] + elem.text
                elif subelem.text.endswith('.') and sent is False:
                    last_index += 1
                    parsed_dict[current_tag].append(subelem.text + ' ')
                else:
                    sent = True
                    last_index += 1
                    parsed_dict[current_tag].append(subelem.text + ' ')
            print(subelem.text)
    return parsed_dict


def create_temp_file(xml_parse_result, file_name, base_dir=os.path.join('Input', 'xmlParse')):
    sub_path = os.path.join(base_dir, file_name[:-8])
    if not os.path.exists(sub_path):
        os.mkdir(sub_path)
    for section in xml_parse_result.keys():
        with open(os.path.join(sub_path, file_name[:-8] + '_' + section.replace(' ', '_') + '.txt'), mode='w') as tmp_files:
            for item in xml_parse_result[section]:
                tmp_files.write(item.encode('utf-8') + '\n')


def parse_xml_to_sub_file(file_name):  # Input example: '17.txt.xml'
    parsed_xml = read_xml_file(file_name)
    for key in parsed_xml.keys():
        if not parsed_xml[key]:
            del parsed_xml[key]
    # text = remove_long_sentences(parsed_xml)
    # create_temp_file(text.split('\n'), file_name)
    create_temp_file(parsed_xml, file_name)




# endregion
# run_presentation('Input/xmlParse/17/17_chairmans_statement')
# parse_xml_to_sub_file('19.txt.xml')
