import requests
import sys
from datetime import datetime
from colored import stylize, fg

class Main:
    @staticmethod
    def format_console_date(date):
        # Formats the current date and time for console output
        return '[' + date.strftime('%A %m-%d-%Y %H-%M-%S') + ']'

class PlayerFinder:
    @staticmethod
    def fetch_all_servers():
        """
        Fetches the list of all active FiveM servers.

        Returns:
            list: A list of server data, including their IDs.
        """
        url = "https://servers-frontend.fivem.net/api/servers/"
        response = requests.get(url)

        if response.status_code != 200:
            raise Exception(f"Failed to fetch servers. Status Code: {response.status_code}")

        return response.json()["servers"]

    @staticmethod
    def search_player(player_name):
        """
        Searches for a player across all servers.

        Args:
            player_name (str): The name of the player to search for.

        Returns:
            list: A list of servers where the player is found.
        """
        servers = PlayerFinder.fetch_all_servers()
        matched_servers = []

        for server in servers:
            try:
                server_id = server["id"]
                server_data = PlayerFinder.fetch_server_details(server_id)

                # Check if the player is in the server's player list
                for player in server_data["players"]:
                    if player_name.lower() in player["name"].lower():
                        matched_servers.append({
                            "ip": server_data["ip"],
                            "hostname": server_data["hostname"],
                            "player_name": player["name"]
                        })

            except Exception as e:
                # Skip servers that fail
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
        response = requests.get(url)

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
           player locator
    ''', fg('red')))

    # Check for player name input
    if len(sys.argv) < 2:
        print(stylize("[ERROR] Missing player name!", fg('red')) +
              "\nUsage:\n  python3 main.py <player_name>")
        sys.exit(1)

    player_name = sys.argv[1]

    try:
        print(stylize(Main.format_console_date(datetime.today()), fg('yellow')) +
              stylize(f" Searching for player: {player_name}", fg('green')))

        # Search for the player
        results = PlayerFinder.search_player(player_name)

        if results:
            print(stylize("\n[RESULTS] Player found in the following servers:", fg('cyan')))
            for server in results:
                print(f"  - Server IP: {server['ip']}, Hostname: {server['hostname']}, Player Name: {server['player_name']}")
        else:
            print(stylize("\n[RESULTS] Player not found on any server.", fg('red')))

    except Exception as e:
        print(stylize(f"[ERROR] {str(e)}", fg('red')))
