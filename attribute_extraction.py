import csv
import urllib.parse
import string
import traceback
from random import shuffle
from tqdm import tqdm

STANDARD_HEADERS = ["Accept", "Accept-Charset", "Accept-Datetime", "Accept-Encoding", "Accept-Language",
                    "Access-Control-Request-Method", "Access-Control-Request-Headers", "Authorization", "Cache-Control", "Connection",
                    "Content-Length", "Content-MD5", "Content-Type", "Cookie",
                    "Date", "Expect", "From", "Host", "If-Match",
                    "If-Modified-Since", "If-None-Match", "If-Range", "If-Unmodified-Since", "Max-Forwards",
                    "Origin", "Pragma", "Proxy-Authorization", "Range", "Referer",
                    "TE", "User-Agent", "Upgrade", "Via", "Warning"]

# STANDARD_HEADERS=[]

def urldecode(url):
    return urllib.parse.unquote(url)


def read_file_text(filename):
    '''
    Read each line in file text
    Skip new line, only text line
    Return block of requests
    Each block is a request
    '''
    tmp_lines = []
    with open(filename, "r") as f:
        for line in f:
            if line is not '\n':
                tmp_lines.append(line.strip())
    blocks = []
    for x in range(0, len(tmp_lines)-1):
        if "HTTP/1.1" in tmp_lines[x]:
            line = []
            line.append(tmp_lines[x])
            for i in range(x+1, len(tmp_lines)-1):
                if "HTTP/1.1" not in tmp_lines[i]:
                    line.append(tmp_lines[i])
                else:
                    break
            blocks.append(line)
        else:
            pass
    return blocks


def extract_headers(child_block):
    '''
    Extract header
    Get header name and header value
    '''
    try:
        header_name = child_block.split(": ")[0]
        header_value = child_block.split(": ")[1]
    except Exception:
        # File format error
        header_name = child_block.split(":")[0]
        header_value = child_block.split(":")[1]
    return header_name, header_value


def normalize_request(block):
    '''
    Extract headers, method, url, params, value
    Return a request as dictionary
    '''
    headers = {}
    method = ""
    url = ""
    body = []
    http_version = ""
    params = {}
    parts = block[0].split(" ")
    (method, url, http_version) = (parts[0], parts[1], parts[2])
    if method == "GET":
        for h in range(1, len(block)):
            header_name, header_value = extract_headers(block[h])
            headers.update({header_name: header_value})
        if "?" in url:
            parts = url.split("?", 1)[1].split("&")
            for p in parts:
                try:
                    key = p.split("=")[0]
                    value = p.split("=")[1]
                    params.update({key: value})
                except Exception:
                    params.update({key: ""})
    else:
        for h in range(1, len(block) - 1):
            header_name, header_value = extract_headers(block[h])
            headers.update({header_name: header_value})
        body = block[-1]
        parts = block[-1].split("&")
        for p in parts:
            try:
                key = p.split("=")[0]
                value = p.split("=")[1]
                params.update({key: value})
            except Exception:
                params.update({key: ""})
    return {
        "method": method,
        "http_version": http_version,
        "headers": headers,
        "url": url,
        "params": params,
        "body": body
    }


def num_headers(request):
    '''
    Return number of headers
    '''
    return [len(request["headers"])]


def standard_headers_ratio(request):
    '''
    Count ratio of headers in STANDARD_HEADERS
    '''
    count = 0
    for header in request["headers"]:
        if header in STANDARD_HEADERS:
            count += 1
    return [count/len(request["headers"])]


def non_standard_headers_ratio(request):
    '''
    Count ratio of headers not in STANDARD_HEADERS
    '''
    count = 0
    for header in request["headers"]:
        if header not in STANDARD_HEADERS:
            count += 1
    return [count/len(request["headers"])]


def length_header(request):
    '''
    Return headers in STANDARD_HEADERS
    and its length
    '''
    lh = []
    for header in STANDARD_HEADERS:
        try:
            lh.append(len(request["headers"][header]))
        except Exception:
            # If not exist
            lh.append(-1)
    return lh


def printable_characters_ratio_header(request):
    '''
    Return ratio of printable charcters in headers
    in STANDARD_HEADERS
    '''
    pcrh = []
    for header in STANDARD_HEADERS:
        try:
            value = request["headers"][header]
            count = 0
            for c in value:
                if c in string.printable:
                    count += 1
            pcrh.append(count/len(value))
        except Exception:
            # If not exist
            pcrh.append(-1)
    return pcrh


def non_printable_characters_ratio_header(request):
    '''
    Return ratio of non-printable charcters in headers
    in STANDARD_HEADERS
    '''
    npcrh = []
    for header in STANDARD_HEADERS:
        try:
            value = request["headers"][header]
            count = 0
            for c in value:
                if c not in string.printable:
                    count += 1
            npcrh.append(count/len(value))
        except Exception:
            # If not exist
            npcrh.append(-1)
    return npcrh


def letter_ratio_header(request):
    '''
    Return letter ratio in headers in in STANDARD_HEADERS
    Letter is from a->z and A->Z
    '''
    lrh = []
    for header in STANDARD_HEADERS:
        try:
            value = request["headers"][header]
            count = 0
            for c in value:
                if c.isalpha():
                    count += 1
            lrh.append(count/len(value))
        except Exception:
            # If not exist
            lrh.append(-1)
    return lrh


def digit_ratio_header(request):
    '''
    Return digit ratio in headers in in STANDARD_HEADERS
    Digit is from 0->9
    '''
    drh = []
    for header in STANDARD_HEADERS:
        try:
            value = request["headers"][header]
            count = 0
            for c in value:
                if c.isdigit():
                    count += 1
            drh.append(count/len(value))
        except Exception:
            # If not exist
            drh.append(-1)
    return drh


def is_standard_header(request):
    '''
    Return if header is in STANDARD_HEADERS
    '''
    ish = []
    for header in STANDARD_HEADERS:
        try:
            request["headers"][header]
            ish.append(1)
        except Exception:
            ish.append(0)
    return ish


def is_persistent_connection(request):
    try:
        return [request["headers"]["Connection"]]
    except Exception:
        return [-1]


def content_type(request):
    '''
    Return MIME
    Only in POST requests 
    '''
    try:
        return [request["headers"]["Content-Type"]]
    except Exception:
        return [-1]


def length_body(request):
    '''
    Return Content-Length
    Only in POST requests 
    '''
    try:
        return [request["headers"]["Content-Length"]]
    except Exception:
        return [-1]


def printable_characters_ratio_body(request):
    if request["method"] == "GET":
        return [-1]
    count = 0
    for c in request["body"]:
        if c in string.printable:
            count += 1
    return [count/len(request["body"])]


def non_printable_characters_ratio_body(request):
    if request["method"] == "GET":
        return [-1]
    count = 0
    for c in request["body"]:
        if c not in string.printable:
            count += 1
    return [count/len(request["body"])]


def letter_ratio_body(request):
    if request["method"] == "GET":
        return [-1]
    letter_count = 0
    for c in request["body"]:
        if c.isalpha():
            letter_count += 1
    return [letter_count/len(request["body"])]


def digit_ratio_body(request):
    if request["method"] == "GET":
        return [-1]
    digit_count = 0
    for c in request["body"]:
        try:
            int(c)
            digit_count += 1
        except Exception:
            pass
    return [digit_count/len(request["body"])]


def printable_characters_ratio_path(request):
    url = urldecode(request["url"])
    count = 0
    for x in url:
        if x in string.printable:
            count += 1
    return [count/len(url)]


def non_printable_characters_ratio_path(request):
    url = urldecode(request["url"])
    count = 0
    for x in url:
        if x not in string.printable:
            count += 1
    return [count/len(url)]


def length_path(request):
    return [len(request["url"])]


def letter_ratio_path(request):
    letter_count = 0
    for char in request["url"]:
        if char.isalpha():
            letter_count += 1
    return [letter_count/len(request["url"])]


def digit_ratio_path(request):
    digit_count = 0
    for char in request["url"]:
        try:
            int(char)
            digit_count += 1
        except Exception:
            pass
    return [digit_count/len(request["url"])]


def num_segment(request):
    segs = request["url"].split("//")[1].split("/")
    return [len(segs)]


def is_file(request):
    if "." in request["url"].split("/")[-1]:
        return [1]
    else:
        return [0]


def file_extension(request):
    if is_file(request)[0] == 1:
        s = request["url"].split("?")[0].split(".")
        s.pop(0)
        return [".".join(s)]
    return [-1]


def num_parameters(request):
    return [len(request["params"])]


def length_query(request):
    try:
        return [len(request["url"].split("?")[1])]
    except Exception:
        return [0]


def letter_ratio_query(request):
    try:
        query = request["url"].split("?")[1]
        letter_count = 0
        for char in query:
            if char.isalpha():
                letter_count += 1
        return [letter_count/len(query)]
    except Exception:
        return [-1]


def digit_ratio_query(request):
    try:
        query = request["url"].split("?")[1]
        digit_count = 0
        for char in query:
            try:
                int(char)
                digit_count += 1
            except Exception:
                pass
        return [digit_count/len(query)]
    except Exception:
        return [-1]


def printable_characters_ratio_query(request):
    try:
        query = urldecode(request["url"].split("?", 1)[1])
        count = 0
        for x in query:
            if x in string.printable:
                count += 1
        return [count/len(query)]
    except Exception:
        return [-1]


def non_printable_characters_ratio_query(request):
    try:
        query = urldecode(request["url"].split("?", 1)[1])
        count = 0
        for x in query:
            if x not in string.printable:
                count += 1
        return [count/len(query)]
    except Exception:
        return [-1]


def method(request):
    return [request["method"]]


def symbol_ratio_path(request):
    pass


def symbol_ratio_body(request):
    pass


def num_line(request):
    pass


def num_word(request):
    pass


def id(request):
    pass


def symbol_ratio_header(request):
    pass


def symbol_ratio_query(request):
    pass


def read_data(file_name, request_type):
    requests = []
    blocks = read_file_text(file_name)
    for block in tqdm(blocks):
        request = normalize_request(block)
        requests.append(method(request) + length_path(request) + printable_characters_ratio_path(request) + non_printable_characters_ratio_path(request) + letter_ratio_path(request) + digit_ratio_path(request) + num_segment(request) + is_file(request) + file_extension(request) + num_parameters(request) + length_query(request) + printable_characters_ratio_query(request) + non_printable_characters_ratio_query(request) + letter_ratio_query(request) + digit_ratio_query(request) + num_headers(request) + standard_headers_ratio(request) + non_standard_headers_ratio(request)+ length_header(request) + printable_characters_ratio_header(request) + non_printable_characters_ratio_header(request) + letter_ratio_header(request) + digit_ratio_header(request)+ is_standard_header(request) + is_persistent_connection(request) + content_type(request) + length_body(request) + printable_characters_ratio_body(request) + non_printable_characters_ratio_body(request) + letter_ratio_body(request) + digit_ratio_body(request) + [request_type])
    return requests


def save_to_file(outfile, data):
    FIELD_NAMES = ["method", "length_path",
                   "printable_characters_ratio_path", "non_printable_characters_ratio_path", "letter_ratio_path",
                   "digit_ratio_path", "num_segment", "is_file", "file_extension", "num_parameters",
                   "length_query", "printable_characters_ratio_query", "non_printable_characters_ratio_query",
                   "letter_ratio_query", "digit_ratio_query", "num_headers",
                   "standard_headers_ratio", "non_standard_headers_ratio"]
    for h in STANDARD_HEADERS:
        FIELD_NAMES.append("length_header_" + h)
    for h in STANDARD_HEADERS:
        FIELD_NAMES.append("printable_characters_ratio_header_" + h)
    for h in STANDARD_HEADERS:
        FIELD_NAMES.append("non_printable_characters_ratio_header_" + h)
    for h in STANDARD_HEADERS:
        FIELD_NAMES.append("letter_ratio_header_" + h)
    for h in STANDARD_HEADERS:
        FIELD_NAMES.append("digit_ratio_header_" + h)
    for h in STANDARD_HEADERS:
        FIELD_NAMES.append("is_standard_header_" + h)
    FIELD_NAMES += ["is_persistent_connection", "content_type", "length_body", "printable_characters_ratio_body",
                    "non_printable_characters_ratio_body", "letter_ratio_body", "digit_ratio_body", "label"]
    with open(outfile, "w", newline="") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(FIELD_NAMES)
        for d in data:
            writer.writerow(d)

if __name__ == "__main__":
    anomalous_requests = read_data("anomalous_test.txt", 1)
    split = len(anomalous_requests)*10//7
    anomalous_requests_train = anomalous_requests[:split]
    anomalous_requests_test = anomalous_requests[split:]
    normal_requests_test = read_data("normal_test.txt", 0)
    normal_requests_train = read_data("normal_train.txt", 0)
    save_to_file("trainning.csv", anomalous_requests_train + normal_requests_train)
    save_to_file("testing.csv", anomalous_requests_test+normal_requests_test)