#!/usr/bin/env python3
#
# Python/HTTPServer echo app publishing example.
# Will display HTTP request header and bodies.
# Showcases how to extract and validate app user tokens.
#
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from http.server import HTTPServer, BaseHTTPRequestHandler
from jwt import decode, get_unverified_header
from jwt.exceptions import InvalidTokenError
from pprint import pformat
import base64
import html
import json
import jwt
import os
import requests
import socket
import sys

class RequestHandler(BaseHTTPRequestHandler):

    def extract_token(self, headers):
        auth_header = headers.get('Authorization', '')
        return auth_header[7:] if auth_header.startswith('Bearer ') else None

    def verify_jwt_token(self, token):
        # Public key URL
        keycloak_domain = "http://keycloak-http.domino-platform" # Use the external domain if running the app on a remote data plane.
        jwks_url = f"{keycloak_domain}/auth/realms/DominoRealm/protocol/openid-connect/certs"

        # Retrieve JWKS (JSON Web Key Set) from URL
        jwks = requests.get(jwks_url).text
        jwks_dict = json.loads(jwks)

        # Get the key ID from the token header
        unverified_header = get_unverified_header(token)
        kid = unverified_header.get('kid')

        if not kid:
            raise ValueError("No 'kid' found in token header")

        # Find the corresponding public key
        public_key = None
        for key in jwks_dict['keys']:
            if key['kid'] == kid:
                x5c = key['x5c'][0]
                cert_bytes = x5c.encode('ascii')
                cert_der = base64.b64decode(cert_bytes)
                cert = x509.load_der_x509_certificate(cert_der, default_backend())
                public_key = cert.public_key()
                break

        if not public_key:
            raise ValueError(f"No public key found for kid: {kid}")

        # Convert the public key to PEM format
        pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )

        try:
            # Verify the token
            payload = jwt.decode(
                token,
                pem,
                algorithms=['RS256'],
                audience="apps",
                options={"verify_signature": True}
            )
            return payload
        except jwt.InvalidSignatureError:
            raise ValueError("Invalid signature")
        except jwt.ExpiredSignatureError:
            raise ValueError("Token has expired")
        except jwt.InvalidTokenError as e:
            raise ValueError(f"Invalid token: {str(e)}")

    def write(self, content):
        self.wfile.write(content.encode('utf-8'))

    def respond(self, verb):
        request_path = self.path
        request_headers = self.headers
        content_length = request_headers.get('content-length')
        length = int(content_length) if content_length else 0
        body = self.rfile.read(length).decode('utf-8')

        headers_string = "\n".join(f"{k}: {v}" for k, v in request_headers.items())
        headers_display = f'<textarea disabled cols="120">{html.escape(str(headers_string))}</textarea>'

        token = self.extract_token(request_headers)
        if token:
            token_display = f'<textarea disabled cols="120">{html.escape(token)}</textarea>'
            try:
                token_payload = self.verify_jwt_token(token)
                formatted_payload = pformat(token_payload, indent=2)
                payload_display = f'<textarea disabled cols="120">{html.escape(formatted_payload)}</textarea>'
            except Exception as e:
                payload_display = f"Token verification error: {html.escape(str(e))}"
        else:
            token_display = "Not present"
            payload_display = "Not present"

        body_display = f'<textarea disabled cols="120">{html.escape(body)}</textarea>' if body.strip() else "Not present"

        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()

        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Request Info</title>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; padding: 20px; }}
        h1 {{ color: #333; }}
        textarea {{ background-color: #f4f4f4; padding: 10px; border-radius: 5px; }}
    </style>
</head>
<body>
    <h1>Request Information</h1>
    <p><strong>Method:</strong> {html.escape(verb)}</p>
    <p><strong>URL:</strong> {html.escape(request_path)}</p>
    <h2>Request headers:</h2>
    {headers_display}
    <h2>Authorization token:</h2>
    {token_display}
    <h2>Token payload:</h2>
    {payload_display}
    <h2>Request Body:</h2>
    {body_display}
    <script>
    window.onload = function() {{
      var tx = document.getElementsByTagName('textarea');
      for (var i = 0; i < tx.length; i++) {{
        tx[i].setAttribute("style", "height:auto");
        tx[i].setAttribute("style", "height:" + tx[i].scrollHeight + 'px');
      }}
    }}
    </script>
</body>
</html>
"""
        self.write(html_content)

    def do_GET(self):
        self.respond("GET")

    def do_POST(self):
        self.respond("POST")

    def do_PUT(self):
        self.respond("PUT")

    def do_DELETE(self):
        self.respond("DELETE")

def log(message):
    sys.stdout.write(message)
    sys.stdout.write("\n")
    sys.stdout.flush()

def main():
    port = int(os.environ.get('PORT', 8888))
    log('Listening on localhost:%s' % port)
    server = HTTPServer(('localhost', port), RequestHandler)
    server.serve_forever()

if __name__ == "__main__":
    main()
