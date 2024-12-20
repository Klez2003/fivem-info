import os
import requests
import sys
from datetime import datetime
from colored import stylize, fg


class Main:
    @staticmethod
    def format_console_date(date):
        # Formats the current date and time for console output
        return '[' + date.strftime('%A %m-%d-%Y %H-%M-%S') + ']'

    @staticmethod
    def get_args():
        # Retrieves command-line arguments passed to the script
        return sys.argv


class Resolver:
    @staticmethod
    def solve_link(target_id):
        """
        Fetches server data from the FiveM API using the target ID.

        Args:
            target_id (str): The unique identifier of the server.

        Returns:
            dict: A dictionary containing server information, players, and resources.
        """
        headers = {
            "accept": "application/json, text/plain, */*",
            "accept-language": "en-US,en;q=0.9",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36"
        }
        url = f"https://servers-frontend.fivem.net/api/servers/single/{target_id}"
        response = requests.get(url, headers=headers)

        # Check if the response is valid
        if response.status_code != 200:
            raise Exception(f"Failed to fetch server data. Status Code: {response.status_code}")

        data = response.json()

        # Extract relevant server data
        server_info = {
            "ip": data["Data"]["connectEndPoints"][0],  # Server IP address
            "hostname": data["Data"]["hostname"],  # Server hostname
            "players": [{"id": p["id"], "name": p["name"], "ping": p["ping"]} for p in data["Data"]["players"]],  # Player list
            "resources": data["Data"].get("resources", []),  # Server resources
            "max_clients": data["Data"].get("vars", {}).get("sv_maxClients", "Unknown"),  # Maximum clients allowed
        }
        return server_info

    @staticmethod
    def fetch_all_servers():
        """
        Fetches the list of all active FiveM servers.

        Returns:
            list: A list of server data, including their IDs.
        """
        url = "https://servers-frontend.fivem.net/api/servers/"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36",
            "Referer": "https://servers.fivem.net/"
        }

        response = requests.get(url, headers=headers)

        if response.status_code == 404:
            raise Exception("404 Not Found: The API endpoint or server data is not accessible.")

        if response.status_code != 200:
            raise Exception(f"Failed to fetch servers. Status Code: {response.status_code}")

        return response.json().get("servers", [])

    @staticmethod
    def search_player(player_name):
        """
        Searches for a player across all servers.

        Args:
            player_name (str): The name of the player to search for.

        Returns:
            list: A list of servers where the player is found.
        """
        try:
            servers = Resolver.fetch_all_servers()
        except Exception as e:
            print(stylize(f"[ERROR] {str(e)}", fg('red')))
            return []

        matched_servers = []

        for server in servers:
            try:
                server_id = server["id"]
                server_data = Resolver.fetch_server_details(server_id)

                # Check if the player is in the server's player list
                for player in server_data["players"]:
                    if player_name.lower() in player["name"].lower():
                        matched_servers.append({
                            "ip": server_data["ip"],
                            "hostname": server_data["hostname"],
                            "player_name": player["name"]
                        })

            except Exception as e:
                print(stylize(f"[WARNING] Failed to fetch data for server {server.get('id', 'Unknown')}: {str(e)}", fg('yellow')))
                continue

        return matched_servers

    @staticmethod
    def fetch_server_details(server_id):
        """
        Fetches server details including player list.

        Args:
            server_id (str): The unique ID of the server.

        Returns:
            dict: Server information and player list.
        """
        url = f"https://servers-frontend.fivem.net/api/servers/single/{server_id}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36",
            "Referer": "https://servers.fivem.net/"
        }
        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            raise Exception(f"Failed to fetch server details. Status Code: {response.status_code}")

        data = response.json()
        return {
            "ip": data["Data"]["connectEndPoints"][0],
            "hostname": data["Data"]["hostname"],
            "players": [{"name": p["name"], "id": p["id"], "ping": p["ping"]} for p in data["Data"]["players"]]
        }


if __name__ == '__main__':
    # Display script banner
    print(stylize('''
╔════════════════════════════════╗
║██╗  ██╗██╗     ███████╗███████╗║
║██║ ██╔╝██║     ██╔════╝╚══███╔╝║
║█████╔╝ ██║     █████╗    ███╔╝ ║
║██╔═██╗ ██║     ██╔══╝   ███╔╝  ║
║██║  ██╗███████╗███████╗███████╗║
║╚═╝  ╚═╝╚══════╝╚══════╝╚══════╝║
╚════════════════════════════════╝
           advanced server resolver
    ''', fg('red')))

    # Validate command-line arguments
    if len(sys.argv) < 2:
        print(stylize("""
    [ERROR] Bad command usage
        """, fg('red'), attr('underlined'))
              + """\nUsage:
                - python3 main.py <cfx.re-link>
        """)
        sys.exit(1)

    target_link = Main.get_args()[1]
    target_id = os.path.basename(target_link)

    try:
        # Retrieve server information
        server_data = Resolver.solve_link(target_id)

        # Display server information
        print(stylize(Main.format_console_date(datetime.today()), fg('yellow')) +
              stylize(" Target Info:", fg('green')))

        print(stylize(f"""
+-----------------------------------------------------+
|                  Server Info                        |
+-----------------------------------------------------+
|  Server IP: {server_data['ip']}
|  Hostname: {server_data['hostname']}
|  Max Clients: {server_data['max_clients']}
+-----------------------------------------------------+
|                  Player Info                        |
+-----------------------------------------------------+""", fg('cyan')))

        # Display each player's details
        for player in server_data['players']:
            print(stylize(f"  - ID: {player['id']} | Name: {player['name']} | Ping: {player['ping']}", fg('white')))

        # Display server resources
        print(stylize("""
+-----------------------------------------------------+
|                 Resources Info                      |
+-----------------------------------------------------+""", fg('magenta')))
        for resource in server_data['resources']:
            print(f"  - {resource}")

    except Exception as e:
        print(stylize(f"[ERROR] {str(e)}", fg('red')))
