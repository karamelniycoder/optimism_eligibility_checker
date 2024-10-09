from loguru import logger
from time import sleep
from sys import stderr
import requests

from excel import Excel

logger.remove()
logger.add(stderr, format="<white>{time:HH:mm:ss}</white> | <level>{message}</level>")


def fetch_eligibility():
    r = requests.get("https://raw.githubusercontent.com/ethereum-optimism/op-analytics/refs/heads/main/reference_data/address_lists/op_airdrop_5_simple_list.csv")
    return r.text.split('\n')


if __name__ == "__main__":
    logger.info(f'Optimism Checker\n')

    zk_addresses = {
            wallet.split(',')[0].lower(): float(wallet.split(',')[1])
            for wallet in fetch_eligibility()
            if wallet not in ['address,op_total', '']
        }
    with open('addresses.txt') as f: addresses = f.read().splitlines()
    excel = Excel(total_len=len(addresses), name="optimism_checker")

    total_tokens = 0
    total_eligibility = 0
    wallets = []
    for address in addresses:
        tokens_reward = zk_addresses.get(address.lower(), 0)
        total_tokens += tokens_reward
        if tokens_reward:
            logger.success(f'[+] {address} ELIGIBLE {tokens_reward} OP')
            total_eligibility += 1
        else:
            logger.error(f'[-] {address} NOT ELIGIBLE')
        wallets.append([
            address,
            "Eligible" if tokens_reward else "Not Eligible",
            tokens_reward
        ])

    eligible_percent = str(round(total_eligibility / len(addresses) * 100, 2)) + "%"
    total_tokens = round(total_tokens, 2)
    eligible_count = f'[{total_eligibility}/{len(addresses)}]'

    wallets[0] += ["", f"Total tokens: {total_tokens} $OP"]
    wallets[1] += ["", f"Total eligible addresses: {eligible_count}"]
    excel.edit_table(wallet_data=wallets)

    sleep(0.1)
    print('')
    logger.info(
        f'Results saved in "results/{excel.file_name}"\n\n'
        f'Total eligibility: {eligible_percent} {eligible_count} with {total_tokens} $OP\n\n'
    )
    sleep(0.1)
    input('> Exit')
