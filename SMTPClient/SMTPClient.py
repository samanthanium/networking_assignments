#!/usr/bin/python3.8
import socket
import ssl
import re
from base64 import b64encode
from sys import exit


class SMTP_CLIENT:
    """ SMTP Client for sending mail primarily through Gmail (Networking studies project!)"""

    def __init__(self, name, receiver, message):
        self.receiver = receiver
        self.name = name
        self.message = message

        # AUTH only
        self.username = ''
        self.password = ''

        self._socket = None

        # The bool defines ESMTP availability
        self._mailservers = {
            'gmail': ('smtp.gmail.com', True)
        }

        self._ports = [22, 465, 587]

        self._commands = {
            # A tuple consisting of command and response code values respectively
            'helo': ('EHLO ' + self.name + '\r\n', '250'),
            'ehlo': ('EHLO ' + self.name + '\r\n', '250'),
            'starttls': ('STARTTLS\r\n', '220'),
            'auth': ('AUTH PLAIN ', '250'),
            'mail_from': ('MAIL FROM: <' + self.name + '>\r\n', '250'),
            'rcpt_to': ('RCPT TO: <' + self.receiver + '>\r\n', '250'),
            'data': ('DATA\r\n', '354'),
            'end_msg': ('\r\n.\r\n', '250'),
            'quit': ('QUIT\r\n', '221'),
        }

    @property
    def receiver(self):
        return self._receiver

    @receiver.setter
    def receiver(self, receiver):
        email_re = re.compile(r'^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w+$')
        if email_re.fullmatch(receiver) != None:
            self._receiver = receiver
        else:
            print("Receiver's address is invalid")
            exit()

    def _get_command(self, SMTP_command):
        """ Helper function for retrieving commands """
        return self._commands[SMTP_command.lower()]

    def _parse_SMTP_response(self, bytes_length):
        """ Receives and parses incoming response message """
        res = self._socket.recv(bytes_length).decode()
        print(res)
        # (CODE, MESSAGE) format
        return (res[:3], res[3:])

    def _send_SMTP_message(self, message):
        self._socket.send(message)
        return

    def _send_QUIT(self):
        self._socket.send(self._commands['quit'][0].encode())
        self._parse_SMTP_response(1024)
        exit()

    def _TLS_EHLO(self, hostname, port):
        # Create socket and connect
        if hostname in self._mailservers and self._mailservers[hostname][1]:
            self._socket = socket.create_connection(
                (self._mailservers[hostname][0], port))
            res_code, res_message = self._parse_SMTP_response(1024)
            try:
                # Establishing connection
                if res_code != '220':
                    self._send_QUIT()
                    return 1

                # EHLO
                ehlo = self._get_command('ehlo')
                self._send_SMTP_message(ehlo[0].encode())
                res_code, res_message = self._parse_SMTP_response(1024)
                if res_code != ehlo[1]:
                    self._send_QUIT()
                    return 1

                # STARTTLS
                ehlo = self._get_command('starttls')
                self._send_SMTP_message(ehlo[0].encode())
                res_code, res_message = self._parse_SMTP_response(1024)
                if res_code != ehlo[1]:
                    self._send_QUIT()
                    return 1

                # TLS Handshake
                context = ssl.create_default_context()
                tls_socket = context.wrap_socket(
                    self._socket, server_hostname=self._mailservers[hostname][0])
                self._socket = tls_socket

                # EHLO
                ehlo = self._get_command('ehlo')
                self._send_SMTP_message(ehlo[0].encode())
                res_code, res_message = self._parse_SMTP_response(1024)
                if res_code != ehlo[1]:
                    self._send_QUIT()
                    return 1

                # AUTH
                has_auth = re.search(r'AUTH\s(.+\s?)+?', res_message)
                # has_auth.group(1) returns the params for auth command
                if has_auth != None:
                    self.username = input('Username: ')
                    self.password = input('Password: ')
                    auth = self._get_command('auth')
                    self._send_SMTP_message(auth[0].encode())
                    self._send_SMTP_message(
                        b64encode(f'\0{self.username}\0{self.password}'.encode())+'\r\n'.encode())
                    res_code, res_message = self._parse_SMTP_response(1024)
                    if res_code != '235':
                        self._send_QUIT()
                        return 1

                return

            except Exception as e:
                print(e)

        else:
            print('Unsupported mailserver')
            return

    def send_mail(self, TLS=True):
        """ Main function the mail sending process """
        # Parse receiver hostname
        hostname = self.receiver.split('@')[1].split('.')[0]

        # Assign port number and negotiate TLS
        if TLS == True:
            port = self._ports[2]
            result = self._TLS_EHLO(hostname, port)

        else:
            # No TLS
            port = self._ports[1]
            # TODO: self._socket = self._HELO(hostname, port)

        # TODO: MAIL FROM
        mail_from = f'MAIL FROM: <{self.username}>\r\n'

        self._send_SMTP_message(mail_from.encode())
        res_code, res_message = self._parse_SMTP_response(1024)
        if res_code != '250':
            self._send_QUIT()
            return 1

        # TODO: RCPT TO
        rcpt_to = self._get_command('rcpt_to')
        self._send_SMTP_message(rcpt_to[0].encode())
        res_code, res_message = self._parse_SMTP_response(1024)
        if res_code != rcpt_to[1]:
            self._send_QUIT()
            return 1

        # TODO: DATA - use email module to form messages
        data = self._get_command('data')
        self._send_SMTP_message(data[0].encode())
        res_code, res_message = self._parse_SMTP_response(1024)
        if res_code != data[1]:
            self._send_QUIT()
            return 1

        # TODO: send data
        self._send_SMTP_message(f'{self.message}\r\n'.encode())

        end_msg = self._get_command('end_msg')
        self._send_SMTP_message(end_msg[0].encode())
        res_code, res_message = self._parse_SMTP_response(1024)
        if res_code != end_msg[1]:
            self._send_QUIT()
            return 1

        # TODO: QUIT
        self._send_QUIT
        # TODO: 221 closing response check

        # Every errors must be exited with QUIT

        # if error.code == 500 or 502: TLS=false || QUIT
        exit()


if __name__ == '__main__':
    name = input('Who are you?: ')
    receiver = input('Receiver email: ')
    message = input('Message: ')

    smtp = SMTP_CLIENT(name, receiver, message)
    smtp.send_mail()
