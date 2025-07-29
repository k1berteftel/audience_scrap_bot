import sqlite3


class database():
    def __init__(self, name):
        self.connection = sqlite3.connect(name)
        self.cursor = self.connection.cursor()

    def add_account(self, user_id: int, account: str) -> None:
        with self.connection:
            self.cursor.execute('INSERT INTO `accounts` (`user_id`, `account`) VALUES(?, ?)', (user_id, account,))

    def get_account(self, user_id: int) -> str | None:
        with self.connection:
            result = self.cursor.execute('SELECT `account` FROM `accounts` WHERE `user_id` = ?', (user_id, )).fetchmany(1)
        print(result)
        return result[0][0] if result else None

    def del_account(self, user_id: int):
        with self.connection:
            self.cursor.execute('DELETE FROM `accounts` WHERE `user_id` = ?', (user_id, ))

    def del_database(self):
        with self.connection:
            self.cursor.execute('DELETE FROM `accounts`')
