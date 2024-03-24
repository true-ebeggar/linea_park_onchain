import random
import traceback
import warnings
from concurrent.futures import ThreadPoolExecutor, as_completed, wait, FIRST_COMPLETED
from eth_account import Account as Acccount
from sqlalchemy.exc import LegacyAPIWarning


from data.db import get_session, excel_to_sql
from staff import LineaTxnManager
from gas_staff.gas import *
from config import *

excel_to_sql('data/data.xlsx')
DBSession, Account = get_session()


def dummy_function_1(account_number, logger):
    logger.info(f"Performing dummy function 1 for account {account_number}")
    time.sleep(random.uniform(1, 5))

def dummy_function_2(account_number, logger):
    logger.info(f"Performing dummy function 2 for account {account_number}")
    time.sleep(random.uniform(1, 5))


def process_account(account_number, logger):
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", category=LegacyAPIWarning)
            with DBSession() as session:
                account = session.query(Account).get(account_number)
                if not account:
                    logger.error(f"Account number: {account_number} not found. Exiting process.")
                    return
                acc = Acccount.from_key(account.privatekey)
                manager = LineaTxnManager(account.privatekey, account.proxystring)

                tasks_action_map = {
                    # 'Task_101': dummy_function_2,
                    # 'Task_102': dummy_function_2,
                    # 'Task_103': dummy_function_1,
                    # 'Task_104': dummy_function_2,
                    # 'Task_201': dummy_function_1,
                    'Task_202': manager.mint_genesis_proof,
                    # 'Task_203': dummy_function_1,
                    # 'Task_204': dummy_function_2,
                    # 'Task_205': dummy_function_1,
                    # 'Task_206': dummy_function_2,
                    'Task_301': manager.mint_token_abyss_world,
                    'Task_302': manager.pictograph_wrap,
                    # 'Task_303': dummy_function_1,
                    'Task_304': manager.mint_satoshi_universe_battle_pass,
                    'Task_305': manager.check_in_yooldo,
                    'Task_401': manager.send_dmail_message,
                    'Task_402': manager.swap_on_gamic_dex,
                    'Task_403': manager.mint_emerald_enchanted_key,
                    'Task_404': manager.bit_avatar_wrap,
                    'Task_405': manager.read_on_curate,
                    'Task_406': manager.fire_moneygun_sending_me,
                    # 'Task_407': dummy_function_2,
                    # 'Task_408': dummy_function_1,
                    # 'Task_501': dummy_function_2,
                    'Task_502': manager.mint_tanuki_nft,
                    'Task_503': manager.mint2048,
                    # 'Task_504': dummy_function_1,
                    # 'Task_505': dummy_function_2,
                    # 'Task_506': dummy_function_1,
                    # 'Task_507': dummy_function_2,
                    'Task_508': manager.adopt_cat_call,
                    'Task_509': manager.mint_ultipilots,
                    'Task_601': manager.mint_NFTbadge,
                    'Task_602': manager.mint_battlemon,
                    'Task_603': manager.mint_nounce,
                    # 'Task_604': manager.mint_expedition_legacy,
                    # 'Task_605': dummy_function_1,
                    # 'Task_606': dummy_function_2,
                    # 'Task_607': dummy_function_1,
                    # 'Task_608': dummy_function_2,
                    # 'Task_609': dummy_function_1,
                    # 'Task_610': dummy_function_2,
                    # 'Task_611': dummy_function_1,
                    # 'Task_701': dummy_function_2,
                    # 'Task_702': dummy_function_1,
                    # 'Task_703': dummy_function_2,
                    # 'Task_704': dummy_function_1,
                    # 'Task_705': dummy_function_2,
                    # 'Task_706': dummy_function_1,
                    # 'Task_707': dummy_function_2,
                    # 'Task_708': dummy_function_1,
                    # 'Task_709': dummy_function_2,
                    # 'Task_710': dummy_function_1,
                    # 'Task_711': dummy_function_2,
                    # 'Task_801': dummy_function_1,
                    # 'Task_802': dummy_function_2,
                    # 'Task_803': dummy_function_1
                }

                tasks_list = list(tasks_action_map.items())
                random.shuffle(tasks_list)

                for column, action_function in tasks_list:
                    if getattr(account, column) == 0:
                        logger.info(f'{column} is incomplete, fixing it now...')
                        logger.info(
                            f'Acc {acc.address} going to execute {action_function.__name__} function')

                        gas_gate()
                        result = action_function()

                        if result == 1:
                            setattr(account, column, 1)
                            session.commit()
                            logger.success(f'{column} completed for account {acc.address}')
                            sleep = random.randint(MIN_SLEEP, MAX_SLEEP)
                            logger.info(f'Acc {acc.address} going to sleep for {sleep}-sec before continue')
                            time.sleep(sleep)
                        else:
                            logger.error(f'Failed to complete {column} for account {acc.address}')
                            continue
                    else:
                        continue

                logger.warning(f'it look like all possible action is done for account {acc.address}')
    except Exception as e:
        logger.critical(f"{e}")
        logger.critical(f"traceback: {traceback.format_exc()}")


def main():
    with DBSession() as session:
        accounts = session.query(Account).all()
        if SHUFFLE_ACCOUNTS:
            accounts = random.sample(accounts, len(accounts))

    with ThreadPoolExecutor(max_workers=MAX_THREAD) as executor:
        futures = []
        for account in accounts:
            future = executor.submit(process_account, account.account_number, logger)
            futures.append(future)

            s = random.randint(SLEEP_FOR_THREAD_MIN, SLEEP_FOR_THREAD_MAX)
            logger.info(f'Waiting for {s} seconds before starting the next thread.')
            time.sleep(s)

            if len(futures) >= MAX_THREAD:
                done, _ = wait(futures, return_when=FIRST_COMPLETED)
                futures = [f for f in futures if f not in done]

    for future in as_completed(futures):
        future.result()


if __name__ == "__main__":
    main()
    