import time
import ts3

from pay2ban.exceptions import ClientNotConnectedException, ActionNotAllowedException


class TeamspeakConnection(object):
    def __init__(self, username, password):
        self.ts3conn = ts3.query.TS3Connection("10.0.0.10")
        try:
            self.ts3conn.login(
                client_login_name=username,
                client_login_password=password
            )
        except ts3.query.TS3QueryError as err:
            error = "Login failed:", err.resp.error["msg"]

        self.ts3conn.use(sid=1)

    def close(self):
        self.ts3conn.close()

    def list_users(self):
        # Note, that the client will wait for the response and raise a
        # **TS3QueryError** if the error id of the response is not 0.

        client_list_resp = self.ts3conn.clientlist(uid=True)
        channel_list_resp = self.ts3conn.channellist()

        if int(client_list_resp.error["id"]) != 0:
            error = "Error: " + client_list_resp.error["msg"]

        channels = []

        for channel in channel_list_resp.parsed:
            type = "normal"
            if "[cspacer" in channel['channel_name']:
                type = "spacer"

            channels.append({
                "name": channel['channel_name'],
                "cid": channel['cid'],
                "type": type,
                "clients": []
            })

        for client in client_list_resp.parsed:
            if int(client["client_type"]) == 0:
                for channel in channels:
                    if client["cid"] == channel["cid"]:
                        channel["clients"].append({
                            "name": client["client_nickname"],
                            "cui": client["client_unique_identifier"]
                        })
                        break

        return channels

    def kick_user(self, cui, reason="You were kicked by pay2ban.nickolaj.com"):
        clid = self.clid_from_cui(cui)
        self.ts3conn.clientkick(clid=clid, reasonid=5, reasonmsg=reason)

    def ban_user(self, cui, minutes, reason="You were banned by pay2ban.nickolaj.com"):
        self.ts3conn.banadd(uid=cui, time=int(minutes*60), banreason=reason)

    def clid_from_cui(self, cui):
        client_list_resp = self.ts3conn.clientlist(uid=True)

        for client in client_list_resp.parsed:
            if cui == client["client_unique_identifier"]:
                return client["clid"]

        raise ClientNotConnectedException("Client not connected")

    def cdbid_from_cui(self, cui):
        client_list_resp = self.ts3conn.clientlist(uid=True)

        for client in client_list_resp.parsed:
            if cui == client["client_unique_identifier"]:
                return client["client_database_id"]

        raise ClientNotConnectedException("Client not connected")

    def name_from_cui(self, cui):
        client_list_resp = self.ts3conn.clientlist(uid=True)

        for client in client_list_resp.parsed:
            if cui == client["client_unique_identifier"]:
                return client["client_nickname"]

        raise ClientNotConnectedException("Client not connected")

    def mute(self, cdbid):
        try:
            self.ts3conn.servergroupaddclient(sgid=13, cldbid=cdbid)
        except ts3.query.TS3QueryError:
            raise ActionNotAllowedException("Client Already Muted")

    def unmute(self, cdbid):
        try:
            self.ts3conn.servergroupdelclient(sgid=13, cldbid=cdbid)
        except ts3.query.TS3QueryError:
            raise ActionNotAllowedException("Client Already Unmuted")
