# Copyright (c) 2009 Upi Tamminen <desaster@gmail.com>
# See the COPYRIGHT file for more information


import getopt
import ipaddress
import os
import time

from twisted.internet import reactor, ssl
from twisted.python import compat, log
from twisted.web import client

from cowrie.core.artifact import Artifact
from cowrie.core.config import CowrieConfig
from cowrie.shell.command import HoneyPotCommand

commands = {}

CURL_HELP = """Usage: curl [options...] <url>
Options: (H) means HTTP/HTTPS only, (F) means FTP only
     --anyauth       Pick "any" authentication method (H)
 -a, --append        Append to target file when uploading (F/SFTP)
     --basic         Use HTTP Basic Authentication (H)
     --cacert FILE   CA certificate to verify peer against (SSL)
     --capath DIR    CA directory to verify peer against (SSL)
 -E, --cert CERT[:PASSWD] Client certificate file and password (SSL)
     --cert-type TYPE Certificate file type (DER/PEM/ENG) (SSL)
     --ciphers LIST  SSL ciphers to use (SSL)
     --compressed    Request compressed response (using deflate or gzip)
 -K, --config FILE   Specify which config file to read
     --connect-timeout SECONDS  Maximum time allowed for connection
 -C, --continue-at OFFSET  Resumed transfer offset
 -b, --cookie STRING/FILE  String or file to read cookies from (H)
 -c, --cookie-jar FILE  Write cookies to this file after operation (H)
     --create-dirs   Create necessary local directory hierarchy
     --crlf          Convert LF to CRLF in upload
     --crlfile FILE  Get a CRL list in PEM format from the given file
 -d, --data DATA     HTTP POST data (H)
     --data-ascii DATA  HTTP POST ASCII data (H)
     --data-binary DATA  HTTP POST binary data (H)
     --data-urlencode DATA  HTTP POST data url encoded (H)
     --delegation STRING GSS-API delegation permission
     --digest        Use HTTP Digest Authentication (H)
     --disable-eprt  Inhibit using EPRT or LPRT (F)
     --disable-epsv  Inhibit using EPSV (F)
 -D, --dump-header FILE  Write the headers to this file
     --egd-file FILE  EGD socket path for random data (SSL)
     --engine ENGINGE  Crypto engine (SSL). "--engine list" for list
 -f, --fail          Fail silently (no output at all) on HTTP errors (H)
 -F, --form CONTENT  Specify HTTP multipart POST data (H)
     --form-string STRING  Specify HTTP multipart POST data (H)
     --ftp-account DATA  Account data string (F)
     --ftp-alternative-to-user COMMAND  String to replace "USER [name]" (F)
     --ftp-create-dirs  Create the remote dirs if not present (F)
     --ftp-method [MULTICWD/NOCWD/SINGLECWD] Control CWD usage (F)
     --ftp-pasv      Use PASV/EPSV instead of PORT (F)
 -P, --ftp-port ADR  Use PORT with given address instead of PASV (F)
     --ftp-skip-pasv-ip Skip the IP address for PASV (F)
     --ftp-pret      Send PRET before PASV (for drftpd) (F)
     --ftp-ssl-ccc   Send CCC after authenticating (F)
     --ftp-ssl-ccc-mode ACTIVE/PASSIVE  Set CCC mode (F)
     --ftp-ssl-control Require SSL/TLS for ftp login, clear for transfer (F)
 -G, --get           Send the -d data with a HTTP GET (H)
 -g, --globoff       Disable URL sequences and ranges using {} and []
 -H, --header LINE   Custom header to pass to server (H)
 -I, --head          Show document info only
 -h, --help          This help text
     --hostpubmd5 MD5  Hex encoded MD5 string of the host public key. (SSH)
 -0, --http1.0       Use HTTP 1.0 (H)
     --ignore-content-length  Ignore the HTTP Content-Length header
 -i, --include       Include protocol headers in the output (H/F)
 -k, --insecure      Allow connections to SSL sites without certs (H)
     --interface INTERFACE  Specify network interface/address to use
 -4, --ipv4          Resolve name to IPv4 address
 -6, --ipv6          Resolve name to IPv6 address
 -j, --junk-session-cookies Ignore session cookies read from file (H)
     --keepalive-time SECONDS  Interval between keepalive probes
     --key KEY       Private key file name (SSL/SSH)
     --key-type TYPE Private key file type (DER/PEM/ENG) (SSL)
     --krb LEVEL     Enable Kerberos with specified security level (F)
     --libcurl FILE  Dump libcurl equivalent code of this command line
     --limit-rate RATE  Limit transfer speed to this rate
 -l, --list-only     List only names of an FTP directory (F)
     --local-port RANGE  Force use of these local port numbers
 -L, --location      Follow redirects (H)
     --location-trusted like --location and send auth to other hosts (H)
 -M, --manual        Display the full manual
     --mail-from FROM  Mail from this address
     --mail-rcpt TO  Mail to this receiver(s)
     --mail-auth AUTH  Originator address of the original email
     --max-filesize BYTES  Maximum file size to download (H/F)
     --max-redirs NUM  Maximum number of redirects allowed (H)
 -m, --max-time SECONDS  Maximum time allowed for the transfer
     --negotiate     Use HTTP Negotiate Authentication (H)
 -n, --netrc         Must read .netrc for user name and password
     --netrc-optional Use either .netrc or URL; overrides -n
     --netrc-file FILE  Set up the netrc filename to use
 -N, --no-buffer     Disable buffering of the output stream
     --no-keepalive  Disable keepalive use on the connection
     --no-sessionid  Disable SSL session-ID reusing (SSL)
     --noproxy       List of hosts which do not use proxy
     --ntlm          Use HTTP NTLM authentication (H)
 -o, --output FILE   Write output to <file> instead of stdout
     --pass PASS     Pass phrase for the private key (SSL/SSH)
     --post301       Do not switch to GET after following a 301 redirect (H)
     --post302       Do not switch to GET after following a 302 redirect (H)
     --post303       Do not switch to GET after following a 303 redirect (H)
 -#, --progress-bar  Display transfer progress as a progress bar
     --proto PROTOCOLS  Enable/disable specified protocols
     --proto-redir PROTOCOLS  Enable/disable specified protocols on redirect
 -x, --proxy [PROTOCOL://]HOST[:PORT] Use proxy on given port
     --proxy-anyauth Pick "any" proxy authentication method (H)
     --proxy-basic   Use Basic authentication on the proxy (H)
     --proxy-digest  Use Digest authentication on the proxy (H)
     --proxy-negotiate Use Negotiate authentication on the proxy (H)
     --proxy-ntlm    Use NTLM authentication on the proxy (H)
 -U, --proxy-user USER[:PASSWORD]  Proxy user and password
     --proxy1.0 HOST[:PORT]  Use HTTP/1.0 proxy on given port
 -p, --proxytunnel   Operate through a HTTP proxy tunnel (using CONNECT)
     --pubkey KEY    Public key file name (SSH)
 -Q, --quote CMD     Send command(s) to server before transfer (F/SFTP)
     --random-file FILE  File for reading random data from (SSL)
 -r, --range RANGE   Retrieve only the bytes within a range
     --raw           Do HTTP "raw", without any transfer decoding (H)
 -e, --referer       Referer URL (H)
 -J, --remote-header-name Use the header-provided filename (H)
 -O, --remote-name   Write output to a file named as the remote file
     --remote-name-all Use the remote file name for all URLs
 -R, --remote-time   Set the remote file's time on the local output
 -X, --request COMMAND  Specify request command to use
     --resolve HOST:PORT:ADDRESS  Force resolve of HOST:PORT to ADDRESS
     --retry NUM   Retry request NUM times if transient problems occur
     --retry-delay SECONDS When retrying, wait this many seconds between each
     --retry-max-time SECONDS  Retry only within this period
 -S, --show-error    Show error. With -s, make curl show errors when they occur
 -s, --silent        Silent mode. Don't output anything
     --socks4 HOST[:PORT]  SOCKS4 proxy on given host + port
     --socks4a HOST[:PORT]  SOCKS4a proxy on given host + port
     --socks5 HOST[:PORT]  SOCKS5 proxy on given host + port
     --socks5-hostname HOST[:PORT] SOCKS5 proxy, pass host name to proxy
     --socks5-gssapi-service NAME  SOCKS5 proxy service name for gssapi
     --socks5-gssapi-nec  Compatibility with NEC SOCKS5 server
 -Y, --speed-limit RATE  Stop transfers below speed-limit for 'speed-time' secs
 -y, --speed-time SECONDS  Time for trig speed-limit abort. Defaults to 30
     --ssl           Try SSL/TLS (FTP, IMAP, POP3, SMTP)
     --ssl-reqd      Require SSL/TLS (FTP, IMAP, POP3, SMTP)
 -2, --sslv2         Use SSLv2 (SSL)
 -3, --sslv3         Use SSLv3 (SSL)
     --ssl-allow-beast Allow security flaw to improve interop (SSL)
     --stderr FILE   Where to redirect stderr. - means stdout
     --tcp-nodelay   Use the TCP_NODELAY option
 -t, --telnet-option OPT=VAL  Set telnet option
     --tftp-blksize VALUE  Set TFTP BLKSIZE option (must be >512)
 -z, --time-cond TIME  Transfer based on a time condition
 -1, --tlsv1         Use TLSv1 (SSL)
     --trace FILE    Write a debug trace to the given file
     --trace-ascii FILE  Like --trace but without the hex output
     --trace-time    Add time stamps to trace/verbose output
     --tr-encoding   Request compressed transfer encoding (H)
 -T, --upload-file FILE  Transfer FILE to destination
     --url URL       URL to work with
 -B, --use-ascii     Use ASCII/text transfer
 -u, --user USER[:PASSWORD]  Server user and password
     --tlsuser USER  TLS username
     --tlspassword STRING TLS password
     --tlsauthtype STRING  TLS authentication type (default SRP)
 -A, --user-agent STRING  User-Agent to send to server (H)
 -v, --verbose       Make the operation more talkative
 -V, --version       Show version number and quit
 -w, --write-out FORMAT  What to output after completion
     --xattr        Store metadata in extended file attributes
 -q                 If used as the first parameter disables .curlrc
 """


class Command_curl(HoneyPotCommand):
    """
    curl command
    """

    limit_size = CowrieConfig.getint("honeypot", "download_limit_size", fallback=0)
    download_path = CowrieConfig.get("honeypot", "download_path")

    def start(self):
        try:
            optlist, args = getopt.getopt(
                self.args, "sho:O", ["help", "manual", "silent"]
            )
        except getopt.GetoptError as err:
            # TODO: should be 'unknown' instead of 'not recognized'
            self.write(f"curl: {err}\n")
            self.write(
                "curl: try 'curl --help' or 'curl --manual' for more information\n"
            )
            self.exit()
            return

        for opt in optlist:
            if opt[0] == "-h" or opt[0] == "--help":
                self.write(CURL_HELP)
                self.exit()
                return
            elif opt[0] == "-s" or opt[0] == "--silent":
                self.silent = True

        if len(args):
            if args[0] is not None:
                url = str(args[0]).strip()
        else:
            self.write(
                "curl: try 'curl --help' or 'curl --manual' for more information\n"
            )
            self.exit()
            return

        if "://" not in url:
            url = "http://" + url
        urldata = compat.urllib_parse.urlparse(url)

        outfile = None
        for opt in optlist:
            if opt[0] == "-o":
                outfile = opt[1]
            if opt[0] == "-O":
                outfile = urldata.path.split("/")[-1]
                if (
                    outfile is None
                    or not len(outfile.strip())
                    or not urldata.path.count("/")
                ):
                    self.write("curl: Remote file name has no length!\n")
                    self.exit()
                    return

        if outfile:
            outfile = self.fs.resolve_path(outfile, self.protocol.cwd)
            path = os.path.dirname(outfile)
            if not path or not self.fs.exists(path) or not self.fs.isdir(path):
                self.write(f"curl: {outfile}: Cannot open: No such file or directory\n")
                self.exit()
                return

        url = url.encode("ascii")
        self.url = url

        self.artifactFile = Artifact(outfile)
        # HTTPDownloader will close() the file object so need to preserve the name

        self.deferred = self.download(url, outfile, self.artifactFile)
        if self.deferred:
            self.deferred.addCallback(self.success, outfile)
            self.deferred.addErrback(self.error, url)

    def download(self, url, fakeoutfile, outputfile, *args, **kwargs):
        scheme: bytes
        try:
            parsed = compat.urllib_parse.urlparse(url)
            scheme = parsed.scheme
            host: str = parsed.hostname.decode("utf8")
            port: int = parsed.port or (443 if scheme == "https" else 80)
            if scheme != b"http" and scheme != b"https":
                raise NotImplementedError
        except Exception:
            self.errorWrite(
                f'curl: (1) Protocol "{scheme.encode("utf8")}" not supported or disabled in libcurl\n'
            )
            self.exit()
            return None

        # TODO: need to do full name resolution.
        if ipaddress.ip_address(host).is_private:
            self.errorWrite("curl: (6) Could not resolve host: {}\n".format(host))
            return None

        factory = HTTPProgressDownloader(
            self, fakeoutfile, url, outputfile, *args, **kwargs
        )
        out_addr = None
        if CowrieConfig.has_option("honeypot", "out_addr"):
            out_addr = (CowrieConfig.get("honeypot", "out_addr"), 0)

        if scheme == "https":
            context_factory = ssl.optionsForClientTLS(hostname=host)
            self.connection = reactor.connectSSL(
                host, port, factory, context_factory, bindAddress=out_addr
            )
        else:  # Can only be http
            self.connection = reactor.connectTCP(
                host, port, factory, bindAddress=out_addr
            )

        return factory.deferred

    def handle_CTRL_C(self):
        self.write("^C\n")
        self.connection.transport.loseConnection()

    def success(self, data, outfile):
        if not os.path.isfile(self.artifactFile.shasumFilename):
            log.msg("there's no file " + self.artifactFile.shasumFilename)
            self.exit()

        self.protocol.logDispatch(
            eventid="cowrie.session.file_download",
            format="Downloaded URL (%(url)s) with SHA-256 %(shasum)s to %(outfile)s",
            url=self.url,
            outfile=self.artifactFile.shasumFilename,
            shasum=self.artifactFile.shasum,
        )

        # Update the honeyfs to point to downloaded file if output is a file
        if outfile:
            self.fs.update_realfile(
                self.fs.getfile(outfile), self.artifactFile.shasumFilename
            )
            self.fs.chown(outfile, self.protocol.user.uid, self.protocol.user.gid)
        else:
            with open(self.artifactFile.shasumFilename, "rb") as f:
                self.writeBytes(f.read())

        self.exit()

    def error(self, error, url):

        log.msg(error.printTraceback())
        if hasattr(error, "getErrorMessage"):  # Exceptions
            errormsg = error.getErrorMessage()
        log.msg(errormsg)
        self.write("\n")
        self.protocol.logDispatch(
            eventid="cowrie.session.file_download.failed",
            format="Attempt to download file(s) from URL (%(url)s) failed",
            url=self.url,
        )
        self.exit()


class HTTPProgressDownloader(client.HTTPDownloader):
    """
    From http://code.activestate.com/recipes/525493/
    """

    totallength = 0
    currentlength = 0
    lastupdate = 0

    def __init__(self, curl, fakeoutfile, url, outfile, headers=None):
        client.HTTPDownloader.__init__(
            self,
            url,
            outfile,
            headers=headers,
            agent=b"curl/7.38.0",
            followRedirect=False,
        )
        self.status = None
        self.curl = curl
        self.fakeoutfile = fakeoutfile
        self.started = time.time()
        self.proglen = 0
        self.nomore = False

    def noPage(self, reason):
        """
        Called for non-200 responses
        """
        if self.status == b"304":
            client.HTTPDownloader.page(self, "")
        else:
            client.HTTPDownloader.noPage(self, reason)

    def gotHeaders(self, headers):
        if self.status == b"200":
            if b"content-length" in headers:
                self.totallength = int(headers[b"content-length"][0].decode())
            else:
                self.totallength = 0
            if b"content-type" in headers:
                self.contenttype = headers[b"content-type"][0].decode()
            else:
                self.contenttype = "text/whatever"
            self.currentlength = 0.0

            if self.curl.limit_size > 0 and self.totallength > self.curl.limit_size:
                log.msg(f"Not saving URL ({self.curl.url}) due to file size limit")
                self.fileName = os.path.devnull
                self.nomore = True

            if self.fakeoutfile:
                self.curl.write(
                    "  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current\n"
                )
                self.curl.write(
                    "                                 Dload  Upload   Total   Spent    Left  Speed\n"
                )

        return client.HTTPDownloader.gotHeaders(self, headers)

    def pagePart(self, data):
        if self.status == b"200":
            self.currentlength += len(data)

            # If downloading files of unspecified size, this could happen:
            if (
                not self.nomore
                and self.curl.limit_size > 0
                and self.currentlength > self.curl.limit_size
            ):
                log.msg("File limit reached, not saving any more data!")
                self.nomore = True
                self.file.close()
                self.fileName = os.path.devnull
                self.file = self.openFile(data)

            if (time.time() - self.lastupdate) < 0.5:
                return client.HTTPDownloader.pagePart(self, data)

            self.speed = self.currentlength / (time.time() - self.started)
            self.lastupdate = time.time()
        return client.HTTPDownloader.pagePart(self, data)

    def pageEnd(self):
        if self.totallength != 0 and self.currentlength != self.totallength:
            return client.HTTPDownloader.pageEnd(self)

        if self.fakeoutfile:
            self.curl.write(
                "\r100  {}  100  {}    0     0  {}      0 --:--:-- --:--:-- --:--:-- {}\n".format(
                    self.currentlength, self.currentlength, 63673, 65181
                )
            )
            self.curl.fs.mkfile(self.fakeoutfile, 0, 0, self.totallength, 33188)

        return client.HTTPDownloader.pageEnd(self)


commands["/usr/bin/curl"] = Command_curl
commands["curl"] = Command_curl
