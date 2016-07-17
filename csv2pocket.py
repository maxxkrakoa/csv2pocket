#! /usr/bin/env python

import webbrowser
import urllib
import urllib2
import json
import ConfigParser
import os.path
import csv
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer

# app specific key
pocket_consumer_key = "56591-da2824b2f016fe024988b0c6"

# basic Pocket API endpoints
oauth_request_url = "https://getpocket.com/v3/oauth/request"
oauth_authorize_url = "https://getpocket.com/v3/oauth/authorize"
web_authorize_url = "https://getpocket.com/auth/authorize?request_token={}&redirect_uri={}"
pocket_add_url = "https://getpocket.com/v3/add"

# local webserver setup
redirect_uri = "http://localhost:{}/authorized"
port_number = 54321  # TODO: randomize this to avoid port collision

# user stuff
user_authorized_access = False

# config location
config_file = os.path.expanduser("~/.csv2pocket")


def set_user_authorized_access(b):
    global user_authorized_access
    user_authorized_access = b


def parse_response(resp):
    resp_content = resp.readlines()[0]
    values = {}
    splits = resp_content.split("&")
    for v in splits:
        v_split = v.split("=")
        values[v_split[0]] = v_split[1]
    return values


class getHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        set_user_authorized_access(True)
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        return


class PocketItem:
    """An item to put in Pocket"""

    def __init__(self, url, title, tags):
        self.url = url
        self.title = title
        self.tags = tags


def read_pocket_items_from_csv(csv_file_name):
    pocket_items = []

    with open(csv_file_name, "r") as csvfile:
        item_reader = csv.reader(csvfile)
        for row in item_reader:
            if (len(row) == 1):
                # just a url
                pocket_items.append(PocketItem(row[0], "", ""))
            elif (len(row) == 2):
                # url and title
                pocket_items.append(PocketItem(row[0], row[1], ""))
            else:  # assume len == 3
                # url and title and tags
                pocket_items.append(PocketItem(row[0], row[1], row[2]))
    return pocket_items


def do_pocket_auth():
    oauth_request_post_body = urllib.urlencode(
        {"consumer_key": pocket_consumer_key, "redirect_uri": redirect_uri})
    resp = urllib2.urlopen(oauth_request_url, oauth_request_post_body)
    if (resp.getcode() == 200):
        request_token = parse_response(resp)["code"]

        server = HTTPServer(("", port_number), getHandler)
        print "Started httpserver on port", port_number
        webbrowser.open(web_authorize_url.format(
            request_token, redirect_uri.format(port_number)))
        while (not user_authorized_access):
            server.handle_request()

        print "User access granted. Getting authorization token."

        oauth_authorize_post_body = urllib.urlencode(
            {"consumer_key": pocket_consumer_key, "code": request_token})
        resp = urllib2.urlopen(oauth_authorize_url, oauth_authorize_post_body)
        if (resp.getcode() == 200):
            resp_values = parse_response(resp)
            print "Authorized for user", resp_values["username"]
            user_access_token = resp_values["access_token"]
            return user_access_token
        else:
            print "An error happened during oauth authorize: " + resp.getcode()
            # TODO: print content of X-Error-Code header
    else:
        print "An error happened setting up oauth request: " + resp.getcode()
        # TODO: print content of X-Error-Code header


def add_to_pocket(pocket_consumer_key, user_access_token,
                  url, title, tags):
    print "Adding", url,
    pocket_add_post_body = json.dumps(
        {"consumer_key": pocket_consumer_key,
         "access_token": user_access_token,
         "url": url,
         "title": title,
         "tags": tags})
    req = urllib2.Request(pocket_add_url, pocket_add_post_body,
                          {'Content-Type': 'application/json'})
    resp = urllib2.urlopen(req)
    if (resp.getcode() == 200):
        # TODO: handle return data
        print " --- done"
    else:
        print " --- An error happened during add: " + resp.getcode()


def main():
    print "csv2pocket"

    if (os.path.exists(config_file)):
        # load user_access_token from file
        config = ConfigParser.RawConfigParser()
        config.readfp(open(config_file, "r"))
        user_access_token = config.get("main", "user_access_token")
    else:
        # authorize and save user_access_token to avoid making
        # authorization again
        user_access_token = do_pocket_auth()
        config = ConfigParser.RawConfigParser()
        config.add_section("main")
        config.set("main", "user_access_token", user_access_token)
        config.write(open(config_file, "w"))

    # parse csv and add each item to Pocket
    pocket_items = read_pocket_items_from_csv("test.csv")
    for p in pocket_items:
        # append csv2pocket tag to all items imported
        extended_tags = p.tags
        if (extended_tags == ""):
            extended_tags = "csv2pocket"
        else:
            extended_tags += ",csv2pocket"

        add_to_pocket(pocket_consumer_key, user_access_token,
                      p.url, p.title, extended_tags)


if __name__ == "__main__":
    main()
