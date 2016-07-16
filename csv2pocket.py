#! /usr/bin/env python

import webbrowser
import urllib
import urllib2
import json
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
    # TODO: save user_access_token to avoid making authorization again
    user_access_token = do_pocket_auth()

    # TODO: parse csv
    add_to_pocket(pocket_consumer_key, user_access_token,
                  "http://www.slashdot.org", "slashdot", "csv2pocket")

if __name__ == "__main__":
    main()
