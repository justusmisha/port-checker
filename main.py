import argparse
import asyncio
import subprocess
import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException

load_dotenv()

app = FastAPI()


async def get_connected_users(port: int) -> int:
    command = f"sudo netstat -tnp | grep ':{port}'"
    proc = await asyncio.create_subprocess_shell(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    stdout, stderr = await proc.communicate()

    if proc.returncode != 0:
        print(f"No connections found on port {port}.")
        return 0

    # Decode the output and split it into lines
    lines = stdout.decode().splitlines()

    # If no lines are found, log that no connections were found
    if not lines:
        print(f"No connections found on port {port}.")
        return 0

    # Extract unique IP addresses
    ip_addresses = set()
    for line in lines:
        # Split the line and extract the remote IP address
        parts = line.split()
        if len(parts) > 4:
            remote_ip = parts[4].split(':')[0]
            ip_addresses.add(remote_ip)

    return len(ip_addresses)


@app.get("/get_usage")
async def check_port(key: int, v: int = None, sh: int = None):
    secretkey = str(os.getenv("SECRETKEY"))
    try:
        if not key or key != secretkey:
            raise HTTPException(status_code=403)
        if v and sh:
            connected_users_v = await get_connected_users(v)
            connected_users_sh = await get_connected_users(sh)
            return {v: connected_users_v,
                    sh: connected_users_sh}
        elif v and sh is None:
            connected_users_v = await get_connected_users(v)
            return {v: connected_users_v}
        elif sh and v is None:
            connected_users_sh = await get_connected_users(sh)
            return {sh: connected_users_sh}
        else:
            return {'message': 'specify port'}

    except Exception as e:
        return {'error': str(e)}


# Main function to handle command-line arguments
def main():
    parser = argparse.ArgumentParser(description="Port Checker Program")
    parser.add_argument('-v', '--vless', type=int, help='vless port')
    parser.add_argument('-sh', '--shadowsocks', type=int, help='shadowsocks port')

    args = parser.parse_args()

    # Set default port values if not provided
    vless_port = args.vless if args.vless is not None else 8443
    shadowsocks_port = args.shadowsocks if args.shadowsocks is not None else 1080

    print(f"Checking VLESS port {vless_port}...")
    vless_users = asyncio.run(get_connected_users(vless_port))
    print(f"Number of users connected to VLESS port {vless_port}: {vless_users}")

    print(f"Checking Shadowsocks port {shadowsocks_port}...")
    shadowsocks_users = asyncio.run(get_connected_users(shadowsocks_port))
    print(f"Number of users connected to Shadowsocks port {shadowsocks_port}: {shadowsocks_users}")


if __name__ == "__main__":
    main()
