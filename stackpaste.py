#!/usr/bin/env python3

import sys
import requests
import json

import re

from html.parser import HTMLParser

""" Thanks to https://github.com/rinas7/StackOverflowSnippets """


def unescape(lst):
    return HTMLParser().unescape(lst)


def get_snippets(text):
    code_start_tag = '<pre><code>'
    code_end_tag = '</code></pre>'
    snippets = []
    i = 0
    while True:
        start = text.find(code_start_tag, i)
        if start == -1:
            break
        end = text.find(
            code_end_tag, start + len(code_start_tag))
        if end == -1:
            break
        r = re.compile(r'^(>{3}|>|\.{3}) ', flags=re.M)
        snippet = unescape(text[start+len(code_start_tag):end])
        snippet = r.sub('', snippet)
        snippets.append(snippet)
        i = end
    return snippets


def error(msg):
    sys.stderr.write(msg + '\n')
    sys.exit(1)


def execute_line(line):
    match = re.search(r'/questions/(\d*)/', line)
    if not match:
        error('Wrong link (question id not found): {}'.format(line))
    question_id = match.group(1)
    query = "https://api.stackexchange.com/2.2/questions/{}/answers?order=desc&sort=activity&site=stackoverflow&filter=withbody" \
        .format(question_id)

    r = requests.get(query)
    if r.status_code != 200:
        error('API call failed: response code {}'.format(r.status_code))

    answers = json.loads(r.text)['items']

    # Get first answer id
    if len(answers) < 1:
        error('No answer found!')

    snippets = get_snippets(answers[0]['body'])
    if len(snippets) < 1:
        error('No code in first answer!')

    # TODO: smart selection of question/snippet
    # TODO: implement safe exec
    exec(snippets[0])


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Usage: {} <path to script>'.format(sys.argv[0]))
        sys.exit(2)

    with open(sys.argv[1], 'r') as f:
        source = f.readlines()

    # TODO: check each link here

    for line in source:
        execute_line(line)
