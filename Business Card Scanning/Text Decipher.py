# Imports
import re


def print_pattern(pattern):
    for i, element in enumerate(pattern):
        print(i, element)


def clear_duplicates(pattern):
    new_pattern = list(dict.fromkeys(pattern))
    return new_pattern


def caps_string(string):
    str_list = string.split()
    full_string = ''
    for i in range(len(str_list)):
        str_list[i] = str_list[i].capitalize()
        full_string += str_list[i] + ' '
    return full_string[:-1]


def caps_list(lst):
    for i in range(len(lst)):
        lst[i] = caps_string(lst[i])
    return lst


'''

Each pattern is composed of a template and an addon (prefix and/or suffix). When a new prefix, suffix, or template is
discovered, simply added it to the corresponding list (in RegEx syntax) and the algorithm will search for it. The 
algorithm also generates every possible combination with the new added feature. 

'''

# Email RegEx Patterns
email_templates = ['({}@{})']
email_prefixes = ['\w+\.\w+', '\w+', '\w+\.\w+\-\w+']
email_suffixes = ['\w+\.\w+', '\w+\.\w+\.\w+', '\w+\-\w+\.\w+']
email_addons = []
for prefix in email_prefixes:
    for suffix in email_suffixes:
        email_addons.append([prefix, suffix])

email_patterns = []
for template in email_templates:
    for addon in email_addons:
        email_patterns.append(template.format(addon[0], addon[1]))

email_patterns = clear_duplicates(email_patterns)

# Phone Number RegEx Patterns
phone_templates = ['({}\(\d+\)\s\d+\-\d+{})', '({}\d+.\d+.\d+{})', '({}\d+\s\d+\s\d+{})']
phone_prefixes = ['', '\+\d+\s', '\+\d+\.']
phone_suffixes = ['', '\s[x]\d+', '\s[x]\:\s\d+']
phone_addons = []
for prefix in phone_prefixes:
    for suffix in phone_suffixes:
        phone_addons.append([prefix, suffix])

phone_patterns = []
for template in phone_templates:
    for addon in phone_addons:
        phone_patterns.append(template.format(addon[0], addon[1]))

phone_patterns = clear_duplicates(phone_patterns)

# Name RegEx Patterns
name_patterns = ['(\w+\.\w+)@', '(\w+)@', '(\w+\.\w+\-\w+)@']

name_patterns = clear_duplicates(name_patterns)

# Company Name RegEx Patterns (Note: Contains three patterns)

# Searches for company name in the email
comp_email_patterns = ['@(\w+)\.\w+', '@(\w+\-\w+)\.\w+']
comp_email_patterns = clear_duplicates(comp_email_patterns)

# Checks if email contains public email urls
comp_exclude_templates = ['@(?:{})\.\w+']
comp_exclude_words = ['gmail', 'msn', 'outlook']
comp_exclude_patterns = []
for template in comp_exclude_templates:
    for word in comp_exclude_words:
        comp_exclude_patterns.append(template.format(word))
comp_exclude_patterns = clear_duplicates(comp_exclude_patterns)

# Searches for company if email contains public url
comp_search_templates = ['(\w+\s\w+\s(?:{}))', '(\w+\s(?:{}))']
comp_search_words = ['company', 'inc.', 'co.', 'corporation', 'corp.']
for word in comp_search_words:
    if word.find('.') != -1:
        comp_search_words.append(word.replace('.', ''))

comp_search_patterns = []
for template in comp_search_templates:
    for word in comp_search_words:
        comp_search_patterns.append(template.format(word))

comp_search_patterns = clear_duplicates(comp_search_patterns)

# Address RegEx Patterns
address_templates = ['(\d+\s\w+\s(?:{}))', '(\d+\s\w+\s\w+\s(?:{}))', '(\d+\s\w+\.\s\w+\s(?:{}))']
address_endings = ['road', 'street', 'avenue', 'boulevard', 'way', 'drive', 'lane', 'square', 'parkway', 'circle', 'rd',
                   'st', 'ave', 'blvd', 'dr', 'sq', 'pkwy']
address_patterns = []
for template in address_templates:
    for ending in address_endings:
        address_patterns.append(template.format(ending))

address_patterns = clear_duplicates(address_patterns)

# Website RegEx Patterns
website_templates = ['((?:www.)\w+(?:.{}))', '((?:www.)\w+(?:.{}/)\w+)', '((?:www.)\w+\-\w+(?:.{}))',
                     '((?:www.)\w+\-\w+(?:.{}/)\w+)']
website_suffixes = ['com', 'net', 'ca', 'org', 'gov']
website_patterns = []
for template in website_templates:
    for suffix in website_suffixes:
        website_patterns.append(template.format(suffix))

website_patterns = clear_duplicates(website_patterns)

# Location RegEx Patterns
location_patterns = ['san francisco, ca', 'denver, co', 'toronto, on', 'nashua, nh', 'albuquerque, nm', 'burbank, ca',
                     'wilmington, de', 'redwood city, ca', 'dunn, nc', 'fremont, ca', 'portland, tn', 'boulder, co']
locations_no_comma = []
for place in location_patterns:
    locations_no_comma.append(place.replace(',', ''))
location_patterns += locations_no_comma

location_patterns = clear_duplicates(location_patterns)

# Position RegEx Patterns
position_template_prefixes = ['(?:{})', '\w+']
position_template_suffixes = ['(?:{})', '\w+']
position_template_addons = []
for prefix in position_template_prefixes:
    for suffix in position_template_suffixes:
        position_template_addons.append([prefix, suffix])

for i, element in enumerate(position_template_addons):
    if element[0] == element[1] and element[0] == '\w+':
        del position_template_addons[i]

position_template_templates = ['({}\s{})', '({}\s\w+\s{})']
position_templates = []
for template in position_template_templates:
    for addon in position_template_addons:
        position_templates.append(template.format(addon[0], addon[1]))

position_templates = ['((?:{})\s(?:{}))', '((?:{})\s\w+\s(?:{}))']

position_prefixes = ['senior', 'director', 'manager', 'chief', 'lead', 'marketing', 'sales', 'vice', 'business']
position_suffixes = ['engineer', 'director', 'officer', 'scientist', 'consultant', 'research and development',
                     'research & development', 'operations', 'specialist', 'marketing', 'executive', 'development',
                     'analyst']
position_addons = []
for prefix in position_prefixes:
    for suffix in position_suffixes:
        position_addons.append([prefix, suffix])

position_patterns = []
for i, template in enumerate(position_templates):
    for addon in position_addons:
        #         if i == 0 or i == 3:
        position_patterns.append(template.format(addon[0], addon[1]))
#         elif i == 1 or i == 4:
#             position_patterns.append(template.format(addon[0]))
#         elif i == 2 or i == 5:
#             position_patterns.append(template.format(addon[1]))

position_patterns.append('(?:vice)\s(?:president)')
position_patterns.append('(?:president)')
position_patterns = clear_duplicates(position_patterns)

# Unit Number RegEx Patterns
unit_templates = ['(?:{})\s\d+\w+', '(?:{})\s\d+', '\d+\w+\s(?:{})', '\d+\s(?:{})']
unit_prefixes = ['rm.', 'rm', 'suite']
unit_suffixes = ['floor']

unit_patterns = []
for i, template in enumerate(unit_templates):
    if i == 0 or i == 1:
        for prefix in unit_prefixes:
            unit_patterns.append(template.format(prefix))
    elif i == 2 or i == 3:
        for suffix in unit_suffixes:
            unit_patterns.append(template.format(suffix))

unit_patterns = clear_duplicates(unit_patterns)

text = 'Hi\n' \
       'Bye'

lower_text = text.lower()
print(lower_text + '\n')


def decipher(patterns, string):
    # List to store all patterns pulled from string
    var_list = []
    # Looks for all possible patterns
    for i, pattern in enumerate(patterns):
        if re.search(pattern, string) != None:
            var_list.append(re.findall(pattern, string))

    #     print('1:', var_list)
    # Finds the longest strings since they contain the most information
    length = -1
    index = []
    var = []
    for i, num in enumerate(var_list):
        for j in range(len(num)):
            if len(num[j]) > length:
                length = len(num[j])
                index.append((i, j))
            elif len(num[j]) == length:
                index.append((i, j))

    # Removes elements if they were added to var_list before the longest
    for i in range(len(index)):
        var.append(var_list[index[i][0]][index[i][1]])
    #     print('2:', var)
    counter = 0
    for i, element in enumerate(var):
        if len(element) < length:
            counter += 1
    var = var[counter:]
    #     print('3:', var)

    # Removes duplicates
    unique_var = list(dict.fromkeys(var))
    var = unique_var
    #     print('4:', var)

    return var


emails = decipher(email_patterns, lower_text)

if len(emails) == 0:
    print('No emails found.')
else:
    print('Email:', emails)


phone_nums = decipher(phone_patterns, lower_text)
# Determines the fax number (only if "Fax:" is before the word)
if len(phone_nums) > 1:
    lower_text = text.lower()
    if re.search('fax', lower_text) != None:
        for i, num in enumerate(phone_nums):
            end = re.search(num, text).start()
            start = re.search('Fax', text).start()
            if start == end - 5 or start == end - 6:
                phone_nums[i] = 'Fax: ' + num

if len(phone_nums) == 0:
    print('No phone numbers found.')
else:
    print('Phone Number:', phone_nums)


address = decipher(address_patterns, lower_text)

if len(address) == 0:
    print('No address found.')
else:
    print('Address:', caps_list(address))

website = decipher(website_patterns, lower_text)
if len(website) == 0:
    # Assume email contains website url
    for email in emails:
        at_index = re.search('@', email).end()
        website = 'www.' + email[at_index:]
        print('No specific website url could be found, could we use', website, 'instead?', )
else:
    print('Website:', website)

location = decipher(location_patterns, lower_text)

if len(location) == 0:
    print('No location found.')
else:
    print('Locations:', caps_list(location))

# Finds the names per email
for i, email in enumerate(emails):
    name = decipher(name_patterns, email)

    # Replaces "." in email names with " "
    name[i] = re.sub('\.', ' ', name[i])

    # Splits the name into each word and capitalize
    name[i] = re.split('\s', name[i])
    for j, word in enumerate(name[i]):
        name[i][j] = word.capitalize()
    name[i] = ' '.join(name[i])

    # Checks if the email name is First Initial, Last Name
    first_initial = ''
    last_name = ''
    if name[i].find(' ') == -1:
        last_name = name[i][1:].lower()
        first_initial = name[i][:1].lower()
        if lower_text.find(last_name) != -1:
            end = re.search(last_name, lower_text).start()
            start = re.search(first_initial, lower_text).start()
            if start < end:
                name[i] = lower_text[start:end + len(last_name)]
                name[i] = caps_string(name[i])

    # Checks if the email has no space between names
    first_name = ''
    if name[i].find(' ') == -1:
        for j in range(len(name[i])):
            first_name = name[i][:j].lower()
            last_name = name[i][j:].lower()
            if re.search(first_name, lower_text) != None and re.search(last_name, lower_text) != None:
                if re.search(first_name, lower_text).end() + 1 == re.search(last_name, lower_text).start():
                    name[i] = first_name.capitalize() + ' ' + last_name.capitalize()

    if len(name) == 0:
        print('No name found.')
    else:
        print('Name:', name)

for i, email in enumerate(emails):
    comp_email = decipher(comp_email_patterns, email)
    comp_exclude = decipher(comp_exclude_patterns, email)
    if len(comp_exclude) > 0:
        comp_search = decipher(comp_search_patterns, lower_text)
        print('Company:', comp_search)
    else:
        # Checks if the email has no space between names (checks for two words and three words only)
        word_found = False
        if comp_email[i].find(' ') == -1:
            front_half = ''
            back_half = ''
            for j in range(len(comp_email[i]) - 1):
                front_half = comp_email[i][:j + 1].lower()
                back_half = comp_email[i][j + 1:].lower()
                full_word = front_half + ' ' + back_half
                if re.search(full_word, lower_text) != None:
                    comp_email[i] = front_half.capitalize() + ' ' + back_half.capitalize()
                    word_found = True
        if word_found == False:
            front = ''
            middle = ''
            end = ''
            for j in range(len(comp_email[i]) - 1):
                front = comp_email[i][:j + 1]
                for k in range(len(comp_email[i]) - j):
                    middle = comp_email[i][j + 1:k + 1]
                    end = comp_email[i][k + 1:]
                    full_word = front + ' ' + middle + ' ' + end
                    if re.search(full_word, lower_text) != None:
                        comp_email[i] = front.capitalize() + ' ' + middle.capitalize() + ' ' + end.capitalize()
                        word_found = True

        acronym = ''
        comp_acronym_search = []
        for comp in comp_email:
            if len(comp) < 5:
                copy = comp.upper()
                for letter in copy:
                    acronym += '[{}]\w+\s'.format(letter)
                comp_acronym_search = re.findall(acronym, text)
                for index, element in enumerate(comp_acronym_search):
                    comp_acronym_search[index] = element.replace('\n', ' ')

        if text.find(comp_email[i].upper()) != -1:
            comp_email[i] = comp_email[i].upper()

        if len(comp_acronym_search) != 0:
            print('Company:', comp_acronym_search)
        else:
            print('Company:', comp_email)


position = decipher(position_patterns, lower_text)

if len(position) == 0:
    print('No position found.')
else:
    print('Position:', caps_list(position))

unit = decipher(unit_patterns, lower_text)

if len(unit) == 0:
    print('No unit found.')
else:
    print('Unit:', caps_list(unit))