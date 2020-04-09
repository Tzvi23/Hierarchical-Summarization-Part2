#!/usr/bin/env python2
import sys

import js2py
import unicodedata
import json
# NL = \n
# QU = \"


def read_strip_output(path='Output/17_chairmans statement_strip_output.txt'):
    with open(path, mode='r') as inputstring:
        text = inputstring.read()
    return text


def run_javascript(text, mode='script'):
    js = "rhetoricParsingOutput='" + text + "';" + """
    var index = 0;
    var searchterm = "";
    var nucleus_selected = 0;
    var satellite_selected = 1;
    var nodenum = -1;
    var currentjsonstring; 
    var scrollison = 0;
    function help(){
    document.write('Test12');
    }
    // This function is called to start the recursive read function off on the provided input, and feed the json string back to addtext 
                function make_JSON_string(inputstring) 
                {
                    var jsonstringoutput = "";
                    var remaining_input = inputstring.trim();
                    nodenum = -1;
                    jsonstringoutput += recursiveread(remaining_input);
                    return jsonstringoutput;
                }
    function find_closed_bracket(input) 
                {
                    // The number of open brackets not closed currently
                    bracket_count = 0;
                    // The location of the closed bracket of the first open bracket in the input, within the remaining input
                    location_of_closed = 0;
                    /* The amount of input discarded so far. Also, the value that needs to be added to any value that refers to a
                     position within the remaining input, in order to obtain a position within the total input. */
                    var current_base_index = 0;
                    // The amount of input left to be considered
                    var remaining_input = input;
                    // This var is set to 1 to signal that no closed bracket has been found for the first open bracket in the input
                    var errorboolean = 0;
                    /* This var is set to 1 to signal that the first open bracket in the input has been found; 
                     after this, the while loop will search for the matching closed bracket */
                    var first_open_bracket_found = 0;
    
                    while (true) 
                    {
                        var nextopen = remaining_input.indexOf("(");
                        var nextclosed = remaining_input.indexOf(")");
                        // If the next bracket is an open bracket: 
                        if ((nextopen < nextclosed) && (nextopen != -1) && (nextclosed != -1)) 
                        {
                            first_open_bracket_found = 1;
                            bracket_count++;
                            remaining_input = remaining_input.substring(nextopen + 1, remaining_input.length);
                            current_base_index += nextopen + 1;
                        } 
                        // If the next bracket is a closed bracket or there is no open bracket: 
                        else if (((nextopen > nextclosed) || (nextopen == -1)) && (nextclosed != -1)) 
                        {
                            // If we're in the active portion of the search for a closed bracket, because we've found the first open bracket: 
                            if (first_open_bracket_found) 
                            {
                                bracket_count--;
                                // If we've found the closed bracket that matches the first open bracket in the input: 
                                if (bracket_count == 0) 
                                {
                                    location_of_closed = nextclosed;
                                    break;
                                } 
                                // If we haven't found the result, we keep looking: 
                                else 
                                {
                                    remaining_input = remaining_input.substring(nextclosed + 1, remaining_input.length);
                                    current_base_index += nextclosed + 1;
                                }
                            } 
                            // If we haven't yet found the first open bracket: 
                            else 
                            {
                                remaining_input = remaining_input.substring(nextclosed + 1, remaining_input.length);
                                current_base_index += nextclosed + 1;
                            }
    
                        } 
                        else if (nextclosed == -1) 
                        {
                            errorboolean = 1;
                            break;
                        }
                    }
    
                    if (errorboolean == 0)
                        return (location_of_closed + current_base_index);
                    else
                        return "BADFORMATERROR";
                }
    // This function creates a tree-structured json-format string from the output of the rhetorical parser 
    function recursiveread(inputstring) 
    {
                    nodenum += 1;
                    var output = " NL {";
    
                    //Determine the types of the parent 
                    var spanloc = inputstring.indexOf("span");
                    var leafloc = inputstring.indexOf("leaf");
                    //This type determines if it's a root or not 
                    var type;
                    //This type (type2) determines if it's a span or a leaf 
                    var type2;
                    if ((spanloc != -1) && ((spanloc < leafloc) || (leafloc == -1))) 
                    {
                        type = inputstring.substring(1, spanloc - 1);
    
                        type = type.trim();
                        type2 = "span"; 
    
                    }
                    else if ((leafloc != -1) && ((spanloc > leafloc) || (spanloc == -1)))
                    {
                        type = inputstring.substring(1, leafloc - 1);
                        type = type.trim();
                        type2 = "leaf";
    
                    }
    
                    //Use parent type to determine what to do next 
                    if (type == "Root")
                    {
    
                        //Add name and 1 bracket of metatext to output 
                        var txt = inputstring.substring(inputstring.indexOf(type), inputstring.indexOf(")") + 1);
                        output += " NL  QU name QU  :  QU " + nodenum + "ENDNODENUM" + txt + " QU ";
                        output += ", NL  QU children QU  :  NL [";
                        
                        //Call recursively on children 
                        //Set initial current location to just after root metatext 
                        var currentloc = inputstring.indexOf(")") + 1;
                        var parentcloseloc = find_closed_bracket(inputstring);
                        
                        //Find appropriate initial open location 
                        var childopenloc = (inputstring.substring(currentloc, parentcloseloc + 1)).indexOf("(") + currentloc;
                        var done = 0;
                        var count = 0;
                        //TODO: take into account quoted brackets? 
                        while (done != 1)
                        {
    
                            //Find and set childcloseloc 
                            var childcloseloc = find_closed_bracket(inputstring.substring(childopenloc, parentcloseloc + 1)) + childopenloc;
                            // Recursive call
                            var childjsondata = recursiveread(inputstring.substring(childopenloc, childcloseloc + 1));
                            if (count > 0) 
                            {
                                output += ",";
                            }
                            output += childjsondata;
    
                            //Set new currentloc to the location just after the closed bracket of the current child 
                            currentloc = childcloseloc + 1;
                            // Check if there are no more children of the parent 
                            if (((inputstring.substring(currentloc, parentcloseloc + 1)).indexOf("(")) == -1) 
                            {
                                done = 1;
                            }
                            else
                            {
                                //Set new childopenloc to the location of the next open bracket between the end of the current child's bracket and the end of the root's bracket
                                childopenloc = (inputstring.substring(currentloc, parentcloseloc + 1)).indexOf("(") + currentloc;
                            }
    
                            count++;
                        }
                        
                        output += " NL ]";
                    }
                    else if ((type == "Satellite") || (type == "Nucleus") || (type == "DUMMY"))
                    {
    
                        //Read name and 2 brackets of metatext to output (don't close quotation mark on name field yet - more text is to be added)
                        
                        //Decide what to do next on the basis of 2nd level type
                        if (type2 == "leaf")
                        {
                            var txt = inputstring.substring(inputstring.indexOf(type), (inputstring.substring(inputstring.indexOf(")") + 1, inputstring.length)).indexOf(")") + 2 + inputstring.indexOf(")"));
                            output += " NL  QU name QU  :  QU " + nodenum + "ENDNODENUM" + txt;
    
                            var contained_text_startloc = inputstring.indexOf("text _!") + 7;
                            var contained_text_endloc = (inputstring.substring(contained_text_startloc, inputstring.length)).indexOf("_!") + contained_text_startloc;
                            var contained_text = inputstring.substring(contained_text_startloc, contained_text_endloc);
                            //Close quotation mark on name field
    
                            var text_to_be_added = " | Text: " + contained_text + "  QU ";
                            output += text_to_be_added;
                        }
                        else if (type2 == "span")
                        {
                            //Read name and 2 brackets of metatext to output 
                            var txt = inputstring.substring(inputstring.indexOf(type), (inputstring.substring(inputstring.indexOf(")") + 1, inputstring.length)).indexOf(")") + 2 + inputstring.indexOf(")"));
                            output += " NL  QU name QU  :  QU " + nodenum + "ENDNODENUM" + txt + " QU ";
                            output += ", NL  QU children QU  :  NL [";
                            
                            //Call recursively on children 
                            //Set initial current location to just after 2nd bracket of metatext 
                            var currentloc = (inputstring.substring(inputstring.indexOf(")") + 1, inputstring.length)).indexOf(")") + 1 + inputstring.indexOf(")");
    
                            var parentcloseloc = find_closed_bracket(inputstring);
                            
                            //Find appropriate initial open location 
                            var childopenloc = (inputstring.substring(currentloc, parentcloseloc + 1)).indexOf("(") + currentloc;
                            //TODO: take into account quoted brackets? 
                            var done = 0;
                            var count = 0;
                            while (done != 1)
                            {
                                //Find and set childcloseloc 
                                var childcloseloc = find_closed_bracket(inputstring.substring(childopenloc, parentcloseloc + 1)) + childopenloc;
    
                                // Recursive call 
                                var childjsondata = recursiveread(inputstring.substring(childopenloc, childcloseloc + 1));
                                if (count > 0) 
                                {
                                    output += ",";
                                }
                                output += childjsondata;
    
                                //Set new currentloc to the location just after the closed bracket of the current child 
                                currentloc = childcloseloc + 1;
                                // Check if there are no more children of the parent 
                                if (((inputstring.substring(currentloc, parentcloseloc + 1)).indexOf("(")) == -1) 
                                {
                                    done = 1;
                                }
                                else
                                {
                                    //Set new childopenloc to the location of the next open bracket between the end of the current child's bracket and the end of the root's bracket 
                                    childopenloc = (inputstring.substring(currentloc, parentcloseloc + 1)).indexOf("(") + currentloc;
                                }
    
                                count++;
                            }
                            
                            output += " NL ]";
    
                        }
                        
                    }
                    
                    output += " NL }";
                    return output;
    }
    make_JSON_string(rhetoricParsingOutput)
    """.replace("document.write", "return ")

    result = js2py.eval_js(js)
    output_string = unicodedata.normalize('NFKD', result).encode('ascii', 'ignore')  # Normalize the unicode data
    output_string = output_string.replace(' NL ', '\n').replace(' QU ', '\"')  # replace back the encoded symbols for the JS to work
    if mode == 'script':
        return output_string
    elif mode == 'local':
        output_json = json.loads(output_string)  # Parse the json string
        return output_json


def strip_name(input_name):
    name = input_name.replace('(', '').replace(')', '').split()  # Remove ( ) and split by space
    node_type = name[0].split('ENDNODENUM')[1]  # Nucleus or Satellite
    node_edge = name[1]  # leaf or other
    node_number = name[2]  # leaf number
    node_relation = name[4]  # rel2par
    return [node_type, node_edge, node_number, node_relation]


def recursive_read_text(json_output, node_filter=None):
    text_output = ""
    if len(json_output) == 1:
        content = json_output['name']
        content = content.split('|')
        content_text = content[1][6:].strip()  # Leaf text
        content_leaf = content[0]
        [node_type, node_edge, node_number, node_relation] = strip_name(content_leaf)
        if node_filter is None:
            return text_output + ' ' + content_text
        elif node_filter == node_type:
            return text_output + ' ' + content_text
        else:
            return text_output
    text_output += recursive_read_text(json_output['children'][0], node_filter)
    if len(json_output['children']) > 1:
        text_output += recursive_read_text(json_output['children'][1], node_filter)
    return text_output


def recursive_read_list(json_output):
    nucleus_list = []
    if len(json_output) == 1:
        content = json_output['name']
        content = content.split('|')
        content_text = content[1][6:].strip()  # Leaf text
        content_leaf = content[0]
        [node_type, node_edge, node_number, node_relation] = strip_name(content_leaf)
        # nucleus_list.append((content_text, node_edge + node_number, node_type, node_relation))
        return content_text, node_edge + node_number, node_type, node_relation
    nucleus_list.append(recursive_read_list(json_output['children'][0]))
    nucleus_list.append(recursive_read_list(json_output['children'][1]))
    return nucleus_list


def find_nucleus_text(file_path='/home/tzvi/PycharmProjects/linuxDiscourse/src/Output/19_chief_executive_officer_ceo_review_strip_output.txt'):
    current_text = read_strip_output(file_path)  # Read the output file in the strip version
    output = run_javascript(current_text, 'local')  # Run the java script code to create an json string
    output_list = recursive_read_text(output, 'Nucleus')
    print(output_list)
    return output_list


# file_path='/home/tzvi/PycharmProjects/linuxDiscourse/src/Output/19_chief_executive_officer_ceo_review_strip_output.txt'
# print(sys.argv[1])
if __name__ == '__main__':
    print(run_javascript(read_strip_output(sys.argv[1])))

